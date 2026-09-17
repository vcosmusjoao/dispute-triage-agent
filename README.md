# Dispute Triage Agent

A FastAPI + LangGraph + Claude service that takes a card **dispute** and recommends
whether the merchant should **fight or accept** it — with a confidence score, a
plain-English rationale, and (in a later milestone) a drafted representment
(rebuttal) letter.

Domain: card chargebacks. All sample data is synthetic — see [docs/decisions.md](docs/decisions.md) (ADR-005).

Design docs: [docs/architecture.md](docs/architecture.md), [docs/decisions.md](docs/decisions.md).

## Setup

```bash
uv sync
cp .env.example .env  # then fill in ANTHROPIC_API_KEY
```

## Run

```bash
uv run uvicorn app.main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

## Test

```bash
uv run pytest
```

## Status

Milestone 0 — project scaffolding, data contracts, and sample disputes. The
LangGraph agent (classify → assess → decide → draft) lands in later milestones.
