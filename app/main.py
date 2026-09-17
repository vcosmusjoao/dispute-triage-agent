from fastapi import FastAPI

from app.agent.graph import dispute_graph
from app.models import Dispute, Verdict

app = FastAPI(title="Dispute Triage Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/disputes/analyze")
def analyze(dispute: Dispute) -> Verdict:
    final_state = dispute_graph.invoke({"dispute": dispute})
    return Verdict(
        recommendation=final_state["recommendation"],
        confidence=final_state["confidence"],
        reason_code_meaning=final_state["reason_code_meaning"],
        why=final_state["why"],
        required_evidence=final_state["required_evidence"],
        draft_rebuttal=final_state.get("draft_rebuttal"),
    )
