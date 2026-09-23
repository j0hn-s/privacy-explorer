#!/usr/bin/env python3
"""Regenerate README.md's T0-T4 markdown tables from the canonical data/*.yaml.

Closes the hand-sync drift risk named in DIAGRAM.md's "Suggested Further
Iterations" #6: every prior round of catalogue edits required manually
re-editing README's tables to match, which is exactly the kind of mechanical
step a human will eventually get wrong or forget.

Usage:
    python scripts/generate_tables.py            # rewrite README.md in place
    python scripts/generate_tables.py --check     # exit 1 if README.md is stale (CI use)

Every cell is hard-capped in length (see CHAR_CAP / LIST_CAP below). The
first pass at this generator used a "first sentence" rule with no outer
bound, which for fields like `use_case` and `assurance_posture` had no cap
at all — some cells ran 200+ characters, which is what made the rendered
tables on GitHub genuinely too wide to read. These tables are documented
elsewhere as summaries ("A summary" / "designed to be read relationally"),
not the full record, so hard-capping and pointing to the YAML for the full
text is a correction, not a loss of information — the YAML was always the
canonical source.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
README = ROOT / "README.md"

# Hard caps. Deliberately tight — GFM table columns size to their widest
# cell, so one long row makes every row in that column wide. Tuned so a
# 6-7 column table stays inside a normal viewport without horizontal
# scrolling on GitHub.
CHAR_CAP = 48
LIST_ITEM_CAP = 2


def load(name: str) -> list[dict]:
    doc = yaml.safe_load((DATA / name).read_text())
    key = next(k for k in doc if isinstance(doc[k], list))
    return doc[key]


_ABBREVS = {"e.g", "i.e", "etc", "vs", "cf", "approx", "u.s", "u.k", "eu", "al", "et al", "fig", "eqn"}


def first_sentence(text: str | None) -> str:
    if not text:
        return ""
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


def truncate_chars(text: str, max_len: int = CHAR_CAP) -> str:
    """Hard character cap, cut at the last word boundary, ellipsised."""
    if not text:
        return "—"
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


def short_prose(text: str | None, max_len: int = CHAR_CAP) -> str:
    """first-sentence, then hard-capped — natural phrasing when it fits,
    a guaranteed bound when it doesn't."""
    return truncate_chars(first_sentence(text), max_len)


def short_list(items: list[str], max_items: int = LIST_ITEM_CAP, max_len: int = CHAR_CAP) -> str:
    if not items:
        return "—"
    shown = truncate_chars(", ".join(items[:max_items]), max_len)
    remaining = len(items) - max_items
    if remaining > 0:
        shown += f" (+{remaining} more)"
    return shown


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
        anchor = e["assurance_anchors"][0] if e["assurance_anchors"] else "—"
        anchor = truncate_chars(anchor[0].upper() + anchor[1:], CHAR_CAP) if anchor != "—" else anchor
        rows.append([f"`{e['id']}`", e["name"], refs, anchor])
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
            short_prose(p["trust_model"]),
            short_list(p["core_artefacts"]),
            short_prose(p["bottleneck"]),
            short_prose(p["maturity_notes"]),
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
            short_prose(p["combination_logic"]),
            truncate_chars(p["survey_paper_anchor"]),
            short_list(p["artefacts"]),
            short_prose(p["advantage"]),
            short_prose(p["shortcoming"]),
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
            truncate_chars(s["survey_paper_anchor"]),
            short_prose(s["use_case"]),
            short_prose(s["assurance_narrative"]),
        ])
    return table(rows)


SECTOR_LABELS = {
    "public_sector": "Public sector / official statistics",
    "healthcare": "Healthcare / biomedical research",
    "finance": "Finance / fraud analytics",
    "technology": "Technology / consumer AI",
    "web3": "Web3 / verifiable infrastructure",
}


def gen_t4(sectors: list[dict], pairs_by_id: dict[str, dict], stacks_by_id: dict[str, dict]) -> str:
    rows = []
    for s in sectors:
        stacks_col = []
        for ref in s["primary_stacks"]:
            rid = ref["ref"]
            stacks_col.append(f"`{rid}`")
        label = SECTOR_LABELS.get(s["id"], s["id"])
        rows.append([
            f"**{label}**",
            ", ".join(stacks_col),
            short_prose(s["assurance_posture"]),
            truncate_chars(s["dominant_anchor"]),
            short_prose(s["maturity_notes"]),
            short_prose(s["blocker"]),
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
