# Contributing to YAPS

YAPS is designed to be forked, contested, and extended. The rule set and data files are the canonical contribution targets — not the engine code.

Contributions are reviewed and merged periodically by the repository maintainer. Please use the PR workflow described below rather than opening issues requesting real-time responses.

---

## What to contribute

### Rules (`rules/rules.yaml`)

The most valuable contributions. If you:
- Disagree with an existing rule (severity, condition logic, or finding text)
- Know of a failure mode not covered
- Want to add a sector, regulation, or standard not yet represented

...open a PR with the changed or added rule and a brief rationale in the PR description. The rule `id` must be unique; follow the existing `CATEGORY-NNN` format. Propose a new category prefix if your rule genuinely doesn't fit an existing one.

**What makes a good rule:**
- Condition is precise (not "always fires" or "never fires")
- Finding text explains *why* this matters and *what to do*, not just *what was detected*
- References point to a published source (paper, standard, regulatory guidance)
- Severity is calibrated: RED = blocks deployment readiness; AMBER = notable gap; GREEN = best practice; INFO = advisory

### Example cards (`cards/examples/`)

New cards should demonstrate a real deployment pattern — ideally one referenced in the survey paper or a documented production deployment. Include:
- A realistic trust model with named threat actors
- Assurance artefacts with honest `status` values (don't mark things `exists` that don't)
- A populated `residual_risks` section
- All explorer cross-references (pairing_ref or stack_ref; sector_ref)

Cards will be reviewed for consistency with the T1–T4 tables before merge.

### Tooling references

If you want to add a tool to the `tooling_candidates` field of an existing example card, or propose a new tool category, submit a PR with:
- Tool name, URL, and licence
- Which T1 `primitive_ids` it implements
- Maturity level and a one-sentence note
- A brief rationale for inclusion (production deployment, peer-reviewed evaluation, or active maintenance)

The maintainer will periodically review tool additions. Tools will not be added solely on the basis of vendor submission — a deployment reference, peer-reviewed evaluation, or community endorsement is required.

### Data profile examples (`cards/examples/`)

Data profiles (following `schemas/data_profile.schema.json`) can accompany example cards. Name them `<card_slug>_data_profile.json` and reference them from the card's `data_profile_ref` field.

### Explorer table data (`../data/`)

Fork and edit `data/primitives.yaml`, `data/pairings.yaml`, `data/stacks.yaml`, or `data/sectors.yaml` to contest maturity assessments, add combinations, or update references. These are deliberately designed to be forkable and contestable. Include a brief PR description explaining the evidence basis for any change.

---

## What not to contribute

- **Real personal data** — no data files containing actual individual records
- **Vendor marketing** — tooling additions must be technically evidenced, not self-promotional
- **Compliance checklists** — YAPS is a conceptual risk assessment tool, not a compliance product; contributions that claim definitive regulatory compliance for specific configurations are out of scope
- **LLM-based rule evaluation** — the engine is intentionally rule-based; proposals to replace condition evaluation with model calls will not be accepted

---

## PR workflow

1. Fork the repository
2. Create a branch named descriptively: `rule/add-he-composition-risk`, `card/web3-zkp-credential`, `data/update-zkp-maturity`
3. Make your changes; run the engine against affected example cards to verify no unintended behaviour: `python yaps/engine/risk_engine.py yaps/cards/examples/<card>.json --full`
4. Open a PR with:
   - A one-paragraph description of the change and its rationale
   - For rule changes: the evidence basis (paper, incident, regulatory guidance)
   - For card changes: the deployment reference or survey paper section
5. The maintainer reviews periodically — expect a response within a few weeks for substantive contributions
6. Merged contributions are attributed in the PR history; authors may add themselves to the `authors` field of cards they contribute

---

## Contesting existing entries

If you believe an existing rule, maturity assessment, or combination pairing is wrong:
1. Open a PR with the proposed change
2. Include a brief argument in the PR description — the evidence basis, the failure mode of the current entry, and what a better assessment would look like
3. Reasonable experts will disagree on maturity stages and rule severities; disagreement is welcome and expected

The `confidence` field in `data/pairings.yaml` and `data/stacks.yaml` exists precisely to signal how strongly the current entry is evidenced. `theoretical` entries are the most contestable; `deployment_documented` entries require deployment-level counter-evidence to revise.

---

## Code of conduct

Contributions should be made in a professional and constructive spirit. Disputes about technical content should be argued with evidence, not assertion. The maintainer reserves the right to reject contributions that are technically unsound, commercially motivated, or not in keeping with the spirit of the project.
