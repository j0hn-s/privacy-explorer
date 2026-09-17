# `workbench/backend/` — FastAPI service

The backend half of the workbench. Imports the canonical YAPS engine
directly from `/repo/yaps/engine/risk_engine.py`; persists cards in
Elasticsearch; serves a server-rendered Jinja UI with HTMX + Alpine.js
for the small amount of client-side interactivity.

> See [../README.md](../README.md) for setup. This README is implementation
> detail for contributors.

## Layout

```
backend/
├── Dockerfile
├── pyproject.toml
├── README.md                  # this file
└── app/
    ├── __init__.py
    ├── main.py                # FastAPI entrypoint + page routes
    ├── data_loader.py         # /repo/data/*.yaml (mtime-cached)
    ├── schema_loader.py       # JSON Schema validation
    ├── engine_adapter.py      # imports yaps.engine.risk_engine
    ├── es_client.py           # async Elasticsearch CRUD + index mgmt
    ├── routes/
    │   ├── reference.py       # GET /api/reference/{key}
    │   ├── cards.py           # CRUD /api/cards/...
    │   ├── evaluate.py        # POST /api/evaluate/{id} + /ingest-eval
    │   ├── rules.py           # GET /api/rules/
    │   └── search.py          # GET /api/search/?q=
    ├── templates/             # Jinja2 — base, index, card_list, card_editor, evaluation, reference_browser
    └── static/                # CSS + JS (Alpine + HTMX loaded from CDN)
```

## API surface (MVP)

| Endpoint | Purpose |
|---|---|
| `GET  /health` | Backend version + ES reachability |
| `GET  /api/reference/` | Enumerate T0–T4 keys |
| `GET  /api/reference/{key}` | Return parsed YAML for one of the reference files |
| `GET  /api/cards/` | List cards (optional `?sector=`) |
| `GET  /api/cards/{id}` | Fetch a card |
| `POST /api/cards/` | Save / upsert a card (schema-validated) |
| `DELETE /api/cards/{id}` | Delete a card |
| `GET  /api/cards/{id}/versions` | Card version history from `card-versions-v1` |
| `POST /api/evaluate/` | Evaluate an inline card (no persistence) |
| `POST /api/evaluate/{id}` | Evaluate a saved card; persists evaluation + findings_summary |
| `POST /api/evaluate/{id}/ingest-eval` | Ingest a privacy-eval result into the card's `risk_calibration.attack_target` |
| `GET  /api/rules/` | Return the current rule set from `yaps/rules/rules.yaml` |
| `GET  /api/search/?q=` | Free-text search across saved cards |

## Engine import pattern

```python
# engine_adapter.py
sys.path.insert(0, str(repo_root / "yaps" / "engine"))
from risk_engine import evaluate_rule, build_report, _overall_rating
```

This is a deliberate choice over subprocess execution:
- Identical semantics to the CLI (`python yaps/engine/risk_engine.py …`).
- Single source of truth — any refactor of the engine is caught at import.
- Cheap enough to re-import on demand if hot-reload is desired.

The trade-off: the engine evaluates rule `condition_logic` strings via
Python `eval()` against a restricted namespace defined in
`risk_engine._build_eval_context()`. The backend inherits this posture —
do not import untrusted external rule sets. See [`../limitations.md`](../limitations.md).

## Extending

### Add a new API route

1. Add a module under `app/routes/`.
2. Add an `APIRouter()` and the endpoint functions.
3. `app.include_router(...)` in `app/main.py` with the desired prefix.
4. If the route needs ES, use `request.app.state.es`. If it needs the repo
   root, use `request.app.state.repo_root`.

### Add a new accessor or rule

This is canonical-side work — edit `yaps/engine/risk_engine.py` and
`yaps/rules/rules.yaml`. The workbench picks up rule changes on each
evaluation request; engine changes require a backend restart (or running
uvicorn with `--reload` in development).

### Add a new index

1. Add the mapping in `app/es_client.py::INDICES`.
2. `ensure_indices` will create it on next startup.
3. Add helper methods on `ElasticsearchClient` as needed.

## Tests

Lightweight pytest suite under `../tests/`. The runtime tests require a
running Elasticsearch; for unit-level checks, see `tests/test_smoke.py` which
exercises the imports and the engine adapter against an in-memory card.

```bash
# Inside the running compose stack:
docker-compose exec backend pytest -q
```

## Health and versioning

`/health` returns `{"ok": true|false, "version": "0.1.0-wip", "status": "wip", "elasticsearch": "ok"|"unreachable"}`.
Use this as the docker-compose healthcheck target and as a workshop diagnostic.
