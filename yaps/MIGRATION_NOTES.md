# YAPS Schema — Migration Notes (1.2 → 2.0)

Schema 2.0 is a deliberate breaking change from 1.2. The breakage is concentrated in the structure of evidence references and the `risk_calibration` block; the rest of the card surface is additive. This document explains what changed, why, and how to migrate.

## Why 2.0 is breaking

Three problems with 1.2 motivated the bump:

1. **Evidence references were strings.** A bare `"results/sq1/foo.json"` cannot tell a reviewer *what kind of evidence* is on offer. Is it a reproducible record, a signed receipt, or a notarised attestation? Practically every dispute scenario turns on this distinction, and 1.2 made it impossible to express on the card.
2. **The three ε quantities were not first-class.** Cards in the wild used `mu_dp_design_target`, `measured_epsilon.rdp_envelope`, etc. — but the schema only formalised one of them (`mu_dp`). Cards routinely fell out of schema validation because the schema lagged the usage.
3. **`threat_profile` was implicit.** Every empirical attack-rate on a card is calibrated against exactly one threat model. The schema let cards omit this, which is exactly the over-reading Boenisch et al. (2023, §5) warn against — moving from honest-but-curious to malicious-server shifts ε\* by approximately 2×.

Schema 2.0 fixes all three. Existing 1.2 cards revalidate under 2.0 only after the migration below; the engine is responsible for emitting a clear error message pointing here.

## Field-by-field diff

### Added: `$defs.evidence_reference` (object replaces string)

Every evidence pointer is now structured:

```json
{
  "location": "results/sq1/mia_per_record__B-LiRA__bloodmnist.json",
  "evidence_class": "reproducible-record",
  "produced_by": "did:web:bloodmnist-fl.example.org",
  "notes": "..."
}
```

**Why structured.** The `evidence_class` enum makes the tamper-resistance hierarchy explicit on the card. The enum is monotonic in resistance:

| Value | What it means | Sufficient for |
|---|---|---|
| `reproducible-record` | Audit-trailed metric, reproducible from config + seed + dataset hash. Not cryptographically signed. | Internal reproducibility, *not* dispute evidence. |
| `signed-record` | Record (or its hash) signed by producing party with a verifiable key (JWS via WebID-DPoP, or equivalent). | Non-repudiation against producer alone. |
| `countersigned-record` | Additionally signed by a second party with an independent key (witness, audit body). | Non-repudiation across two trust domains. |
| `hash-chain-committed` | Committed to an append-only log with periodic external anchors. | Time-ordering of claims; protects against late-stage fabrication. |
| `notarised` | Anchored to a public ledger or notary service. | Third-party attestation of time-of-commit. |

**Academic anchors for the enum design.**
- **Duddu, Järvinen, Gunn, Asokan, "Laminator," CODASPY 2025, §3** — defines the property-card-with-attestation pattern; our `signed-record` and `countersigned-record` track Laminator's signing-party hierarchy.
- **IBM Atlas, arXiv:2502.19567, §4** — uses in-toto attestations to construct an SLSA-compatible provenance graph for the ML pipeline; our `hash-chain-committed` traces to the in-toto append-only-log primitive.
- **Guo, Vaswani, Paverd, Pietzuch, "VerifiableFL," arXiv:2412.10537, §3** — produces attested data-flow graphs for FL using exclaves; their attestation surface is the model for our `notarised` class when the anchor is an external attestation service.
- **Rosenthal et al., arXiv:2310.05731 (2023), §4** — blockchain-driven usage control on Solid pods; cited as one peer-reviewed instance of the `notarised` end of the enum (we do not adopt the blockchain layer in this repository, but the citation establishes the design exists).

**Migration recipe for 1.2 cards.** Wherever 1.2 used a bare string evidence reference:

```json
// 1.2
"evidence_ref": "results/sq1/foo.json"

// 2.0
"evidence": {
  "location": "results/sq1/foo.json",
  "evidence_class": "reproducible-record"
}
```

A migration script in `yaps/engine/migrate_1_2_to_2_0.py` does this automatically and is what the engine invokes on legacy cards. The default `evidence_class` is `reproducible-record`; this is the silent default per the design decision in §3 (operator note: this is also what RISKCAL-004 fires AMBER on if the threat model demands a stronger class — see `rules/cps_rules.yaml`).

### Added: `$defs.device_class` (enum on `pet_components[]`)

New `device_class` field on each PET component:

```json
"device_class": "edge-gateway"
```

**Why added.** Two FL deployments with identical (ε, δ) can offer different actual privacy depending on which devices participated. The CPS/IoT literature is consistent on this:

- **Mo et al., "DarkneTZ," MobiSys 2020, §5** — demonstrates that partitioning a model across an ARM-TrustZone-equipped edge device measurably reduces MIA against the sensitive layers; the privacy outcome is bound to the device class, not just (ε, δ).
- **Gupta et al., arXiv:2511.00037 (2025), §4** — head-to-head FL framework benchmark across PathMNIST showing that device-assumption differences (FLARE production, Flower prototyping, Substra compliance) materially change the deployment's effective privacy surface.

The enum is deliberately small and CPS/IoT-flavoured. New values can be added without breaking the schema if the use case is justified.

### Added: `$defs.trust_zone` (enum on `stepwise_chain[]`)

New `trust_zone` field on each chain step:

```json
"trust_zone": "enclave"
```

**Why added.** A chain step that operates inside a TEE (`enclave`) makes a different kind of trust claim than one operating in the application layer. Reviewers need to be able to read the zone at a glance.

**Academic anchor.** Aligned with **NIST 1500-201, "Framework for Cyber-Physical Systems: Volume 1, Overview" (2017), §3** — the trust-zone vocabulary (perception, network, application, platform) is from the NIST reference architecture. The `enclave` and `off-platform` values are CPS/IoT-specific additions motivated by Mo et al. (DarkneTZ 2020) and the third-party-witness pattern (Solid CG "Trustless Cross-POD Verification" community thread, 2024).

### Added: `$defs.threat_profile` (enum), required in `risk_calibration`

New mandatory field in `risk_calibration`:

```json
"risk_calibration": {
  "threat_profile": "honest-but-curious-server",
  ...
}
```

**Why required.** Every empirical attack-rate on a card is calibrated against exactly one threat model. Conflating profiles is the most common over-reading of FL privacy claims:

- **Boenisch, Dziedzic et al., "When the Curious Abandon Honesty," EuroS&P 2023, §5** — demonstrates an active server reconstruction even when DP and SecAgg are both deployed. The shift from honest-but-curious to malicious-server reduces the operationally meaningful ε\* by approximately 2× (their Table 4).
- **Carlini et al., "Membership Inference from First Principles," IEEE S&P 2022, §6** — the worst-record TPR-at-low-FPR framing assumes a stated adversary; without it, the metric is unbounded.

Cards that omit `threat_profile` cannot be evaluated against any RISKCAL-* rule in 2.0 (the rules read this field). The engine raises an error rather than silently passing.

### Added: `$defs.cps_subject_type` (enum on `deployment_context`)

New field for CPS/IoT cards:

```json
"deployment_context": {
  "cps_subject_type": "patient",
  ...
}
```

**Why added.** The natural unit of disclosure differs by subject role. For `patient`, the relevant MIA is often subject-level (each patient may have many records across pods); for `vehicle-owner`, it may be linkage; for `industrial-operator`, often singling-out.

**Academic anchor.** **Suri et al., "Subject Membership Inference Attacks in Federated Learning," PoPETs 2023, §3** — first to demonstrate subject-level MIA in cross-silo FL; shows the attack is potent even with only a handful of known-subject labels. The schema's `attack` enum now distinguishes `MIA-per-record` from `MIA-per-subject` in response.

### Refactored: `risk_calibration` block (BREAKING)

The 1.2 `risk_calibration` block had a flat structure mixing design target, accountant output, and measured advantage. 2.0 separates these into three first-class sub-blocks: `design_target`, `accountant`, `empirical_audit`, plus the existing `measured_advantage`.

```json
"risk_calibration": {
  "threat_profile": "honest-but-curious-server",
  "design_target": { "epsilon": 2.0, "delta": 1e-5, "attack_target": { ... } },
  "accountant": { "rdp_envelope": 44.6, "prv": 24.9, "delta": 1e-5, "evidence": { ... } },
  "empirical_audit": { "method": "canary-one-run", "epsilon_lower_bound": 0.0, "delta": 1e-5, "evidence": { ... } },
  "measured_advantage": { "attack_method": "LiRA", "value": 0.0424, ... },
  "trade_off_curve": { "location": "...", "evidence_class": "..." },
  "operational_interpretation": "...",
  "source_library": "manual"
}
```

**Why refactored.** Reporting only one of the three ε quantities mis-leads reviewers about which assurance is actually on offer:

- **Desfontaines, "Reporting privacy guarantees in machine learning," desfontain.es blog (2023)** — argues that single-ε reporting hides the gap between what the deployment promises, what composition bounds, and what an audit can falsify.
- **Kulynych, Hsu, Troncoso, Kasiviswanathan, "Attack-Aware Noise Calibration for Differential Privacy," NeurIPS 2024, §3** — formalises the f-DP-to-attack-rate mapping that `target_advantage` instantiates. Critical citation for justifying why design-target attack-rate, not design-target ε, is the right primary handle.
- **Steinke, Nasr, Jagielski, "Privacy Auditing with One (1) Training Run," NeurIPS 2023 Outstanding Paper** — single-training-run multi-canary empirical lower bounds at approximately 100× lower compute than multi-run methods. The `empirical_audit.method` enum surfaces this as the recommended technique; `canary-multi-run` is retained for backward-compatibility with Jagielski-2020-style audits.
- **Maddock, Sablayrolles, Stock, "CANIFE: Crafting Canaries for Empirical Privacy Measurement in Federated Learning," ICLR 2023, §4** — FL-specific canary crafting yielding per-round empirical ε 4-5× lower than random-canary baselines. The `method: "canife"` value names this as a distinct technique.

**Migration recipe for 1.2 cards.**

```json
// 1.2
"risk_calibration": {
  "mu_dp_design_target": 0.85,
  "attack_target": {
    "attack": "MIA",
    "target_advantage": 0.030,
    "target_fpr": 0.001,
    "evidence_ref": "results/sq1/foo.json"
  },
  "measured_epsilon": {
    "rdp_envelope": 44.57,
    "prv_gopi_2021": 24.92,
    "delta": 1e-5,
    "evidence_ref": "results/accountant_comparison.json"
  },
  "operational_interpretation": "...",
  "source_library": "manual"
}

// 2.0
"risk_calibration": {
  "threat_profile": "honest-but-curious-server",   // NEW REQUIRED — set per reading of card text
  "design_target": {
    "epsilon": 2.0,
    "mu_dp": 0.85,
    "delta": 1e-5,
    "attack_target": {
      "attack": "MIA-per-record",     // 1.2's "MIA" expands to "MIA-per-record" or "MIA-per-subject"
      "target_advantage": 0.030,
      "target_fpr": 0.001
    }
  },
  "accountant": {
    "rdp_envelope": 44.57,
    "prv": 24.92,
    "delta": 1e-5,
    "evidence": {
      "location": "results/accountant_comparison.json",
      "evidence_class": "reproducible-record"
    }
  },
  "empirical_audit": {                  // NEW BLOCK — populate from canary-audit result records
    "method": "canary-one-run",
    "epsilon_lower_bound": 0.0,
    "delta": 1e-5,
    "evidence": { "location": "...", "evidence_class": "reproducible-record" }
  },
  "measured_advantage": {               // NEW BLOCK — populate from MIA result records
    "attack_method": "LiRA",
    "value": 0.0424,
    "evidence": { "location": "results/sq1/foo.json", "evidence_class": "reproducible-record" }
  },
  "operational_interpretation": "...",
  "source_library": "manual"
}
```

### Added: `attestation_evidence` on `pet_components[]`

When a PET component requires hardware attestation (typically `primitive_id: "TEE"`), the attestation document is now a first-class field on the component:

```json
{
  "primitive_id": "TEE",
  "attestation_evidence": {
    "location": "internal/attestation/round_12.json",
    "evidence_class": "signed-record",
    "produced_by": "aws:nitro:enclave-attestation"
  },
  ...
}
```

**Why added.** A deployment that claims a TEE without producing the attestation receipt is asserting a security property without evidence. The new CPSDEV-ATTEST-001 rule fires AMBER if this field is missing on a deployed TEE component. Academic anchor: Laminator (Duddu 2025) and VerifiableFL (Guo 2024) both motivate attestation-as-evidence; the Trail of Bits 2024 walkthrough on Nitro attestation document structure is the practical reference for what the artefact contains.

## Engine behaviour

The risk engine (`yaps/engine/risk_engine.py`) is updated to:

1. Accept both 1.2 and 2.0 schemas at the input boundary.
2. Auto-migrate 1.2 cards to 2.0 in memory using the recipes above, emitting a console warning naming the fields it inferred (e.g. "evidence_class defaulted to `reproducible-record`"; "threat_profile defaulted to `honest-but-curious-server`").
3. Refuse to validate cards whose declared `schema_version: "2.0"` is missing now-required fields.

The auto-migration writes a migrated-card-on-disk only if the user explicitly requests it (`--migrate` CLI flag); otherwise the migration is in-memory and the on-disk card is left intact.

## Rules updated

The rule families now read 2.0 fields:

- **RISKCAL-002** — fires when `measured_advantage.value` exceeds `design_target.attack_target.target_advantage` (was: `measured_advantage` exceeded `attack_target.target_advantage`).
- **RISKCAL-004** *(new)* — fires AMBER when any evidence reference has `evidence_class: "reproducible-record"` on a claim that the deployment's `threat_profile` indicates needs `signed-record` or stronger. This is the explicit surfacing of Naman's tamper-evidence concern at the rule level.
- **CPSDEV-ATTEST-001** *(new in `rules/cps_rules.yaml`)* — fires AMBER when a `pet_components[]` entry with `primitive_id: "TEE"` and `implementation_status: "deployed"` has no `attestation_evidence`. Academic anchor: Laminator §3, VerifiableFL §3.
- **CPSDEV-DEVHET-001** *(new)* — fires AMBER when `pet_components[]` device classes change across stepwise chain entries without re-attestation. Academic anchor: DarkneTZ §5; Gupta et al. 2025 §4.
- **CPSDEV-OTA-001** *(new)* — fires RED when participating device firmware version is below the deployment's stated minimum (a field the schema does not yet carry; the rule's presence is itself the argument that future deployments should report it). Academic anchor: tee.fail 2024 §3 — side channels concentrate in older silicon.

## Implementation timeline

1. Schema 2.0 lands in `yaps/schemas/privacy_card.schema.json` (this PR).
2. `engine/risk_engine.py` updated to read 2.0; auto-migration shim in `engine/migrate_1_2_to_2_0.py` (next PR).
3. Existing cards in `yaps/cards/examples/` migrated to 2.0 with `--migrate` (same PR as engine update).
4. New CPSDEV-* rules added to `rules/cps_rules.yaml` (same PR).
5. Companion stepwise-privacy-cards repo updated to 2.0 example chain (cross-repo PR — companion artefact for the CPSIoTSec paper).

## Open question for the workshop programme

When workshop participants construct a card under W2 (workshops/W2-card-construction.md), the evidence-class question — *"which dispute scenarios would each of your `evidence_ref` entries survive?"* — should now be part of the construction protocol. The W2 facilitator notes will be updated to cover this. (Naman Goel's evidence-mechanism concern is the empirical motivation for elevating this question to the workshop construction phase; see his feedback summarised in the stepwise-privacy-cards `docs/EVIDENCE_LIMITS.md`.)
