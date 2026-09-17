"""Smoke tests for the workbench backend that do NOT require Elasticsearch.

These exercise:
- Reference-data loading from the repo
- JSON-schema validation against the current card schema
- Engine adapter against a real example card

Run from the repo root with:
    privacy-eval/.venv/bin/python -m pytest workbench/tests -q
(or any Python with pyyaml + jsonschema available; ES-dependent tests are
elsewhere).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make the backend app importable when running from the repo root.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_APP = REPO_ROOT / "workbench" / "backend"
sys.path.insert(0, str(BACKEND_APP))


def test_reference_yaml_loads():
    from app.data_loader import DATA_FILES, load_yaml
    for key in DATA_FILES:
        payload = load_yaml(REPO_ROOT, key)
        assert isinstance(payload, dict), f"{key} should load as a dict"


def test_rules_load():
    from app.data_loader import load_rules
    rules = load_rules(REPO_ROOT)
    assert isinstance(rules, list)
    assert len(rules) > 10
    # Smoke-check that the RISKCAL rules we added are present.
    rule_ids = {r.get("id") for r in rules}
    assert "RISKCAL-001" in rule_ids
    assert "RISKCAL-002" in rule_ids
    assert "RISKCAL-003" in rule_ids


def test_card_schema_validates_examples():
    from app.schema_loader import validate_card
    examples_dir = REPO_ROOT / "yaps" / "cards" / "examples"
    cards = list(examples_dir.glob("*.json"))
    assert cards, "no example cards found"
    for card_path in cards:
        card = json.loads(card_path.read_text())
        errors = validate_card(card, REPO_ROOT)
        assert errors == [], f"{card_path.name} failed validation: {errors}"


def test_card_schema_rejects_invalid():
    from app.schema_loader import validate_card
    card = {"card_id": "no-required-fields"}
    errors = validate_card(card, REPO_ROOT)
    assert errors, "schema validation should have produced errors"


def test_engine_adapter_evaluates_example():
    from app.engine_adapter import evaluate_card
    card_path = REPO_ROOT / "yaps" / "cards" / "examples" / "cross_jurisdictional_fl_tee_dpc.json"
    card = json.loads(card_path.read_text())
    result = evaluate_card(card, REPO_ROOT)
    assert "findings" in result
    assert "rating" in result
    assert "report_md" in result
    assert result["rating"] in {"RED", "AMBER", "GREEN", "INFO"}
    # The cross-jurisdictional card has a populated risk_calibration block,
    # so RISKCAL-001 must NOT fire.
    fired = {f["id"] for f in result["findings"]}
    assert "RISKCAL-001" not in fired, "RISKCAL-001 should not fire on a card with risk_calibration"


def test_engine_adapter_fires_riskcal_001_when_block_absent():
    """Strip the risk_calibration block from the example card; confirm RISKCAL-001 fires."""
    from app.engine_adapter import evaluate_card
    card_path = REPO_ROOT / "yaps" / "cards" / "examples" / "cross_jurisdictional_fl_tee_dpc.json"
    card = json.loads(card_path.read_text())
    card.pop("risk_calibration", None)
    result = evaluate_card(card, REPO_ROOT)
    fired = {f["id"] for f in result["findings"]}
    assert "RISKCAL-001" in fired, "RISKCAL-001 should fire when risk_calibration is absent"
