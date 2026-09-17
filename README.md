# Dispute Triage Agent

A FastAPI + LangGraph + Claude service that takes a card **dispute** and recommends
whether the merchant should **fight or accept** it — with a confidence score, a
plain-English rationale, and, when it recommends fighting, a drafted representment
(rebuttal) letter. A thin Next.js frontend lets you demo the whole thing in a browser.

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

## Run the frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # defaults to the local API above
npm run dev
```

Open http://localhost:3000 — pick a sample dispute (or paste your own JSON) and hit
"Analyze dispute". Use `localhost`, not `127.0.0.1`: Next.js's dev server blocks its
own hot-reload/client assets from an origin it doesn't recognize as itself, and the
page will render but never come alive if you open it via the IP.

## Test

```bash
uv run pytest
```

Hermetic — the Claude client is mocked, so this never hits the network.

## Eval

```bash
uv run python -m eval.run
```

Not a pytest test: it makes real Claude calls (2 per case, plus a 3rd —
drafting the letter — for every "fight" case), so it costs a little and
isn't run automatically. Use it after touching a prompt, the assess/decide
policy, or the reason-code data, to check the agent didn't regress.
Clear-cut cases are asserted; ambiguous cases print their reasoning for you
to read; every fight case is also checked against the dispute's real
evidence, to catch the drafted letter citing something the merchant
doesn't actually have.

## Status

v1 functional scope is complete: the full agent graph (classify → assess →
decide → draft) runs end to end against the real Claude API, and the
Next.js frontend demos it in a browser. `classify`, `assess`, and `draft`
all reason with Claude (structured output, with a deterministic fallback
if the call fails); `decide` is a transparent policy over `assess`'s
win-probability estimate. See [docs/conceitos.md](docs/conceitos.md) for a
running concept-by-concept study log of how this was built.
