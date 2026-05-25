# Glossary of Terms

A short, deliberately constrained set of definitions used consistently across the privacy-explorer tables, YAPS, and the workshop materials. The aim is to make it easier to compare entries: when a primitive in [T1](README.md) says it depends on "attestation" or "an untrusted curator", these terms always mean the same thing.

> **Methodological basis.** Where possible, definitions are drawn from canonical primary sources — Dwork & Roth (2014) for differential privacy; the Article 29 Working Party Opinion 05/2014 (re-identification criteria); NIST SP 800-188 (de-identification disclosure types); Costan & Devadas (2016) for trusted execution environment semantics; Evans, Kolesnikov & Rosulek (2018) for secure multi-party computation. Where terms are still contested in the literature (e.g. what counts as "production-ready"), we say so explicitly and pick the most common reading. The choice to keep the set small is deliberate: a long glossary is rarely consulted; a short one can become a shared vocabulary.

---

## 1. Trust assumption terms

These terms describe **who is trusted to do what** in a deployment. Every PET primitive in [T1](README.md) declares a trust model using this vocabulary.

| Term | Definition | Primary source |
|---|---|---|
| **Trusted curator** | A single party that sees raw inputs from data subjects, performs computation, and releases an output. Privacy guarantees apply to the output. Examples: ONS for census aggregates; an Apple aggregation server in a non-local-DP path. | Dwork & Roth (2014) §2.1 |
| **Untrusted curator** | The party that aggregates or releases data is not trusted with raw inputs. Privacy guarantees must hold against this party — typical of local-DP and MPC-based settings. | Dwork & Roth (2014) §2.1; Evans et al. (2018) |
| **Honest-but-curious adversary** | A party follows the protocol but tries to infer additional information from the messages it receives. The standard semi-honest model for SMPC and FL coordinators. | Goldreich (2004) *Foundations of Cryptography II* §7.2 |
| **Malicious adversary** | A party may deviate arbitrarily from the protocol. Stronger model than honest-but-curious; protocols proven secure here remain secure against active attackers. | Goldreich (2004) §7.4 |
| **Threshold (k-of-n) trust** | Privacy holds provided fewer than `k` of the `n` parties are corrupted. Standard for threshold MPC. The specific (k, n) is a parameter of the deployment. | Cramer, Damgård & Nielsen (2015) *Secure Multiparty Computation* |
| **Hardware-anchored trust** | Trust is rooted in a hardware vendor's attested manufacturing process (e.g. Intel SGX, AMD SEV-SNP, Arm CCA). The vendor is a trust anchor; compromise of the vendor invalidates the guarantee. | Costan & Devadas (2016) |
| **Institutional trust** | Trust derives from an organisation's governance regime — accreditation, audit logs, output checking. Examples: a Trusted Research Environment under the Five Safes framework. | ONS (2024); Goldacre Review (2022) |

**Why this matters for the framework.** A combination of two PETs is only as strong as the *weakest* trust assumption in the stack. The card construction process should make every trust assumption explicit, not assume them away.

---

## 2. Disclosure-risk terms

These terms describe **what can go wrong from the data subject's perspective**. They map directly to the assurance-gap argument in YAPS and to the headline categories in NIST SP 800-188.

| Term | Definition | Primary source |
|---|---|---|
| **Identity disclosure / singling out** | An attacker can isolate a single individual's record from a release. The canonical example is a uniquely-rare combination of attributes. | NIST SP 800-188 §3.1; Article 29 WP Opinion 05/2014 |
| **Attribute disclosure / inference** | An attacker can infer a sensitive attribute of an individual from a release, without necessarily picking them out by identity. | NIST SP 800-188 §3.1; Article 29 WP |
| **Membership disclosure** | An attacker can determine whether a specific individual's record was used to produce a release (e.g. used in model training, included in a statistical aggregate). | NIST SP 800-188 §3.1; Shokri et al. (2017) |
| **Linkage / linkability** | Two or more records can be matched to the same individual across releases. Article 29 WP names this as one of three re-identification routes. | Article 29 WP Opinion 05/2014 |
| **Reconstruction** | Per-record values can be recovered from a series of aggregate releases (e.g. Dinur–Nissim style). A strong form of identity + attribute disclosure. | Dinur & Nissim (2003) |
| **Composition leakage** | Privacy loss accumulates across releases. A bound that is acceptable for one release can become meaningless across many. | Dwork & Roth (2014) §3.5 |

**Why this matters for the framework.** Cards record the *assurance* against each of these failure modes, not the *probability* of attack. The stepwise-from-private approach (see [STEPWISE_RISK.md](STEPWISE_RISK.md)) walks through which disclosure type each PET addresses.

---

## 3. Assurance-artefact terms

These are the recurring **evidence types** that show up across PETs. The YAPS rules in [yaps/rules/rules.yaml](yaps/rules/rules.yaml) check for their presence and quality.

| Term | Definition | Where it applies |
|---|---|---|
| **Attestation** | A cryptographic statement, signed by a hardware root of trust, that a specific code measurement is executing on a genuine platform. Proves *what is running*, not *that it is correct*. | TEE primitives |
| **Privacy accountant** | A software component that tracks cumulative privacy loss (ε, δ) across queries or training steps under a stated composition theorem. Examples: Google's `dp_accounting`, Opacus' RDP accountant. | DP primitives |
| **Parameter manifest** | A versioned, immutable record of every parameter affecting a privacy guarantee: ε, δ, sensitivity, clipping norm, noise mechanism, HE security level, MPC adversary model, etc. | All primitives |
| **Adversary-model declaration** | Explicit statement of which adversary class a protocol is proven secure against (e.g. "static semi-honest, 1-of-3 corruption"). Required for any MPC claim. | MPC, ZKP |
| **Disclosure-risk evaluation** | An empirical test of how identifiable a release is. Membership-inference attacks, linkage tests, k-anonymity-style checks, motivated-intruder simulations all qualify. | Synthetic data, DP releases, TRE outputs |
| **Output-clearance log** | A workflow record of what releases were requested, reviewed, approved or refused, and on what basis. The defining assurance mechanism of a TRE. | TRE primitives |
| **Bridge / cross-validation record** | Where a tool emulates a system under test (rather than running it), evidence that the emulator matches the system on a defined battery of cases. | Empirical PET evaluations |

**Why this matters for the framework.** YAPS rules fire on the *absence* of these artefacts, not on the absence of "privacy". This is the operational form of the assurance-gap argument.

---

## 4. PET-family terms

Used throughout the survey paper and the explorer tables.

| Term | Definition | Note |
|---|---|---|
| **Algorithmic PET** | A privacy-preserving transformation rooted in cryptography or a formal privacy definition (DP, MPC, HE, SYN, ZKP). | Survey §2.1 |
| **Architectural PET** | A system or governance arrangement that constrains data exposure by design (FL, TEE, TRE). | Survey §2.2 |
| **Composition** | The interaction between multiple PETs when stacked. Composition is rarely a free property — it must be designed and proved, not assumed. | Dwork & Roth (2014) §3.5 |
| **In-use confidentiality** | Protection of data *while being computed on* (vs. at rest or in transit). The headline property of TEEs and FHE. | Industry usage; ODI (2024) |
| **Output bound** | A formal limit on what a released artefact (statistic, model, synthetic dataset) can reveal about any individual. Provided by DP at release, or by ZKP for selective-disclosure proofs. | Dwork & Roth (2014) |

---

## 5. Reading conventions used in this repository

- **PET IDs** (`DP`, `DP-L`, `DP-C`, `MPC`, `HE`, `ZKP`, `SYN`, `FL`, `TEE`, `TRE`) are the short keys defined in [data/primitives.yaml](data/primitives.yaml). They are stable foreign keys used across all tables and cards.
- **Pairing IDs** (`P-01` … `P-08`) and **stack IDs** (`S-01` … `S-04`) are stable across versions. New entries get the next free ID; deprecated entries are marked, not renumbered.
- **Confidence levels** for combinations are: `peer_reviewed`, `deployment_documented`, `practitioner_reported`, `theoretical`. Defined in [data/pairings.yaml](data/pairings.yaml).
- **Maturity stages** (1–4) are defined once in [README.md §Assurance Maturity Rubric](README.md). They apply uniformly to primitives, combinations, and sectoral deployments.

---

## Citing this glossary

The methodological commitment is: *use a small, citable vocabulary consistently across the framework*. When the framework is reused (in a workshop, a card, a report), citing this glossary alongside the relevant primary source is sufficient — there is no separate Privacy-Explorer-specific vocabulary to learn.

See [CITATION.cff](CITATION.cff) for citation metadata.
