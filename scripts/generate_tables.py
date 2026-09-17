#!/usr/bin/env python3
"""Regenerate README.md's T0-T4 markdown tables from the canonical data/*.yaml.

Closes the hand-sync drift risk named in DIAGRAM.md's "Suggested Further
Iterations" #6: every prior round of catalogue edits required manually
re-editing README's tables to match, which is exactly the kind of mechanical
step a human will eventually get wrong or forget.

Usage:
    python scripts/generate_tables.py            # rewrite README.md in place
    python scripts/generate_tables.py --check     # exit 1 if README.md is stale (CI use)

Table cells that condense a longer YAML field (e.g. a one-clause "Dominant
Bottleneck" drawn from a full `bottleneck` paragraph) use the first sentence
of that field. This is a deliberate, simple, and stable rule — it will not
always read as smoothly as a hand-tuned cell, but it cannot silently drift
from the source the way a hand-written cell can.
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


_ABBREVS = {"e.g", "i.e", "etc", "vs", "cf", "approx", "u.s", "u.k", "eu", "al", "et al", "fig", "eqn"}


def first_sentence(text: str | None) -> str:
    if not text:
        return "—"
    text = " ".join(text.split())  # collapse YAML block-scalar whitespace
    for m in re.finditer(r"[.!?](\s|$)", text):
        before = text[: m.start()]
        if not before:
            continue
        if before[-1].isupper():
            continue  # single-capital initials, e.g. "J.P."
        tail = re.sub(r"[^a-z.]", "", before.split(" ")[-1].lower())
        if tail in _ABBREVS:
            continue
        return text[: m.start() + 1].strip()
    return text.strip()


def md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def backticks(items) -> str:
    return ", ".join(f"`{i}`" for i in items)


def table(rows: list[list[str]]) -> str:
    return "\n".join("| " + " | ".join(md_escape(c) for c in r) + " |" for r in rows)


def gen_t0(eps: list[dict]) -> str:
    rows = []
    for e in eps:
        refs = backticks([rp["ref"] for rp in e["responding_pets"] if rp.get("ref")])
        if not refs:
            # entries with only a bare `note` (no ref), e.g. EP-10's "machine unlearning"
            refs = ", ".join(rp["note"].split(" — ")[0] for rp in e["responding_pets"] if not rp.get("ref"))
        anchors = " + ".join(e["assurance_anchors"][:2])
        anchors = anchors[0].upper() + anchors[1:] if anchors else "—"
        rows.append([f"`{e['id']}`", e["name"], refs, anchors])
    return table(rows)


def gen_t1(prims: list[dict]) -> str:
    # Variants before their family pointer (DP-L, DP-C, then DP), matching the
    # explorer's stated reading order; otherwise YAML order.
    ordered = sorted(prims, key=lambda p: (bool(p.get("is_family_pointer")),))
    rows = []
    for p in ordered:
        family = p["family"].capitalize() + ("*" if p["id"] == "SDC" else "")
        rows.append([
            f"`{p['id']}`", p["technique"], family,
            first_sentence(p["trust_model"]),
            ", ".join(p["core_artefacts"]),
            first_sentence(p["bottleneck"]),
            first_sentence(p["maturity_notes"]),
        ])
    return table(rows)


def pet_label(pid: str, pairing: dict) -> str:
    """Prefer the pairing's typical_dp_variant (e.g. DP-C) over the bare 'DP'
    family pointer in pets[], so the table stays as precise as the YAML
    intends — pets[] is the foreign-key list, typical_dp_variant is the
    display refinement."""
    if pid == "DP" and pairing.get("typical_dp_variant"):
        return pairing["typical_dp_variant"]
    return pid


def gen_t2(pairs: list[dict]) -> str:
    rows = []
    for p in pairs:
        a, b = (pet_label(x, p) for x in p["pets"])
        rows.append([
            f"`{p['id']}`", f"`{a}`", f"`{b}`",
            first_sentence(p["combination_logic"]),
            p["survey_paper_anchor"],
            ", ".join(p["artefacts"]),
            first_sentence(p["advantage"]),
            first_sentence(p["shortcoming"]),
        ])
    return table(rows)


def gen_t3(stacks: list[dict], pairs_by_id: dict[str, dict]) -> str:
    rows = []
    for s in stacks:
        base = pairs_by_id[s["base_pair"]]
        base_pets = [pet_label(x, base) for x in base["pets"]]
        base_label = f"`{s['base_pair']}` ({' + '.join(base_pets)})"
        rows.append([
            f"`{s['id']}`", base_label, f"`{s['added_layer']}`",
            " + ".join(s["full_stack"]),
            s["survey_paper_anchor"],
            " ".join(s["use_case"].split()),
            first_sentence(s["assurance_narrative"]),
        ])
    return table(rows)


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
        stacks_col = []
        for ref in s["primary_stacks"]:
            rid = ref["ref"]
            if rid in pairs_by_id:
                p = pairs_by_id[rid]
                pets = " + ".join(pet_label(x, p) for x in p["pets"])
            elif rid in stacks_by_id:
                pets = " + ".join(stacks_by_id[rid]["full_stack"])
            else:
                pets = "?"
            stacks_col.append(f"`{rid}` ({pets})")
        label = SECTOR_LABELS.get(s["id"], s["id"])
        rows.append([
            f"**{label}**",
            ", ".join(stacks_col),
            " ".join(s["assurance_posture"].split()),
            s["dominant_anchor"],
            first_sentence(s["maturity_notes"]),
            first_sentence(s["blocker"]),
        ])
    return table(rows)


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
