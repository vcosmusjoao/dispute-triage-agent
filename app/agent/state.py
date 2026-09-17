"""Graph state for the dispute-triage agent.

Angular/NgRx bridge: this TypedDict is the store's shape. Each node is a
reducer that returns a *partial* update; LangGraph merges it into the state
dict (default behaviour: last write per key wins, same as an object spread
`{...state, ...update}` in a default reducer case - no custom reducer
function needed here since nothing accumulates across nodes).
"""

from typing import TypedDict

from app.models import Dispute


class DisputeState(TypedDict, total=False):
    # input
    dispute: Dispute

    # populated by `classify`
    reason_code_meaning: str
    required_evidence: list[str]

    # populated by `assess`
    win_probability: float
    assess_reasoning: str

    # populated by `decide`
    recommendation: str  # "fight" | "accept"
    confidence: float
    why: str

    # populated by `draft` (only reached when recommendation == "fight")
    draft_rebuttal: str | None
