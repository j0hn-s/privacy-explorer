"""Thin async wrapper around the Elasticsearch client.

Indices managed:
- cards-v1            : authoritative current card per card_id
- card-versions-v1    : append-only version history (one doc per save)
- evaluations-v1      : append-only evaluation runs (card snapshot + findings)

Index mappings are deliberately loose for the schema-evolving fields and
explicit for query-relevant fields. Schema 1.0 / 1.1 / 1.2 cards all index
under the same mapping.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError

logger = logging.getLogger("workbench.es")


CARDS_INDEX = "cards-v1"
CARD_VERSIONS_INDEX = "card-versions-v1"
EVALUATIONS_INDEX = "evaluations-v1"


CARDS_MAPPING = {
    "mappings": {
        "dynamic": "true",
        "properties": {
            "card_id": {"type": "keyword"},
            "schema_version": {"type": "keyword"},
            "title": {"type": "text"},
            "status": {"type": "keyword"},
            "last_updated": {"type": "date", "ignore_malformed": True},
            "deployment_context": {
                "properties": {
                    "sector_ref": {"type": "keyword"},
                    "scale": {"type": "keyword"},
                }
            },
            "primitive_ids": {"type": "keyword"},                # materialised on save
            "findings_summary": {
                "properties": {
                    "rating": {"type": "keyword"},
                    "red": {"type": "integer"},
                    "amber": {"type": "integer"},
                    "green": {"type": "integer"},
                    "info": {"type": "integer"},
                    "evaluated_at": {"type": "date"},
                }
            },
            "exposure_problem_refs": {"type": "keyword"},
        },
    }
}


CARD_VERSIONS_MAPPING = {
    "mappings": {
        "dynamic": "true",
        "properties": {
            "card_id": {"type": "keyword"},
            "saved_at": {"type": "date"},
            "schema_version": {"type": "keyword"},
        },
    }
}


EVALUATIONS_MAPPING = {
    "mappings": {
        "dynamic": "true",
        "properties": {
            "card_id": {"type": "keyword"},
            "evaluated_at": {"type": "date"},
            "rating": {"type": "keyword"},
            "rules_count": {"type": "integer"},
        },
    }
}


INDICES = {
    CARDS_INDEX: CARDS_MAPPING,
    CARD_VERSIONS_INDEX: CARD_VERSIONS_MAPPING,
    EVALUATIONS_INDEX: EVALUATIONS_MAPPING,
}


def _materialise_primitive_ids(card: dict) -> list[str]:
    return [c.get("primitive_id") for c in (card.get("pet_components") or []) if c.get("primitive_id")]


class ElasticsearchClient:
    def __init__(self, url: str):
        self.url = url
        self._es: AsyncElasticsearch | None = None

    def _client(self) -> AsyncElasticsearch:
        if self._es is None:
            self._es = AsyncElasticsearch(self.url, request_timeout=10)
        return self._es

    async def wait_for_ready(self, timeout_s: int = 60) -> None:
        es = self._client()
        deadline = asyncio.get_event_loop().time() + timeout_s
        while True:
            try:
                if await es.ping():
                    return
            except Exception:  # noqa: BLE001
                pass
            if asyncio.get_event_loop().time() > deadline:
                raise RuntimeError(f"Elasticsearch at {self.url} did not become ready within {timeout_s}s")
            await asyncio.sleep(1)

    async def ping(self) -> bool:
        try:
            return await self._client().ping()
        except Exception:  # noqa: BLE001
            return False

    async def close(self) -> None:
        if self._es is not None:
            await self._es.close()

    async def ensure_indices(self) -> None:
        es = self._client()
        for name, body in INDICES.items():
            exists = await es.indices.exists(index=name)
            if not exists:
                logger.info("Creating index %s", name)
                await es.indices.create(index=name, body=body)

    async def seed_examples_if_empty(self, examples_dir: Path) -> int:
        """If cards-v1 is empty, bulk-load every *.json from examples_dir."""
        es = self._client()
        count_resp = await es.count(index=CARDS_INDEX)
        if count_resp.get("count", 0) > 0:
            return 0
        if not examples_dir.exists():
            logger.warning("Examples directory not found: %s", examples_dir)
            return 0
        seeded = 0
        for path in sorted(examples_dir.glob("*.json")):
            try:
                card = json.loads(path.read_text())
            except json.JSONDecodeError as exc:
                logger.warning("Skipping %s — invalid JSON: %s", path, exc)
                continue
            card_id = card.get("card_id")
            if not card_id:
                logger.warning("Skipping %s — missing card_id", path)
                continue
            card.setdefault("schema_version", "1.0")
            card.setdefault("primitive_ids", _materialise_primitive_ids(card))
            await es.index(index=CARDS_INDEX, id=card_id, document=card)
            seeded += 1
        if seeded:
            await es.indices.refresh(index=CARDS_INDEX)
        return seeded

    async def get_card(self, card_id: str) -> dict | None:
        es = self._client()
        try:
            resp = await es.get(index=CARDS_INDEX, id=card_id)
        except NotFoundError:
            return None
        return resp["_source"]

    async def list_cards(self, size: int = 100, filter_sector: str | None = None) -> list[dict]:
        es = self._client()
        body: dict[str, Any] = {"size": size, "sort": [{"last_updated": {"order": "desc", "missing": "_last"}}]}
        if filter_sector:
            body["query"] = {"term": {"deployment_context.sector_ref": filter_sector}}
        resp = await es.search(index=CARDS_INDEX, body=body)
        return [hit["_source"] for hit in resp["hits"]["hits"]]

    async def save_card(self, card: dict, evaluation_summary: dict | None = None) -> dict:
        es = self._client()
        card_id = card.get("card_id")
        if not card_id:
            raise ValueError("card_id is required")
        # Materialise query-helpful fields.
        card = dict(card)
        card["primitive_ids"] = _materialise_primitive_ids(card)
        if evaluation_summary:
            card["findings_summary"] = evaluation_summary
        # Append a version record before overwriting cards-v1.
        version_doc = dict(card)
        version_doc["card_id"] = card_id
        version_doc["saved_at"] = _now_iso()
        await es.index(index=CARD_VERSIONS_INDEX, document=version_doc)
        await es.index(index=CARDS_INDEX, id=card_id, document=card)
        await es.indices.refresh(index=CARDS_INDEX)
        return {"card_id": card_id, "saved_at": version_doc["saved_at"]}

    async def delete_card(self, card_id: str) -> bool:
        es = self._client()
        try:
            await es.delete(index=CARDS_INDEX, id=card_id)
            return True
        except NotFoundError:
            return False

    async def list_card_versions(self, card_id: str, size: int = 50) -> list[dict]:
        es = self._client()
        resp = await es.search(
            index=CARD_VERSIONS_INDEX,
            body={
                "size": size,
                "sort": [{"saved_at": {"order": "desc"}}],
                "query": {"term": {"card_id": card_id}},
            },
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]

    async def record_evaluation(self, card_id: str, evaluation: dict) -> None:
        es = self._client()
        await es.index(
            index=EVALUATIONS_INDEX,
            document={
                "card_id": card_id,
                "evaluated_at": _now_iso(),
                "rating": evaluation.get("rating"),
                "rules_count": evaluation.get("rules_count"),
                "findings": evaluation.get("findings", []),
                "errors": evaluation.get("errors", []),
            },
        )

    async def search_cards(self, query: str, size: int = 25) -> list[dict]:
        es = self._client()
        resp = await es.search(
            index=CARDS_INDEX,
            body={
                "size": size,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["card_id^2", "title^2", "description", "primitive_ids"],
                    }
                },
            },
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
