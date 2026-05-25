# Stepwise-from-Private Risk Approach

A methodological note on how privacy cards in this repository are intended to be constructed. This is a deliberate alternative to risk-first approaches like the Data Protection Impact Assessment (DPIA), which carry a well-known critique: if the privacy risk is unknown, how can it be effectively mitigated?

> **Short version.** Start from a completely-private baseline (data does not flow at all). Each PET-enabled access pattern is recorded as a *deviation* from that baseline. Each deviation has a named purpose, a named exposure problem ([T0](EXPOSURE_PROBLEMS.md)), a named PET response, and a named residual risk. The card is the documented chain of deviations.

---

## The DPIA critique, and why this matters

The DPIA process — anchored in GDPR Art. 35 and equivalent regimes — asks a project to assess the risk to data subjects' rights and freedoms before processing begins. The familiar critique is recursive: if the practitioner already knew which risks the architecture creates, they would already have mitigated them. A DPIA can therefore lapse into either:

- a **compliance ritual** — generic risks are listed, generic mitigations are claimed, the document is filed and never revisited; or
- an **incomplete enumeration** — the team identifies the risks they happen to know about, misses the ones they do not, and the document is treated as authoritative anyway.

A privacy card aims for something different: a **structured argument** rather than an enumeration. The argument is constructed by starting from a state where no risk exists (no data flows) and recording each PET-enabled deviation that the deployment requires.

This is not a replacement for DPIAs. A privacy card constructed this way can function as the *technical annex* to a DPIA, providing the substantive content that the DPIA's procedural form references. The distinction we are drawing is methodological, not legal.

---

## The completely-private baseline

The baseline state for any card is:

| Aspect | Baseline value |
|---|---|
| Data flow | None. Data sits at source; no party receives, computes on, or releases anything derived from it. |
| Exposure surface | Zero. No release, no joint computation, no model update, no synthetic artefact, no query result. |
| Trust assumptions | Trivial — the data custodian trusts itself. |
| Privacy risk to data subjects | Trivial — nothing leaves the controlled environment. |
| Utility | Zero. The data supports no analysis, no service, no decision. |

This is a useful baseline precisely because **it is unworkable**. Real deployments must deviate from it. The question is *how* — and the discipline is to make each deviation explicit, justified, and bounded.

---

## The stepwise construction

A card is constructed as an ordered sequence of *enabling steps*. Each step has the same shape:

```
Step N: <name of the enabling step>

  Purpose:           Why does the deployment need this?
  Exposure problem:  Which T0 entry (EP-) does this introduce or address?
  PET response:      Which T1 primitive, T2 pairing, or T3 stack is being added?
  Trust assumption:  What trust does this step now require? (glossary terms)
  Assurance anchor:  Which artefact makes this step's privacy claim credible?
  Residual risk:     What remains exposed after this step that the next step
                     may need to address?
```

Steps build cumulatively. The card is the ordered list, ending when the deployment's actual access pattern is in place. The residual risks declared at each step are exactly the surface area the YAPS rules check for and that the card holder is accountable for managing over time.

Where the `assurance anchor` for a step is a DP parameter manifest, the anchor SHOULD include either a μ-DP value or a stated operational attack-rate target (recorded on the card's `risk_calibration` block, schema 1.2), so the parameter's privacy implication is legible without re-derivation. Single ε reporting hides the underlying privacy trade-off; YAPS rule `RISKCAL-001` (GREEN) surfaces this on cards that declare any DP variant but omit the calibration block.

---

## A worked example — federated training on hospital data

The following is illustrative, not normative. The point is the *shape* of the argument, not the specific PET choices.

**Step 0 — Baseline.**
- Data: patient records sitting in each hospital's local store.
- Exposure: none.
- Utility: none — no joint analytics possible.
- The deployment must deviate from this to support cross-institutional model training.

**Step 1 — Enable computation on local data without movement.**
- Purpose: enable each hospital to compute model gradients on its own data.
- Exposure problem introduced: **EP-04** (distributed training where updates may leak training data).
- PET response: `FL` (federated learning) — raw data stays local; only model updates leave.
- Trust assumption added: the coordinator is honest-but-curious (sees updates).
- Assurance anchor: training protocol specification, audit log of round participation.
- Residual risk after step 1: updates leak training data via gradient inversion or membership inference. Coordinator can see per-hospital updates.

**Step 2 — Bound what each update can reveal about any individual.**
- Purpose: address the per-update leakage from step 1.
- Exposure problem addressed: EP-04 (continuing); also introduces **EP-08** (composition across rounds).
- PET response: `DP-C` (central differential privacy applied during aggregation) — combination becomes **P-01 (FL + DP)**.
- Trust assumption added: parameter governance (ε, δ, sensitivity); composition theorem named.
- Assurance anchor: privacy accountant, parameter manifest, named composition theorem.
- Residual risk after step 2: coordinator sees individual DP-noised updates before aggregation; this is less than raw updates but more than only the sum.

**Step 3 — Make the coordinator blind to individual updates.**
- Purpose: close the coordinator-visibility gap left in step 2.
- Exposure problem addressed: EP-04 (continuing).
- PET response: `MPC` for secure aggregation — combination becomes **S-03 (FL + MPC + DP-C)**.
- Trust assumption added: corruption threshold for secure aggregation (typically `k`-of-`n` semi-honest).
- Assurance anchor: secure-aggregation protocol specification, correctness proof, adversary-model declaration.
- Residual risk after step 3: coordinator infrastructure operator may still see encrypted intermediate state; side-channel and compromised-host risks remain.

**Step 4 — Protect the aggregation environment itself.**
- Purpose: address infrastructure-operator visibility into encrypted intermediates and run-time state.
- Exposure problem addressed: **EP-03** (untrusted compute environment).
- PET response: `TEE` for the aggregation server — combination becomes essentially **S-01 (FL + TEE + DP-C)** with the secure aggregation handled inside the enclave, or a four-layer stack depending on design choices.
- Trust assumption added: hardware vendor + attestation chain.
- Assurance anchor: attestation report, enclave measurement, side-channel mitigation declaration.
- Residual risk after step 4: hardware vendor compromise; side-channel attacks not covered by declared mitigations; the *release* — the final model — still needs bounded leakage (already addressed in step 2, but the budget must hold across the full deployment).

**End state.** The card now documents an FL + secure-aggregation + DP-C + TEE deployment with four explicit deviations from the completely-private baseline. Each deviation has a named purpose, exposure problem, PET response, trust assumption, assurance anchor, and residual risk. The total privacy claim is the conjunction of the assurance anchors; the total trust footprint is the union of the trust assumptions; the total residual risk is the union of the per-step residuals.

A reviewer can inspect the chain step-by-step and ask:
1. Is each step's purpose legitimate?
2. Is each PET response evidenced (does the assurance anchor exist)?
3. Are the trust assumptions named and acceptable?
4. Is the residual risk after the final step acceptable for the use?

These are the four questions the framework is built to support.

---

## How this addresses the DPIA critique

The DPIA critique was: if the risk is unknown, the mitigation cannot be effective. The stepwise approach inverts the structure:

- The starting state has a *known* privacy posture: trivially private, trivially useless.
- Each deviation introduces a *named* risk (the exposure problem it solves *and* the residual risk it leaves).
- The deployment cannot drift to a state where the privacy risk is "unknown" — every step is recorded, and any state that is not on the card is not authorised.

This is closer to how statistical-disclosure-control analysts have long worked: start from "no release" as the safe state and justify each release that deviates from it. The privacy card extends this discipline to architectural and assurance choices, not only to statistical releases.

---

## Relationship to YAPS rule evaluation

A card constructed this way maps cleanly onto YAPS rule evaluation:

| Stepwise element | YAPS rule category |
|---|---|
| **Trust assumption added** | IFACE rules — what crosses a component boundary |
| **PET response chosen** | COMP rules — composition risks between PETs |
| **Assurance anchor named** | ASSUR rules — required artefacts and their status |
| **Residual risk declared** | GOV rules — governance and procedural controls |
| **Exposure problem (T0) referenced** | SECTOR + REG rules — sectoral and regulatory implications |

A rule firing red means: a step's assurance anchor is absent, or its trust assumption is unnamed, or its residual risk has not been declared. The rule report is, in this reading, a structured critique of the chain of deviations.

---

## Workshop questions

This methodology is intended to be tested through the workshop series. Key questions to surface (see [workshops/W2-card-construction.md](workshops/W2-card-construction.md)):

1. Does the "step" granularity match how practitioners think? Some teams may prefer fewer, coarser steps; others finer.
2. Can teams reach agreement on what constitutes a legitimate *purpose* for each step? This is where business / clinical / public-interest justifications enter the framework.
3. How is the chain *maintained* over time? A card is a living document; deployments change. The framework needs explicit support for adding, removing, or revising steps with audit trail.
4. Does the chain remain legible to non-technical reviewers (DPOs, ethics committees, regulators)? If not, the workshop should surface what abstractions or visual aids are needed.
5. Where the chain converges with an existing DPIA, how should the documents be linked? (Recommendation: privacy card as technical annex; DPIA as legal-procedural carrier.)

See [workshops/](workshops/) for the workshop materials.
