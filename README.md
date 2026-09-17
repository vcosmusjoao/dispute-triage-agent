# Dispute Triage Agent

A FastAPI + LangGraph + Claude service that takes a card **dispute** and recommends
whether the merchant should **fight or accept** it — with a confidence score, a
plain-English rationale, and, when it recommends fighting, a drafted representment
(rebuttal) letter. A thin Next.js frontend lets you demo the whole thing in a browser.

Domain: card chargebacks. All sample data is synthetic — see [docs/decisions.md](docs/decisions.md) (ADR-005).

Design docs: [docs/architecture.md](docs/architecture.md), [docs/decisions.md](docs/decisions.md).

## Pipeline

One dispute flows through a LangGraph agent, four nodes deep:

`classify` (interpret the reason code) → `assess` (weigh the merchant's actual signals against
each other) → `decide` (deterministic fight/accept policy over `assess`'s probability) → `draft`
(write the representment letter — only reached on "fight"). See the app's
[How It Works](frontend/src/app/how-it-works/page.tsx) page or
[docs/architecture.md](docs/architecture.md) for the full breakdown.

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

## Example

```bash
curl http://127.0.0.1:8000/disputes/samples | jq '.[0]' > dispute.json
curl -X POST http://127.0.0.1:8000/disputes/analyze \
  -H "Content-Type: application/json" -d @dispute.json
```

```json
{
  "recommendation": "fight",
  "confidence": 0.87,
  "reason_code_meaning": "Merchandise/services not received",
  "why": "Fight — estimated 87% chance of winning if contested. Strong delivery proof and a clean auth/history profile outweigh the claim.",
  "required_evidence": ["Proof of delivery", "Tracking number showing delivery", "Terms accepted at purchase"],
  "draft_rebuttal": "Re: Dispute DSP-1001 - Reason Code 13.1\n..."
}
```

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

## Config

| Env var | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | — (required) | Claude API access. |
| `FRONTEND_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | CORS allowlist, comma-separated. Add the deployed frontend's URL here. |
| `ANALYZE_RATE_LIMIT` | `10/minute` | Per-IP cap on `POST /disputes/analyze` — the only endpoint that spends real Claude credits. Exists so a public deployment can't be hit with an unbounded bill by a bot/crawler (no auth in v1, see `architecture.md` §7). |

## Deploy

**Backend (Render):** [render.yaml](render.yaml) is a Blueprint — on Render, "New +" →
"Blueprint" → connect this repo. It reads the file, sets up the build (`pip install .`)
and start (`uvicorn ... --host 0.0.0.0 --port $PORT`) commands, and prompts you for
`ANTHROPIC_API_KEY` (never stored in the repo). Deploy, then copy the resulting URL
(`https://<name>.onrender.com`).

**Frontend (Vercel):** import the repo, set the project **root directory to `frontend`**
(it's a subfolder, not the repo root), and set `NEXT_PUBLIC_API_URL` to the Render URL
from above. Deploy, then copy the resulting URL.

**Wire them together:** back on Render, add a `FRONTEND_ORIGINS` env var set to the
Vercel URL (comma-separate if you keep localhost too) and redeploy — until this is set,
the browser will block the frontend's requests as CORS violations, same as the
localhost-vs-127.0.0.1 mismatch during local dev.

Render's free tier spins the service down after inactivity; the first request after a
while sleeping takes ~30-50s to cold-start. Expected, not a bug.

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
