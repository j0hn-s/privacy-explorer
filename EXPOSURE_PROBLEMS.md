# T0 — Common Exposure Problems

A working index of the exposure problems that PET combinations are deployed to address. Where [T1–T4](README.md) read *technique → combination → stack → sector*, T0 reads *exposure problem → responding PETs → assurance anchors → canonical failure mode*.

> **Why this index exists.** PET combinations multiply faster than any table can usefully characterise. The combinatorial space includes increasingly exotic stacks (e.g. SMPC + DP + FL + TEE), and a survey-paper-style table cannot enumerate them all. T0 reframes the question: instead of asking *what combinations exist?*, ask *what exposure problem does the combination solve?* A combination is legitimate when it answers a named exposure problem with an inspectable assurance story. Combinations that do not map to a named problem are usually either redundant or premature.

This is intended to be **workshopped, not finalised**. The set will grow and contract as practitioners use it.

The canonical source is [data/exposure_problems.yaml](data/exposure_problems.yaml). Cross-references use the IDs defined in [T1](README.md#t1--pet-primitives), [T2](README.md#t2--two-pet-pairings), and [T3](README.md#t3--three-pet-stacks).

---

## How to read this index

Each entry has the same shape:

- **What goes wrong** — a one-paragraph description of the exposure problem in plain language.
- **Disclosure types** — which of the recognised re-identification routes are in scope. See [GLOSSARY.md §2](GLOSSARY.md).
- **Responding PETs** — the primitives, pairings, or stacks that practitioners deploy. Each is annotated with its specific contribution.
- **Assurance anchors** — the evidence that makes the response credible (the artefacts YAPS rules check for).
- **Canonical failure mode** — the way deployments most often go wrong here. Useful for designing test cases and for sanity-checking a card.

---

## The index (summary)

| EP | Exposure problem | Primary responding PETs | Dominant assurance anchor |
|---|---|---|---|
| **EP-01** | Aggregated outputs may reveal individual records | `DP-C`, `P-07`, `P-08`, `SDC` | Privacy accountant + parameter manifest + μ-DP / attack-rate target (schema 1.2 `risk_calibration`) |
| **EP-02** | Data cannot leave its source for joint computation | `MPC`, `HE`, `FL`, `P-02` | Adversary-model declaration + protocol spec |
| **EP-03** | Computation must happen inside an untrusted environment | `TEE`, `HE`, `P-04` | Attestation + side-channel mitigation |
| **EP-04** | Distributed model training where updates may leak training data | `P-01`, `P-02`, `P-03`, `S-01`, `S-03` | Secure-aggregation spec + privacy accountant |
| **EP-05** | Need to share or republish a dataset-shaped artefact | `SYN`, `P-08`, `S-04`, `P-10` | Disclosure-risk evaluation + utility benchmark |
| **EP-06** | Repeated, governed access to sensitive data for research | `TRE`, `P-07`, `S-02`, `P-09`, `P-10` | Output-clearance log + accreditation records |
| **EP-07** | Prove a property without revealing the underlying data | `ZKP`, `P-06` | Circuit definition + verification parameters |
| **EP-08** | Cumulative privacy loss across multiple releases | `DP-C`, `DP-L` | Privacy accountant with composition theorem named + μ-DP / attack-rate target (schema 1.2 `risk_calibration`) |
| **EP-09** | Re-identification from quasi-identifiers in low-dimensional release | `DP-C`, `SYN`, `TRE`, `SDC` | Singling-out test + motivated-intruder simulation |
| **EP-10** | Lifecycle controls — withdrawal, retraining, deprecated artefacts | `SYN`, machine unlearning | Change log linked to model versions |
| **EP-11** | Cross-jurisdictional analytics with conflicting legal regimes | `FL`, `P-04`, `S-01` | Jurisdictional applicability declaration + DPIA per jurisdiction |

---

## Detailed entries

The full entries — with descriptions, canonical failure modes, and survey-paper references — live in [data/exposure_problems.yaml](data/exposure_problems.yaml). YAML is the canonical form so the entries can be programmatically rendered into tables, surfaced in YAPS cards, and revised through pull requests.

Each YAPS card SHOULD declare which `EP-` entries it is responding to. This makes the card's *rationale* legible — not just "we used FL + DP + TEE" but "we used FL + DP + TEE because we are responding to EP-04 (update leakage) and EP-03 (untrusted aggregation environment) under EP-11 (cross-jurisdictional analysis)."

---

## How T0 changes the framework

This reframing is the user-visible part of a methodological shift. It is **complementary** to T1–T4, not a replacement.

| Before T0 | With T0 |
|---|---|
| The framework characterises combinations of PETs and reports which appear "mature" | The framework starts from the exposure problems practitioners face, and *uses* the maturity data in T1–T4 to indicate which response is best-supported by evidence |
| Practitioners ask "which PETs should I use?" and the framework offers a table | Practitioners ask "what is my exposure problem?" and the framework offers a small number of well-evidenced responses for each |
| Exotic combinations look as legitimate as canonical ones because both fit in the same table | Combinations are legitimate only when they map to a named exposure problem with a coherent assurance story |
| Sector tables list combinations | Sector tables now also list the dominant exposure problems for that sector (see updated `data/sectors.yaml`) |

This shift addresses one of the most common critiques of combination-first frameworks: that they conflate the question *which PETs can be combined?* (combinatorial) with *which combinations should be deployed?* (rational, problem-driven).

---

## Relationship to the survey paper

This index is **complementary** to the survey paper. The survey paper provides the conceptual basis — algorithmic vs architectural typologies, the assurance-gap argument, the comparative tables in §4 — and remains the authoritative reference for the technical claims. T0 operationalises a specific use of the survey's logic: for a practitioner facing a concrete exposure problem, which responses are evidenced and what assurance bundle is required?

The survey itself does not need a T0 section to be coherent. The recommendation is that the survey mention the concept of exposure-problem-led PET selection briefly in §5 (Cross-Cutting Limitations and Potential Future Directions) and point readers to this repository for the operational form.

---

## Open questions for workshops

These are deliberately surfaced for the workshop series ([workshops/](workshops/)):

1. **Is the EP set complete?** Practitioners may name exposure problems we have missed — particularly in sectors we have under-represented (insurance, telecoms, defence under controlled scope, third-sector).
2. **Are the boundaries crisp?** EP-04 and EP-08 both touch composition; EP-01 and EP-09 both touch identity disclosure. Workshop tests whether practitioners can route their concrete problem to a single EP, or whether the boundaries need redrawing.
3. **What is the right granularity?** Some practitioners may prefer finer-grained EPs (e.g. splitting EP-04 into gradient-inversion vs participation-inference). Others may prefer coarser. The right level is the one that supports concrete card construction.
4. **Are the assurance anchors generalisable?** The anchors named per EP must work across sectors and jurisdictions. If they do not, the EP itself is too narrow.

See [workshops/W1-exposure-problems.md](workshops/W1-exposure-problems.md) for the workshop prompts that test these questions.
