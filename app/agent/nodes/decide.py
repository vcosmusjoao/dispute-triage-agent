"""decide: the policy node (Option B — deterministic, no LLM call).

The judgment already happened in `assess` (the win-probability estimate).
This node applies a transparent, auditable business rule on top of it:
fight above a threshold, accept below it, with a confidence derived from
how far the estimate sits from a coin-flip. Keeping this deterministic
means the decision boundary is testable without mocking an LLM and easy to
explain/tune.
"""

from app.agent.state import DisputeState

FIGHT_THRESHOLD = 0.5


def decide(state: DisputeState) -> dict:
    probability = state["win_probability"]
    recommendation = "fight" if probability >= FIGHT_THRESHOLD else "accept"

    # Distance from the 0.5 coin-flip, scaled to [0.5, 1.0]. A probability
    # sitting on the threshold is maximally uncertain (~0.5); one far from it
    # is a clear call (~1.0).
    confidence = round(0.5 + abs(probability - FIGHT_THRESHOLD), 2)

    why = (
        f"{recommendation.capitalize()} — estimated {probability:.0%} chance of winning if contested. "
        f"{state.get('assess_reasoning', '')}"
    ).strip()

    return {
        "recommendation": recommendation,
        "confidence": confidence,
        "why": why,
    }
