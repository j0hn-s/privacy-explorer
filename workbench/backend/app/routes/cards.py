"""Card CRUD against Elasticsearch."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.schema_loader import validate_card

router = APIRouter()


@router.get("/")
async def list_cards(request: Request, sector: str | None = None, size: int = 100):
    es = request.app.state.es
    return await es.list_cards(size=size, filter_sector=sector)


@router.get("/{card_id}")
async def get_card(request: Request, card_id: str):
    es = request.app.state.es
    card = await es.get_card(card_id)
    if card is None:
        raise HTTPException(404, f"Card not found: {card_id}")
    return card


@router.post("/")
async def save_card(request: Request, card: dict):
    if "card_id" not in card:
        raise HTTPException(400, "card_id is required")
    errors = validate_card(card, request.app.state.repo_root)
    if errors:
        raise HTTPException(422, {"validation_errors": errors})
    es = request.app.state.es
    summary = await es.save_card(card)
    return summary


@router.delete("/{card_id}")
async def delete_card(request: Request, card_id: str):
    es = request.app.state.es
    ok = await es.delete_card(card_id)
    if not ok:
        raise HTTPException(404, f"Card not found: {card_id}")
    return {"deleted": card_id}


@router.get("/{card_id}/versions")
async def list_card_versions(request: Request, card_id: str):
    es = request.app.state.es
    return await es.list_card_versions(card_id)
