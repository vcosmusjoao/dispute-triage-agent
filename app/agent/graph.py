"""LangGraph wiring: classify -> assess -> decide -> (draft | END).

Angular/NgRx bridge: `StateGraph(DisputeState)` is the store definition.
`add_node("classify", classify)` registers a reducer under an action name.
`add_edge("classify", "assess")` is an effect that always dispatches the
next action. `add_conditional_edges` is a `switch` on the current state that
picks which action fires next - here, skip drafting a letter for a dispute
we're not fighting.
"""

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agent.nodes.assess import assess
from app.agent.nodes.classify import classify
from app.agent.nodes.decide import decide
from app.agent.nodes.draft import draft
from app.agent.state import DisputeState


def _route_after_decide(state: DisputeState) -> str:
    return "draft" if state["recommendation"] == "fight" else END


def build_graph() -> CompiledStateGraph:
    graph = StateGraph(DisputeState)

    graph.add_node("classify", classify)
    graph.add_node("assess", assess)
    graph.add_node("decide", decide)
    graph.add_node("draft", draft)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "assess")
    graph.add_edge("assess", "decide")
    graph.add_conditional_edges("decide", _route_after_decide, {"draft": "draft", END: END})
    graph.add_edge("draft", END)

    return graph.compile()


dispute_graph = build_graph()
