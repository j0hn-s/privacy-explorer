# YAPS Risk Model

This document explains how the YAPS risk engine works, why it is designed the way it is, and how it relates to existing risk assessment frameworks. It is intended to be read by practitioners who want to understand the rule logic, researchers who want to contest or extend the model, and organisations considering adopting it.

---

## Privacy risk is not the same as security risk

Most established risk frameworks — the NCSC Cyber Assessment Framework, NIST SP 800-30, ISO/IEC 27005 — are built around the **CIA triad**: confidentiality, integrity, and availability. The fundamental question they ask is: *what is the likelihood and impact of a threat actor exploiting a vulnerability in a system?*

Privacy risk is different in two important ways.

**First, the harm is different.** Security risk is primarily about organisational harm — data breach costs, operational disruption, reputational damage. Privacy risk is primarily about **individual harm**: loss of autonomy, discriminatory exposure, chilling effects on behaviour, re-identification leading to real-world consequences. The "asset" at stake is not primarily the organisation's; it belongs to data subjects who may have had no choice in the matter.

**Second, the evidence problem is different.** Security risk can often be quantified: breach rates are tracked, vulnerability exploit databases exist, actuarial models apply. Privacy risk from PET deployment is harder to quantify because the harm is often diffuse, future-facing, and depends on auxiliary data an attacker may hold. The question is not "how likely is an attack?" but "how credible is the privacy claim, and what evidence exists to support it?"

YAPS is designed for this second type of question. It does not try to quantify likelihood × impact. Instead, it asks: **given the architecture recorded in this card, which assurance claims are unsubstantiated, which governance controls are absent, and which regulatory expectations are unmet?** This is an **assurance-gap model** rather than a threat-probability model.

> **Construction methodology.** YAPS evaluates cards constructed using the [stepwise-from-private methodology](../STEPWISE_RISK.md): each PET-enabled access pattern is recorded as a deviation from a completely-private baseline. The rule categories below map onto the elements of each stepwise deviation — IFACE rules check trust assumptions added, COMP rules check the interactions between deviations, ASSUR rules check that named assurance anchors exist, GOV/SECTOR/REG rules check the broader procedural and regulatory layer.

---

## The assurance-gap model

The core idea is simple: a privacy claim becomes credible when it can be rendered into repeatable, inspectable artefacts. A claim without artefacts is a statement of intent, not evidence. YAPS rules encode the artefact requirements that follow from specific architectural choices and surface the gaps.

This framing is grounded in the survey paper's central argument and parallels the approach taken in:

- **NIST SP 800-226 (Draft)** — which defines evaluation criteria for differential privacy claims and explicitly requires parameter manifests, composition accounting, and sensitivity analysis as the basis for any DP assurance claim. Our COMP-001, ASSUR-003, and REG-001 rules operationalise this requirement.
- **The Five Safes framework** (ONS/ADR UK) — which treats governance artefacts (safe outputs, access logs, clearance records) as first-class assurance mechanisms on equal footing with technical controls. Our GOV-001 and GOV-002 rules reflect this.
- **The ICO Anonymisation Code of Practice (2022)** — which requires that any anonymisation or de-identification claim be supported by a documented risk assessment and testing methodology. Our IFACE-003 and ASSUR-002 rules encode this requirement for synthetic data deployments.

The model does not claim equivalence with these frameworks. It draws on their logic selectively, for the specific context of PET deployment assurance.

---

## Relationship to NIST Privacy Framework

The NIST Privacy Framework (2020) organises privacy risk management into five core functions: **IDENTIFY, GOVERN, CONTROL, COMMUNICATE, PROTECT**. The YAPS rule categories map loosely onto these functions:

| NIST PF function | YAPS rule categories | What this means in practice |
|-----------------|---------------------|----------------------------|
| IDENTIFY | IFACE, COMP | Surface what crosses boundaries and where interaction effects arise |
| GOVERN | GOV | Audit logs, output controls, DPIA references, framework alignment |
| CONTROL | ASSUR | Required artefacts exist and are documented |
| COMMUNICATE | REG | Regulatory alignment is declared and gaps are surfaced |
| PROTECT | IFACE, COMP, SECTOR | Technical controls address the stated threat surface |

YAPS does not implement the NIST PF as a compliance checklist — it uses the same conceptual structure to organise rules about PET-specific failure modes.

---

## Relationship to NCSC Cyber Assessment Framework

The NCSC CAF (Cyber Assessment Framework) uses a tiered maturity model (A–D for each objective) and structured indicator questions to assess whether an organisation achieves specific security outcomes. Its primary audience is UK CNI operators.

YAPS shares the CAF's **outcome-oriented** structure — rules ask "does this artefact exist?" rather than "does this process have documentation?" — and its use of a small number of severity tiers (RED/AMBER/GREEN parallels CAF's "not achieved / partially achieved / achieved").

The key divergences:

1. **Scope.** CAF covers the full security picture for an organisation. YAPS covers only the privacy-assurance posture of a specific PET deployment. They are complementary, not competing.
2. **Threat model.** CAF is built around adversarial attack vectors against systems. YAPS is built around assurance gaps in privacy claims — the "attacker" may be a curious coordinator, a privacy auditor, or a future regulator, not a malicious external actor.
3. **Artefact focus.** CAF objectives are process-oriented (policies, training, patching). YAPS objectives are evidence-oriented: not "do you have a DP policy?" but "does a privacy accountant documenting composition across releases exist?"
4. **No likelihood scoring.** YAPS does not assign probability estimates to findings. RED means a gap that blocks credible assurance, not a gap with high exploit probability.

---

## Rule categories — narrative description

### IFACE — Interface Risks

Interface rules fire when something crosses a component boundary in a way that the architecture does not adequately protect. The intuition is that combining PETs creates new exposure surfaces at the interfaces between them — surfaces that are not covered by the individual primitives' assurance claims.

**IFACE-001 (FL without DP or MPC)** encodes a well-documented attack surface: federated learning distributes computation but model updates carry information about training data. Gradient inversion attacks (Zhu et al. 2019) and update-leakage attacks (Melis et al. 2019) show that a curious coordinator can reconstruct individual records from per-client updates. Without DP noise or MPC secure aggregation at the aggregation step, the coordinator has unmediated access to this information. This is an AMBER finding rather than RED because FL alone is still better than centralised data pooling — the gap is in not closing the coordinator-visibility attack surface.

**IFACE-002 (TEE without formal output bound)** addresses a common misconception: hardware isolation protects data *in use* but does not constrain what information is disclosed in *outputs*. An attacker who receives model outputs or query results can still perform membership inference or reconstruction attacks regardless of whether those outputs were computed inside an enclave. DP or ZKP at the release boundary is required to close this gap.

**IFACE-003 (SYN without DP)** is RED because synthetic data without a formal privacy coupling has a documented, specific failure mode — not just a theoretical gap. Stadler et al. (2022) and Houssiau et al. (2022) demonstrate that a significant proportion of synthetic data releases are re-identifiable under realistic attack models. Without DP or a completed adversarial audit (e.g. TAPAS), any privacy claim for a synthetic release is unsubstantiated. This mirrors the ICO's position that "anonymisation" claims require active testing, not just intent.

**IFACE-004 and IFACE-005** (MPC adversary model, ZKP trusted setup) encode specific documentation requirements that practitioners often omit. MPC security properties are adversary-model-dependent in a way that is non-obvious to non-specialists; ZKP trusted-setup failure is a well-known attack vector in zkSNARK deployments.

### COMP — Composition Risks

Composition rules fire when the interaction *between* PETs in a stack creates risks that are not present in either primitive alone. These are the hardest risks for practitioners to see, because each primitive looks fine in isolation.

**COMP-001 (DP composition accounting)** is RED because this is the most common and consequential mistake in DP deployments. Applying ε=1.0 per query sounds reasonable until you realise that 1000 queries compounds to ε=1000 under naive composition — at which point the privacy guarantee is essentially void. Advanced composition theorems (Kairouz et al. 2015), Rényi DP accounting, and PRV accounting exist precisely to manage this, but they only work if someone is running them. NIST SP 800-226 makes composition accounting a core evaluation requirement; this rule operationalises that requirement.

**COMP-002 (FL + DP without MPC)** is a subtler version of IFACE-001. When DP is applied to FL without secure aggregation, the coordinator sees individual DP-noised updates before summing them. This is a weaker protection than it appears: DP was designed for a trusted-curator setting where the curator sees the aggregate. If the coordinator is untrusted, seeing individual noised updates still leaks information — less than seeing raw updates, but more than seeing only the sum. The S-03 stack (FL + MPC + DP) closes this gap by ensuring the coordinator sees only a cryptographically aggregated sum before DP noise is applied.

**COMP-003 (TEE + DP dual trust anchors)** and **COMP-004 (three-layer composability)** encode documentation requirements for complex stacks. When two or more trust mechanisms are combined, the combined assurance claim is only as strong as its weakest declared element. If the threat models are not explicitly aligned, an auditor cannot tell whether the stack actually covers the full threat surface or just papers over it with multiple mechanisms.

### ASSUR — Assurance Artefact Completeness

Assurance rules are the most direct operationalisation of the survey paper's core argument: the artefact is the evidence. These rules fire when a PET primitive is present but its primary assurance artefact is absent or planned-only.

**ASSUR-001 (TEE attestation)** is RED because attestation is *the* mechanism by which a TEE's hardware isolation claim is verifiable. Without an attestation report, a deployment may be using a genuine TEE correctly — but it cannot demonstrate this to any external party. The privacy claim is present only as an assertion.

**ASSUR-002 (SYN disclosure risk evaluation)** is RED for the same reason as IFACE-003: the ICO and OECD are explicit that anonymisation claims require testing, not just assertion. A disclosure-risk evaluation is not a nice-to-have — it is the mechanism by which any re-identification risk claim becomes auditable.

**ASSUR-003 (DP parameter manifest)** is RED because a DP deployment without documented epsilon, delta, noise mechanism, and sensitivity values is not reproducible or auditable. Anyone reviewing the deployment cannot verify whether the parameters are appropriate for the stated use case, whether composition has been accounted for, or whether the claimed guarantee is valid.

**ASSUR-004 and ASSUR-005** (MPC audit, ZKP circuit audit) are AMBER because implementation errors in these primitives are known to be consequential and common — but the finding is AMBER rather than RED because pilot deployments may reasonably defer formal auditing until pre-production.

### GOV — Governance Controls

Governance rules encode the procedural and institutional controls that are necessary for a privacy claim to be credible in a non-technical context. Technical artefacts are necessary but not sufficient; governance artefacts cover the human accountability layer.

**GOV-001 (audit log)** is AMBER because an audit log is a minimum accountability requirement for any personal data processing system. Without it, there is no record of who accessed what, when, and what outputs were released — making the deployment unauditable in a forensic sense.

**GOV-002 (TRE output control)** is RED because output checking is the defining assurance mechanism of a TRE — it is what makes TREs different from ordinary data access systems. A TRE without output checking is not a TRE in any meaningful sense; it is just restricted access. The Five Safes framework treats "safe outputs" as a non-negotiable safeguard, not an optional supplement.

**GOV-003 (DPIA)** is AMBER — a documentation reminder rather than a blocking finding, because the DPIA process is managed outside the technical architecture. The rule fires when GDPR applies and no DPIA reference is recorded, prompting the practitioner to link the technical card to the corresponding legal documentation.

**GOV-004 (governance framework)** is GREEN — a best-practice prompt rather than a gap finding. Aligning to a named framework (Five Safes, NIST PF, ISO/IEC 27701) makes the governance claim legible to external reviewers and procurement processes.

### SECTOR — Sector-Specific Requirements

Sector rules fire when a deployment context implies requirements beyond the generic assurance baseline. These rules encode the domain knowledge from T4 of the explorer tables.

**SECTOR-001 (healthcare)** reflects the known friction in healthcare federated deployments: the gap between producing technically correct privacy artefacts and getting clinical sign-off is a documented bottleneck (Soltan et al. 2024, OpenSAFELY experience). Clinical utility evidence (AUROC, task-specific benchmarks) is required because a model with strong privacy properties but poor clinical utility is not deployable regardless of its assurance posture.

**SECTOR-002 (public sector)** and **SECTOR-003 (technology/platform scale)** encode the sector-specific dominant failure modes from T4: public sector deployments without TRE governance have historically struggled with accountability; platform-scale DP deployments without composition accounting produce epsilon values that become meaningless.

### REG — Regulatory Alignment

Regulatory rules are informational prompts, not blocking findings. They fire when a deployment has specific regulatory applicability (GDPR, UK GDPR, HIPAA) and the card does not document alignment with the relevant technical guidance standard. They are GREEN or INFO severity because the alignment is the practitioner's responsibility — YAPS can only surface the pointer.

**REG-001 (NIST SP 800-226)** fires for any DP deployment because SP 800-226 is the primary international reference for DP evaluation criteria. Documenting alignment — even as "partial" or "aspirational" — means the practitioner has engaged with the standard.

**REG-002 (ICO PETs guidance)** fires for UK GDPR deployments because the ICO guidance sets the UK regulatory expectation for PET deployment. Non-engagement with it is a discoverable gap in any ICO investigation or procurement review.

**REG-003 (GDPR Art. 25)** is purely informational: it notes that the Privacy Card itself is a candidate Art. 25 documentation artefact, which may be useful for practitioners building compliance documentation.

---

## Traffic light semantics

| Rating | Meaning | Typical implications |
|--------|---------|---------------------|
| 🔴 RED | A specific assurance claim is unsubstantiated or a required artefact is absent. The deployment cannot credibly support the stated privacy claim without resolving this finding. | Block deployment readiness; resolve before production |
| 🟡 AMBER | A notable gap exists that does not fully invalidate the privacy claim but materially weakens it. May be acceptable in a pilot with documented accepted-risk, but should be resolved before production. | Document accepted risk; set resolution timeline |
| 🟢 GREEN | A best-practice recommendation or alignment prompt. No critical gap; the deployment can proceed but would be strengthened by addressing the finding. | Address when resources allow |
| ℹ️ INFO | Contextual note. No action required; the finding is a pointer or reminder that does not affect the overall rating. | Review; take no action |

The overall rating is the worst single finding across all evaluated rules. One RED finding produces a RED report regardless of all other findings. This is intentional: in an assurance-gap model, one unsubstantiated critical claim undermines the credibility of the whole architecture.

---

## Using YAPS alongside empirical privacy-attack simulation

YAPS is an assurance-gap model. It asks whether the **evidence** required to substantiate a privacy claim exists, not how a system performs under attack. This makes YAPS complementary to, not a substitute for, empirical privacy-attack simulation — running named attacks (membership inference, reconstruction, singling-out, linkage) against a deployment and measuring what they recover.

In practice, the two views answer different questions about the same architecture, and the strongest privacy posture pairs them. A YAPS card describes what the deployment *claims* and what evidence backs the claim; an empirical evaluation tests whether the claim holds under a stated adversary. A worked example pairing the two — the `privacy-eval` evaluation of the Solid-based OXFORDIA federated-compute library, with worst-record MIA sweep, Dinur–Nissim reconstruction, and Kaplan–Meier singling-out audits — illustrates the pattern: empirical findings feed back into the card's residual-risk declarations, and YAPS findings flag where the empirical layer is needed.

### What metrics earn their place in the empirical layer

The metrics that proved useful in that evaluation generalise to any stack of similar shape:

- **Membership-inference attack AUC** as a population-average summary, paired with **TPR at fixed low FPR** (typically 0.01 or 0.001) to expose the worst-record tail that average AUC hides. Carlini et al. (2022) and Watson et al. (2022) argue this pairing is non-optional: a deployment with AUC ≈ 0.5 can still permit MIA on outlier records at 25–40× the chance baseline. Per-record vulnerability sweeps make this visible.
- **Reconstructed-fraction at staged query budgets** (Q = 100, 1000, 10 000) for any aggregation API. The phase transition at Q ≈ N is a textbook Dinur–Nissim signature; the metric exposes whether the deployment is one query budget away from full reconstruction.
- **Singled-out count and minimum risk-set size** for any time-to-event or per-record release. These are the operational form of the Article 29 WP / NIST SP 800-188 singling-out criterion; if either is non-trivial, no aggregation has occurred where aggregation was the claim.
- **Mean / median / p95 / p99 absolute reconstruction error** alongside the headline reconstruction fraction, because a "0% reconstructed within tolerance" headline can mask values reconstructed to within a meaningful margin.

A useful evaluation reports each metric *both* averaged and at the tail — the average-case story rarely tells the full story, and a benchmark that hides outliers will produce a card that overstates its own assurance.

### What to benchmark against

The benchmark surfaces depend on what the card is claiming:

1. **The deployment's own claimed assurance.** If the card declares DP-C with ε = 4, the empirical MIA AUC for the worst record should be compatible with that ε under the relevant composition theorem. A measured MIA materially exceeding the theoretical bound signals either a parameterisation error, a composition-accounting error, or an unrecognised leakage channel.
2. **A mechanism baseline from the literature.** Synthetic-data fidelity attacks compare against TAPAS or the NIST DP-Synthetic Challenge methodology; MIA compares against shadow-model AUC under Shokri (2017) and Carlini (2022); reconstruction compares against Dinur–Nissim's theoretical query-count threshold.
3. **A non-private control.** What does the same evaluation produce on the deployment with the PET layer removed? This bounds the PET's contribution to the overall posture and surfaces over-claiming when the PET adds little.
4. **A standards crosswalk.** NIST SP 800-188 names three disclosure types (identity, attribute, membership); Article 29 WP 05/2014 names three re-identification criteria (singling-out, linkability, inference). The evaluation should exercise all three failure modes; if it tests only one, the card's claim that all three are addressed is unsupported.

The OXFORDIA evaluation took this seriously after an early critique that average-case MIA undersells worst-record risk and that the bridge layer (the Python emulator) might not faithfully reproduce the actual plugin. Both critiques were addressed in a second pass — per-record sweep, cross-validation against the actual TypeScript plugin via a Node CLI wrapper — and the result was a stronger card. The lesson generalises: a YAPS card and an empirical evaluation should be revisable in light of each other.

### How the approach differs across PET stacks, sectors, and data-use intents

The same metrics rarely matter equally across deployments. Differences worth surfacing on the card:

**Per PET stack.**
- `FL + DP-C` (P-01) — MIA on the released model is the headline; per-record sweep is the priority refinement; reconstruction is less direct.
- `FL + MPC + DP-C` (S-03) — coordinator-blindness should be tested separately from output disclosure: the empirical test for the MPC layer is correctness + non-leakage of intermediate state, distinct from the DP layer's MIA bound.
- `TRE + DP-C` (P-07) — output-clearance logs are the canonical artefact; the empirical work is singling-out audits of the cleared outputs over time, not attacks on a model.
- `SYN + DP-C` (P-08) — TAPAS-style attacks on the synthetic release are the canonical empirical layer; the evaluation needs to also report utility vs. real-data baseline because a "perfectly private" synthetic dataset that has lost utility is not deployment-grade.
- TEE-anchored stacks — empirical attacks on the API output channel must be distinguished from attacks on the enclave itself; the latter is usually out of scope for an application-level evaluation and is instead the vendor's responsibility, but the card should declare which side of the boundary is being tested.
- ZKP-bearing stacks (P-06) — empirical work is closer to circuit auditing than statistical attack; the metrics are under-constraint analysis and benchmark reproducibility, not AUC.

**Per sector.**
- *Healthcare* — small subgroups bite hardest; the worst-record sweep is essential; clinical validity (AUROC, sensitivity / specificity) is benchmarked alongside privacy, because a card that records a strong privacy claim with no utility evidence is not deployable. The `idiosyncratic_constraints` block for healthcare in `data/sectors.yaml` lists what the sector expects.
- *Public sector / official statistics* — composition leakage across a long programme of releases is the dominant concern; the relevant metric is *cumulative* privacy loss tracked by an accountant, not single-release AUC. Empirical work focuses on differencing attacks against published table patterns.
- *Finance* — adversarial reconstruction is the most credible threat in cross-bank fraud or risk-pooling contexts; the metric is reconstructed fraction at production query budgets; the assurance audience is model-risk governance, so reproducibility and explainability constraints often rule out stochastic mechanisms whose outputs cannot be re-derived.
- *Technology platforms* — per-user, per-time-window budget accounting for DP-L is the metric, and the empirical work is *longitudinal* (does the budget hold over months of telemetry?) rather than one-shot.
- *Web3 / verifiable infrastructure* — circuit correctness and prover-cost reproducibility are the empirical metrics; classical re-identification attacks rarely apply.

**Per data type and data-use intent.**
- *Tabular records with rich quasi-identifiers* — singling-out and linkage are the relevant attacks; auxiliary-data tests should be part of the evaluation.
- *Time-to-event data* — per-step Kaplan-Meier disclosure (singling-out at the curve) is a specific failure mode; the relevant metrics are singled-out count and minimum risk-set size, not AUC.
- *Free text* — re-identification via ML methods (Manzanares-Salor et al. 2024) is the relevant attack; the empirical layer needs ML adversaries, not statistical ones.
- *Genomic data* — linkage to public genomic resources and Homer-style allele-frequency attacks are sector-specific failure modes; the framework's general primitives are insufficient on their own, and a domain-specific audit is typically required.
- *Use intent: research vs. statistical release vs. production decision-making* — the threshold of actionability differs sharply. A research-grade card may accept residual risk that a production-decision card must not, because the harm calculus is different. The card should declare the use intent explicitly; the empirical evaluation should be calibrated against it.

Across these variants, the YAPS finding is unchanged in structure: *which assurance anchors are required for the card's claim, and which are missing*. What changes is the empirical evidence that supports each anchor — the metrics, the benchmarks, the adversary model. The two layers are most useful when they iterate against each other: empirical attacks reveal which claims actually hold under pressure, and the card revises to declare the residual that the empirical layer surfaced.

### Reporting DP claims operationally: μ-DP, conversion regret, and the trade-off curve

A separate observation, also pushed by the empirical evaluation, is that **single-ε reporting is not enough on the card side either**. Desfontaines (2023, *Reporting privacy guarantees in machine learning*) argues that two DP deployments with the same ε can have materially different privacy properties at the attack operating point that actually matters, because (ε, δ) is a piecewise-linear boundary on the underlying trade-off curve and a single number hides the curve's shape. The card-level analogue of the per-record vulnerability sweep is therefore: **report the curve, not just the point**.

Schema 1.2 introduces an optional `risk_calibration` block on the card to carry this reporting. The block accepts a μ-DP single-parameter summary (Gaussian-DP per Dong, Roth & Su 2022), an `attack_target` declaring which attack the claim is targeting and at what advantage / FPR / FNR, a `conversion_regret` value bounding how lossy the μ-DP summary is at the operating point of interest, and a `trade_off_curve_ref` pointing to FPR-vs-FNR data when the regret is non-negligible. The `gdpnum` library (interpretable-dp.org) does the (ε, δ) → μ-DP conversion and produces the curve; `riskcal` (same group) calibrates noise to a target attack rate and so closes the empirical ↔ assurance loop in the other direction. The two libraries split naturally: `gdpnum` is a card-reporting helper, `riskcal` is an attack-simulation helper, and the same μ-DP value flows between them.

The corresponding rule category is **RISKCAL-*** (rules.yaml). RISKCAL-001 (GREEN, best-practice first iteration) fires when any DP variant is declared but no `risk_calibration` block exists; RISKCAL-002 (AMBER) fires when μ-DP is reported without the regret bound; RISKCAL-003 (INFO) fires when DP-coupled synthetic data lacks a trade-off curve. The severities are deliberately light for the first iteration — the framework's intent is to nudge cards toward operationally legible reporting without breaking existing GREEN cards. Workshop feedback may justify escalating RISKCAL-001 to AMBER in a later revision.

---

## What this model does not do

- **Quantify re-identification probability.** The model cannot tell you how likely a specific attack is. It tells you whether the evidence exists to rule it out.
- **Provide legal advice.** Regulatory alignment findings are pointers to standards, not legal opinions. Consult your data protection officer and legal counsel for compliance determinations.
- **Replace domain expertise.** Clinical validity, financial regulatory compliance, and sector-specific deployment knowledge are outside scope. The SECTOR rules prompt for these; they do not evaluate them.
- **Model auxiliary data risk dynamically.** The current rule set cannot evaluate linkage risk from external datasets — this requires per-dataset analysis. The data profile schema has a reserved `auxiliary_data_risk` field for future tooling.
- **Evaluate tool implementations.** Rules check for documented artefacts, not whether a specific tool is implemented correctly. Implementation correctness requires code audit, not card review.

---

## Related artefacts in the repository

The risk model interacts with several other parts of the framework. Readers may find these directly useful:

- [GLOSSARY.md](../GLOSSARY.md) — the formalised trust-assumption, disclosure-risk, and assurance-artefact terms used by every rule.
- [EXPOSURE_PROBLEMS.md](../EXPOSURE_PROBLEMS.md) — the T0 problem-first index. Cards may declare which `EP-` entries each step is responding to; rules can in turn check whether the named response is evidenced.
- [STEPWISE_RISK.md](../STEPWISE_RISK.md) — the card construction methodology. Rule findings map onto specific positions in the stepwise chain.
- [data/sectors.yaml](../data/sectors.yaml) — sector entries now carry an `idiosyncratic_constraints` block (laws, regulatory expectations, institutional frameworks). SECTOR rules consult these when evaluating sector-specific gaps.
- [workshops/](../workshops/) — the framework's open questions (including those about this risk model) are tracked in [workshops/OPEN_QUESTIONS.md](../workshops/OPEN_QUESTIONS.md).
