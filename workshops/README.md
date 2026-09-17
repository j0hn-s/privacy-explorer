# Workshops — Testing the Privacy Explorer / YAPS Framework

A series of workshops designed to test, refine, and stress-test the conceptual framework encoded in this repository. The workshops are intentionally *iterative*: each is a structured opportunity for practitioners, researchers, designers, and regulators to interrogate one part of the framework and surface what works, what does not, and what is missing.

> **Goal.** A successful framework is one that practitioners can pick up, use to construct a card for a real deployment, and have that card be useful for review by someone other than the author. The workshops test each of those properties in turn.

---

## The workshop series

| | Workshop | Tests | Approximate duration |
|---|---|---|---|
| [W1](W1-exposure-problems.md) | **Exposure problems** | Whether practitioners think in terms of common exposure problems, whether the [T0 index](../EXPOSURE_PROBLEMS.md) is complete, whether the boundaries are crisp | 2.5 hours |
| [W2](W2-card-construction.md) | **Card construction (stepwise-from-private)** | Whether the [stepwise approach](../STEPWISE_RISK.md) is workable, what step granularity feels natural, how the chain is maintained over time | 3 hours |
| [W3](W3-sector-deepening.md) | **Sector deepening** | Whether the [idiosyncratic constraints](../data/sectors.yaml) per sector are accurate and complete, what is missing for non-canonical sectors (insurance, telecoms, defence under controlled scope) | 2.5 hours |
| [W4](W4-design-and-visuals.md) | **Design and visual representation** | Whether the card concept can be made appealing and legible — explicitly as a *design exercise* with creative practitioners as participants | 3.5 hours (longer, hands-on) |

The order matters. W1 tests the conceptual reframing that everything else depends on. W2 tests the construction process. W3 tests the contextual fit. W4 tests usability and aesthetic — the dimension that determines whether the framework gets picked up at all.

A full cycle of W1–W4 with separate participant pools produces enough material for a substantive iteration of the framework. Some questions will only resolve after two or three cycles.

---

## Cross-cutting reference documents

| Document | Purpose |
|---|---|
| [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) | The set of open questions across all workshops, drawn from the survey paper and from feedback so far. Updated after every workshop. |
| [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) | The framework's design decisions and the rationale for each. Workshop outputs may close, reopen, or revise these. |
| [FACILITATOR_NOTES.md](FACILITATOR_NOTES.md) | Practical guidance for running each workshop: room setup, materials, time-keeping, common derailments. |
| [PARTICIPANT_PROFILES.md](PARTICIPANT_PROFILES.md) | Who to invite to each workshop and why. Mix of roles is deliberate. |

---

## What the workshops are *not*

- **Not consultations.** The workshops are not asking participants to approve or rubber-stamp the framework. They are designed to actively test it.
- **Not user-testing for a product.** The framework is a *conceptual* artefact. The workshops test the concept, not a specific UI or tool implementation.
- **Not a substitute for evidence from real deployments.** A worked card in a workshop is a useful artefact; it is not the same as a card maintained alongside a live deployment over six months. The latter is the harder evidence and remains future work.
- **Not academic peer review.** The workshops complement peer review of the survey paper; they do not replace it. Submitting the framework's conceptual claims to a peer-reviewed venue is a separate activity.

---

## Outputs from a workshop cycle

After each workshop, the following artefacts should exist:

1. **Updated YAML / Markdown sources** in this repository, with workshop-driven changes committed.
2. **An updated [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md)** with new questions added and resolved questions removed (or marked resolved).
3. **A short workshop summary** (one or two pages) documenting what was tested, what changed, and what remains open. Suggested location: `workshops/runs/<YYYY-MM>-<workshop-id>.md`.
4. **Where applicable, a participant-co-authored card** that illustrates the framework applied to a real deployment from a participant's domain. These cards live in [yaps/cards/examples/](../yaps/cards/examples/) once cleared for inclusion.

---

## Ethics and confidentiality

Workshop participants may bring concrete deployments to use as case studies. The workshop facilitator must establish, before each session, what is shareable and what is not. Concrete defaults:

- **Sensitive deployment details** (specific datasets, named clinical sites, named clients) stay in the room.
- **Architectural patterns and assurance approaches** are recorded; specific deployment ownership is anonymised in any published material.
- **Worked cards** included in this repository are checked by the participant team before inclusion.
- **Workshop notes** are reviewed by participants before any publication or wider sharing.

This is a research process, not a public consultation. Treat it accordingly.
