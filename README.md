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

Hermetic — the Claude client is mocked, so this never hits the network.

## Eval

```bash
uv run python -m eval.run
```

Not a pytest test: it makes real Claude calls (~20 for the 10-case set), so
it costs a little and isn't run automatically. Use it after touching a
prompt, the assess/decide policy, or the reason-code data, to check the
agent didn't regress. Clear-cut cases are asserted; ambiguous cases print
their reasoning for you to read.

## Status

Milestone 3 — the agent graph (classify → assess → decide → draft) is live:
`classify` and `assess` reason with Claude (structured output, with a
deterministic fallback if the call fails); `decide` is a transparent policy
over `assess`'s win-probability estimate; `draft` is still a stub
(Milestone 4). See [docs/conceitos.md](docs/conceitos.md) for a running
concept-by-concept study log of how this was built.
