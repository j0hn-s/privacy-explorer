# Workshop 3 — Sector Deepening

**Tests:** Whether the [idiosyncratic constraints per sector](../data/sectors.yaml) capture what actually drives PET decisions in those sectors, what is missing for under-represented sectors, and whether the cross-jurisdictional dimension (the same PET deployed under different legal regimes) is workable in the framework.

**Duration:** 2.5 hours.

**Participants:** 6–10, by sector. Run this workshop *separately per sector* — a healthcare-focused W3, a finance-focused W3, a public-sector W3, etc. Each session needs participants who actually work in that sector and can name the laws, frameworks, and institutional norms in play. Where possible, include at least one regulator-side participant per session.

---

## The workshop's central claim under test

> Each sector has a set of *idiosyncratic constraints* — laws, regulatory expectations, institutional frameworks — that shape PET decisions in ways that pure technical merit does not capture. A framework that does not surface these constraints alongside its technical recommendations cannot support deployment-realistic decisions. T4's sector entries are an attempt to encode those constraints. The test is whether sector experts find the encoding accurate, useful, and complete.

The constraints we have encoded so far are **suggestive and incomplete** — explicitly marked as such in the YAML. W3 is the deepening process.

---

## Pre-reading

- The relevant sector entry in [data/sectors.yaml](../data/sectors.yaml). Participants receive a printed copy of just their sector.
- [EXPOSURE_PROBLEMS.md](../EXPOSURE_PROBLEMS.md) — the index of EPs the sector entry references.
- A skim of [README.md](../README.md) (just the T4 sectoral table).

Participants should bring: their honest answer to the question *what makes my sector different?* — both the technical and the non-technical answers.

---

## Session structure

### 0:00 — 0:15 · Setup

- Facilitator names the sector and the central claim under test.
- Each participant names the most recent PET-related decision they were involved in and *one constraint that shaped it* that was not technical.

### 0:15 — 0:55 · Constraint mapping

The current sector entry is read aloud field-by-field:

- `legal_instruments`
- `regulatory_expectations`
- `institutional_frameworks`
- `what_this_implies_for_pets`

For each field, participants annotate the printed copy with:

- ✓ where the entry is accurate.
- ✗ where it is wrong, outdated, or oversimplified.
- ✚ where something material is missing.
- ? where the entry is correct in principle but the participant is unsure how to apply it in practice.

These annotations are pooled at the end of the field.

### 0:55 — 1:25 · The "things that don't transfer" round

Each participant names one thing about their sector that practitioners *outside* the sector consistently fail to understand. Examples to seed the discussion:

- "People outside healthcare assume 'anonymised' means out-of-scope under GDPR. It doesn't, because of the common-law duty of confidentiality."
- "People outside finance underestimate how much the second-line model-governance regime constrains stochastic mechanisms."
- "People outside national statistics underestimate how political the parameter choice is — and how visible the choice has to be."

These should map directly into the `what_this_implies_for_pets` field of the YAML.

### 1:25 — 1:35 · Break

### 1:35 — 2:05 · Cross-sector mapping (cross-jurisdictional dimension)

If the workshop has participants who span jurisdictions (UK + US + EU is the typical mix for healthcare and finance), spend this slot specifically on what *the same deployment* looks like under different regimes.

Worked prompt: "An FL + DP deployment running on a US infrastructure provider, training a model from EEA hospital data, for downstream use by a UK NHS commissioner. What changes about the card under: GDPR alone; UK GDPR + Common Law Duty + DSPT; US HIPAA-only; all three simultaneously?"

The aim is not to produce a legal answer — it is to surface what the framework needs to support cross-jurisdictional cards.

### 2:05 — 2:25 · Aggregate findings

Facilitator collects:

- Concrete changes to the sector entry (additions, removals, rewrites).
- Constraints that *cut across* sectors and may belong in a separate "cross-cutting constraints" section.
- The shortlist of things that "don't transfer" — for inclusion in the workshop summary and feedback into the framework's positioning.
- New sectors that were nominated but not yet represented (insurance, telecoms, defence within appropriate scope, environmental, third sector).

### 2:25 — 2:30 · Close

- One *thing the framework currently gets wrong about this sector* from each participant. Goes into [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) under the sector heading.
- Thanks; mention of when the revised entry will be pushed to the repository.

---

## What good output looks like

A productive sector-specific W3 ends with:

- A list of concrete YAML changes for the sector entry — additions and corrections.
- A clear signal on which `idiosyncratic_constraints` sub-block (legal / regulatory / institutional) is doing the most work in that sector and which is under-developed.
- A handful of cross-sector observations that may inform the framework as a whole.
- Two or three "doesn't transfer" notes that can be embedded in the framework's external communication.

---

## What to watch for

- **Legal-clause fishing.** Participants may try to use the workshop to debate specific clauses ("does Article 6(1)(f) GDPR really cover this?"). Redirect to: does this constraint shape PET choice in your sector? The framework is not the place to settle legal questions; it should reflect the constraints practitioners actually navigate.
- **Sector vs use-case slippage.** Some constraints belong to a specific use case (e.g. clinical trials) rather than the sector (healthcare). Watch for this and tag accordingly.
- **Regulator participation dynamics.** Regulator-side participants are valuable but can chill candour. The facilitator must explicitly frame the session as informing the framework, not as a public commitment by the regulator.
- **Cross-sector echo.** If healthcare and finance keep naming the same constraint (e.g. model-governance regimes for stochastic outputs), that constraint may need to be elevated out of sector-specific entries into a cross-cutting note.

---

## Sectors to prioritise

Order of W3 sessions, based on framework gaps:

| Order | Sector | Why this priority |
|---|---|---|
| 1 | Healthcare (UK + US, joint where possible) | Most fragmented regulatory regime; high practitioner pain |
| 2 | Public sector / official statistics | Best-documented sector but most political (DP parameter debates) |
| 3 | Finance / inter-organisational analytics | Strong commercial deployment evidence; least-engaged with privacy-research community |
| 4 | Technology platforms | Maturity exists but transferability is contested |
| 5 | Sectors not yet in T4 (insurance, telecoms, defence within scope) | Coverage extension |

---

## Materials

- Printed sector entry (one per participant).
- Coloured pens for ✓ / ✗ / ✚ / ? annotation.
- The cross-jurisdictional worked prompt printed on a separate sheet.
- T0 index summary for cross-reference.

---

## Specific questions to surface during W3

1. Are the categories `legal_instruments` / `regulatory_expectations` / `institutional_frameworks` the right cut, or are they overlapping?
2. Where is the line between a *sectoral* constraint and a *jurisdictional* constraint, given that many sectoral regimes are jurisdiction-specific?
3. Should cards declare the jurisdiction(s) their data subjects sit in, or the jurisdiction(s) their controller operates from, or both?
4. What is the relationship between the `idiosyncratic_constraints` block and the `regulatory_context` block in the privacy card schema? Are they redundant?
5. For sectors with strong existing governance regimes (NHS DSPT, NIST RMF, FCA model risk), should the framework offer pre-populated card templates? Or would that be premature standardisation?
