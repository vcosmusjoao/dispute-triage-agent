import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.agent.graph import dispute_graph
from app.data.samples import SAMPLE_DISPUTES
from app.models import Dispute, Verdict

app = FastAPI(title="Dispute Triage Agent")

app.add_middleware(
    CORSMiddleware,
    # The Next.js demo (Milestone 5) calls this API from a different origin.
    # Comma-separated so a deployed frontend's URL can be added via env var
    # without touching code. Both localhost and 127.0.0.1 are listed by
    # default since a browser treats them as different origins even when
    # they're the same machine.
    allow_origins=os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# /disputes/analyze is the only endpoint that costs real money (it calls
# Claude 2-3 times), so it's the only one worth capping. Once deployed
# publicly with no auth, this is what stands between a bot/crawler and an
# unbounded Anthropic bill - see architecture.md §7.
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
ANALYZE_RATE_LIMIT = os.getenv("ANALYZE_RATE_LIMIT", "10/minute")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/disputes/samples")
def list_samples() -> list[Dispute]:
    """Synthetic sample disputes for the frontend's dispute picker - same
    source of truth as the eval harness and tests, so front and backend
    can't drift apart on what a "sample" looks like.
    """
    return SAMPLE_DISPUTES


@app.post("/disputes/analyze")
@limiter.limit(ANALYZE_RATE_LIMIT)
def analyze(request: Request, dispute: Dispute) -> Verdict:
    final_state = dispute_graph.invoke({"dispute": dispute})
    return Verdict(
        recommendation=final_state["recommendation"],
        confidence=final_state["confidence"],
        reason_code_meaning=final_state["reason_code_meaning"],
        why=final_state["why"],
        required_evidence=final_state["required_evidence"],
        draft_rebuttal=final_state.get("draft_rebuttal"),
    )
