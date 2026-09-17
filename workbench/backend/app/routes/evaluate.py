"""Evaluate a card against the canonical YAPS rule set.

Two endpoints:
- POST /api/evaluate/         — evaluate an inline card JSON; no persistence.
- POST /api/evaluate/{id}      — evaluate the stored card with that id; persists
                                an evaluation record and updates findings_summary.

Plus the privacy-eval ingestion endpoint:
- POST /api/evaluate/{id}/ingest-eval — accept a privacy-eval/results/*.json
                                          record and populate the card's
                                          risk_calibration.attack_target.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from app.engine_adapter import evaluate_card

router = APIRouter()


def _findings_summary(rating: str, findings: list[dict]) -> dict:
    by_sev = {"RED": 0, "AMBER": 0, "GREEN": 0, "INFO": 0}
    for f in findings:
        sev = f.get("severity")
        if sev in by_sev:
            by_sev[sev] += 1
    return {
        "rating": rating,
        "red": by_sev["RED"],
        "amber": by_sev["AMBER"],
        "green": by_sev["GREEN"],
        "info": by_sev["INFO"],
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/")
async def evaluate_inline(request: Request, card: dict):
    """Evaluate an inline card without saving it."""
    result = evaluate_card(card, request.app.state.repo_root)
    return result


@router.post("/{card_id}")
async def evaluate_stored(request: Request, card_id: str):
    es = request.app.state.es
    card = await es.get_card(card_id)
    if card is None:
        raise HTTPException(404, f"Card not found: {card_id}")
    result = evaluate_card(card, request.app.state.repo_root)
    summary = _findings_summary(result["rating"], result["findings"])
    # Persist the evaluation and update the card's findings_summary.
    await es.record_evaluation(card_id, {**result, **summary})
    await es.save_card(card, evaluation_summary=summary)
    return result


@router.post("/{card_id}/ingest-eval")
async def ingest_eval_result(request: Request, card_id: str, eval_record: dict):
    """Ingest a privacy-eval result record and populate the card's
    risk_calibration.attack_target with the measured advantage.

    Expected shape (matches privacy-eval/results/.../*.json):
        {
          "attack_tag": "A" | "B" | "C",
          "attack_variant": "...",
          "primary_metric": {
            "name": "worst_record_tpr_at_fpr_0.001" | "auc_full_output" | ...,
            "value": <float>,
            ...
          },
          "secondary_metrics": [...],
          "bridge": {...}
        }
    """
    es = request.app.state.es
    card = await es.get_card(card_id)
    if card is None:
        raise HTTPException(404, f"Card not found: {card_id}")

    primary = eval_record.get("primary_metric") or {}
    metric_name = primary.get("name") or "unknown"
    metric_value = primary.get("value")

    # Map the privacy-eval attack_tag onto the risk_calibration attack vocabulary.
    tag_to_attack = {"A": "MIA", "B": "reconstruction", "C": "singling-out"}
    attack = tag_to_attack.get(eval_record.get("attack_tag"), "MIA")

    rc = card.get("risk_calibration") or {}
    attack_target = rc.get("attack_target") or {}
    attack_target.update({
        "attack": attack,
        "measured_advantage": metric_value,
        "evidence_ref": eval_record.get("bridge", {}).get("path") or f"primary_metric:{metric_name}",
    })
    rc["attack_target"] = attack_target
    rc.setdefault("source_library", "riskcal")
    rc.setdefault("operational_interpretation",
                  f"Empirical {attack} measurement of {metric_name} = {metric_value} ingested from privacy-eval.")
    card["risk_calibration"] = rc

    # Bump schema_version to 1.2 if the card was lower — risk_calibration
    # only applies from 1.2 onwards. Conservative: only promote, never demote.
    if card.get("schema_version") in (None, "1.0", "1.1"):
        card["schema_version"] = "1.2"

    summary = await es.save_card(card)
    return {
        "card_id": card_id,
        "updated_field": "risk_calibration.attack_target",
        "ingested_metric": {"name": metric_name, "value": metric_value, "attack": attack},
        "saved_at": summary.get("saved_at"),
    }
