"""FastAPI entrypoint for the workbench backend.

The app mounts:
- API routers under /api/* for reference data, cards, rules, evaluate, search,
  and privacy-eval result ingestion.
- Jinja-rendered pages at /, /cards/{id}, /reference, etc.

On startup it:
- Connects to Elasticsearch and ensures the required indices exist.
- Seeds the cards-v1 index with the example cards from
  ../yaps/cards/examples/ if the index is empty.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import __version__
from app.es_client import ElasticsearchClient
from app.routes import cards, evaluate, reference, rules, search

logger = logging.getLogger("workbench")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")

REPO_ROOT = Path(os.environ.get("REPO_ROOT", "/repo"))
ES_URL = os.environ.get("ES_URL", "http://localhost:9200")
WORKBENCH_VERSION = os.environ.get("WORKBENCH_VERSION", __version__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connect to ES, ensure indices, seed if empty."""
    es = ElasticsearchClient(ES_URL)
    await es.wait_for_ready()
    await es.ensure_indices()
    seeded = await es.seed_examples_if_empty(REPO_ROOT / "yaps" / "cards" / "examples")
    if seeded:
        logger.info("Seeded %d example cards into cards-v1.", seeded)
    app.state.es = es
    app.state.repo_root = REPO_ROOT
    app.state.version = WORKBENCH_VERSION
    logger.info("Workbench %s ready. Repo mounted at %s.", WORKBENCH_VERSION, REPO_ROOT)
    yield
    await es.close()


app = FastAPI(
    title="Privacy Explorer — Workbench",
    version=WORKBENCH_VERSION,
    description="WIP local sandbox. Research scaffolding, not production. See workbench/limitations.md.",
    lifespan=lifespan,
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.state.templates = templates

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# API routers
app.include_router(reference.router, prefix="/api/reference", tags=["reference"])
app.include_router(cards.router, prefix="/api/cards", tags=["cards"])
app.include_router(evaluate.router, prefix="/api/evaluate", tags=["evaluate"])
app.include_router(rules.router, prefix="/api/rules", tags=["rules"])
app.include_router(search.router, prefix="/api/search", tags=["search"])


@app.get("/health")
async def health(request: Request):
    """Health endpoint — also reports workbench state for debugging."""
    es = request.app.state.es
    es_ok = await es.ping()
    return JSONResponse({
        "ok": es_ok,
        "version": request.app.state.version,
        "status": "wip",
        "elasticsearch": "ok" if es_ok else "unreachable",
    })


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Landing page — links to card list, reference browser, evaluate."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "version": request.app.state.version,
    })


@app.get("/cards", response_class=HTMLResponse)
async def cards_list_page(request: Request):
    return templates.TemplateResponse("card_list.html", {
        "request": request,
        "version": request.app.state.version,
    })


@app.get("/cards/new", response_class=HTMLResponse)
async def card_new_page(request: Request):
    return templates.TemplateResponse("card_editor.html", {
        "request": request,
        "version": request.app.state.version,
        "card": None,
    })


@app.get("/cards/{card_id}", response_class=HTMLResponse)
async def card_view_page(request: Request, card_id: str):
    es = request.app.state.es
    card = await es.get_card(card_id)
    return templates.TemplateResponse("card_editor.html", {
        "request": request,
        "version": request.app.state.version,
        "card": card,
    })


@app.get("/cards/{card_id}/evaluate", response_class=HTMLResponse)
async def card_evaluate_page(request: Request, card_id: str):
    return templates.TemplateResponse("evaluation.html", {
        "request": request,
        "version": request.app.state.version,
        "card_id": card_id,
    })


@app.get("/reference", response_class=HTMLResponse)
async def reference_page(request: Request):
    return templates.TemplateResponse("reference_browser.html", {
        "request": request,
        "version": request.app.state.version,
    })
