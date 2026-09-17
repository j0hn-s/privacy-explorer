# Participant Profiles

Who to invite to each workshop and why. The mix matters; running a workshop with the wrong participants will produce output that looks productive but tests the wrong thing.

---

## Cross-workshop principles

- **Six to ten participants** is the working range. Below six the discussion lacks diversity; above ten the structured sections do not work.
- **Mix roles deliberately.** Single-role rooms (all engineers, all regulators) test the framework only against one audience and produce skewed signal.
- **At least one participant should be a *plausible adopter*.** Someone who, after the workshop, could conceivably use the framework on a real deployment within the next quarter. Their reaction is the most predictive.
- **Conflict-of-interest awareness.** If a participant has a commercial stake in a particular PET vendor or product, their participation is fine but the facilitator should note it. The framework is technology-agnostic; advocacy needs to be visible.
- **Compensation and travel.** Workshop participants should be compensated for time as project budget allows, especially academics and public-sector staff for whom this is not core work. Travel and access should not be barriers.

---

## W1 — Exposure problems

**Aim of the mix.** Test whether the T0 reframing makes sense across roles. The room should include people who *do not* normally agree.

| Role | Why | Approximate number |
|---|---|---|
| Privacy engineers | They are the framework's most likely first adopters | 2 |
| Data protection officers (DPOs) | They will read cards from a governance perspective; their language is the bridge to legal | 1–2 |
| Statistical disclosure control (SDC) practitioners | They already think in "exposure problem" terms; valuable for vocabulary | 1 |
| Federated systems or distributed analytics engineers | Concrete deployments to test against | 1–2 |
| Applied cryptographer (MPC / HE / ZKP background) | Sanity-check on the cryptographic-PET entries | 1 |
| Sectoral regulator (informal capacity) | Tests whether the routing is legible to someone reading from outside | 1 |

**Avoid:** A room entirely of privacy researchers. The framework is operational, not academic. A room of researchers will critique the academic positioning without testing the operational use.

---

## W2 — Card construction

**Aim of the mix.** Test whether the stepwise-from-private method holds up in live construction. The pair forcing is the test mechanism.

| Role | Why | Approximate number |
|---|---|---|
| Pairs of one technical + one governance from the same real or composite deployment | The pair structure forces alignment; the disagreement signal is where the framework either helps or fails | 2–3 pairs |
| Regulator-side reviewer (one) | Reads cards cold at the end; provides legibility-to-outsider signal | 1 |
| Privacy engineer with cross-organisation experience | Can spot when a step has been smuggled in implicitly | 1 |

**Avoid:** Pairs from the same role (two engineers, two governance). The pair forcing depends on the cross-role tension; without it, the workshop becomes parallel solo work.

**Critical note.** W2 needs participants who are willing to bring an actual deployment, including its inelegant parts. If pairs bring only polished textbook examples, the test will be too easy and the framework will appear to work better than it does.

---

## W3 — Sector deepening

**Aim of the mix.** Test whether the sector-specific constraints are accurate and complete. Run *per sector*; do not mix sectors in one W3.

### Healthcare W3

| Role | Why | Approximate number |
|---|---|---|
| Clinical research data stewards (NHS, US academic medical centre, EU hospital network) | Operational knowledge of the constraints in practice | 2–3 |
| Health-data IG (information governance) leads | Section 251, DSPT, HIPAA equivalents — what they require day-to-day | 1–2 |
| Data scientist or ML engineer working on real clinical datasets | Where technical merit meets governance reality | 1–2 |
| Health Research Authority / IRB representative (where possible, informal) | The framework's claim that pre-existing approval regimes gate PET adoption needs this representation | 1 |
| ICO or equivalent national regulator representative (informal capacity) | Tests whether the framework's framing is legible to the regulator | 0–1 |

### Public sector / official statistics W3

| Role | Why | Approximate number |
|---|---|---|
| National statistical institute staff (ONS, US Census, ABS, equivalents) | Where DP / TRE / synthetic data actually meet political reality | 2–3 |
| TRE operators (ADR UK, Statistics Authority equivalents) | Five Safes and output-clearance pragmatics | 1–2 |
| ICO / privacy regulator | Sets the bar for what counts as acceptable | 1 |
| Academic researcher who uses TRE-mediated data | The "end user" side | 1 |

### Finance W3

| Role | Why | Approximate number |
|---|---|---|
| Bank or insurer privacy / data governance lead | The model risk regime and three-lines-of-defence in practice | 2 |
| Inter-organisational analytics platform engineer (e.g. cross-bank fraud) | Where MPC / TEE actually deploy | 1–2 |
| Regulatory / compliance lead from a financial-services context | FCA / Basel / equivalent model-governance expectations | 1 |
| Privacy engineer with payments / financial-data background | Mechanism-fit perspective | 1 |

### Technology platforms W3

| Role | Why | Approximate number |
|---|---|---|
| Platform privacy engineer (Google / Apple / Meta / open-source equivalent) | DP-L and FL at scale | 1–2 |
| Ad-tech / measurement engineer | Privacy Sandbox / IPA, the most-criticised current deployments | 1 |
| Regulator with platform competence (UK CMA, ICO, EU DMA enforcement, FTC) | Where platform claims meet scrutiny | 1 |
| Academic researcher studying platform PETs (Carlini-style, de Montjoye-style) | Adversarial-eye perspective | 1 |

---

## W4 — Design and visuals

**Aim of the mix.** Test whether non-specialists can engage with the framework when given the right form. This is the workshop where *not* having a room full of privacy specialists is the right call.

| Role | Why | Approximate number |
|---|---|---|
| Visual designer (UI, information design, editorial design) | Knows how to make something readable at a glance | 2–3 |
| Information architect | Knows how to structure complex information for cross-audience use | 1 |
| Science communicator or technical writer with no privacy background | Tests whether the framework is communicable to non-specialists at all | 1 |
| Technical practitioner (one) | Acts as domain consultant; *does not* design | 1 |
| Regulator-side reviewer | Reads final designs cold; provides the legibility signal | 1 |

**Avoid:** A room of privacy engineers attempting to design. Their privacy knowledge will make them over-confident readers of cards that are not yet legible to anyone else. The W4 test is precisely whether *non-specialists* can read the card.

**Critical note.** The technical practitioner participant is there to answer questions when the designers need to know what something means, *not* to lead. If the practitioner ends up driving the design, restart the session.

---

## Across the cycle

Over a full W1–W4 cycle, the participant pools may overlap but should not be identical. The framework benefits from:

- Some participants who attend two workshops in sequence (W1 → W2, or W2 → W3) — they bring continuity.
- Most participants attending one workshop — they bring fresh eyes.
- Almost no participants attending three or more — at that point they have become quasi-authors and lose adversarial value.

The exception is the **regulator-side reviewer**. The same person attending W1, W2, and W3 as a reviewer (not a participant) builds a longitudinal understanding that benefits both the regulator and the framework. This should be sought where the relationship allows.
