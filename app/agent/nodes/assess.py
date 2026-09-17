"""assess: deterministic placeholder, ported from the Milestone 1 rules
baseline (app/rules.py). Milestone 3 replaces this with real Claude
reasoning over the same signals.
"""

from app.agent.state import DisputeState
from app.rules import score_signals


def assess(state: DisputeState) -> dict:
    score, reasons = score_signals(state["dispute"])
    return {"score": score, "signal_reasons": reasons}
