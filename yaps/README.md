# YAPS — Yet Another Privacy Sandbox

YAPS is the interactive component of the Privacy Explorer repository. It lets practitioners compose privacy architecture decisions in a structured way, apply rule-based risk profiles to those decisions, and produce governance-ready reports — without requiring any AI or ML tooling.

> **Scope:** YAPS is a conceptual risk assessment tool. It is not a formal verification system, a compliance checklist, or a substitute for legal advice. Risk findings are indicative and are best read alongside the T1–T4 tables in the root README.

---

## Why YAPS

The explorer tables (T1–T4) describe *what* PETs are and *how* they combine. YAPS asks *what happens when you commit to a specific combination in a specific context* — and surfaces the governance, interface, and composition risks that follow from that commitment.

The argument from the survey paper applies here: privacy claims become credible when they can be rendered into repeatable, inspectable artefacts. YAPS makes that rendering explicit by:

1. **Capturing architecture decisions** in a structured Privacy Card JSON document
2. **Evaluating those decisions** against a rule set that encodes known failure modes, interface risks, and governance gaps
3. **Producing a traffic-light risk report** in Markdown, suitable for team review or inclusion in a governance dossier
4. **Exposing the logic** so practitioners can fork, extend, and contest the rules

---

## Component Map

```
yaps/
├── README.md                   This file
├── CONTRIBUTING.md             How to add rules, cards, and tool references
│
├── schemas/
│   ├── privacy_card.schema.json    JSON Schema for Privacy Cards
│   └── data_profile.schema.json    JSON Schema for Data Profile (Solid integration)
│
├── rules/
│   └── rules.yaml              Rule definitions — edit to contest or extend
│
├── engine/
│   └── risk_engine.py          CLI: evaluate a card against the rule set
│
├── cards/
│   ├── templates/
│   │   └── blank_card.json     Starter template — copy and fill in
│   └── examples/
│       ├── healthcare_fl_tee_dp.json    S-01 pattern (NVIDIA FLARE / NHS)
│       ├── public_sector_tre_dp.json    P-07 pattern (ONS SRS)
│       └── finance_tee_mpc.json         P-05 pattern (cross-bank analytics)
│
└── frontend/
    └── index.html              Single-file interactive builder (no external deps)
```

---

## Connection to the Explorer Tables

Every Privacy Card carries explicit foreign-key references back to the T1–T4 tables:

| Card field | Explorer table | Example value |
|------------|---------------|---------------|
| `pet_components[].primitive_id` | T1 `ID` column | `"FL"`, `"TEE"`, `"DP"` |
| `architecture_pattern.pairing_ref` | T2 `Pair ID` | `"P-03"` |
| `architecture_pattern.stack_ref` | T3 `Stack ID` | `"S-01"` |
| `deployment_context.sector_ref` | T4 sector `id` | `"healthcare"` |

This means a card is always anchored to a specific row in the maturity / assurance / combination tables, making the risk report reproducible and forkable alongside the underlying data.

---

## Privacy Card Structure

A Privacy Card is a JSON document that records:

- **What** — the PET primitives in use and how they are combined
- **Who trusts whom** — the trust model and threat surface
- **What must exist** — the assurance targets (artefact checklist)
- **How it is governed** — the governance controls in place or planned
- **Where it sits** — the regulatory and sector context

See [schemas/privacy_card.schema.json](schemas/privacy_card.schema.json) for the full schema and [cards/templates/blank_card.json](cards/templates/blank_card.json) for a ready-to-fill template.

---

## Risk Engine

```bash
# Requires Python 3.9+ and PyYAML
pip install pyyaml

# Evaluate a card and print a report to stdout
python yaps/engine/risk_engine.py yaps/cards/examples/healthcare_fl_tee_dp.json

# Write the report to a Markdown file
python yaps/engine/risk_engine.py yaps/cards/examples/healthcare_fl_tee_dp.json --output report.md
```

The engine loads `yaps/rules/rules.yaml`, evaluates each rule against the card, and assigns a **GREEN / AMBER / RED** rating:

| Rating | Meaning |
|--------|---------|
| 🟢 GREEN | No AMBER or RED findings |
| 🟡 AMBER | One or more AMBER findings; no RED |
| 🔴 RED | One or more RED findings — high-priority gaps requiring attention |

The overall rating is the worst single finding. Rules are grouped by category:

| Category prefix | Focus |
|----------------|-------|
| `IFACE-` | Interface risks — what crosses component boundaries |
| `COMP-` | Composition risks — how PETs interact and where accounting gaps arise |
| `ASSUR-` | Assurance artefact completeness |
| `GOV-` | Governance and procedural controls |
| `SECTOR-` | Sector-specific requirements |
| `REG-` | Regulatory alignment pointers |

---

## Governance Considerations

YAPS embeds pointers to the following reference frameworks. These are not compliance checklists — they are orienting documents that a practitioner should read alongside any risk report.

| Framework | Scope | Relevance to YAPS |
|-----------|-------|-------------------|
| **NIST SP 800-226** *(Draft)* | DP evaluation guidelines | DP parameter governance, accounting, legal sufficiency |
| **NIST Privacy Framework 1.0** | Organisational privacy risk | GOV-category rule anchoring |
| **ICO Anonymisation Code of Practice (2022)** | UK data protection / anonymisation | SYN, DP assurance; re-identification risk |
| **ICO PETs Guidance (2023)** | UK PET deployment guidance | Pairing and stack assurance expectations |
| **OECD PETs Report (2023)** | International deployment maturity | Sector maturity cross-reference |
| **ISO/IEC 20889:2018** | Privacy-enhancing data de-identification | SYN and DP technique classification |
| **ISO/IEC 27701:2019** | Privacy information management | Governance artefact structure |
| **Five Safes Framework** | TRE / public-sector governed access | TRE-bearing cards (P-07, S-02) |

Regulatory mapping (GDPR, HIPAA, sector-specific) is handled at the card level via the `regulatory_context` field. Rules in the `REG-` category surface gaps relative to these requirements but do not constitute legal advice.

---

## Data Profile and decentralised-storage integration

Each Privacy Card can optionally reference a **Data Profile** ([schemas/data_profile.schema.json](schemas/data_profile.schema.json)) that records the nature of the data being processed, linkage risks, and access control intent.

The framework is architecture-agnostic, but speaks particularly clearly to **decentralised storage models** where data control sits with the data subject and computation crosses pod, institutional, or jurisdictional boundaries. [Solid](https://github.com/solid/solid) is the canonical example: its WebID-OIDC identity layer, ACL-based access control, and per-pod governance produce exactly the explicit, inspectable artefacts that YAPS's IFACE (interface) and GOV (governance) rule categories are designed to evaluate. Federated statistical-compute deployments built on top of Solid expose a per-pod governance surface that maps directly onto a Privacy Card's `governance_controls` and `solid_integration` fields.

The `solid_integration` block on a Privacy Card is a **record of intent**, not a runtime integration — YAPS does not connect to any live Solid server. The field documents that data-level access control is planned and points to the relevant Pod location and ACL policy.

Future development: live risk profiling against a Solid Pod's published data profile, enabling the engine to evaluate cards against actual data properties rather than self-reported fields.

---

## Auxiliary Data Risk (Future Work)

The current rule set does not model **auxiliary data risk** — the additional re-identification hazard introduced when an attacker holds external linked datasets (voter rolls, social media profiles, published registries). This is a known gap:

- Auxiliary data risk is context-dependent and hard to encode as a static rule
- Linkage risk increases non-linearly with the number of released outputs and the availability of quasi-identifiers in the target population
- Tools like TAPAS (Houssiau et al. 2022) and the NIST DP Synthetic Data Challenge assets offer evaluation frameworks but require per-dataset configuration

The `auxiliary_data_risk` field in the data profile schema is reserved for future tooling in this area.

---

## Live Risk Profiling (Future Development)

The current engine is a static evaluator: it reads a card file and applies rules. Future development directions include:

- **Streaming card evaluation** — evaluate risk as a user builds a card in the frontend
- **Solid Pod integration** — pull a live data profile from a Pod to parameterise risk rules
- **Composition accounting** — integrate a DP accountant (e.g. Google's `dp_accounting` library) to give live epsilon estimates as PETs are added
- **Tool registry** — map rule findings to candidate open-source tools (e.g. OpenDP, PySyft, TensorFlow Privacy)

Contributions to any of these directions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Forking and Extending

The canonical data files for the explorer tables are in [../data/](../data/). Fork there to revise maturity assessments, add pairings, or contest confidence levels.

To extend YAPS specifically:
- **Add a rule:** edit `rules/rules.yaml` and submit a PR (see CONTRIBUTING.md)
- **Add an example card:** add a JSON file to `cards/examples/` using the schema
- **Add a tool reference:** add to the `tooling_candidates` field in a card or propose a new `TOOL-` rule category
- **Contest an existing rule:** open an issue with your argument — the rule set is intentionally contestable
