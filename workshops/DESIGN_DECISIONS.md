# Design Decisions

The framework's deliberate choices, with their rationale and the workshop signal that should reopen each one. Editing the framework without consulting this document risks unintentionally reversing a position taken for considered reasons.

> **What this is not.** This is not a list of features. It is a list of decisions that constrain how the framework is built, where rationale needs to be visible so the decision can be revisited intentionally.

---

## Conceptual choices

### D-01 Exposure-problem-first index (T0) sits *alongside* T1–T4, not replacing them

**Decision.** T0 (exposure problems) and T1–T4 (primitives, pairings, stacks, sectors) coexist. Practitioners enter the framework from whichever direction matches their task: from T0 if they have a problem and want to know which PETs respond; from T1–T4 if they know the techniques and want to see combinations and sector context.

**Rationale.** Replacing T1–T4 with T0 would lose the technical-reference value that researchers and engineers use the tables for. Replacing T0 with T1–T4 would lose the problem-led routing that practitioners ask for. The two views serve different audiences.

**Workshop signal to reopen.** If W1 shows that practitioners never use T1–T4 directly, the framework could fold them into appendices and lead with T0. If W1 shows that T0 confuses rather than clarifies, the layering needs revision.

---

### D-02 Stepwise-from-private as the construction methodology for cards

**Decision.** Privacy cards are constructed as ordered chains of deviations from a completely-private baseline. Each step records purpose, exposure problem, PET response, trust assumption added, assurance anchor, and residual risk.

**Rationale.** Addresses the recursive DPIA critique: starting from a known-private baseline means each deviation introduces a *named* risk, so the document cannot drift to "unknown privacy risk". This matches how statistical-disclosure-control analysts already work for releases; the framework extends it to architecture and assurance.

**Workshop signal to reopen.** If W2 shows that pairs cannot agree on what counts as a step, or find the chain unmaintainable, the methodology may need to admit a coarser alternative (a single "architectural declaration" instead of a chain). Reopen if multiple W2 runs show step inflation or step compression with no stable middle ground.

---

### D-03 The framework is *complementary* to the survey paper, not its outcome

**Decision.** The repository is a companion to the survey paper, with the survey as the authoritative reference for technical claims. The repository operationalises the survey's argument; it does not stand alone, and the survey does not stand alone *with the repository as its conclusion*.

**Rationale.** The survey's argument is general; the repository's framework is one possible operationalisation of it. Treating the repository as the *only* operationalisation would over-narrow the survey's contribution. Other operationalisations may emerge.

**Workshop signal to reopen.** Mostly a positioning decision. Re-examine if the framework develops to a state where the survey reads as an extended introduction to the framework rather than a standalone synthesis.

---

### D-04 No likelihood scoring

**Decision.** The framework does not score the *probability* of a privacy attack. It records whether *evidence* exists to rule out a class of attack. YAPS RED / AMBER / GREEN ratings are about evidence completeness, not attack probability.

**Rationale.** Privacy attack probability is poorly quantified across most settings. Scoring it would imply false precision. The assurance-gap model is honest about what it does and does not measure.

**Workshop signal to reopen.** If sectoral reviewers (W3) consistently demand probability estimates and refuse to use the framework without them, this position needs revisiting. Mitigation in that case: optionally allow cards to *carry* sector-specific probability estimates produced elsewhere, while not generating them inside the framework.

---

## Methodological choices

### D-10 Maturity ratings are 1–4, sector-relative, and forkable

**Decision.** Maturity stages 1 (experimental) through 4 (audit-ready) are defined once and applied uniformly across primitives, combinations, stacks, and sectors. The YAML is the canonical source; readers who disagree are expected to fork and revise.

**Rationale.** Maturity is contested. Forkability makes contention explicit rather than hiding it. The four-level rubric is coarse enough to be defensible across PETs without being so coarse it loses signal.

**Workshop signal to reopen.** If multiple W3 runs show that the same primitive sits at different stages in different sectors *and there is no useful way to express that* in the current schema, the schema may need per-sector maturity overlays.

---

### D-11 DP is split into DP-L (local) and DP-C (central) but DP is retained as a family pointer

**Decision.** In T1, `DP-L` and `DP-C` are separate primitives with distinct trust models. `DP` remains as a family pointer for backward compatibility and as a way to reference the family without committing to a variant.

**Rationale.** Local and central DP have materially different trust assumptions; treating them as one primitive obscures real choices. Retaining `DP` as a pointer lets existing references survive without churn.

**Workshop signal to reopen.** Resolved on theoretical grounds (Dwork & Roth 2014). Reopen only if a third variant (shuffle DP, federated DP) gains enough deployment evidence to warrant a third entry.

---

### D-12 Sector entries name idiosyncratic constraints (laws, regulatory expectations, institutional frameworks) explicitly

**Decision.** Each sector entry in T4 carries an `idiosyncratic_constraints` block. This was added 2026-05-24 in response to the observation that sector context drives PET choices in ways that pure technical maturity does not capture.

**Rationale.** "Healthcare" is not a single regulatory regime — HIPAA, GDPR Art. 9, NHS DSPT, and Common Law Duty of Confidentiality impose distinct constraints that map to different PET decisions. Without this block, the sector entries oversimplify.

**Workshop signal to reopen.** W3 may show that the sub-block categories (`legal_instruments` / `regulatory_expectations` / `institutional_frameworks`) are wrong; if so, the schema needs revising. Q30 in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

---

### D-13 Glossary terms are deliberately small and citable

**Decision.** [GLOSSARY.md](../GLOSSARY.md) defines a small set of terms (trust-assumption, disclosure-risk, assurance-artefact) with primary-source citations. The framework uses this vocabulary consistently; new framework-specific jargon is avoided.

**Rationale.** A long glossary is not read. A small, citable glossary becomes a shared vocabulary. Citing primary sources prevents the framework from claiming ownership of pre-existing terms.

**Workshop signal to reopen.** If W1 shows that practitioners systematically use different terms, add the practitioner terms as synonyms rather than replacing the formal terms. Reopen only if the formal terms turn out to be wrong (e.g. a new survey supersedes one of the primary sources).

---

## Engineering / structural choices

### D-20 YAML is the canonical form; Markdown is rendered from it

**Decision.** The data files (`primitives.yaml`, `pairings.yaml`, `stacks.yaml`, `sectors.yaml`, `exposure_problems.yaml`) are canonical. Markdown reference tables are intended to be regenerated from them.

**Rationale.** YAML is forkable, diffable, and machine-readable. Markdown is human-readable but loses fidelity when copy-edited. The canonical-and-rendered split is standard for documentation-as-code.

**Workshop signal to reopen.** If contributors keep editing markdown directly and the YAML drifts, the generation pipeline needs to be in place. (Currently future work; flagged.)

---

### D-21 No external dependencies for YAPS frontend

**Decision.** [yaps/frontend/index.html](../yaps/frontend/index.html) is a single file with no external dependencies. Practitioners open it locally, no install required.

**Rationale.** Adoption hinges on zero-friction trial. Anything that requires installing a toolchain raises the bar for participation.

**Workshop signal to reopen.** If W4 design directions require an interactive feature that cannot be implemented as a single file, the trade-off needs explicit consideration.

---

### D-22 Cards reference T1–T4 IDs as foreign keys

**Decision.** Every privacy card uses the IDs from T1 (`DP-C`, `FL`, etc.), T2 (`P-01`, `P-04`, etc.), T3 (`S-01`, etc.), T4 (sector IDs), and now T0 (`EP-01`, etc.) as foreign keys. This is how the card is anchored to the reference base.

**Rationale.** Cards must be auditable. Foreign-key references mean a reviewer can trace any claim back to its canonical source and check the maturity assessment, the assurance anchors, the survey citations.

**Workshop signal to reopen.** If W2 shows that cards become unreadable because of FK noise, consider whether some references can be implicit. Reopen only with clear evidence that the FK approach is harming the card's usability.

---

## Visual and design choices (provisional — pending W4)

### D-30 Cards have a traffic-light summary but the colours alone are not enough

**Decision.** YAPS returns a RED / AMBER / GREEN overall rating, but the framework treats this as a *summary*, not a sufficient artefact. The substantive content is the chain of steps, the assurance anchors, and the residual-risk declarations.

**Rationale.** Traffic lights are intuitive but coarse. Treating them as authoritative would invite compliance-shield behaviour ("we are GREEN, therefore we are safe"). The framework's discipline is to make the underlying chain inspectable, not to optimise the summary colour.

**Workshop signal to reopen.** W4 will test whether the summary-plus-detail combination communicates effectively. If not, the form of the summary may need to change (e.g. per-step ratings instead of one card-level rating).

---

### D-31 Visual / design work follows conceptual work, not the other way around

**Decision.** The framework's *concept* (W1–W3) is tested before its *form* (W4). Design directions emerge from understanding what cards need to communicate, not from a pre-existing aesthetic.

**Rationale.** Design-first risks committing to a visual language that turns out to clash with the framework's substance. Concept-first leaves design open until the substance is settled.

**Workshop signal to reopen.** This is a sequencing decision. Reopen only if running W1–W3 turns out to be impossible without a designed card to work with (in which case design becomes a prerequisite, not a follow-up).

---

## Decisions explicitly *not* yet made

These are choices the framework has consciously deferred until evidence accumulates.

- Should YAPS be reimplemented in a different language (currently Python)? No reason to change yet.
- Should the framework define new PET primitives beyond the canonical eight? Adding new primitives is high-cost; deferred until a primitive emerges with clear deployment evidence not coverable by existing entries.
- Should the framework integrate with privacy registries (NIST IR 8588's draft DP registry, OpenDP registry)? Loosely related future work; not currently a dependency.
- Should the framework produce a *compliance-mappable* output (e.g. cards as ISO/IEC 27559 evidence)? Deferred — too early to standardise an output that has not been workshopped.
