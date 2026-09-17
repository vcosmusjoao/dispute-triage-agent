"""draft: stub for this milestone. Only reached when decide recommends
"fight" (see the conditional edge in app/agent/graph.py). Milestone 4
replaces this with a real Claude-generated representment letter.
"""

from app.agent.state import DisputeState


def draft(state: DisputeState) -> dict:
    dispute = state["dispute"]
    placeholder = (
        f"[DRAFT PLACEHOLDER] Representment letter for dispute {dispute.dispute_id} "
        f"(reason code {dispute.reason_code}) - generated in Milestone 4."
    )
    return {"draft_rebuttal": placeholder}
