# Workshop 1 — Exposure Problems

**Tests:** Whether the [T0 exposure-problems index](../EXPOSURE_PROBLEMS.md) reflects how practitioners actually think about privacy challenges, whether the boundaries between exposure problems are crisp, whether the set is complete, and whether each entry routes cleanly to a PET response.

**Duration:** 2.5 hours.

**Participants:** 6–10. Mix of: privacy engineers, data protection officers, statistical disclosure control practitioners, federated-systems engineers, applied cryptographers, sectoral regulators. Avoid all-technical or all-policy rooms; the test of the framework is whether it works across roles.

---

## The workshop's central claim under test

> Practitioners deciding which PETs to deploy do not think *PET-first*. They think *exposure-problem-first*: "what is it about my proposed processing that creates risk to data subjects?" The T0 index is an attempt to enumerate the canonical exposure problems and route each to PET responses with inspectable assurance.

We test this by asking participants to describe their own real (or composite) cases, and observing whether the T0 vocabulary fits — or whether participants have to translate, hedge, or use different categories.

---

## Pre-reading (sent 1 week in advance)

- [EXPOSURE_PROBLEMS.md](../EXPOSURE_PROBLEMS.md) — the working index.
- [GLOSSARY.md](../GLOSSARY.md) — the formalised terms used throughout.
- README of the repository (skim).

Participants should bring: one real-or-composite case from their work where privacy considerations shaped an architectural decision. They will not be asked to share confidential details.

---

## Session structure

### 0:00 — 0:15 · Setup

- Facilitator restates the workshop's central claim under test (above) and the scope: this is testing the framework, not approving it.
- Round-the-table: each participant names their role and the *kind* of deployment they will draw on. No detail yet.

### 0:15 — 0:45 · Self-routing exercise

Each participant takes the T0 index and, for their case, attempts to:

1. Identify the **exposure problem(s)** their case is responding to.
2. Note whether the routing felt natural, partial, forced, or impossible.
3. Note whether they had to **invent a new EP** to describe their case.

Output: each participant fills a one-page card (template provided) with the routing they did. Cards are pooled.

**Prompt for participants:** "When you decided to add PET *X* to this deployment, what were you trying to stop from happening? Write that down in plain words first, then route it to an EP entry — or note that you cannot."

### 0:45 — 1:15 · Group walk-through

Facilitator picks 3–5 cards from the pool (or asks for volunteers) and walks the group through the routing. Group discussion focuses on:

- Did the routing match what the participant actually decided when they were deploying?
- If two participants routed similar cases differently, why?
- For cases that routed to multiple EPs, which was *primary*?

This surfaces both **boundary issues** (where EPs blur) and **completeness issues** (where an EP is missing).

### 1:15 — 1:25 · Break

### 1:25 — 1:55 · Adversarial test — the "make me wrong" round

Each participant takes a different participant's card. Their task: try to argue that the routing is wrong — that a different EP fits better, or that no EP fits, or that the responding PET is wrong for the EP.

This is not a hostile exercise; it surfaces the *contestability* of the framework. If two competent practitioners can route the same case to different EPs, that is information the framework needs.

Output: red-line annotations on the original cards.

### 1:55 — 2:20 · Aggregate findings

Facilitator collects:

- Cases that resisted routing (the gap surface).
- EPs that nobody used (potential redundancy).
- EPs that everyone used (potential over-generality — too broad to be useful).
- New EPs proposed during the session.
- Boundary clashes (two EPs that competed for the same case).

These are recorded directly in a workshop summary; the facilitator commits to revising [exposure_problems.yaml](../data/exposure_problems.yaml) with the deltas within two working weeks.

### 2:20 — 2:30 · Close

- Open the floor for one *unanswered question* from each participant — the one they leave the workshop wanting answered. These go into [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).
- Thanks; next workshop date / topic announced if known.

---

## What good output looks like

A productive W1 ends with:

- 6–10 worked routings, of which roughly two-thirds should route cleanly to a single EP. (Significantly less than two-thirds suggests the framework's reframing is not yet working.)
- 1–3 proposed new EPs or EP-boundary changes.
- A clear list of which EPs are heavily-used vs unused.
- Each participant able to articulate, in their own words, what an exposure problem is and why it is *not* a PET-shaped category. If they cannot, the framing is failing.

---

## What to watch for

- **Translation drag.** If most participants spend the session translating their problem into the framework's vocabulary, the framework has not landed. Watch for this and adjust.
- **PET-first relapse.** If participants keep saying "we used X" rather than "we faced Y", the question prompts need sharpening — or the reframing genuinely does not match practitioner intuition.
- **Coverage holes.** Insurance, telecoms, defence (within appropriate scope), policing data, environmental data — these sectors are likely to surface exposure problems the current index does not name. Capture these explicitly.
- **Disagreement on EP scope.** If participants from different sectors routinely route the *same* type of case to different EPs, that is a signal that the EP scopes need redrawing, not that practitioners are confused.

---

## Materials

- T0 index (one printed page per participant): summary table from [EXPOSURE_PROBLEMS.md](../EXPOSURE_PROBLEMS.md).
- Card template (one per participant): pre-printed with the fields *case description (short, anonymised) · trying to stop · routed to EP · confidence in routing · notes*.
- Glossary excerpts: trust-assumption terms + disclosure-risk terms from [GLOSSARY.md](../GLOSSARY.md).
- Wall space or whiteboard for the pooled cards.
- Post-it notes for the adversarial round.

---

## Specific questions to surface during W1

Each of these maps to an entry in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md). The facilitator should ensure each gets some discussion time.

1. Is "exposure problem" the right name, or does a different term land better with practitioners?
2. Should EPs be sector-tagged, or kept sector-agnostic?
3. Are participants comfortable with the disclosure-type vocabulary in the glossary (identity / attribute / membership / linkage / reconstruction / composition leakage), or do they use different terms?
4. Where the framework conflicts with familiar terms-of-art ("anonymisation", "de-identification"), how should we handle this in cards?
5. Should the workshop output (worked routings) be published as part of the framework, or kept as background material for facilitator use?
