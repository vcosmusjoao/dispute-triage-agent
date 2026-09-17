# Architecture — Dispute Triage Agent

## 1. System shape

A **stateless HTTP service**. One meaningful endpoint. No database in v1 (synthetic
in-memory sample disputes). The intelligence lives in a **LangGraph agent** invoked per request.

```
Client (React/Next demo, or Swagger UI, or curl)
        │  POST /disputes/analyze  { dispute JSON }
        ▼
FastAPI  ──►  LangGraph agent  ──►  Claude API (reasoning + drafting)
        ◄──  { verdict JSON }
```

**Angular bridge:** FastAPI ≈ NestJS — decorators define routes, Pydantic models are your
DTOs with runtime validation (like `class-validator`), and dependency injection works the same
way. If you know Nest, you already half-know FastAPI.

## 2. Stack & why

| Layer | Choice | One-line reason |
|-------|--------|-----------------|
| Language | **Python 3.12** | Matches the USD lead + AI-eng market. |
| API | **FastAPI** | Typed endpoints, auto-generated Swagger docs, async. |
| Agent | **LangGraph** | Multi-step *stateful* reasoning as a graph (see §4). |
| LLM | **Claude API** (`anthropic` SDK) | João knows it; strong structured output / tool use. |
| Validation | **Pydantic v2** | The data contracts (§3). Auto-validates request/response. |
| Tests | **pytest** | Standard. Test the graph nodes + the endpoint. |
| Package mgmt | **uv** (fallback: venv + pip) | Fast, modern; one tool for venv + deps. |
| Frontend (v1 stretch) | **Next.js (App Router) + TS + Tailwind** | João's comfort zone; the fullstack story. |
| Deploy — API | **Render** (free tier; fallback Railway) | Simple Python web-service deploy. |
| Deploy — Front | **Vercel** | Same as FinLivre; zero-config Next.js. |
| Secrets | **env vars** (`ANTHROPIC_API_KEY`) | Never commit keys. `.env` gitignored. |

## 3. Data contracts (Pydantic models)

These are the API's contract — lock them early; everything else builds on them.

### Input — `Dispute`
```python
class Transaction(BaseModel):
    amount: float
    currency: str                 # "USD", "BRL", ...
    date: datetime
    card_country: str             # ISO-2, e.g. "US"
    ip_country: str | None        # ISO-2, may be missing
    avs_match: bool | None        # address verification
    cvv_match: bool | None

class CustomerHistory(BaseModel):
    prior_purchases: int
    prior_chargebacks: int
    account_age_days: int

class EvidenceAvailable(BaseModel):
    proof_of_delivery: bool = False
    tracking_number: str | None = None
    terms_accepted: bool = False
    ip_logs: bool = False

class Dispute(BaseModel):
    dispute_id: str
    reason_code: str              # e.g. "13.1", "10.4"
    transaction: Transaction
    customer_history: CustomerHistory
    evidence_available: EvidenceAvailable
```

### Output — `Verdict`
```python
class Verdict(BaseModel):
    recommendation: Literal["fight", "accept"]
    confidence: float             # 0.0–1.0
    reason_code_meaning: str      # human-readable interpretation
    why: str                      # plain-English rationale
    required_evidence: list[str]  # what would win this
    draft_rebuttal: str | None    # the representment letter (None if accept)
```

## 4. The agent graph (LangGraph)

**Angular bridge:** LangGraph is basically **NgRx over a directed graph**. There's one shared
`state` object (the store). Each **node** is a function `(state) -> partial state update`
(a reducer). **Edges** decide which node runs next (like effects routing to the next action).
A **conditional edge** is a `switch` on the state. You already think in this shape from RxJS/NgRx.

```
        ┌─────────────┐
START ─►│  classify   │  interpret reason_code → category + what evidence wins
        └──────┬──────┘
               ▼
        ┌─────────────┐
        │   assess    │  reason over signals → win-probability + confidence
        └──────┬──────┘
               ▼
        ┌─────────────┐
        │   decide    │  fight vs accept + why + required_evidence
        └──────┬──────┘
               │  conditional edge:
        ┌──────┴───────────────┐
        │ recommendation==fight │ else
        ▼                       ▼
  ┌───────────┐              (END)
  │  draft    │  generate representment letter matched to reason_code
  └─────┬─────┘
        ▼
      (END)
```

- **State** carries the `Dispute`, intermediate findings, and the building `Verdict`.
- Nodes that need judgment call **Claude** with **structured output** (tool-use / JSON schema)
  so responses parse straight into Pydantic — no brittle string parsing.
- The **conditional edge** after `decide` skips drafting when we recommend *accept*
  (don't waste a letter on a dispute we're not fighting).

## 5. Where AI earns its place (defend this in interviews)

- A rules engine handles the easy signals (AVS mismatch + foreign IP → likely lose).
- The **LLM reasoning step** weighs *conflicting* signals (clean 380-day account vs. CVV
  mismatch vs. delivery proof) — judgment, not `if/else`.
- **Drafting the rebuttal** is language generation matched to domain rules — pure LLM job.
- That's why we start with a rules baseline (Milestone 1) and *upgrade* to the agent — so you
  can articulate exactly what the AI adds over the boring version.

## 6. Repository layout (target, in `C:\dev\dispute-triage-agent`)

```
dispute-triage-agent/
├── docs/                 # architecture.md + decisions.md copied here (Milestone 0)
├── app/
│   ├── main.py           # FastAPI app + /health + /disputes/analyze
│   ├── models.py         # Pydantic contracts (§3)
│   ├── agent/
│   │   ├── graph.py      # LangGraph wiring
│   │   ├── state.py      # graph state schema
│   │   └── nodes/        # classify.py, assess.py, decide.py, draft.py
│   └── data/samples.py   # synthetic sample disputes
├── tests/
├── frontend/             # Next.js demo (Milestone 5)
├── .env.example
├── pyproject.toml
└── README.md
```

## 7. Out of scope for v1 (name it, so scope stays honest)

- No real card-network / processor integration (no live RDR/Ethoca).
- No database / persistence (stateless; add only if a "case history" feature is wanted later).
- No auth (it's a demo; add an API key header only if deployed publicly and abused).
- No ML-trained win-probability model — the estimate is *reasoned*, not trained on labels.
