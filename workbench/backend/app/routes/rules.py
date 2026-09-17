"""GET the canonical rule set."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.data_loader import load_rules

router = APIRouter()


@router.get("/")
async def get_rules(request: Request) -> dict:
    rules = load_rules(request.app.state.repo_root)
    return {"rules": rules, "count": len(rules)}
