# `workbench/` — local sandbox for the privacy-explorer framework

> **WIP — research scaffolding, not production.** This component is intended for
> local-only workshop use. It has no authentication, no multi-user isolation,
> no TLS, and executes rule expressions via Python `eval()`. See
> [`limitations.md`](limitations.md) for the full list of what this is not.

A persistent local sandbox for working with the privacy-explorer framework —
authoring [Privacy Cards](../yaps/CARDS_GUIDE.md), running them through the
[YAPS rule engine](../yaps/engine/risk_engine.py), browsing the T0–T4
reference materials, and ingesting empirical results from
[`privacy-eval/`](../privacy-eval/) into a card's `risk_calibration` block.
Backed by Elasticsearch so cards are version-tracked and searchable across
a workshop session.

Sibling to [`/yaps/`](../yaps/). Consumes the canonical YAML reference data,
JSON schemas, and rule set as read-only sources; ES is the only thing that
gets written to.

## Quick start

Requires Docker + docker-compose. From this directory:

```bash
cp .env.example .env             # local-only defaults are fine
docker-compose up                # ES on :9200, backend on :8000
```

Then open <http://localhost:8000>.

First-time startup takes ~30s for Elasticsearch + ~10s for the backend.
On first boot the backend seeds the `cards-v1` index with the four
example cards from [`../yaps/cards/examples/`](../yaps/cards/examples/).

## What it does

1. **Browses T0–T4 reference data** in a sidebar — primitives, pairings, stacks,
   sectors, exposure problems. Read live from
   [`../data/*.yaml`](../data/) on each request; if you edit a YAML file on
   the host, the next reference-browser refresh sees the change.
2. **Creates / edits Privacy Cards** via a form derived from
   [`privacy_card.schema.json`](../yaps/schemas/privacy_card.schema.json).
   Supports schema 1.0, 1.1, and 1.2 — including the schema 1.2
   `risk_calibration` block (μ-DP, attack target, conversion regret,
   trade-off curve reference).
3. **Saves cards to Elasticsearch with auto-versioning.** Every save
   appends a new document to `card-versions-v1`; the active card lives in
   `cards-v1` keyed by `card_id`.
4. **Evaluates cards against the YAPS rule set.** The workbench imports
   `risk_engine` directly from [`../yaps/engine/`](../yaps/engine/) — same
   semantics as `python yaps/engine/risk_engine.py <card.json>`. Findings
   and the full Markdown risk report are rendered inline.
5. **Hot-reloads rules.** Edit [`../yaps/rules/rules.yaml`](../yaps/rules/rules.yaml)
   on the host; the next *Evaluate* click sees the change without restart.
6. **Lists / searches saved cards** by sector, primitive, rating, schema version.
7. **Imports / exports card JSON.** Drag-and-drop a card JSON to load; export
   any card back to JSON for inclusion in the repository or sharing.
8. **Ingests `privacy-eval/results/...json` records.** Drop in a per-record MIA
   sweep result (or any empirical result file with a `primary_metric` block);
   the workbench parses it and populates the target card's
   `risk_calibration.attack_target.measured_advantage` and `evidence_ref`,
   then re-evaluates. Closes the empirical ↔ assurance loop within a single
   workshop session.

## What it explicitly is *not*

Listed in full in [`limitations.md`](limitations.md). Headline items:

- **Not multi-user.** No authentication, no per-user data isolation. Everything
  in ES is shared across whoever opens the URL on the local host.
- **Not network-secure.** ES is exposed on :9200 with security disabled.
  Do not bind to public interfaces. Local-only.
- **Not sandboxed for rule code.** Rule `condition_logic` strings are evaluated
  via Python `eval()` (matching the canonical engine). The eval context is
  restricted but not hardened against adversarial rule files.
- **Not production-grade ES.** Single-node, 512MB heap, no backups beyond the
  compose volume.
- **Not a replacement for [`yaps/frontend/index.html`](../yaps/frontend/index.html)**.
  The single-file frontend stays as the "open in a browser, no server" forkability
  artefact — they coexist and serve different audiences. The workbench is for
  workshop participants who need persistence and multi-card workflows; the
  single-file frontend is for drive-by readers and quick demos.

## How it relates to the rest of the repo

```
privacy-explorer/
├── data/                       # T0–T4 YAML — read-only consumed by workbench
├── yaps/
│   ├── engine/risk_engine.py   # imported directly by workbench/backend
│   ├── rules/rules.yaml        # read at request time (hot-reload)
│   ├── schemas/                # JSON Schema validation in workbench
│   ├── cards/examples/         # seeded into ES on first boot
│   └── frontend/index.html     # untouched; complementary surface
├── privacy-eval/results/       # result records ingested into card risk_calibration
└── workbench/                  # THIS COMPONENT
    ├── docker-compose.yml
    └── backend/                # FastAPI + Jinja + HTMX
```

The workbench owns no canonical data. It is a tool for using the framework,
not part of the framework itself. Removing the directory leaves the rest of
the repository functioning identically.

## Development

For implementation detail, API surface, and how to extend the backend, see
[`backend/README.md`](backend/README.md).

For the planning context that produced this component, see the design
decisions section of the relevant pull request — schema 1.2 `risk_calibration`
block and the workbench were planned together to close the empirical ↔
assurance loop in the workshop demo.
