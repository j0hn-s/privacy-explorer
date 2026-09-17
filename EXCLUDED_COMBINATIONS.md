# T5 — Assessed and Excluded Combinations

A working audit trail of PET combinations that were *considered* for T2/T3 and where they landed. Where [T1–T4](README.md) read *technique → combination → stack → sector*, T5 reads *candidate combination → assessed → admitted or excluded, with reasons*.

> **Why this exists.** An empty cell in T2/T3 is ambiguous: is a combination absent because it doesn't make architectural sense, because no one has looked, or because it was looked at and rejected? Those are three very different claims, and only the third is a substantive finding. T5 makes the distinction explicit, so the design space reads as narrow for stated reasons rather than by omission — directly addressing the combinatorics-vs-practice gap the survey paper names in its concluding section. Named as a gap in [DIAGRAM.md](DIAGRAM.md)'s "Suggested Further Iterations" #3; this document and [data/exclusions.yaml](data/exclusions.yaml) are the first pass at closing it.

This is intended to be **contested at workshops**, more than any other table in this repository. Each entry names a specific evidence gap and a specific revisit trigger — if you know of a deployment or a paper that closes one of those gaps, that is exactly the kind of contribution this table exists to receive.

---

## How to read this table

Each entry has:

- **Considered as** — what the combination would represent if admitted, in plain language.
- **Status** — `excluded` (assessed, not currently admitted — see the evidence gap and revisit trigger) or `promoted` (was excluded, has since been admitted to T2/T3; kept here as the audit-trail record).
- **Reason** — why the current assessment landed where it did.
- **Evidence gap** — specifically what is missing, not a vague "not enough evidence."
- **Revisit trigger** — the specific thing that would change the assessment. Not "more research" — a named type of evidence.

The canonical source is [data/exclusions.yaml](data/exclusions.yaml).

---

## The register

| ID | Combination | Status | One-line reason |
|---|---|---|---|
| `E-01` | `HE` + `FL` (HE-based secure aggregation) | excluded | Prototype-level only; no deployment-documented or peer-reviewed instance at practical FL scale |
| `E-02` | `MPC` + `DP` (standalone, no FL layer) | excluded | Every documented instance already reduces to `S-03` (FL + MPC + DP-C); no distinct assurance story found outside FL |
| `E-03` | `TRE` + `SYN` (synthetic development data ahead of TRE access) | **promoted → `P-10`** | Re-assessed 2026-09; found peer-reviewed and deployment-documented evidence (Simulacrum, ONS synthetic dummy data) stronger than several combinations already admitted at `theoretical` confidence |

---

## E-03 in more detail, as a worked example of the process

`E-03` is deliberately kept in this table even though it has been promoted, because it is the clearest illustration of what T5 is for. `TRE + SYN` was originally passed over in an earlier pass at this repository's "Suggested Further Iterations" list, on the reasoning that "deployment evidence is thin." Revisiting that assumption directly — rather than leaving the gap unexamined — surfaced two strong precedents already adjacent to material this repository cites elsewhere:

- The **ONS Data Science Campus** documents issuing synthetic "dummy data" ahead of Secure Research Service / Integrated Data Service accreditation, specifically so researchers can develop and test code before requesting real access.
- **Simulacrum** (Health Data Insight, built with NHS England's National Disease Registration Service) is a synthetic cancer registry used for exactly this purpose ahead of Cancer Analysis System access — with a **peer-reviewed** evaluation across 18 projects reporting an average 2.3-month code-development-to-data-release cycle.

That evidence base is stronger than several combinations already sitting in T2 at `confidence: theoretical`. The lesson generalises: **"thin evidence" is a claim that decays, not a permanent classification** — it should be re-checked periodically and whenever a workshop participant flags a precedent, not treated as settled once written down. See [data/pairings.yaml](data/pairings.yaml) `P-10` for the resulting entry.

---

## Workshop use

This table is a natural prompt for an industry-stakeholder session: for each `excluded` entry, ask participants directly whether they know of a deployment or evaluation that would close the named evidence gap. A stakeholder naming a real `HE`+`FL` production deployment, or a genuinely non-FL `MPC`+`DP` pattern, is exactly the kind of finding that should move an entry from `excluded` toward a proposed new T2 row — following the same path `E-03` already took.

Contributions follow the same PR workflow as the rest of `data/` — see [CONTRIBUTING.md](CONTRIBUTING.md). A proposed promotion should arrive with the same evidence bar CONTRIBUTING.md sets for any new T2 pairing: an artefacts list and at least one published reference with a `url` field.
