# YAPS Tests

Fixture cards and a runner that verify the rule engine fires the rules we expect on cards designed to trigger them. Fixtures are kept deliberately small — each one targets a specific rule or small group of rules so the test diagnosis is unambiguous when something breaks.

## Layout

```
yaps/tests/
├── README.md
├── run_tests.py                       # Test runner (Python; reads each fixture + expected.yaml)
└── fixtures/
    ├── stepwise_minimal_well_formed.json     # Minimal well-formed stepwise card (passes STEP-*)
    ├── stepwise_missing_field.json           # Step with missing required field (fails STEP-002)
    ├── stepwise_no_final_residual.json       # Final step's residual_risk empty (fails STEP-003)
    ├── stepwise_pet_mismatch.json            # step.pet_added not in pet_components (fails STEP-004)
    ├── dpl_no_per_user_budget.json           # DP-L without per-user accountant (fails DP-VAR-001)
    ├── dpc_no_composition.json               # DP-C without composition assumption (fails DP-VAR-002)
    ├── cross_jur_no_mechanism.json           # Cross-jurisdictional without cross-border mechanism (fails JURIS-002)
    ├── no_exposure_problems.json             # Otherwise-valid card with no EP declarations (fails T0-001)
    └── expected.yaml                         # Per-fixture expected findings + must-not-fire list
```

## Running

```bash
# From the repository root (PyYAML required):
python yaps/tests/run_tests.py
```

Exit code 0 if every fixture's actual findings match the expected ones (i.e. all expected rules fire **and** no must-not-fire rules fire). Exit code 1 on any mismatch, with a per-fixture diff printed to stdout.

## Adding a new fixture

1. Add a card JSON to `fixtures/` with a name describing what it tests.
2. Add an `expected.yaml` entry listing:
   - `must_fire:` rule IDs that should appear in findings
   - `must_not_fire:` rule IDs that must NOT appear (regression guard)
   - `description:` short note on what this fixture is for
3. Run `python yaps/tests/run_tests.py` and verify the diagnosis matches your intent.

## What this is *not*

These fixtures test the **rule firing logic**, not the substantive correctness of the rules themselves. A rule could fire correctly on a fixture and still encode the wrong privacy posture. Rule content is tested by the workshop process and by application to real cards.
