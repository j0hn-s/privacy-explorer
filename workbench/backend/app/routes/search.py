"""Free-text search across saved cards."""

from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
async def search_cards(request: Request, q: str, size: int = 25):
    es = request.app.state.es
    return await es.search_cards(q, size=size)
