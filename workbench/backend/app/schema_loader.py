"""Load JSON Schemas for card validation."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


def load_card_schema(repo_root: Path) -> dict:
    path = repo_root / "yaps" / "schemas" / "privacy_card.schema.json"
    if not path.exists():
        raise FileNotFoundError(f"Card schema not found: {path}")
    return json.loads(path.read_text())


def validate_card(card: dict, repo_root: Path) -> list[str]:
    """Validate a card against the current schema. Returns a list of error
    strings — empty list if the card validates."""
    schema = load_card_schema(repo_root)
    validator = Draft202012Validator(schema)
    errors = []
    for err in validator.iter_errors(card):
        path = ".".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"{path}: {err.message}")
    return errors
