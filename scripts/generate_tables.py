#!/usr/bin/env python3
"""Regenerate README.md's T0-T4 reference materials from the canonical data/*.yaml.

Closes the hand-sync drift risk named in DIAGRAM.md's "Suggested Further
Iterations" #6: every prior round of catalogue edits required manually
re-editing README's tables to match, which is exactly the kind of mechanical
step a human will eventually get wrong or forget.

Usage:
    python scripts/generate_tables.py            # rewrite README.md in place
    python scripts/generate_tables.py --check     # exit 1 if README.md is stale (CI use)

Structural note (v2, 2026-09): the first version of this generator kept the
original one-wide-table-per-T shape and just shortened cell text to fit. That
treated it as a content problem; it's actually a structural one — a 7-8
column GFM table renders wide on GitHub regardless of how short the cells
are, because GitHub doesn't wrap table cells and column widths compound.
Shortening text made individual cells more honest but didn't fix the width.

This version instead renders each T as a short, narrow index table (2-4
columns, nothing but IDs/names/confidence — genuinely short, not truncated)
followed by one `<details>` block per entry carrying the *complete* text —
full artefact lists, full trust models, full references as links. Nothing
is cut short in the details blocks; there is no truncation logic in this
file at all, deliberately, because truncation was the wrong lever last time.
GitHub renders `<details>/<summary>` natively in READMEs; a blank line right
after `<summary>` is required for GitHub to parse the block's contents as
markdown rather than raw HTML — every details() call below includes it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
README = ROOT / "README.md"


def load(name: str) -> list[dict]:
    doc = yaml.safe_load((DATA / name).read_text())
    key = next(k for k in doc if isinstance(doc[k], list))
    return doc[key]


def clean(text: str | None) -> str:
    """Collapse YAML block-scalar whitespace. No truncation — see module docstring."""
    return " ".join((text or "").split())


def md_escape(text: str) -> str:
    """Only needed inside table cells, where a literal '|' breaks the row."""
    return text.replace("|", "\\|")


def backticks(items) -> str:
    return ", ".join(f"`{i}`" for i in items)


def table(headers: list[str], rows: list[list[str]]) -> str:
    """Generates its own header + separator row — see the v2 note above.
    The very first version of this script relied on a static header/
    separator sitting *inside* the AUTOGEN block in README.md; the first
    time the generator ran, it silently replaced that block (data rows
    only, no separator) and every run since produced pipe-delimited text
    with no `|---|---|` line — which GitHub does not render as a table at
    all, just literal text with visible pipe characters. Owning the header
    here means that class of bug can't recur."""
    sep = ["---"] * len(headers)
    all_rows = [headers, sep] + rows
    return "\n".join("| " + " | ".join(md_escape(c) for c in r) + " |" for r in all_rows)


def bullet(label: str, value: str | None) -> str | None:
    value = clean(value) if value else value
    if not value or value == "—":
        return None
    return f"- **{label}:** {value}"


def bullet_list(label: str, items: list[str] | None) -> list[str]:
    if not items:
        return []
    out = [f"- **{label}:**"]
    out.extend(f"  - {clean(i)}" for i in items)
    return out


def ref_list(label: str, refs: list) -> list[str]:
    """references entries are either {text, url} dicts (T2/T3) or bare
    strings (T1's key_references). Render as markdown links where a url
    exists, plain text otherwise."""
    if not refs:
        return []
    out = [f"- **{label}:**"]
    for r in refs:
        if isinstance(r, dict):
            text, url = r.get("text", ""), r.get("url", "")
            out.append(f"  - [{text}]({url})" if url else f"  - {text}")
        else:
            out.append(f"  - {r}")
    return out


def details(summary: str, body: list[str]) -> str:
    lines = ["<details>", f"<summary>{summary}</summary>", ""]  # blank line: see module docstring
    lines.extend(l for l in body if l is not None)
    lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


# ─── T0 — Exposure Problems ────────────────────────────────────────────────

def gen_t0(eps: list[dict]) -> str:
    rows = []
    for e in eps:
        refs = backticks([rp["ref"] for rp in e["responding_pets"] if rp.get("ref")])
        if not refs:
            refs = ", ".join(rp["note"].split(" — ")[0] for rp in e["responding_pets"] if not rp.get("ref"))
        rows.append([f"`{e['id']}`", e["name"], refs])
    idx = table(["EP", "Exposure problem", "Primary responding PETs"], rows)

    blocks = []
    for e in eps:
        body = [
            bullet("Description", e.get("description")),
            "\n".join(bullet_list("Disclosure types", e.get("disclosure_types"))) or None,
        ]
        rp_lines = ["- **Responding PETs:**"]
        for rp in e["responding_pets"]:
            label = f"`{rp['ref']}`" if rp.get("ref") else "(no catalogued primitive)"
            rp_lines.append(f"  - {label} — {clean(rp.get('note', ''))}")
        body.append("\n".join(rp_lines))
        body.append("\n".join(bullet_list("Assurance anchors", e.get("assurance_anchors"))) or None)
        body.append(bullet("Canonical failure mode", e.get("canonical_failure_mode")))
        if e.get("survey_paper_refs"):
            body.append(bullet("Survey paper refs", ", ".join(e["survey_paper_refs"])))
        blocks.append(details(f"<code>{e['id']}</code> — {e['name']}", body))

    return idx + "\n\n" + "\n\n".join(blocks)


# ─── T1 — Primitives ───────────────────────────────────────────────────────

def gen_t1(prims: list[dict]) -> str:
    ordered = sorted(prims, key=lambda p: (bool(p.get("is_family_pointer")),))
    rows = []
    for p in ordered:
        family = p["family"].capitalize() + ("*" if p["id"] == "SDC" else "")
        rows.append([f"`{p['id']}`", p["technique"], family, f"Stage {p.get('maturity_stage', '—')}"])
    idx = table(["ID", "Technique", "Family", "Maturity"], rows)

    blocks = []
    for p in ordered:
        body = [
            bullet("Trust model", p.get("trust_model")),
            "\n".join(bullet_list("Core artefacts", p.get("core_artefacts"))) or None,
            bullet("Bottleneck", p.get("bottleneck")),
            bullet("Maturity notes", p.get("maturity_notes")),
            "\n".join(ref_list("Key references", p.get("key_references"))) or None,
        ]
        blocks.append(details(f"<code>{p['id']}</code> — {p['technique']}", body))

    return idx + "\n\n" + "\n\n".join(blocks)


# ─── T2 — Pairings ──────────────────────────────────────────────────────────

def pet_label(pid: str, pairing: dict) -> str:
    """Prefer the pairing's typical_dp_variant (e.g. DP-C) over the bare 'DP'
    family pointer in pets[] — pets[] is the foreign-key list,
    typical_dp_variant is the display refinement."""
    if pid == "DP" and pairing.get("typical_dp_variant"):
        return pairing["typical_dp_variant"]
    return pid


def gen_t2(pairs: list[dict]) -> str:
    rows = []
    for p in pairs:
        a, b = (pet_label(x, p) for x in p["pets"])
        rows.append([f"`{p['id']}`", f"`{a}`", f"`{b}`", p["confidence"]])
    idx = table(["Pair ID", "PET A", "PET B", "Confidence"], rows)

    blocks = []
    for p in pairs:
        a, b = (pet_label(x, p) for x in p["pets"])
        body = [
            bullet("Combination logic", p.get("combination_logic")),
            bullet("Survey anchor", p.get("survey_paper_anchor")),
            "\n".join(bullet_list("Artefacts", p.get("artefacts"))) or None,
            bullet("Advantage", p.get("advantage")),
            bullet("Shortcoming", p.get("shortcoming")),
            bullet("First documented", p.get("first_documented")),
            bullet("Evidence last checked", p.get("evidence_last_updated")),
            "\n".join(ref_list("References", p.get("references"))) or None,
        ]
        blocks.append(details(f"<code>{p['id']}</code> — {a} + {b}", body))

    return idx + "\n\n" + "\n\n".join(blocks)


# ─── T3 — Stacks ────────────────────────────────────────────────────────────

def gen_t3(stacks: list[dict], pairs_by_id: dict[str, dict]) -> str:
    rows = []
    for s in stacks:
        rows.append([f"`{s['id']}`", " + ".join(s["full_stack"]), s["confidence"]])
    idx = table(["Stack ID", "Full Stack", "Confidence"], rows)

    blocks = []
    for s in stacks:
        base = pairs_by_id[s["base_pair"]]
        base_pets = " + ".join(pet_label(x, base) for x in base["pets"])
        body = [
            bullet("Base pair", f"`{s['base_pair']}` ({base_pets})"),
            bullet("Added layer", f"`{s['added_layer']}`"),
            bullet("Rationale", s.get("rationale")),
            bullet("Use case", s.get("use_case")),
            bullet("Assurance narrative", s.get("assurance_narrative")),
            "\n".join(bullet_list("Key artefacts", s.get("key_artefacts"))) or None,
            bullet("Shortcoming", s.get("shortcoming")),
            bullet("First documented", s.get("first_documented")),
            bullet("Evidence last checked", s.get("evidence_last_updated")),
            "\n".join(ref_list("References", s.get("references"))) or None,
        ]
        blocks.append(details(f"<code>{s['id']}</code> — {' + '.join(s['full_stack'])}", body))

    return idx + "\n\n" + "\n\n".join(blocks)


# ─── T4 — Sectors ───────────────────────────────────────────────────────────

SECTOR_LABELS = {
    "public_sector": "Public sector / official statistics / governed research",
    "healthcare": "Healthcare / biomedical research",
    "finance": "Finance / fraud / inter-organisational analytics",
    "technology": "Technology platforms / consumer AI / large-scale telemetry",
    "web3": "Web3 / verifiable infrastructure / credential ecosystems",
}


def gen_t4(sectors: list[dict], pairs_by_id: dict[str, dict], stacks_by_id: dict[str, dict]) -> str:
    rows = []
    for s in sectors:
        stacks_col = backticks([ref["ref"] for ref in s["primary_stacks"]])
        label = SECTOR_LABELS.get(s["id"], s["id"])
        rows.append([f"**{label}**", stacks_col, f"Stage {s.get('maturity_stage', '—')}"])
    idx = table(["Sector", "Primary stacks", "Maturity"], rows)

    blocks = []
    for s in sectors:
        label = SECTOR_LABELS.get(s["id"], s["id"])
        ic = s.get("idiosyncratic_constraints", {}) or {}
        body = [
            bullet("Typical problem", s.get("typical_problem")),
            "\n".join(bullet_list("Primary exposure problems", [f"`{e}`" for e in s.get("primary_exposure_problems", [])])) or None,
            bullet("Assurance posture", s.get("assurance_posture")),
            bullet("Dominant anchor", s.get("dominant_anchor")),
            bullet("Maturity notes", s.get("maturity_notes")),
            bullet("Blocker", s.get("blocker")),
            "\n".join(bullet_list("Key examples", s.get("key_examples"))) or None,
            "\n".join(bullet_list("Legal instruments", ic.get("legal_instruments"))) or None,
            "\n".join(bullet_list("Regulatory expectations", ic.get("regulatory_expectations"))) or None,
            "\n".join(bullet_list("Institutional frameworks", ic.get("institutional_frameworks"))) or None,
            bullet("What this implies for PETs", ic.get("what_this_implies_for_pets")),
        ]
        blocks.append(details(f"{label}", body))

    return idx + "\n\n" + "\n\n".join(blocks)


def replace_block(content: str, tag: str, body: str) -> str:
    pattern = re.compile(
        rf"(<!-- AUTOGEN:{tag} START.*?-->\n).*?(\n<!-- AUTOGEN:{tag} END -->)",
        re.DOTALL,
    )
    if not pattern.search(content):
        raise SystemExit(f"Marker pair AUTOGEN:{tag} not found in README.md")
    return pattern.sub(lambda m: m.group(1) + body + m.group(2), content)


def main() -> None:
    check_only = "--check" in sys.argv

    primitives = load("primitives.yaml")
    pairings = load("pairings.yaml")
    stacks = load("stacks.yaml")
    eps = load("exposure_problems.yaml")
    sectors = load("sectors.yaml")

    pairs_by_id = {p["id"]: p for p in pairings}
    stacks_by_id = {s["id"]: s for s in stacks}

    content = README.read_text()
    original = content
    content = replace_block(content, "T0", gen_t0(eps))
    content = replace_block(content, "T1", gen_t1(primitives))
    content = replace_block(content, "T2", gen_t2(pairings))
    content = replace_block(content, "T3", gen_t3(stacks, pairs_by_id))
    content = replace_block(content, "T4", gen_t4(sectors, pairs_by_id, stacks_by_id))

    if check_only:
        if content != original:
            print("README.md tables are stale — run scripts/generate_tables.py", file=sys.stderr)
            sys.exit(1)
        print("README.md tables are up to date.")
        return

    if content != original:
        README.write_text(content)
        print("README.md tables regenerated.")
    else:
        print("README.md tables already up to date; no changes written.")


if __name__ == "__main__":
    main()
