#!/usr/bin/env python3
"""
YAPS Risk Engine — evaluates a Privacy Card JSON against the YAPS rule set
and produces a traffic-light risk report.

Schema support: 2.0 (current). 1.0 / 1.1 / 1.2 cards are auto-migrated in
memory before evaluation; use migrate_1_2_to_2_0.py for on-disk migration.

Usage:
    python risk_engine.py <card.json> [--rules <rules.yaml>] [--output <report.md>] [--full]

Options:
    --rules     Path to rules.yaml (default: ../rules/rules.yaml relative to this script)
    --output    Write report to this Markdown file instead of stdout
    --full      Evaluate all rules even after a RED finding
    --no-migrate  Refuse to evaluate non-2.0 cards (raises an error). Default is
                  to auto-migrate 1.x cards in memory with a warning.

Exit codes:
    0 — GREEN (no AMBER or RED findings)
    1 — AMBER (one or more AMBER findings, no RED)
    2 — RED   (one or more RED findings)
    3 — Error (invalid card, missing rules file, etc.)
"""

import argparse
import json
import sys
import textwrap
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(3)


SEVERITY_ORDER = {"RED": 3, "AMBER": 2, "GREEN": 1, "INFO": 0}
SEVERITY_EMOJI = {"RED": "🔴", "AMBER": "🟡", "GREEN": "🟢", "INFO": "ℹ️"}


# ─── Card accessor helpers ────────────────────────────────────────────────────

def _primitive_ids(card: dict) -> list[str]:
    return [c.get("primitive_id", "") for c in card.get("pet_components", [])]

def has_primitive(card: dict, pid: str) -> bool:
    return pid in _primitive_ids(card)

def primitive_status(card: dict, pid: str) -> str | None:
    for c in card.get("pet_components", []):
        if c.get("primitive_id") == pid:
            return c.get("implementation_status")
    return None

def has_pairing(card: dict, pid: str) -> bool:
    return card.get("architecture_pattern", {}).get("pairing_ref") == pid

def has_stack(card: dict, sid: str) -> bool:
    return card.get("architecture_pattern", {}).get("stack_ref") == sid

def sector_is(card: dict, sid: str) -> bool:
    return card.get("deployment_context", {}).get("sector_ref") == sid

def scale_is(card: dict, s: str) -> bool:
    return card.get("deployment_context", {}).get("scale") == s

# ─── DP variant awareness (schema 1.1) ────────────────────────────────────────

def has_dp_variant(card: dict, variant: str) -> bool:
    """variant in {'local', 'central', 'family'}.
    - 'local'   → DP-L is present
    - 'central' → DP-C is present
    - 'family'  → any of DP, DP-L, DP-C is present (legacy compatibility)
    """
    ids = _primitive_ids(card)
    if variant == "local":
        return "DP-L" in ids
    if variant == "central":
        return "DP-C" in ids
    if variant == "family":
        return any(p in ids for p in ("DP", "DP-L", "DP-C"))
    return False

def has_any_dp(card: dict) -> bool:
    """Convenience: any form of DP is present (DP family or specific variant)."""
    return has_dp_variant(card, "family")

# ─── Stepwise-chain accessors (schema 1.1) ────────────────────────────────────

def _steps(card: dict) -> list[dict]:
    return card.get("stepwise_chain") or []

def has_steps(card: dict) -> bool:
    return len(_steps(card)) > 0

def step_count(card: dict) -> int:
    return len(_steps(card))

def each_step_has(card: dict, field: str) -> bool:
    """True if every step has a non-empty value for `field`."""
    steps = _steps(card)
    if not steps:
        return False
    return all(bool(s.get(field)) for s in steps)

def step_addresses_ep(card: dict, ep_id: str) -> bool:
    return any(s.get("exposure_problem_ref") == ep_id for s in _steps(card))

def final_residual_declared(card: dict) -> bool:
    steps = _steps(card)
    if not steps:
        return False
    return bool(steps[-1].get("residual_risk"))

def step_pets_match_components(card: dict) -> bool:
    """Every PET added in any step appears in pet_components (except 'none')."""
    pet_ids = set(_primitive_ids(card))
    for s in _steps(card):
        added = s.get("pet_added")
        if added is None or added == "none":
            continue
        if isinstance(added, str):
            if added not in pet_ids:
                return False
        elif isinstance(added, list):
            for p in added:
                if p not in pet_ids:
                    return False
    return True

# ─── Exposure-problem (T0) accessors (schema 1.1) ─────────────────────────────

def declares_exposure_problem(card: dict, ep_id: str | None = None) -> bool:
    """If ep_id is provided, check whether the card declares that specific EP
    (either at card level or in any step). If None, returns True if any EP
    declaration is present anywhere on the card."""
    card_eps = card.get("exposure_problem_refs") or []
    step_eps = [s.get("exposure_problem_ref") for s in _steps(card) if s.get("exposure_problem_ref") and s.get("exposure_problem_ref") != "baseline"]
    all_eps = set(card_eps) | set(step_eps)
    if ep_id is None:
        return len(all_eps) > 0
    return ep_id in all_eps

# ─── Jurisdictional-context accessors (schema 1.1) ────────────────────────────

def has_jurisdictional_context(card: dict) -> bool:
    jc = card.get("jurisdictional_context") or {}
    return bool(jc.get("data_subjects") or jc.get("controllers") or jc.get("operators"))

def declares_jurisdiction(card: dict, role: str, jurisdiction: str) -> bool:
    """role in {'data_subjects', 'controllers', 'operators'}; jurisdiction is the value to match."""
    jc = card.get("jurisdictional_context") or {}
    return jurisdiction in (jc.get(role) or [])

def is_cross_jurisdictional(card: dict) -> bool:
    """True if data_subjects, controllers, and operators are not all in the same single jurisdiction."""
    jc = card.get("jurisdictional_context") or {}
    subjects = set(jc.get("data_subjects") or [])
    controllers = set(jc.get("controllers") or [])
    operators = set(jc.get("operators") or [])
    all_juris = subjects | controllers | operators
    if len(all_juris) <= 1:
        return False
    # cross-jurisdictional if any role-pair has disjoint sets and total set > 1
    return True

# ─── Framework alignment ──────────────────────────────────────────────────────

def aligns_to_framework(card: dict, name: str) -> bool:
    frameworks = card.get("governance_controls", {}).get("frameworks_applied", []) or []
    return any(name.lower() in (f.get("framework", "").lower()) for f in frameworks)

# ─── Risk-calibration block (schema 1.2) ──────────────────────────────────────

def has_risk_calibration(card: dict) -> bool:
    """True iff the optional risk_calibration block exists and has at least one
    field set. An empty {} or absent block both return False."""
    rc = card.get("risk_calibration") or {}
    return any(v not in (None, "", {}, []) for v in rc.values())

def risk_calibration_field(card: dict, name: str):
    """Return a top-level risk_calibration field value, or None."""
    rc = card.get("risk_calibration") or {}
    return rc.get(name)

def attack_target_field(card: dict, name: str):
    """Return a nested risk_calibration.design_target.attack_target.<name> value,
    or None. Reads the 2.0 path; 1.x cards are auto-migrated before evaluation
    so this accessor sees the canonical 2.0 structure either way."""
    dt = (card.get("risk_calibration") or {}).get("design_target") or {}
    at = dt.get("attack_target") or {}
    return at.get(name)


# ─── Schema 2.0 accessors ─────────────────────────────────────────────────────

def card_schema_version(card: dict) -> str:
    return card.get("schema_version", "1.0")

def threat_profile(card: dict) -> str | None:
    """The 2.0 risk_calibration.threat_profile field."""
    return (card.get("risk_calibration") or {}).get("threat_profile")

def design_target_field(card: dict, name: str):
    """risk_calibration.design_target.<name> in 2.0."""
    dt = (card.get("risk_calibration") or {}).get("design_target") or {}
    return dt.get(name)

def accountant_field(card: dict, name: str):
    """risk_calibration.accountant.<name> in 2.0."""
    ac = (card.get("risk_calibration") or {}).get("accountant") or {}
    return ac.get(name)

def empirical_audit_field(card: dict, name: str):
    """risk_calibration.empirical_audit.<name> in 2.0."""
    ea = (card.get("risk_calibration") or {}).get("empirical_audit") or {}
    return ea.get(name)

def measured_advantage_field(card: dict, name: str):
    """risk_calibration.measured_advantage.<name> in 2.0."""
    ma = (card.get("risk_calibration") or {}).get("measured_advantage") or {}
    return ma.get(name)

def measured_exceeds_target(card: dict) -> bool:
    """True iff measured_advantage.value > design_target.attack_target.target_advantage."""
    measured = measured_advantage_field(card, "value")
    target = attack_target_field(card, "target_advantage")
    if measured is None or target is None:
        return False
    try:
        return float(measured) > float(target)
    except (TypeError, ValueError):
        return False

def has_device_class(card: dict, dclass: str) -> bool:
    """Any pet_components entry has the given device_class."""
    return any(c.get("device_class") == dclass for c in card.get("pet_components", []))

def device_classes(card: dict) -> list[str]:
    return [c.get("device_class") for c in card.get("pet_components", []) if c.get("device_class")]

def step_trust_zones(card: dict) -> list[str]:
    return [s.get("trust_zone") for s in _steps(card) if s.get("trust_zone")]

def tee_component_has_attestation(card: dict) -> bool:
    """True iff every deployed TEE component carries attestation_evidence.
    Returns True vacuously if there are no TEE components."""
    tee_components = [c for c in card.get("pet_components", []) if c.get("primitive_id") == "TEE"]
    deployed_tee = [c for c in tee_components if c.get("implementation_status") == "deployed"]
    if not deployed_tee:
        return True
    return all(c.get("attestation_evidence") for c in deployed_tee)

def evidence_class_of_artefact(card: dict, fragment: str) -> str | None:
    """Find an artefact whose name contains `fragment` and return its evidence_class."""
    fragment = fragment.lower()
    for a in _artefact_list(card):
        if fragment in a.get("artefact", "").lower():
            ev = a.get("evidence") or {}
            return ev.get("evidence_class")
    return None

def any_reproducible_only_evidence(card: dict) -> bool:
    """True iff any required_artefact has evidence_class == 'reproducible-record'.
    Drives RISKCAL-004 (silent rule that fires AMBER when the threat profile
    indicates a stronger class is needed)."""
    for a in _artefact_list(card):
        ev = a.get("evidence") or {}
        if ev.get("evidence_class") == "reproducible-record":
            return True
    return False

def cps_subject_type(card: dict) -> str | None:
    return (card.get("deployment_context") or {}).get("cps_subject_type")


def dp_has_parameter_manifest(card: dict) -> bool:
    """True if every DP-family pet_component carries the parameters that make
    its DP claim auditable: epsilon (any synonym), delta, noise mechanism,
    clipping norm.

    Schema-2.0-native equivalent of the legacy ASSUR-003 'parameter manifest'
    artefact check. Reads from pet_components[].parameters so that cards
    don't need a separately-listed artefact entry to satisfy the rule.
    """
    dp_components = [
        c for c in card.get("pet_components", [])
        if c.get("primitive_id") in ("DP", "DP-L", "DP-C")
    ]
    if not dp_components:
        return True   # Vacuously satisfied — no DP means no manifest required.

    # Synonyms a card may use for epsilon. We tolerate either flat (epsilon)
    # or qualified (epsilon_design_target) since both appear in the wild.
    epsilon_keys = {"epsilon", "epsilon_design_target", "eps"}
    delta_keys = {"delta"}
    noise_keys = {"noise_mechanism", "noise"}
    clip_keys = {"clipping_norm", "clip_norm", "c"}

    def _has_any(d: dict, keys: set[str]) -> bool:
        return any(k in d for k in keys)

    for c in dp_components:
        params = c.get("parameters") or {}
        if not (
            _has_any(params, epsilon_keys)
            and _has_any(params, delta_keys)
            and _has_any(params, noise_keys)
            and _has_any(params, clip_keys)
        ):
            return False
    return True


# ─── 1.x → 2.0 in-memory migration ────────────────────────────────────────────

def _migrate_card_1_2_to_2_0(card: dict) -> tuple[dict, list[str]]:
    """In-memory migration of a 1.x card to the 2.0 structure. Returns a tuple
    (migrated_card, warnings). Idempotent for 2.0 cards (returns them unchanged
    with no warnings).

    The migration is conservative: it adds the new required fields with safe
    defaults, restructures risk_calibration if present, wraps bare evidence_ref
    strings in evidence_reference objects, and leaves everything else alone.

    Migration policy decisions (documented in MIGRATION_NOTES.md):
      * Default evidence_class for any wrapped bare string: 'reproducible-record'.
        This is the "silent default" — RISKCAL-004 fires AMBER if the threat
        profile demands stronger.
      * Default threat_profile when risk_calibration is present but the field
        is absent: 'honest-but-curious-server'. This is the most common case
        in the FL literature [Carlini 2022 §6; Boenisch 2023 §5].
      * 'MIA' is widened to 'MIA-per-record' (the 1.2 default semantics).
    """
    version = card.get("schema_version", "1.0")
    if version == "2.0":
        return card, []

    import copy
    migrated = copy.deepcopy(card)
    warnings: list[str] = []

    # 1) bump schema_version
    migrated["schema_version"] = "2.0"
    warnings.append(f"schema_version: {version} → 2.0 (in-memory)")

    # 2) restructure risk_calibration if present
    rc = migrated.get("risk_calibration")
    if rc:
        new_rc: dict = {}

        # 2.0 makes threat_profile required.
        new_rc["threat_profile"] = "honest-but-curious-server"
        warnings.append("risk_calibration.threat_profile defaulted to 'honest-but-curious-server'")

        # 2a) design_target — pull from 1.x flat fields
        design_target: dict = {}
        if rc.get("mu_dp") is not None:
            design_target["mu_dp"] = rc["mu_dp"]
        old_at = rc.get("attack_target") or {}
        if old_at:
            at = {}
            attack = old_at.get("attack")
            if attack == "MIA":
                at["attack"] = "MIA-per-record"
                warnings.append("risk_calibration.attack_target.attack: 'MIA' → 'MIA-per-record'")
            elif attack:
                at["attack"] = attack
            for k in ("target_advantage", "target_fpr", "target_fnr"):
                if old_at.get(k) is not None:
                    at[k] = old_at[k]
            if at:
                design_target["attack_target"] = at
        if design_target:
            new_rc["design_target"] = design_target

        # 2b) accountant — 1.x had no formal block; if old measured fields existed under attack_target.measured_*, leave them be (engine reads new path; 1.2's measured_epsilon-style fields were card-author conventions, not schema)
        # We don't try to fabricate accountant from nothing.

        # 2c) measured_advantage — pull from old attack_target.measured_advantage and evidence_ref
        if old_at.get("measured_advantage") is not None or old_at.get("evidence_ref"):
            ma: dict = {}
            if old_at.get("measured_advantage") is not None:
                ma["value"] = old_at["measured_advantage"]
            ma["attack_method"] = "other"   # unknown in 1.x; reviewer fills in
            if old_at.get("evidence_ref"):
                ma["evidence"] = {
                    "location": old_at["evidence_ref"],
                    "evidence_class": "reproducible-record",
                }
                warnings.append(f"measured_advantage.evidence wrapped from bare string ('{old_at['evidence_ref']}')")
            new_rc["measured_advantage"] = ma

        # 2d) trade_off_curve — wrap bare string
        if rc.get("trade_off_curve_ref"):
            new_rc["trade_off_curve"] = {
                "location": rc["trade_off_curve_ref"],
                "evidence_class": "reproducible-record",
            }

        # 2e) pass-through scalars
        for k in ("operational_interpretation", "source_library", "notes"):
            if rc.get(k):
                new_rc[k] = rc[k]

        migrated["risk_calibration"] = new_rc

    # 3) assurance_targets.required_artefacts: wrap bare 'location' strings into 'evidence'
    artefacts = (migrated.get("assurance_targets") or {}).get("required_artefacts") or []
    for a in artefacts:
        if a.get("status") in ("exists",) and "evidence" not in a and a.get("location"):
            a["evidence"] = {
                "location": a["location"],
                "evidence_class": "reproducible-record",
            }
            # leave the legacy 'location' in place for forward-compat readers; the
            # JSON schema 2.0 will reject this as additionalProperties: false on a
            # strict validator, so on-disk migration via migrate_1_2_to_2_0.py
            # strips the legacy field.
        a.pop("notes", None) if a.get("notes") in (None, "") else None

    # 4) Default missing cps_subject_type when sector_ref is healthcare and stack hints at FL
    dc = migrated.get("deployment_context") or {}
    if dc.get("sector_ref") == "healthcare" and not dc.get("cps_subject_type"):
        # We don't autoset — that's a card-author decision. Just warn.
        warnings.append("deployment_context.cps_subject_type is absent; consider setting (e.g. 'patient'). Rule CPSDEV-* relies on this.")

    return migrated, warnings

def _artefact_list(card: dict) -> list[dict]:
    return card.get("assurance_targets", {}).get("required_artefacts", [])

def artefact_status(card: dict, fragment: str) -> str | None:
    fragment = fragment.lower()
    for a in _artefact_list(card):
        if fragment in a.get("artefact", "").lower():
            return a.get("status")
    return None

def missing_artefact(card: dict, fragment: str) -> bool:
    status = artefact_status(card, fragment)
    return status in ("missing", "planned", None)

def governance_has(card: dict, field: str, value) -> bool:
    return card.get("governance_controls", {}).get(field) == value

def has_regulation(card: dict, reg: str) -> bool:
    regs = card.get("regulatory_context", {}).get("applicable_regulations", [])
    return any(r.get("regulation") == reg for r in regs)

def maturity_stage(card: dict) -> int:
    return card.get("assurance_targets", {}).get("current_maturity_stage", 0)

def output_control_is(card: dict, value: str) -> bool:
    return card.get("governance_controls", {}).get("output_control") == value

def audit_log_present(card: dict) -> bool:
    return card.get("governance_controls", {}).get("audit_log", False)


# ─── Rule evaluator ──────────────────────────────────────────────────────────

def _build_eval_context(card: dict) -> dict:
    """Return a namespace dict for eval() of condition_logic expressions."""
    return {
        "has_primitive":    lambda pid: has_primitive(card, pid),
        "primitive_status": lambda pid: primitive_status(card, pid),
        "has_pairing":      lambda pid: has_pairing(card, pid),
        "has_stack":        lambda sid: has_stack(card, sid),
        "sector_is":        lambda sid: sector_is(card, sid),
        "scale_is":         lambda s:   scale_is(card, s),
        "artefact_status":  lambda f:   artefact_status(card, f),
        "missing_artefact": lambda f:   missing_artefact(card, f),
        "governance_has":   lambda field, val: governance_has(card, field, val),
        "has_regulation":   lambda reg: has_regulation(card, reg),
        "maturity_stage":   lambda: maturity_stage(card),
        "output_control_is": lambda v: output_control_is(card, v),
        "audit_log_present": lambda: audit_log_present(card),
        # schema 1.1 — DP variants
        "has_dp_variant":    lambda variant: has_dp_variant(card, variant),
        "has_any_dp":        lambda: has_any_dp(card),
        # schema 1.1 — stepwise chain
        "has_steps":             lambda: has_steps(card),
        "step_count":            lambda: step_count(card),
        "each_step_has":         lambda field: each_step_has(card, field),
        "step_addresses_ep":     lambda ep: step_addresses_ep(card, ep),
        "final_residual_declared": lambda: final_residual_declared(card),
        "step_pets_match_components": lambda: step_pets_match_components(card),
        # schema 1.1 — exposure-problem references
        "declares_exposure_problem": lambda ep=None: declares_exposure_problem(card, ep),
        # schema 1.1 — jurisdictional context
        "has_jurisdictional_context": lambda: has_jurisdictional_context(card),
        "declares_jurisdiction":  lambda role, j: declares_jurisdiction(card, role, j),
        "is_cross_jurisdictional": lambda: is_cross_jurisdictional(card),
        # schema 1.1 — framework alignment
        "aligns_to_framework":   lambda name: aligns_to_framework(card, name),
        # schema 1.2 — risk calibration block (path updated for 2.0)
        "has_risk_calibration":     lambda: has_risk_calibration(card),
        "risk_calibration_field":   lambda name: risk_calibration_field(card, name),
        "attack_target_field":      lambda name: attack_target_field(card, name),
        # schema 2.0 — three-ε quantities, threat profile, device/zone fields
        "card_schema_version":      lambda: card_schema_version(card),
        "threat_profile":           lambda: threat_profile(card),
        "design_target_field":      lambda name: design_target_field(card, name),
        "accountant_field":         lambda name: accountant_field(card, name),
        "empirical_audit_field":    lambda name: empirical_audit_field(card, name),
        "measured_advantage_field": lambda name: measured_advantage_field(card, name),
        "measured_exceeds_target":  lambda: measured_exceeds_target(card),
        "has_device_class":         lambda dc: has_device_class(card, dc),
        "device_classes":           lambda: device_classes(card),
        "step_trust_zones":         lambda: step_trust_zones(card),
        "tee_component_has_attestation": lambda: tee_component_has_attestation(card),
        "evidence_class_of_artefact":    lambda f: evidence_class_of_artefact(card, f),
        "any_reproducible_only_evidence": lambda: any_reproducible_only_evidence(card),
        "cps_subject_type":         lambda: cps_subject_type(card),
        "dp_has_parameter_manifest": lambda: dp_has_parameter_manifest(card),
        # allow len(), set(), list() in conditions
        "len": len,
        "set": set,
        "list": list,
        # allow card dict traversal in condition_logic
        "governance_controls": card.get("governance_controls", {}),
        "True": True, "False": False,
    }


def evaluate_rule(rule: dict, card: dict) -> tuple[bool, str | None]:
    """
    Returns (triggered: bool, error: str | None).
    triggered=True means the condition fired (finding applies).
    """
    condition = rule.get("condition_logic", "False")
    ctx = _build_eval_context(card)
    try:
        result = eval(condition, {"__builtins__": {}}, ctx)  # noqa: S307
        return bool(result), None
    except Exception as exc:
        return False, f"Condition evaluation error: {exc}"


# ─── Report builder ──────────────────────────────────────────────────────────

def _overall_rating(findings: list[dict]) -> str:
    if not findings:
        return "GREEN"
    worst = max(SEVERITY_ORDER.get(f["severity"], 0) for f in findings)
    for sev, val in SEVERITY_ORDER.items():
        if val == worst:
            return sev
    return "GREEN"


def build_report(card: dict, rules: list[dict], findings: list[dict], errors: list[str]) -> str:
    rating = _overall_rating(findings)
    emoji = SEVERITY_EMOJI[rating]
    card_id = card.get("card_id", "unknown")
    title = card.get("title", card_id)
    sector = card.get("deployment_context", {}).get("sector_ref", "—")
    primitives = ", ".join(f"`{p}`" for p in _primitive_ids(card)) or "—"
    pairing = card.get("architecture_pattern", {}).get("pairing_ref", "—")
    stack = card.get("architecture_pattern", {}).get("stack_ref", "—")
    today = date.today().isoformat()

    lines = [
        f"# YAPS Risk Report — {title}",
        "",
        f"**Card ID:** `{card_id}`  ",
        f"**Generated:** {today}  ",
        f"**Sector:** `{sector}`  ",
        f"**PET Stack:** {primitives}  ",
        f"**Explorer References:** pairing `{pairing}` / stack `{stack}`  ",
        "",
        f"---",
        "",
        f"## Overall Rating: {emoji} {rating}",
        "",
    ]

    if not findings:
        lines += [
            "> No AMBER or RED findings. All evaluated rules passed.",
            "",
        ]
    else:
        red = [f for f in findings if f["severity"] == "RED"]
        amber = [f for f in findings if f["severity"] == "AMBER"]
        green = [f for f in findings if f["severity"] == "GREEN"]
        info = [f for f in findings if f["severity"] == "INFO"]

        if red:
            lines += [f"### 🔴 RED Findings ({len(red)})", ""]
            for f in red:
                lines += _format_finding(f)

        if amber:
            lines += [f"### 🟡 AMBER Findings ({len(amber)})", ""]
            for f in amber:
                lines += _format_finding(f)

        if green:
            lines += [f"### 🟢 GREEN / Best Practice ({len(green)})", ""]
            for f in green:
                lines += _format_finding(f)

        if info:
            lines += [f"### ℹ️ Informational ({len(info)})", ""]
            for f in info:
                lines += _format_finding(f)

    if errors:
        lines += ["---", "", "## Evaluation Errors", ""]
        for e in errors:
            lines.append(f"- {e}")
        lines.append("")

    lines += [
        "---",
        "",
        "## Assurance Artefact Status",
        "",
    ]
    artefacts = card.get("assurance_targets", {}).get("required_artefacts", [])
    if artefacts:
        lines.append("| Artefact | Status | Notes |")
        lines.append("|----------|--------|-------|")
        for a in artefacts:
            status_icon = {"exists": "✅", "planned": "🕐", "missing": "❌", "not-applicable": "—"}.get(
                a.get("status", ""), "?"
            )
            notes = a.get("notes", "").replace("\n", " ")
            lines.append(f"| {a.get('artefact', '')} | {status_icon} {a.get('status', '')} | {notes} |")
    else:
        lines.append("*No required artefacts recorded on this card.*")

    lines += [
        "",
        "---",
        "",
        "## Governance Checklist",
        "",
        f"| Item | Value |",
        f"|------|-------|",
        f"| Output control | `{card.get('governance_controls', {}).get('output_control', '—')}` |",
        f"| Audit log | `{card.get('governance_controls', {}).get('audit_log', '—')}` |",
        f"| DPIA reference | `{card.get('governance_controls', {}).get('dpia_reference', '—')}` |",
        f"| Current maturity stage | `{maturity_stage(card) or '—'}` |",
        "",
        "---",
        "",
        "## Regulatory Context",
        "",
    ]
    regs = card.get("regulatory_context", {}).get("applicable_regulations", [])
    standards = card.get("regulatory_context", {}).get("standards_alignment", [])
    if regs:
        lines.append("**Applicable regulations:**")
        for r in regs:
            lines.append(f"- `{r.get('regulation')}` ({r.get('jurisdiction', '—')}) — {r.get('alignment_status', '—')}")
        lines.append("")
    if standards:
        lines.append("**Standards alignment:**")
        for s in standards:
            lines.append(f"- `{s.get('standard')}` — {s.get('alignment_level', '—')}")
        lines.append("")

    # Risk Calibration block (schema 1.2). Rendered only when present —
    # the section is silently absent for cards that have not opted in.
    if has_risk_calibration(card):
        rc = card.get("risk_calibration") or {}
        at = rc.get("attack_target") or {}
        lines += [
            "---",
            "",
            "## Risk Calibration",
            "",
            "*Operational reporting of the DP claim — complements (ε, δ) on `pet_components[].parameters`. "
            "Frames the privacy guarantee as attack difficulty (Desfontaines 2023; interpretable-dp.org).*",
            "",
            "| Field | Value |",
            "|---|---|",
        ]
        if rc.get("mu_dp") is not None:
            lines.append(f"| μ-DP (Gaussian-DP single-parameter summary) | `{rc.get('mu_dp')}` |")
        if rc.get("conversion_regret") is not None:
            lines.append(f"| Conversion regret | `{rc.get('conversion_regret')}` |")
        if at.get("attack"):
            lines.append(f"| Target attack | `{at.get('attack')}` |")
        if at.get("target_advantage") is not None:
            lines.append(f"| Target advantage | `{at.get('target_advantage')}` |")
        if at.get("target_fpr") is not None or at.get("target_fnr") is not None:
            lines.append(f"| Target (FPR, FNR) | `({at.get('target_fpr')}, {at.get('target_fnr')})` |")
        if at.get("measured_advantage") is not None:
            lines.append(f"| Measured advantage (empirical) | `{at.get('measured_advantage')}` |")
        if at.get("evidence_ref"):
            lines.append(f"| Evidence ref | `{at.get('evidence_ref')}` |")
        if rc.get("trade_off_curve_ref"):
            lines.append(f"| Trade-off curve | `{rc.get('trade_off_curve_ref')}` |")
        if rc.get("source_library"):
            lines.append(f"| Source library | `{rc.get('source_library')}` |")
        if rc.get("operational_interpretation"):
            lines += ["", f"**Operational interpretation:** {rc.get('operational_interpretation')}"]
        if rc.get("notes"):
            lines += ["", f"*Notes:* {rc.get('notes')}"]
        lines.append("")

    lines += [
        "---",
        "",
        "> *This report was produced by the YAPS rule-based risk engine.*  ",
        "> *Findings are indicative and do not constitute legal advice.*  ",
        "> *Rule set version: 1.0. Fork `rules/rules.yaml` to contest or extend.*",
        "",
    ]

    return "\n".join(lines)


def _format_finding(f: dict) -> list[str]:
    lines = [
        f"#### `{f['id']}` — {f['name']}",
        "",
        textwrap.fill(f.get("finding", "").strip(), width=100),
        "",
    ]
    refs = f.get("references", [])
    if refs:
        lines.append("**References:**")
        for r in refs:
            lines.append(f"- {r}")
        lines.append("")
    return lines


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="YAPS risk engine — evaluate a Privacy Card against the rule set."
    )
    parser.add_argument("card", help="Path to Privacy Card JSON file")
    parser.add_argument(
        "--rules",
        default=None,
        help="Path to rules.yaml (default: ../rules/rules.yaml relative to this script)",
    )
    parser.add_argument("--output", default=None, help="Write report to Markdown file")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Evaluate all rules even after RED finding",
    )
    parser.add_argument(
        "--no-migrate",
        action="store_true",
        help="Refuse to evaluate cards with schema_version != '2.0' (default: auto-migrate 1.x in memory)",
    )
    args = parser.parse_args()

    # ── Load card ──
    card_path = Path(args.card)
    if not card_path.exists():
        print(f"ERROR: Card file not found: {card_path}", file=sys.stderr)
        sys.exit(3)
    try:
        with open(card_path) as f:
            card = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in card file: {e}", file=sys.stderr)
        sys.exit(3)

    # ── Migrate if 1.x ──
    card_version = card.get("schema_version", "1.0")
    if card_version != "2.0":
        if args.no_migrate:
            print(
                f"ERROR: Card schema_version is '{card_version}', not '2.0'. "
                f"Re-run without --no-migrate, or migrate the file on disk with "
                f"migrate_1_2_to_2_0.py.",
                file=sys.stderr,
            )
            sys.exit(3)
        card, migration_warnings = _migrate_card_1_2_to_2_0(card)
        for w in migration_warnings:
            print(f"[migrate] {w}", file=sys.stderr)

    # ── Load rules ──
    if args.rules:
        rules_path = Path(args.rules)
    else:
        rules_path = Path(__file__).parent.parent / "rules" / "rules.yaml"

    if not rules_path.exists():
        print(f"ERROR: Rules file not found: {rules_path}", file=sys.stderr)
        sys.exit(3)
    try:
        with open(rules_path) as f:
            rules_doc = yaml.safe_load(f)
        rules = rules_doc.get("rules", [])
    except Exception as e:
        print(f"ERROR: Failed to load rules: {e}", file=sys.stderr)
        sys.exit(3)

    # ── Evaluate ──
    findings = []
    eval_errors = []

    for rule in rules:
        triggered, err = evaluate_rule(rule, card)
        if err:
            eval_errors.append(f"Rule {rule.get('id', '?')}: {err}")
            continue
        if triggered:
            findings.append({
                "id": rule["id"],
                "name": rule["name"],
                "severity": rule["severity"],
                "finding": rule.get("finding", ""),
                "references": rule.get("references", []),
            })
            if not args.full and rule["severity"] == "RED":
                break

    # ── Build report ──
    report = build_report(card, rules, findings, eval_errors)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(report)
        print(f"Report written to {out_path}")
    else:
        print(report)

    # ── Exit code ──
    rating = _overall_rating(findings)
    sys.exit({"GREEN": 0, "AMBER": 1, "RED": 2, "INFO": 0}.get(rating, 0))


if __name__ == "__main__":
    main()
