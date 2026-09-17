# Workshop 4 — Design and Visual Representation

**Tests:** Whether a privacy card can be made *appealing and usable* — explicitly as a creative design problem, not a software-engineering problem. This is a different kind of workshop from W1–W3: a hands-on design session with a more creative, less specialist audience.

**Duration:** 3.5 hours (longer; hands-on).

**Participants:** 6–10. Mix of: visual designers, information architects, science communicators, one or two technical practitioners (acting as domain consultants, not card authors), one regulator-side participant (acting as reviewer of the resulting designs, not a designer themselves).

This workshop deliberately *does not* prioritise privacy-engineering specialists. The framework's adoption depends on usability for people who are not privacy specialists; the design work needs perspectives from outside the field.

---

## The workshop's central claim under test

> A privacy card is a structured document, but its *carrier form* — how it is laid out, what it looks like, what is visible at a glance — materially affects whether anyone uses it. The current text-and-JSON form is functional but not engaging. A workshop with creative practitioners can surface design directions that engineering-led work would miss.

The output of W4 is **directions, not deliverables**. We are not trying to ship a designed card from a workshop. We are trying to surface design constraints, hypotheses, and visual hooks that can inform later engineering work.

---

## Pre-reading

- One example privacy card from [yaps/cards/examples/](../yaps/cards/examples/) — printed in plain text and as JSON.
- A one-page summary of *what a card is for*: (a) the author's documentation of an architectural commitment, (b) a reviewer's reading aid, (c) a maintenance artefact.
- *Not* the full glossary or the methodology documents. The point of the workshop is to test whether the framework can be communicated *without* requiring participants to absorb that material first.

Participants do *not* need to bring a deployment. The facilitator provides 2–3 worked deployments as material to design against.

---

## Session structure

### 0:00 — 0:20 · Setup

- Facilitator introduces the central claim under test.
- Walk through the printed example card cold. Ask: what does this seem to be? Who do you think it is for? What is it saying?
- These first reactions are recorded as the design baseline — what the current form communicates *without* explanation.

### 0:20 — 0:40 · Brief and constraints

The facilitator briefs the group on what a card must accomplish, kept deliberately spare:

- It records an architectural commitment to a particular combination of privacy techniques in a particular context.
- It must be inspectable by someone who is not the author.
- It must be updateable when the architecture changes.
- It must support a traffic-light summary (red / amber / green) but the colours alone are not enough.

Constraints — these are the framework's commitments and cannot be designed away:

- Five layers (data, PETs, assurance, governance, regulatory) are present.
- Each PET in use has a named primitive ID, role, parameters, and an assurance artefact.
- The card has a stepwise chain (W2 output) describing how the architecture deviates from a completely-private baseline.
- The card has a residual-risk statement.

Anything beyond these constraints is fair game for redesign.

### 0:40 — 1:40 · First design sprint — solo

Each participant works alone for 60 minutes. The brief: produce a design for the card — any medium (paper, whiteboard, digital). The audience is named explicitly: *a regulator who has 15 minutes to read it before a meeting and is not a privacy specialist*.

Materials provided:

- A4 / A3 paper, pens, sticky notes.
- A laptop with simple drawing tools (Figma, Excalidraw, Miro — facilitator's choice) for digital-leaning participants.
- The example card content (the same one, in plain text — so participants are designing the *form*, not inventing content).

### 1:40 — 1:55 · Break

### 1:55 — 2:25 · Show-and-tell

Each participant presents their design in 3 minutes. No critique yet; just description.

Facilitator captures recurring patterns: which design choices appear across multiple participants? Where do they diverge?

### 2:25 — 3:00 · Second design sprint — pairs

Participants pair up (mixing creative-leaning with technical-leaning). Each pair takes one of:

- A design from the first sprint and *combines* it with another.
- A specific design challenge the group identified (e.g. "how do you show the stepwise chain visually?", "how do you handle multi-layer trust assumptions without making the card look like a legal document?").

Output: a second-iteration design per pair.

### 3:00 — 3:25 · Adversarial reading

The regulator-side participant takes each design in turn and reads it cold, narrating aloud what they think it says. The pair listens — they do not explain.

This is the most important moment of the workshop. Where the reading diverges from the design's intent, the design is failing. Where the reading aligns, the design is working.

### 3:25 — 3:30 · Close

- One design hypothesis to take forward, from each participant. Goes into [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) under a *visual design* section.
- Thanks; explicit commitment that the workshop's designs are not specifications — they are inputs into later engineering.

---

## Specific design questions to provoke

These are seeded into the workshop facilitator's prompts as needed:

1. **Stepwise chain visualisation.** How do you show the chain of deviations from a completely-private baseline? A flowchart? A timeline? A nested hierarchy? A series of "before / after" panels?
2. **PET stack visualisation.** When multiple PETs are stacked (FL + TEE + DP), what visual metaphor communicates the layering? Bricks? Concentric circles? Three columns?
3. **Trust-assumption visibility.** Trust assumptions are easy to bury. Can a visual treatment force them into prominence?
4. **Maintenance state.** Can a card communicate "this is current" vs "this is stale" at a glance? What about "this has a finding that needs attention"?
5. **Audience adaptation.** Should a single card render differently for an engineering audience, a governance audience, and a regulatory audience? Or should it be one form that all three can read?
6. **The traffic light.** Red / amber / green is intuitive but coarse. What complements it without losing the at-a-glance property?
7. **Spatial vs sequential.** Is a card best read as a single page (spatial) or as a sequence of pages (each layer)? What are the trade-offs?

---

## What good output looks like

A productive W4 ends with:

- 6–10 first-pass designs and 3–5 second-iteration designs.
- A set of named **design hypotheses** — things that some participants tried and that seemed to work. Examples: "the stepwise chain reads better as a vertical timeline than a horizontal flowchart"; "trust assumptions belong adjacent to PETs, not in a separate section"; "the traffic light should annotate each step, not just the whole card".
- 1–3 design directions worth prototyping seriously after the workshop.
- The adversarial-reading transcript — the most valuable artefact for understanding what currently fails to communicate.

We do not expect a finished design. We expect the *inputs* to a finished design.

---

## What to watch for

- **Specialist relapse.** Technical participants may slide into discussing the *content* (what should be in the card) rather than the *form* (how it should be communicated). Redirect.
- **Beautification as design.** A pretty card is not a good card if it fails the adversarial reading. The session has to keep returning to the question: did the reader understand it?
- **The "obvious" answer.** A flowchart-style stepwise chain is obvious. Push for the second answer, the third answer. Workshop is about expanding the design space.
- **Compliance look-and-feel.** Many existing privacy artefacts (DPIA templates, compliance dashboards) have a recognisable look that participants may default to. Name this default and ask: what would the *non-default* form look like?

---

## Materials

- Plenty of paper (A3 minimum). Card stock for participants who want to make physical artefacts.
- Pens, markers, highlighters, sticky notes.
- A laptop with at least one tool for digital design (Figma is the default).
- The chosen example card in *plain text*, no styling — so participants are designing the form, not inheriting an existing one.
- One large surface (whiteboard or floor) for show-and-tell.

---

## Specific questions to surface during W4

1. Is the card best understood as a *document*, a *dashboard*, a *story*, or something else? Each metaphor implies different visual language.
2. What is the relationship between the card and *other* visual artefacts in the privacy ecosystem (DPIAs, model cards, datasheets for datasets, system cards)?
3. Could a card have a *short* form (single-page summary) and a *long* form (full record), and would the short form be the canonical artefact?
4. How does the card carry change over time? If it is updated, do reviewers see the diff, or only the current state?
5. What is the minimum visual element needed to make the card recognisable as a card across the framework? (A small logo? A standard header? A specific layout convention?)

---

## After W4: prototyping pathway

The workshop produces directions; engineering produces prototypes. The likely next steps after a productive W4:

1. Pick the 2–3 strongest design directions.
2. Develop one as a paper / static prototype that can be tested in [W2 follow-up sessions](W2-card-construction.md) (does using the visual form change how teams construct cards?).
3. Develop a digital prototype (Figma or similar) that can be tested with a regulator-side reviewer for a substantive read-cold session.
4. Only after both succeed: invest in implementing the design in the YAPS frontend.

The implication: visual design is on the framework's roadmap, but only after the conceptual workshops (W1–W3) and the first W4 have surfaced what to design *for*. This is not a software-engineering-first activity.
