"""Adapter that calls the canonical YAPS risk engine via direct Python import.

The repo is mounted at /repo:ro inside the container; the engine source lives
at /repo/yaps/engine/risk_engine.py. We add it to sys.path and import the
functions we need. No subprocess overhead, no JSON-via-stdout fragility.

This module deliberately does not re-implement engine semantics. Any change to
the canonical engine is picked up next time this module is reloaded — which
for FastAPI in development means at process restart. To get true hot-reload of
the engine source, run uvicorn with --reload (not the default in compose).

Rules are re-read from disk on every evaluation request (cheap) so workshop
participants can edit yaps/rules/rules.yaml on the host and see findings
change without restarting.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

from app.data_loader import load_rules


def _ensure_engine_on_path(repo_root: Path) -> Any:
    """Import (or re-import) risk_engine from /repo/yaps/engine/.

    Returns the imported module. Safe to call repeatedly.
    """
    engine_dir = str(repo_root / "yaps" / "engine")
    if engine_dir not in sys.path:
        sys.path.insert(0, engine_dir)
    if "risk_engine" in sys.modules:
        return sys.modules["risk_engine"]
    return importlib.import_module("risk_engine")


def evaluate_card(card: dict, repo_root: Path) -> dict:
    """Evaluate a card against the canonical rule set.

    Returns:
        {
            "findings": [ {id, name, severity, finding, references}, ... ],
            "rating": "RED" | "AMBER" | "GREEN" | "INFO",
            "report_md": "<full Markdown risk report>",
            "errors": [ "rule evaluation error strings", ... ],
            "rules_count": <int>,
        }
    """
    engine = _ensure_engine_on_path(repo_root)
    rules = load_rules(repo_root)

    findings: list[dict] = []
    errors: list[str] = []
    for rule in rules:
        triggered, err = engine.evaluate_rule(rule, card)
        if err:
            errors.append(f"{rule.get('id', '?')}: {err}")
            continue
        if triggered:
            findings.append({
                "id": rule.get("id"),
                "name": rule.get("name"),
                "severity": rule.get("severity"),
                "category": rule.get("category"),
                "finding": rule.get("finding"),
                "references": rule.get("references") or [],
            })

    rating = engine._overall_rating(findings)
    report_md = engine.build_report(card, rules, findings, errors)

    return {
        "findings": findings,
        "rating": rating,
        "report_md": report_md,
        "errors": errors,
        "rules_count": len(rules),
    }
