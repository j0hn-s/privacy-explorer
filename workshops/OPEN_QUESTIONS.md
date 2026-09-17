# Open Questions

A live register of questions the framework has not yet answered. Sourced from the survey paper's *Cross-Cutting Limitations and Potential Future Directions* (§5), from workshop observations, and from external feedback. Updated continuously.

> **How to use this register.** Each question has a tag (`scope`, `methodology`, `usability`, `governance`, `sector`, `cross-jurisdictional`, `maintenance`, `design`). Questions in `status: open` are being worked on; `deferred` are noted but parked; `resolved` are kept for the audit trail with a brief note on how they resolved.

---

## Scope and conceptual reframing

| # | Question | Tag | Status |
|---|---|---|---|
| Q01 | Is "exposure problem" the right name for T0, or does another term land better with practitioners (e.g. "disclosure surface", "exposure vector", "privacy concern")? | scope | open — W1 |
| Q02 | Should the T0 entries be sector-tagged (one EP per sector) or kept sector-agnostic (one EP, many sectors)? | scope | open — W1, W3 |
| Q03 | Are 10–12 EPs the right granularity, or should some be split / merged? | scope | open — W1 |
| Q04 | Where the framework conflicts with familiar terms-of-art ("anonymisation", "de-identification"), how should we handle this in cards — translate, replace, footnote? | usability | open — W1 |
| Q05 | Is the framework's conceptual scope clear: empirical PET combinations and assurance, *not* legal interpretation of GDPR / HIPAA / equivalents? | scope | resolved — yes, documented in [README.md](../README.md) and [GLOSSARY.md](../GLOSSARY.md); revisit if workshops show drift |

---

## Methodology — stepwise from private

| # | Question | Tag | Status |
|---|---|---|---|
| Q10 | Does the stepwise-from-private framing reduce DPIA-style "unknown risk" anxiety, or does it introduce a different anxiety ("am I making too many steps?")? | methodology | open — W2 |
| Q11 | Should the framework provide *template chains* for common deployments, or does that risk premature standardisation? | methodology | open — W2 |
| Q12 | How does the chain support *step removal*? (When a PET is dropped because it is no longer needed.) | methodology | open — W2 |
| Q13 | Should the chain support *branching* — one card representing a family of deployments with shared early steps? | methodology | open — W2 |
| Q14 | How should the chain interact with an existing DPIA where one is required? Annex? Reference document? Self-contained alternative? | governance | open — W2; suggested default: annex |
| Q15 | At what point does the chain stop being maintainable? (Number of steps, frequency of revisions, team-size threshold.) | methodology | open — pending real-world deployments |
| Q16 | What is the right level of formality? Should each step assert a property, or simply describe a deviation? | methodology | open — W2 |

---

## Threshold of actionability

| # | Question | Tag | Status |
|---|---|---|---|
| Q20 | When are PET-derived results "actionable evidence" versus "indicative"? Survey §5 names this as an open question; the framework does not currently answer it. | methodology | deferred — needs sector-specific evidence; touch in W3 |
| Q21 | Are confidence intervals, suppression rates, or attack-AUC the right unit for actionability? Practitioners need a portable summary. | methodology | open — feeds into card design (W4) |
| Q22 | How does the framework handle the case where two competent reviewers disagree about whether the residual risk is acceptable? | governance | open — workshop signal needed |

---

## Sector and jurisdictional coverage

| # | Question | Tag | Status |
|---|---|---|---|
| Q30 | Are the categories `legal_instruments` / `regulatory_expectations` / `institutional_frameworks` the right cut for sector idiosyncratic constraints? | sector | open — W3 |
| Q31 | Where is the line between a *sectoral* constraint and a *jurisdictional* constraint, given that many sectoral regimes are jurisdiction-specific? | cross-jurisdictional | open — W3 |
| Q32 | Should cards declare the jurisdiction(s) data subjects sit in, the jurisdiction(s) the controller operates from, or both? | cross-jurisdictional | open — W3 |
| Q33 | Sectors not yet covered: insurance, telecoms, defence (within appropriate scope), environmental data, third sector. Which to add first? | sector | open — W3 priority list |
| Q34 | Should the framework offer pre-populated card templates for high-governance regimes (NHS DSPT, FCA model risk), or is that premature standardisation? | sector | open — W3 |

---

## Maintenance and lifecycle

| # | Question | Tag | Status |
|---|---|---|---|
| Q40 | Will teams actually update a card six months later, or does the framework need explicit lifecycle triggers (re-review on architecture change, parameter change, regulatory change)? | maintenance | open — W2 + post-workshop deployment evidence |
| Q41 | Who owns card maintenance — and is that an explicit role in the framework (e.g. "card steward")? | maintenance | open — W2 |
| Q42 | How is the audit trail preserved across major card revisions — version history, change log, both? | maintenance | partial — current schema has `change_log`; workshop test in W2 |
| Q43 | Machine unlearning (survey §5; Liu et al. 2024) is a lifecycle control affecting cards. How does the framework represent it — as an assurance artefact, a step, both? | methodology | open |

---

## Design and visual representation

| # | Question | Tag | Status |
|---|---|---|---|
| Q50 | Is the card best understood as a *document*, a *dashboard*, a *story*, or something else? | design | open — W4 |
| Q51 | Should a card have a *short form* (single page) and a *long form* (full record), with the short form as the canonical artefact? | design | open — W4 |
| Q52 | What is the relationship between privacy cards and adjacent artefacts (DPIAs, model cards, datasheets for datasets, system cards)? | design | open — feeds into framework positioning |
| Q53 | What is the minimum visual element needed to make a card *recognisable* across the framework? | design | open — W4 |
| Q54 | Should a single card render differently for engineering, governance, and regulatory audiences, or be one form all three can read? | design | open — W4 |

---

## Cross-cutting and governance

| # | Question | Tag | Status |
|---|---|---|---|
| Q60 | How should the framework handle *contested* maturity assessments? T1 declares stage 1–4 but two participants will disagree on any non-trivial primitive. | governance | partial — YAML is forkable; workshop feedback needed |
| Q61 | When the framework's assurance recommendation conflicts with sectoral regulatory guidance, which takes precedence in a card? | governance | open — W3 |
| Q62 | What is the framework's relationship with formal standards work (NIST SP 800-226 (Draft), ISO/IEC 20889, ISO/IEC 27559)? Aligning, complementing, or contesting? | governance | resolved as *complementing*; documented in [GLOSSARY.md](../GLOSSARY.md) and survey §3.5 |
| Q63 | Should the framework eventually be submitted to a standards body, or remain a research artefact for the foreseeable future? | governance | deferred |
| Q64 | How do we prevent the framework from being used as a *compliance shield* (filing a card and claiming privacy by association)? | governance | open — surface in workshop framing |

---

## Survey paper interaction

| # | Question | Tag | Status |
|---|---|---|---|
| Q70 | The survey paper mentions the privacy card concept in §5. Should it remain in §5 (with refined wording), be moved to an appendix, or be removed entirely with a forward reference to this repository? | scope | open |
| Q71 | The survey's Table 4.2 lists six combinations. The repository extends this slightly. How should the repository signal its differences from the survey to readers? | scope | resolved — combinations now carry `survey_paper_anchor` fields; documented in [README.md](../README.md) |
| Q72 | If a future iteration of the survey draws explicit examples from the repository's worked cards, how should attribution and review work? | governance | deferred |

---

## External collaborator feedback (OXFORDIA, 2026-09)

Sourced from a real external stakeholder's own stated research gaps (a Solid-pod-based data access platform, email correspondence 2026-09), rather than from a workshop session — kept as its own section since the source differs from W1–W4.

| # | Question | Tag | Status |
|---|---|---|---|
| Q80 | EP-02 ("data cannot leave its source for joint computation") already covers both training a joint model and computing a joint statistic, but every worked example under it (`P-02`, `S-03`) is model-training-shaped. Does the framework need an actual worked example of the statistic-only case, or is the description refinement (2026-09) sufficient on its own? | scope | open — see `data/exposure_problems.yaml` EP-02 |
| Q81 | `TOOLING.md` is deliberately low-maintenance and version-unpinned. Is that the right trade-off long-term, or will an unmaintained tooling page mislead more than it helps once entries are a year stale? | maintenance | open — revisit after first few PRs land |
| Q82 | For an organisation in OXFORDIA's position — deciding between MPC and DP extensions before funding a developer — what would actually make a stepwise-privacy-card-style output *usable* as a decision input (a report format, a comparison view, something else)? Distinct from whether the card/attack methodology itself is right. | usability | open |
| Q83 | Bias/fairness and scalability are named as first-class concerns by at least one external stakeholder (OXFORDIA) but are not tracked as structured, comparable fields anywhere in T1–T4 today — only as prose asides. Worth a structured field, or does that overstate how comparable fairness effects actually are across primitives? | scope | open |

---

## How questions are resolved

A question moves from `open` to `resolved` when:

1. A workshop session produced consensus that one answer is right, or one answer is clearly *not* right.
2. The framework's documentation has been updated to reflect the answer.
3. The change has been recorded in the workshop summary under [workshops/runs/](./).

A question marked `deferred` is one we have decided not to answer for now, with the rationale recorded inline.

Questions can be reopened by adding a new entry referring to the original (do not edit resolved questions in place).
