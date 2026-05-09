# Contributing to Privacy Explorer

Privacy Explorer is designed to be forked, contested, and extended. The YAML data files are the primary contribution target for the explorer tables; the YAPS rule set and card examples are the primary target for the practitioner tool. Both are maintained on a **PR-based review cycle** — the maintainer reviews contributions periodically rather than on-demand.

> **On tool contributions and endorsement.** Submitting a tool for inclusion in a Privacy Card example, the `tooling_candidates` field, or the YAPS rule set implies that you endorse the tool as technically sound for the context described. Tool submissions are treated as a form of professional recommendation, not a vendor listing. The maintainer reserves the right to seek independent verification before merging. See the [YAPS contribution guide](yaps/CONTRIBUTING.md) for specific tooling criteria.

---

## What this repository accepts

### Explorer table data (`data/`)

The YAML files in `data/` are the canonical source for all four tables. Fork freely — they are designed to be revised.

**Contributions that are most useful:**
- **Contested maturity assessments** — if deployment evidence places a combination at a different stage than the current entry, note the evidence in the `maturity_notes` field. The `confidence` field exists precisely to signal how contestable an entry is.
- **New T2 pairings** — must include an `artefacts` list and at least one published reference with a `url` field. Combinations without identifiable assurance artefacts will not be admitted to T2.
- **New T3 stacks** — must include a `rationale`, `assurance_narrative`, and `key_artefacts` list. Stacks with `confidence: theoretical` are acceptable with a clear rationale.
- **Sector sub-entries** — T4 is deliberately coarse; sub-sector contributions are particularly welcome for jurisdictions not currently represented.

### YAPS rules (`yaps/rules/rules.yaml`)

Rules are the most valuable contribution. See the [YAPS contribution guide](yaps/CONTRIBUTING.md) for the full rule-writing specification.

### YAPS example cards (`yaps/cards/examples/`)

New cards should represent a real deployment pattern with an honest trust model and realistic artefact status values. See [yaps/CARDS_GUIDE.md](yaps/CARDS_GUIDE.md) for the modular card structure.

### Diagrams (`DIAGRAM.md`)

New Mermaid diagrams extending the combination network, sector map, or card architecture views are welcome. Follow the existing `classDef` styling.

---

## What this repository does not accept

- **Personal data** of any kind in any file
- **Vendor marketing** dressed as technical content — tool entries require deployment or peer-review evidence
- **Compliance checklists** that claim definitive regulatory equivalence for specific configurations
- **Contested legal opinions presented as settled** — regulatory alignment is always marked `partial` or `aspirational` unless there is direct regulatory confirmation

---

## PR workflow

1. Fork the repository and create a descriptively named branch: `data/update-synthetic-maturity`, `rule/add-he-output-risk`, `card/web3-zkp-credential`
2. Make your changes; for YAPS contributions, run the engine against affected cards: `python yaps/engine/risk_engine.py yaps/cards/examples/<card>.json --full`
3. Open a PR with a one-paragraph description of the change and its evidence basis
4. Expect a maintainer response within a few weeks for substantive contributions
5. Merged contributions are attributed in the git history; card authors may add themselves to the `authors` field

## Contesting an entry

If you believe an existing rule, maturity assessment, or pairing is wrong, open a PR with the proposed change and an argument in the description. The project is built on the premise that reasonable experts disagree — disagreement with evidence is welcome. Assertions without evidence will not be merged.
