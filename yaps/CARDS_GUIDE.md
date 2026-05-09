# Privacy Card Modularity Guide

A Privacy Card is not a static document. It is designed to be updated as the technology, academic evidence base, or governance landscape around a deployment changes. This guide explains the modular structure of a card, how to swap components, and how to track changes over time.

---

## The five layers

Every Privacy Card has five independently configurable layers. Each layer can be updated without necessarily invalidating the others, though changes in one layer often have implications for adjacent ones.

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5 — REGULATORY                                           │
│  Applicable regulations · standards alignment · DPIA reference  │
│  Changes when: jurisdiction, regulatory guidance, or use        │
│  purpose changes                                                │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4 — GOVERNANCE                                           │
│  Output controls · audit log · DPIA · frameworks applied        │
│  Changes when: institutional controls, approval processes,      │
│  or access policy changes                                       │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3 — ASSURANCE                                            │
│  Required artefacts · status · maturity stage                   │
│  Changes when: new artefacts are produced, maturity is          │
│  re-assessed, or the artefact standard evolves                  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2 — PET LAYER                                            │
│  Primitive IDs · roles · tooling · parameters                   │
│  Changes when: a tool is added, replaced, upgraded, or a        │
│  parameter is tuned                                             │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1 — DATA LAYER                                           │
│  Data categories · sensitivity · linkage risks · access         │
│  control · Solid integration intent                             │
│  Changes when: the data scope, processing purpose, or           │
│  access model changes                                           │
└─────────────────────────────────────────────────────────────────┘
```

Each layer change should be recorded in the `change_log` field with a date and brief description. Significant changes — changing a primitive, upgrading a tool, revising epsilon — may warrant a new card version rather than an in-place edit.

---

## Module types

Within the PET layer, three types of component can be independently modified:

| Module type | JSON location | What it controls |
|------------|---------------|-----------------|
| **Tool module** | `pet_components[].tooling[]` | Which specific implementation is used for a primitive |
| **Parameter module** | `pet_components[].parameters` | How the primitive is configured (ε, δ, vendor, memory) |
| **Governance assumption** | `governance_controls` + `assurance_targets.required_artefacts` | What procedural controls are in place and what evidence is required |
| **Data context** | `data_profile_ref` + `deployment_context` | What data is processed and in what sector context |
| **Regulatory scope** | `regulatory_context` | Which regulations and standards apply |

---

## Example 1 — Swapping a tool (AWS → Azure)

**Scenario:** A deployment is moving its TEE workload from AWS Nitro Enclaves to Azure Confidential Computing (AMD SEV-SNP).

**What changes:** The `tooling` array inside the TEE `pet_components` entry. The `parameters.vendor` field. The `assurance_targets.required_artefacts` entry for attestation (the attestation report format differs between AWS and Azure).

**Before:**
```json
{
  "primitive_id": "TEE",
  "tooling": [{ "name": "AWS Nitro Enclaves", "url": "https://aws.amazon.com/ec2/nitro/nitro-enclaves/" }],
  "parameters": { "vendor": "AWS Nitro Enclaves", "memory_mb": 4096 }
}
```

**After:**
```json
{
  "primitive_id": "TEE",
  "tooling": [
    { "name": "Azure Confidential Computing (AMD SEV-SNP)", "url": "https://azure.microsoft.com/en-us/solutions/confidential-compute/" },
    { "name": "Gramine", "url": "https://gramineproject.io/" }
  ],
  "parameters": { "vendor": "AMD SEV-SNP via Azure Confidential Computing", "memory_mb": 16384 }
}
```

**Risk implications:** The attestation artefact must be updated — Azure generates ECDSA-based attestation reports via Microsoft Azure Attestation, not the Nitro-specific format. The side-channel mitigation declaration should be revised because AMD SEV-SNP has a different side-channel posture than Intel SGX. Add a `change_log` entry and re-run the risk engine — ASSUR-001 will fire until the updated attestation artefact is recorded.

**Change log entry:**
```json
{ "date": "2026-05-09", "change": "TEE layer migrated from AWS Nitro to Azure Confidential Computing (AMD SEV-SNP); attestation format and side-channel declaration updated", "author": "Platform team" }
```

---

## Example 2 — Changing a DP parameter

**Scenario:** An initial deployment used ε=4.0 for utility; after publication of new membership inference results in the target domain, the team decides to tighten to ε=1.0.

**What changes:** The `parameters.epsilon` field. The `utility_evidence` field (utility will likely decrease). The `parameter_notes` narrative. The `maturity_justification` may need updating.

**Before:**
```json
"parameters": { "epsilon": 4.0, "delta": 1e-5, "noise_mechanism": "Gaussian" }
```

**After:**
```json
"parameters": { "epsilon": 1.0, "delta": 1e-5, "noise_mechanism": "Gaussian" }
```

**Risk implications:** COMP-001 will still fire if the privacy accountant artefact is not updated to reflect the new composition budget. SECTOR-003 (platform scale) may resolve if ε=1.0 is now within the acceptable composition range. Update `utility_evidence` to reflect the new utility degradation at ε=1.0. If this change is driven by a new regulatory guidance document, update `regulatory_context.standards_alignment`.

**When to version rather than edit:** If the epsilon change is driven by an external event (new attack paper, regulatory guidance, change of use purpose), consider creating a new card version (`CARD-healthcare-fl-tee-dp-202609`) rather than editing the existing one, so the change history is preserved at the file level rather than only in the `change_log`.

---

## Example 3 — Changing a governance assumption (adding TRE)

**Scenario:** A healthcare FL deployment that started without TRE governance has been adopted into a formal NHS Secure Data Environment. A TRE layer is now in place.

**What changes:** A new entry is added to `pet_components` for TRE. The `architecture_pattern` may need updating from `pairing_ref: P-01` to `stack_ref: S-01` (or a custom pattern if TRE is added on top). `governance_controls.output_control` changes from `automated-statistical` to `both`. The `assurance_targets.required_artefacts` list gains TRE-specific artefacts.

**Adding TRE to pet_components:**
```json
{
  "primitive_id": "TRE",
  "role": "institutional access controls and output checking — NHS Secure Data Environment governance",
  "implementation_status": "deployed",
  "tooling": [{ "name": "NHS England Secure Data Environment", "url": "https://digital.nhs.uk/services/secure-data-environment-service" }],
  "parameters": { "framework": "Five Safes", "accreditation": "NHS DSPT compliant" }
}
```

**Adding TRE artefacts:**
```json
{
  "artefact": "access audit logs and accreditation records (TRE layer)",
  "status": "exists",
  "location": "NHS SDE governance team records"
}
```

**Risk implications:** SECTOR-001 (healthcare without TRE) will no longer fire. GOV-002 will resolve if `output_control` is now `both`. The overall risk rating may move from AMBER toward GREEN as TRE governance fills the procedural accountability gap.

---

## Example 4 — Changing the data context

**Scenario:** A deployment initially processing de-identified administrative data is extended to include genetic data as part of a new research stream.

**What changes:** The linked data profile (`data_profile_ref`) — specifically `data_categories`, `sensitivity_level`, `linkage_risk`. The `regulatory_context` may gain new applicable regulations (Art. 9 GDPR for genetic data). The `trust_model` should be updated to account for the higher re-identification risk of genetic data.

**Data profile changes:**
```json
"data_categories": [
  { "category": "administrative data", "special_category": false },
  { "category": "genomic / genetic data", "special_category": true, "volume": "~5K whole-genome sequences" }
],
"sensitivity_level": "strictly-confidential"
```

**Risk implications:** GOV-003 (DPIA) will fire if the DPIA reference is not updated to cover the new data category. The `auxiliary_data_risk` field should be populated — genetic data is particularly sensitive to linkage with published genomic databases. The `trust_model.threat_actors` section should be reviewed: genetic data enables long-range re-identification that goes beyond standard quasi-identifier linkage.

---

## Removing a component

Components can be removed when technology, governance, or use changes make them no longer applicable. Common removal scenarios:

**Removing a deprecated tool:**
```json
"tooling": [
  { "name": "OpenDP", "url": "https://opendp.org/", "licence": "MIT" }
]
```
Remove the deprecated tool entry entirely. If this is the only tooling entry for a primitive and no replacement is specified, add a `parameter_notes` explaining that tooling selection is pending.

**Removing a regulation:**
If a deployment moves out of GDPR scope (e.g. data subjects are now exclusively non-EU/UK), remove the corresponding entry from `regulatory_context.applicable_regulations`. REG-002 will stop firing. Add a `change_log` entry explaining the scope change.

**Removing a PET primitive:**
This is a significant architectural change and warrants a new card version. Remove the primitive from `pet_components`, update `architecture_pattern.pairing_ref` or `stack_ref`, remove the associated artefacts from `assurance_targets.required_artefacts`, and update the `trust_model` to reflect the changed threat surface. Re-run the risk engine — new findings will likely appear where the removed primitive was covering a threat.

---

## Module versioning and change tracking

The `change_log` field is your primary tracking mechanism. Best practices:

1. **Date every change.** Use ISO 8601 format (`YYYY-MM-DD`).
2. **Reference the specific module changed.** "Updated DP parameters" is less useful than "ε reduced from 4.0 to 1.0 following Doe et al. (2026) membership inference results in oncology domain."
3. **Record the reason.** Especially for parameter changes driven by new evidence or regulatory guidance — this preserves the audit trail.
4. **Version major changes.** For changes that affect the overall risk rating or architectural pattern, create a new card file rather than editing in place. Link the predecessor card in the `description` field.

**Example change log entries showing module evolution:**

```json
"change_log": [
  {
    "date": "2026-01-15",
    "change": "Initial card created for FL+DP pilot",
    "author": "Privacy engineering team"
  },
  {
    "date": "2026-03-20",
    "change": "TEE layer added (AWS Nitro) — PET stack upgraded from P-01 to S-01; attestation artefact added",
    "author": "Platform architecture team"
  },
  {
    "date": "2026-05-01",
    "change": "ε reduced from 4.0 to 1.0 following Doe et al. (2026); utility_evidence updated (AUROC: 0.87 → 0.84)",
    "author": "Privacy engineering team"
  },
  {
    "date": "2026-08-10",
    "change": "TRE governance layer added — NHS SDE accreditation complete; output_control updated to both; SECTOR-001 finding resolved",
    "author": "Governance lead"
  }
]
```

---

## How module changes affect risk ratings

This table summarises which rule categories are likely to be affected by each module type change:

| Module changed | Rules likely affected | Expected direction |
|---------------|----------------------|-------------------|
| Add/swap tool | ASSUR (tool-specific artefacts) | Neutral / improved if artefacts updated |
| Tighten DP parameters | COMP-001 (if accountant updated), REG-001 | Improved |
| Loosen DP parameters | COMP-001, SECTOR-003 | May worsen |
| Add TRE | GOV-002, SECTOR-001/002 | Improved |
| Remove MPC | IFACE-001, COMP-002 | May worsen |
| Add SYN without DP | IFACE-003, ASSUR-002 | Worsened (RED) |
| Add GDPR regulation | GOV-003, REG-002, REG-003 | New findings appear |
| Upgrade from pilot to production | ASSUR-004, GOV-001 | More rules fire (higher bar) |

Running the risk engine after any module change is the fastest way to see the net effect: `python yaps/engine/risk_engine.py <card.json> --full`

---

## Modular cards as living governance documents

The modular structure is designed to support a specific use of Privacy Cards: as **living governance documents** that accompany a deployment from pilot through to production and beyond. In this use, a card is not a one-time artefact — it is maintained alongside the deployment and updated whenever a significant architectural or governance change occurs.

This mirrors the approach taken with Data Protection Impact Assessments under GDPR Art. 35, which are explicitly expected to be reviewed and updated when processing activities change. A Privacy Card can serve as the technical annex to a DPIA: the DPIA records the legal basis and organisational accountability; the card records the technical architecture, artefact evidence, and risk findings.

As the field matures — as new tools, new attack results, and new regulatory guidance emerge — the modular structure means that specific components can be updated without requiring the whole card to be re-authored. The `change_log` provides the audit trail that demonstrates the card has been maintained, not just created.
