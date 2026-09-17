"""decide: deterministic placeholder, ported from the Milestone 1 rules
baseline (app/rules.py). Milestone 3 replaces this with real Claude
reasoning that weighs the classify + assess findings together.
"""

from app.agent.state import DisputeState
from app.rules import explain, recommend_from_score


def decide(state: DisputeState) -> dict:
    recommendation, confidence = recommend_from_score(state["score"])
    why = explain(recommendation, confidence, state["signal_reasons"])
    return {"recommendation": recommendation, "confidence": confidence, "why": why}
