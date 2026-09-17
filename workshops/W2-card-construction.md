# Workshop 2 — Card Construction (Stepwise-from-Private)

**Tests:** Whether the [stepwise-from-private approach](../STEPWISE_RISK.md) is workable, what step granularity feels natural to practitioners, how the card chain is maintained over time, and whether the resulting card is legible to a non-author reviewer.

**Duration:** 3 hours.

**Participants:** 6–8. Pairs of practitioners working on the same deployment (one technical, one governance) where possible. Mix of: privacy engineers, data protection officers, technical solution architects, statistical disclosure control practitioners. At least one regulator-side participant (ICO, ONS, NHS data-access governance, equivalents) where possible — they will not be card *authors* but reviewers.

---

## The workshop's central claim under test

> A privacy card is best constructed not by asking "what risk does this deployment pose?" (the DPIA framing) but by asking "what enabling step has caused us to deviate from a completely-private baseline, and what does each deviation cost?" Starting from a known-private baseline addresses the recursive DPIA problem: if the risk is unknown, the mitigation cannot be effective.

We test this by having pairs construct a real-or-composite card *live*, working through the stepwise method, and observing where the method helps and where it gets in the way.

---

## Pre-reading

- [STEPWISE_RISK.md](../STEPWISE_RISK.md) — the methodology under test.
- [EXPOSURE_PROBLEMS.md](../EXPOSURE_PROBLEMS.md) — referenced by every step.
- [yaps/CARDS_GUIDE.md](../yaps/CARDS_GUIDE.md) — the existing card guide. Will be updated based on this workshop.
- [`stepwise-privacy-cards/card/example_chain.json`](https://github.com/j0hn-s/stepwise-privacy-cards/blob/main/card/example_chain.json) — a worked example card from the FLTA 2026 evaluation; useful as a reference for the agreement-forcing exercise.

Participants should bring: a deployment (real, composite, or anonymised) they can construct a card for. Pairs should agree in advance which deployment.

---

## Session structure

### 0:00 — 0:15 · Setup

- Facilitator restates the central claim under test.
- Each pair states (a) the deployment they have brought, (b) at one sentence, what each step in their architecture is intended to enable.
- Briefly recap the DPIA critique and how stepwise approaches respond to it.

### 0:15 — 1:15 · Build the chain — live

Each pair constructs the chain of steps for their deployment, starting from the completely-private baseline. Facilitator circulates.

Constraints provided to the pairs:

- Use the [stepwise template](#stepwise-template) (below).
- Each step must include: purpose, exposure problem (T0 ref), PET response, trust assumption added, assurance anchor, residual risk after step.
- A step that cannot fill all six fields is not yet a step — interrogate it.
- The pair must agree on every step before moving to the next.

This forced agreement is the test. Where the technical and governance participants disagree, what is the source of the disagreement?

### 1:15 — 1:25 · Break

### 1:25 — 1:55 · Cross-pair reading

Pairs swap chains. Each pair reads the other's chain *cold* and tries to identify:

- Which step's purpose is unclear?
- Which assurance anchor is missing or implausible?
- Which trust assumption has been smuggled in (assumed rather than declared)?
- Where they would push back if they were the regulator-side reviewer.

This is the **non-author legibility test**. A card that only its author can read is not useful for the framework's purpose.

### 1:55 — 2:25 · Maintenance walk-through

For one pair's chain (chosen by the facilitator), the group simulates a maintenance event:

- "Six months later, you have added a new use case that requires sharing model weights externally."
- "Six months later, the regulator has tightened guidance on epsilon at population scale."
- "Six months later, a new institution has joined the federation."

The pair walks through how the chain would be revised. Key questions:

- Is the chain *editable* in this form, or does each change require a rewrite?
- How is the audit trail preserved?
- Who owns the maintenance — and is that an explicit role in the framework?

### 2:25 — 2:50 · Aggregate findings

Facilitator collects:

- Granularity feedback: too many steps, too few, about right?
- Field-by-field critique: which fields participants found necessary, which felt over-specified.
- Where the stepwise method *helped* (named instances) and where it *got in the way* (named instances).
- Maintenance signal: do practitioners think they would actually update a card six months later? If not, why not?

### 2:50 — 3:00 · Close

- One *thing the framework should make easier* from each participant. Goes into [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) and [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md).
- Thanks; next workshop announced.

---

## Stepwise template

Distributed to each pair, one sheet per step:

```
─────────────────────────────────────────────────────
STEP N — <name of this enabling step>

Purpose
  Why does the deployment need this? (1–2 sentences)

Exposure problem introduced or addressed
  Reference: EP-__  (from T0 index)
  How does this step interact with it?

PET response
  Reference: T1/T2/T3 ID(s)
  Specific tooling, parameters, scheme variant

Trust assumption added
  Which glossary term(s) apply? Who is trusted to do what?

Assurance anchor
  Which artefact makes this step's privacy claim credible?
  Where does it live? Who maintains it?

Residual risk after this step
  What remains exposed that the next step (if any) must address?
─────────────────────────────────────────────────────
```

A chain is the ordered set of such sheets, starting from Step 0 (the baseline) and ending when the actual deployed architecture is in place.

---

## What good output looks like

A productive W2 ends with:

- 3–4 worked chains, each with explicit residual risks at every step.
- A clear signal on whether pairs found the *agreement-forcing* property of stepwise construction useful, or frustrating.
- Concrete proposals for additions / removals to the six-field template.
- A defensible answer to: *can a card constructed this way be maintained over time, or is it a one-shot artefact?*
- Each cross-reading pair able to point out at least one substantive critique of the chain they read — evidence that legibility-to-non-authors is working.

---

## What to watch for

- **Step inflation.** If pairs are creating 8+ steps for a simple deployment, the steps are probably too fine. The right granularity is whatever supports the four reviewer questions in [STEPWISE_RISK.md](../STEPWISE_RISK.md).
- **Step compression.** If pairs collapse multiple distinct deviations into a single step ("we use FL+DP+TEE"), the chain has lost its diagnostic value. Push back.
- **Assumed assurance anchors.** Watch for "we have a privacy accountant" without naming where it lives, what library, what composition theorem. The chain is meant to surface these.
- **Maintenance pessimism.** If every pair says "we would never update this six months later," that is critical signal — the framework as designed is then a one-shot artefact, not a living document.
- **DPIA conflation.** If pairs find themselves writing DPIA-style risk descriptions instead of stepwise deviations, the stepwise method has been crossed with the risk-first method. Useful to name when it happens.

---

## Materials

- Stepwise template (multiple copies per pair).
- T0 index summary.
- Glossary excerpts.
- Worked example cards from the FLTA 2026 evaluation, available in the [stepwise-privacy-cards](https://github.com/j0hn-s/stepwise-privacy-cards) companion repository (`card/example_chain.json` + the 16-chain battery), serve as reference cards.
- A wall surface where chains can be laid out left-to-right and reviewed.
- Two surfaces for building the actual card:
  - **Paper / template** for the chain construction itself (preferred for the agreement-forcing element of the workshop).
  - **The workbench** (`workbench/` — see [workbench/README.md](../workbench/README.md)) for typing the chain into JSON, saving it to Elasticsearch, running it through the YAPS engine, and (if a participant has brought one) ingesting a privacy-eval result record into the card's `risk_calibration` block. Facilitator brings up the local instance ahead of the session (`docker-compose up`).
  - Alternative low-friction surface: the single-file [yaps/frontend/index.html](../yaps/frontend/index.html). Faster setup, no persistence. Use this if Docker is unavailable.

---

## Specific questions to surface during W2

1. Does the stepwise framing reduce DPIA-style "unknown risk" anxiety, or replace it with a different kind of anxiety ("am I making too many steps?")?
2. Should some steps be templated (e.g. "Step 1 is almost always 'data must leave its source'")? If so, where does the framework provide these templates?
3. How does the chain handle a step that is *removed* (e.g. dropping a PET because it is no longer needed)?
4. What is the role of the regulator-side reviewer in the chain? Do they review every step, or only the residuals?
5. Should the chain support *branching* — when one card represents a family of deployments with shared early steps?
