# `workbench/limitations.md` — what this sandbox is not

The workbench is **research scaffolding for local workshop use**. This file
records the explicit limitations of the current build so contributors and
workshop facilitators can plan accordingly. Mirrors the pattern in
[`privacy-eval/limitations.txt`](../privacy-eval/limitations.txt).

## Security posture

- **No authentication.** The web UI is open to anyone on `localhost`.
- **No multi-user isolation.** All cards saved by anyone using the local
  workbench are visible to everyone else using the same instance.
- **No TLS.** HTTP only on `localhost:8000`.
- **Elasticsearch security disabled.** ES exposed on `localhost:9200` with
  `xpack.security.enabled=false`. Do **not** bind to a public interface.
- **Rule expressions evaluated via Python `eval()`.** The canonical YAPS
  engine does the same; the workbench inherits the posture. The eval context
  is restricted to the helpers in `risk_engine._build_eval_context()` and a
  small number of built-ins (`len`, `True`, `False`). It is not hardened
  against adversarial rule files. Treat the host's `yaps/rules/rules.yaml`
  as trusted; do not import unreviewed external rule sets through the UI.

## Operational posture

- **Single-node Elasticsearch.** 512 MB heap pinned for laptop fit.
- **Volume persistence only.** The compose volume `es-data` persists between
  `docker-compose down` and `up`. Anything beyond that (backups, cross-host
  migration) is out of scope.
- **No accessibility audit.** The UI has not been tested with assistive
  technology. Workshop participants should be told the workbench is one of
  several surfaces (single-file frontend, CLI engine, raw JSON) and offered
  alternatives if needed.
- **No internationalisation.** UK English only.
- **No observability beyond logs.** Backend logs to stdout; ES has the usual
  internal logging. No metrics, no traces.

## Functional gaps (deliberate, for MVP)

- **No stepwise-chain visual editor.** The chain is edited as nested JSON
  fields in the card form. A drag-reorder visual editor is named as a stretch
  feature; deferred until workshop feedback justifies it.
- **No side-by-side card diff UI.** The `card-versions-v1` index stores every
  save; viewing a diff requires querying ES directly for now.
- **No rule-set fork UI.** A rule-set fork is feasible (ES has a `rulesets-v1`
  index reserved) but the MVP uses the canonical rules at
  [`../yaps/rules/rules.yaml`](../yaps/rules/rules.yaml).
- **No Kibana.** Commented stretch service in `docker-compose.yml`.
- **No live deployment scaffolding.** Caddy / reverse-proxy / ES auth /
  multi-user separation are all post-workshop concerns.

## What schema versions are supported

- **1.0** — read/eval only (legacy cards from before the framework reframing).
- **1.1** — full support: stepwise_chain, exposure_problem_refs, jurisdictional_context.
- **1.2** — full support including the new `risk_calibration` block (μ-DP,
  attack_target, conversion_regret, trade_off_curve_ref, operational_interpretation).
  Privacy-eval ingestion targets schema 1.2 cards.

## When to look elsewhere

- **Drive-by readers / first-time users.** [`yaps/frontend/index.html`](../yaps/frontend/index.html)
  is a single-file sandbox — open in a browser, no server. Faster path to a
  first card.
- **CI / scripted evaluation.** The CLI engine
  [`python yaps/engine/risk_engine.py <card.json>`](../yaps/engine/risk_engine.py)
  is the canonical interface. Workbench is a wrapper, not a replacement.
- **Bulk attack runs / benchmarking.** [`privacy-eval/`](../privacy-eval/) is
  the framework's empirical attack harness. Workbench ingests its results;
  it does not run the attacks itself.

## Live deployment

A future "deployment" iteration (post-workshop, several months out) would
need to address all of the items in the *Security posture* and *Operational
posture* sections above — at minimum: auth, TLS, ES security, multi-user
isolation, rule-expression sandboxing, observability, backups.

The current build is deliberately scoped well short of that.
