from fastapi import FastAPI

from app.models import Dispute, Verdict
from app.rules import evaluate

app = FastAPI(title="Dispute Triage Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/disputes/analyze")
def analyze(dispute: Dispute) -> Verdict:
    return evaluate(dispute)
