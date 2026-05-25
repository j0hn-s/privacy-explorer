#!/usr/bin/env python3
"""
YAPS Risk Engine — evaluates a Privacy Card JSON against the YAPS rule set
and produces a traffic-light risk report.

Usage:
    python risk_engine.py <card.json> [--rules <rules.yaml>] [--output <report.md>] [--full]

Options:
    --rules     Path to rules.yaml (default: ../rules/rules.yaml relative to this script)
    --output    Write report to this Markdown file instead of stdout
    --full      Evaluate all rules even after a RED finding

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
    """Return a nested risk_calibration.attack_target.<name> value, or None."""
    at = (card.get("risk_calibration") or {}).get("attack_target") or {}
    return at.get(name)

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
        # schema 1.2 — risk calibration block
        "has_risk_calibration":     lambda: has_risk_calibration(card),
        "risk_calibration_field":   lambda name: risk_calibration_field(card, name),
        "attack_target_field":      lambda name: attack_target_field(card, name),
        # allow len() in conditions
        "len": len,
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
