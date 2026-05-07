# Privacy Explorer

A companion repository to the survey paper *Implementation-Centred Privacy-Enhancing Technologies: Mechanisms, Combinations, and Assurance* — providing structured, implementation-centred reference tables for reasoning about PET combinations, deployment maturity, and assurance artefacts.

> The survey argues that PET viability depends less on technological strength and more on whether privacy claims can be rendered into repeatable, inspectable assurance artefacts. The tables below encode that argument in a relational form: technique primitives → pairwise combinations → three-layer stacks → sector deployment contexts.

> **These tables are suggestive and indicative, not prescriptive.** Maturity stage assessments reflect a reading of available peer-reviewed literature and documented deployments at time of writing. Reasonable experts will disagree — particularly on maturity stages, which are sensitive to sector context, organisational capacity, and the evidence threshold you apply. The [YAML data files](data/) are the canonical source for forking and revising any entry.

---

## Navigation

| Resource | Purpose |
|----------|---------|
| **This file** | Reference tables (T1–T4) rendered as markdown |
| [DIAGRAM.md](DIAGRAM.md) | Visual diagrams of the same data — ER schema, combination network, sector map |
| [data/primitives.yaml](data/primitives.yaml) | T1 source data — edit to revise individual technique entries |
| [data/pairings.yaml](data/pairings.yaml) | T2 source data — edit to add, remove, or contest two-PET pairings |
| [data/stacks.yaml](data/stacks.yaml) | T3 source data — edit to add or revise three-layer stacks |
| [data/sectors.yaml](data/sectors.yaml) | T4 source data — edit to revise sector mappings and maturity assessments |
| [privacy-cards/](privacy-cards/) | Planned: structured per-deployment privacy artefact cards (not yet built) |

---

## Section 4 — Comparative PET Reference Tables

The four tables below are designed to be read relationally. Each table extends the previous: **T1** defines PET primitives; **T2** pairs them; **T3** builds three-layer stacks from T2 pairings; **T4** maps those stacks to sectors. Cross-references use the short IDs defined in T1 and T2.

---

### T1 — PET Primitives

The base registry. All IDs in T2–T4 reference the `ID` column here. Algorithmic PETs are shown first, followed by architectural PETs.

| ID | Technique | Family | Typical Trust Model | Core Assurance Artefacts | Dominant Bottleneck | Typical Maturity |
|----|-----------|--------|---------------------|--------------------------|---------------------|------------------|
| `DP` | Differential Privacy | Algorithmic | Correct parameterisation and accounting required; no fully trusted curator needed for local DP | Privacy budget/accountant, parameter manifest, composition assumptions, release log | Utility loss; parameter governance; privacy budget composition | Standardised assurance in official statistics and consumer telemetry |
| `MPC` | Secure Multi-Party Computation | Algorithmic | Protocol-dependent adversary model; no single trusted curator | Protocol specification, adversary model declaration, test vectors, implementation audit | Communication and compute overhead | Selective production in finance, genomics, benchmarking |
| `HE` | Homomorphic Encryption | Algorithmic | Security rests on scheme assumptions and parameter regime | Parameter set, security level, precision bounds, benchmark evidence | Compute cost, memory, workload fit | Emerging; niche production with growing hardware co-design |
| `ZKP` | Zero-Knowledge Proofs | Algorithmic | Zero-knowledge depends on proof system, circuit correctness, and setup model | Circuit definition, verification parameters, trusted-setup transcript (if any), benchmark reports | Prover cost; engineering and circuit complexity | Maturing in verification-heavy ecosystems (blockchain); limited elsewhere |
| `SYN` | Synthetic Data | Algorithmic | Privacy contingent on generator, leakage controls, release interface, and downstream context | Disclosure-risk evaluation, utility benchmark, attack-based audit (e.g. membership inference), generation parameters | Validation burden; regulator and user acceptance | High uptake; uneven assurance maturity across deployments |
| `FL` | Federated Learning / Distributed Analytics | Architectural | Participants semi-trusted; coordinator honest-but-curious; updates may leak; poisoning risk | Training protocol, aggregation rules, convergence/robustness reports, audit logs | Communication rounds; non-IID data effects; coordination overhead | Pilot-to-operational in selected sectors, particularly health and technology |
| `TEE` | Trusted Execution Environment | Architectural | Trust in hardware vendor, attestation chain, and implementation; OS may be hostile | Attestation report, enclave measurement, dependency manifest, side-channel mitigations | Vendor trust; enclave memory limits; operational key management | Commercially deployed (cloud TEEs); assurance remains layered |

---

### T2 — Two-PET Pairings

Each row combines two primitives from **T1**. The `Pair ID` is referenced in T3 and T4. Combinations are restricted to those with identifiable assurance regimes and production or near-production use cases.

| Pair ID | PET A → T1 | PET B → T1 | Combination Logic | Required Assurance Artefacts | Key Advantage | Key Shortcoming |
|---------|-----------|-----------|-------------------|------------------------------|---------------|-----------------|
| `P-01` | `FL` | `DP` | Distributed training with formal leakage bounds on model updates | Privacy accountant, clipping/noise parameters, convergence monitoring | Formal privacy bound layered onto distributed training; widely benchmarked | Accuracy degradation; accounting complexity; utility loss under tight ε |
| `P-02` | `FL` | `MPC` | Secure aggregation: coordinator sees only the sum of updates, not individual contributions | Aggregation protocol specification, adversary model, correctness proof | Removes coordinator visibility of per-client updates | Protocol complexity; communication overhead scales with client count |
| `P-03` | `FL` | `TEE` | Local data retention plus hardware isolation for update aggregation | Attestation evidence, enclave measurement, aggregation protocol audit | Stronger protection for intermediate update state | Hardware vendor trust; enclave memory limits; key management overhead |
| `P-04` | `TEE` | `DP` | In-use confidentiality plus formal output control: hardware isolates computation, DP bounds release | Attestation report, DP parameter manifest, release log | Clear separation of in-use privacy from output disclosure risk | Dual trust anchors (vendor + parameter governance); composability risk |
| `P-05` | `TEE` | `MPC` | Hardware isolation reduces MPC coordination and communication cost | Attestation, protocol audit, threat model declaration | Performance gain for some MPC workloads; reduced network exposure | Hybrid assurance narrative harder to audit; enclave memory constraints |
| `P-06` | `TEE` | `ZKP` | Verifiable execution with hardware-enforced isolation of the prover | Circuit definition, verification keys, attestation report, implementation assurance | Verifiability with reduced intermediate disclosure | Specialised infrastructure; proof generation cost; hybrid assurance complexity |
| `P-07` | `TRE` | `DP` | Formal output protection within a governed access environment; DP complements human output checking | Output clearance workflow, DP accountant, release policy, access audit logs | Strong fit for public-sector and accredited research settings | Governance latency; sign-off burden; parameter policy requires domain input |
| `P-08` | `SYN` | `DP` | Formal privacy definition applied to generator training or release, producing defensible synthetic artefacts | DP training/release parameters, privacy/utility evaluation, membership-inference audit | More legally and evidentially defensible synthetic release | Lower fidelity; utility loss is data-dependent and hard to predict ex ante |

---

### T3 — Three-PET Stacks

Each row extends a pairing from **T2** with one additional primitive from **T1**. Three-layer stacks arise where governance pressure or regulatory stakes justify the added coordination overhead. The `Stack ID` is referenced in T4.

| Stack ID | Base Pair → T2 | Added Layer → T1 | Full Stack | Rationale | Representative Use Case | Assurance Narrative |
|----------|---------------|-----------------|------------|-----------|------------------------|---------------------|
| `S-01` | `P-03` (FL + TEE) | `DP` | FL + TEE + DP | Defence-in-depth for distributed training: local data retention + hardware isolation of aggregation + formal output bounds | NVIDIA FLARE healthcare deployments; NHS federated learning pilots (Soltan et al., 2024) | Attestation confirms enclave integrity; privacy accountant bounds release; protocol audit covers aggregation. Strongest layered assurance for federated analytics at the cost of multi-layer composability risk |
| `S-02` | `P-07` (TRE + DP) | `TEE` | TRE + TEE + DP | Layered assurance for high-sensitivity governed analytics: institutional access controls + hardware isolation of compute + formal output bounds | ONS Secure Research Service; ADR UK accredited data environments | Governance logs and output clearance cover institutional accountability; attestation covers in-use confidentiality; DP accountant covers statistical release. Audit-ready but operationally costly |
| `S-03` | `P-02` (FL + MPC) | `DP` | FL + MPC + DP | Secure distributed training with coordinator-blind aggregation and formal per-update privacy bounds; extends P-01 by replacing standard aggregation with cryptographic secure aggregation | Cross-institutional ML with untrusted coordinator; production secure aggregation at scale (Bonawitz et al., 2017) | Aggregation correctness proof + privacy accountant + training protocol documentation. Strongest formal guarantee for cross-party federated settings; communication cost is the binding constraint |
| `S-04` | `P-08` (SYN + DP) | `TEE` | TEE + SYN + DP | Attested, DP-trained synthetic data generation: enclave protects source data during generator training; DP bounds the release | Controlled synthetic releases in regulated environments; TRE sandbox synthetic data | Attestation covers generation environment integrity; DP parameters cover release disclosure risk; disclosure-risk evaluation covers residual linking risk. Strongest synthetic assurance posture; rarely deployed outside high-sensitivity contexts |

---

### T4 — Sectoral Deployment Context

Maps sectors to their preferred stacks from **T2** and **T3**, with the assurance posture and maturity stage that characterises each. Maturity stages follow the four-level rubric: **(1) Experimental → (2) Repeatable → (3) Standardised assurance → (4) Audit-ready**.

| Sector | Primary Stacks → T2 / T3 | Assurance Posture | Dominant Assurance Anchor | Typical Maturity | Key Blocker |
|--------|--------------------------|-------------------|--------------------------|------------------|-------------|
| **Public sector / official statistics / governed research** | `P-07` (TRE + DP), `S-02` (TRE + TEE + DP), `P-08` (SYN + DP) | Output checking, audit logs, reproducible privacy accounting, release policy | Human-in-the-loop clearance + governance artefacts | Stage 3–4 (standardised to audit-ready where PETs slot into existing governance regimes) | Governance latency; legal sufficiency of DP evidence; parameter policy requires non-technical input |
| **Healthcare / biomedical research** | `P-01` (FL + DP), `P-03` (FL + TEE), `S-01` (FL + TEE + DP) | Clinical validity, institutional approval, robustness monitoring, implementation transparency | Regulatory and clinical sign-off alongside technical artefacts | Stage 2–3 (often stalls between repeatable and standardised due to non-technical sign-off burden) | Domain-specific validity requirements; multi-stakeholder approval; fairness and bias concerns under DP |
| **Finance / fraud / inter-organisational analytics** | `P-05` (TEE + MPC), `P-04` (TEE + DP), `P-06` (TEE + ZKP) | Threat-model clarity, implementation audit, benchmarked performance, correctness verification | Technical performance evidence and implementation audit | Stage 2–3 (strongest uptake where high-value cross-party use cases justify specialist engineering) | Compute and communication overhead; commercial incentive required to offset engineering cost |
| **Technology platforms / consumer AI / large-scale telemetry** | `P-01` (FL + DP), `P-02` (FL + MPC), `P-04` (TEE + DP) | Parameter governance, continuous privacy accounting, interface discipline, systems integration | Accountable pipelines with continuous monitoring | Stage 3 (more mature where PETs are built into platform infrastructure rather than handled as bespoke projects) | Accountability of composition over many releases; parameter drift; regulatory clarity on ε at scale |
| **Web3 / verifiable infrastructure / credential ecosystems** | `P-06` (TEE + ZKP), `ZKP` standalone | Proof-system soundness, circuit correctness, benchmark reproducibility, setup transparency | Cryptographic verification as the primary assurance anchor | Stage 2–3 (highest maturity where cryptographic proof replaces procedural governance) | Proof generation cost; circuit under-constraint risk; irreproducible benchmarks; limited outside blockchain contexts |

---

## Assurance Maturity Rubric

The maturity stages referenced in T4 are defined as follows. Technical robustness does not imply procurement maturity: a PET can be cryptographically strong and remain at Stage 1 if its artefacts are not renderable into repeatable, inspectable claims.

| Stage | Technical Profile | Assurance Profile | Operational Profile | What Typically Blocks Progression |
|-------|-------------------|-------------------|---------------------|------------------------------------|
| **1 — Experimental / Pilot** | Mechanism demonstrated on constrained workload | Evidence local to a paper, demo, or prototype | Limited documentation; specialist operators required | No stable assurance artefacts; unclear deployment costs |
| **2 — Repeatable Deployment** | Workflow can be re-run with known dependencies and constraints | Parameter choices, threat model, and outputs documented | Playbooks and known failure modes exist | Lack of standardised reporting or cross-team confidence |
| **3 — Standardised Assurance** | Comparable implementation patterns exist across settings | Shared artefacts emerge: accountants, attestation patterns, benchmark conventions, output-control records | Internal review and vendor comparison are tractable | Weak legal or procurement recognition; sector-specific gaps remain |
| **4 — Audit-Ready / Procurement-Ready** | Technology integrates into production controls and monitoring | Third-party or regulator-facing artefacts support scrutiny | Can be specified in contracts, review processes, and change-control | High maintenance cost; residual legal ambiguity in some contexts |

---

## Repository Structure

```
privacy-explorer/
├── README.md              # This file — Section 4 reference tables
├── privacy-cards/         # Planned: structured privacy card artefacts (not yet built)
└── survey_paper_notes.txt # Source survey manuscript notes
```

### `privacy-cards/`

Planned component. A privacy card is a structured artefact that accompanies any PET-protected asset (model, dataset, pipeline, or query service) and records what mechanisms were used, how they were parameterised, what evidence exists, and what residual risks remain. Key fields under consideration include: threat model and trust assumptions, mechanism parameters and toolchain versions, assurance artefacts, utility and performance metrics, governance mapping, residual risks, and change log.

---

## Key References

The tables above draw on the following works. Full bibliography is available in the survey paper.

- Abadi et al. (2016) — Deep learning with differential privacy
- Bonawitz et al. (2017) — Practical secure aggregation for FL
- Costan & Devadas (2016) — Intel SGX explained
- Dwork & Roth (2014) — Algorithmic foundations of differential privacy
- Ernstberger et al. (2023) — zk-Bench: benchmarking SNARKs
- Evans et al. (2018) — A pragmatic introduction to secure MPC
- Halevi & Shoup (2020) — Homomorphic encryption performance
- Kairouz et al. (2021) — Advances and open problems in federated learning
- McKenna et al. (2021) — Winning the NIST DP synthetic data competition
- OECD (2023) — Emerging Privacy-Enhancing Technologies
- ONS (2021–2024) — Safe Outputs and Secure Research Service guidance
- Royal Society (2019) — Privacy-preserving digital technologies
- Sheller et al. (2020) — Federated learning in medical imaging
- Stadler et al. (2022) — Synthetic data anonymisation groundhog day

## License 
MIT License: Permission is hereby granted, free of charge, to any person obtaining a copy
