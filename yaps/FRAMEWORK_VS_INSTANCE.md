# YAPS — Framework vs Instance

A single document making the distinction the CPSIoTSec 2026 paper relies on for its contribution chain. If a reviewer comes away unable to state which parts of the work are *framework* (reusable, domain-agnostic) and which are *instance* (worked example for one deployment), the paper has failed.

## Two contributions, two repositories

The work spans two repositories with deliberately separated scopes:

| | Framework | Instance |
|---|---|---|
| **Repository** | [privacy-explorer/yaps/](../yaps/) | [stepwise-privacy-cards/](https://github.com/j0hn-s/stepwise-privacy-cards) |
| **What it is** | A schema, a rule engine, and a vocabulary | A worked example demonstrating the framework on one deployment |
| **What it claims** | Domain-agnostic specification for verification artefacts | Medical-CPS FL deployment can be inspected end-to-end via the framework |
| **What it carries** | `privacy_card.schema.json`, `rules.yaml`, `cps_rules.yaml`, `risk_engine.py` | One BloodMNIST FL chain, an attack harness, a Solid pod federation, a TEE ablation |
| **Versioning** | Schema versioned (currently 2.0); released as in-tree module | Reproducibility-pinned to a specific schema version |
| **Audience** | Anyone building or reviewing a privacy artefact for any PET deployment | Anyone reproducing or extending the medical-CPS FL demonstration |
| **Long-term plan** | Built out over multiple papers and workshops across 2 years | Frozen at the CPSIoTSec 2026 submission state; subsequent work in new repositories |

## Why the separation matters

Privacy cards in the lineage of model cards [Mitchell et al. FAccT 2019], datasheets [Gebru et al. CACM 2021], FactSheets [Hind et al. IBM JRD 2019], Laminator [Duddu et al. CODASPY 2025] and Atlas [IBM 2025] have historically been demonstrated *in situ*: each paper proposes a card-like artefact and shows it on one or two examples. The framework and the instance get muddled, and downstream users cannot tell what they are supposed to reuse.

YAPS makes the separation explicit so that:

1. **Reviewers can evaluate the framework on its own merits.** Does the schema cover the right surface? Are the rule families coherent? Is the evidence-class hierarchy defensible? These questions can be answered by reading `privacy_card.schema.json`, `MIGRATION_NOTES.md`, and this document — no FL, no medical CPS, no BloodMNIST.
2. **Reviewers can evaluate the instance on empirical grounds.** Does the medical-CPS deployment actually exhibit the contingencies the card surfaces? Are the attack-rate measurements rigorous? Is the Solid federation real or mocked? These questions are answered by reading the stepwise-privacy-cards repository and the paper's empirical evaluation sections.
3. **Downstream users can pick up the framework without inheriting the instance.** A team building a smart-grid privacy card uses YAPS the framework directly; they do not have to fork stepwise-privacy-cards.
4. **The framework can evolve without breaking the instance.** Schema 2.0 lands in YAPS; stepwise-privacy-cards pins to 2.0 for its submission state. Schema 2.1 can land later without invalidating the paper.

## What is framework

Specifically, the framework includes:

- **The schema** (`yaps/schemas/privacy_card.schema.json`) — `card_id`, `stepwise_chain`, `risk_calibration` with three first-class ε quantities, `evidence_class` taxonomy, `device_class` enum, `trust_zone` enum, `threat_profile` enum, `cps_subject_type` enum.
- **The rule engine** (`yaps/engine/risk_engine.py`) — schema-validates cards, applies rule sets, emits a traffic-light risk report.
- **The rule families** — IFACE, COMP, ASSUR, GOV, SECTOR, REG (core); RISKCAL, CPSDEV (CPS/IoT extensions). Each rule's docstring carries the academic anchor that motivates it.
- **The vocabulary** — terms defined in `../GLOSSARY.md`; PET primitive identifiers in `../data/primitives.yaml`; exposure-problem identifiers in `../EXPOSURE_PROBLEMS.md`; stepwise methodology in `../STEPWISE_RISK.md`.
- **The methodology** — stepwise-from-private construction, the evidence-class hierarchy, the threat-profile-first principle.
- **The workshop programme** (`workshops/W1–W4`) — testing protocols for the framework against external stakeholder groups.

The framework is what gets cited as `[18]` (or its anonymised equivalent for double-blind submission) in the CPSIoTSec paper's bibliography and what claim C2 in the paper's contribution chain refers to.

## What is instance

The medical-CPS FL instance in stepwise-privacy-cards is:

- One worked example chain (BloodMNIST FL + TEE + central DP), as a single 2.0-schema-conformant JSON card.
- One FL harness (Tier A numpy reference path; Tier B Flower + Opacus production-grade path).
- One attack harness (LiRA, RMIA, subject-MIA, gradient inversion, canary audit — one-run + CANIFE-crafted, compromised-edge).
- One Solid pod federation (1 / 2 / 3 CSS instance comparison, deployed via Docker Compose, with an interactive dashboard demonstrating live FL rounds and rule firings).
- One TEE ablation (AWS Nitro Enclaves vs no-TEE baseline).
- One device-heterogeneity simulation (hospital-server / edge-gateway / wearable-simulator).
- One composability battery (16 chains hand-authored, evaluated against expected firings).
- The empirical evaluation result records produced by all of the above.

The instance is what claim C3 in the paper's contribution chain refers to. None of its specific choices (BloodMNIST, 500 patients, Dirichlet α=0.5, σ=1.1, T=20, AWS Nitro) are normative for the framework; they are demonstrating that the framework is exercisable on a realistic deployment.

## How the rest of the paper hangs off this distinction

The paper's contribution chain reads:

- **C1 (the gap)** — scalar ε is insufficient for medical-CPS deployments where edge heterogeneity, multi-IdP trust, TEE substrate choice, and patient-controlled data lifecycles interact.
- **C2 (the framework — co-contribution)** — YAPS. This document and the schema/rule-engine/vocabulary it points to.
- **C3 (the medical-CPS instance)** — stepwise-privacy-cards. The worked example demonstrating C2.
- **C4 (the empirical demonstration)** — the result records from running C3.
- **C5 (the limitations)** — bounded honestly across both repositories.

C2 and C3 are independently reviewable. A reviewer can accept C2 (the framework is well-specified) and reject C3 (the instance's empirical claims are weak), or vice versa. Splitting them is one of the few unilateral decisions the paper has taken that materially eases review.

## Long-term plan

Privacy Explorer (and YAPS within it) will be built out over the next two years across multiple papers and workshops. The stepwise-privacy-cards repository is by contrast tied to the CPSIoTSec 2026 submission; after publication it is frozen as a reproducibility artefact, and subsequent worked examples (for different deployments, different sectors, different threat profiles) live in their own repositories with their own pins to whatever the contemporary schema version is.

This is the right shape: the framework grows; the instances accumulate around it without entangling each other.
