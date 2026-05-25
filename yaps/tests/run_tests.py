#!/usr/bin/env python3
"""YAPS test runner.

For each fixture in `fixtures/`, evaluates the card against the rule set and
compares the actual findings against `expected.yaml`. Exits 0 if every fixture
matches; 1 on any mismatch.

Usage:
    python yaps/tests/run_tests.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure the engine is importable when run from repo root or from tests/.
HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ENGINE_DIR = REPO / "yaps" / "engine"
sys.path.insert(0, str(ENGINE_DIR))

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Import the engine's rule machinery. Reuse rather than re-implement.
import risk_engine  # noqa: E402


RULES_PATH = REPO / "yaps" / "rules" / "rules.yaml"
FIXTURES_DIR = HERE / "fixtures"
EXPECTED_PATH = FIXTURES_DIR / "expected.yaml"


def load_rules() -> list[dict]:
    return yaml.safe_load(RULES_PATH.read_text())["rules"]


def evaluate(card: dict, rules: list[dict]) -> tuple[list[str], list[str]]:
    """Return (rule_ids_fired, rule_ids_errored)."""
    fired = []
    errored = []
    for rule in rules:
        triggered, err = risk_engine.evaluate_rule(rule, card)
        if err:
            errored.append(rule["id"])
            continue
        if triggered:
            fired.append(rule["id"])
    return fired, errored


def main() -> int:
    rules = load_rules()
    expected = yaml.safe_load(EXPECTED_PATH.read_text())

    all_passed = True
    for fixture_name, spec in expected.items():
        card_path = FIXTURES_DIR / f"{fixture_name}.json"
        if not card_path.exists():
            print(f"[!] {fixture_name}: card file not found at {card_path}")
            all_passed = False
            continue

        card = json.loads(card_path.read_text())
        fired, errored = evaluate(card, rules)
        fired_set = set(fired)

        must_fire = set(spec.get("must_fire") or [])
        must_not_fire = set(spec.get("must_not_fire") or [])

        missing = must_fire - fired_set
        unexpected = must_not_fire & fired_set

        status = "PASS" if not missing and not unexpected else "FAIL"
        marker = "✓" if status == "PASS" else "✗"
        print(f"  {marker} {fixture_name:40s} {status}  ({spec.get('description', '')})")
        if missing:
            print(f"     missing (expected but did not fire): {sorted(missing)}")
        if unexpected:
            print(f"     unexpected (must not fire but did): {sorted(unexpected)}")
        if errored:
            print(f"     evaluation errors on rules: {errored}")

        if status == "FAIL":
            all_passed = False

    print()
    if all_passed:
        print("All fixtures passed.")
        return 0
    print("One or more fixtures FAILED.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
