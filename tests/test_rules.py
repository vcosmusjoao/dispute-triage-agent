"""Tests for the deterministic rules baseline (app/rules.py). These stay
pure — no graph, no network. Endpoint/graph coverage lives in
test_agent_graph.py (with the Claude client mocked).
"""

from app.data.samples import DISPUTE_CLEAR_ACCEPT, DISPUTE_CLEAR_FIGHT
from app.rules import evaluate


def test_evaluate_recommends_fight_on_the_clear_fight_sample():
    verdict = evaluate(DISPUTE_CLEAR_FIGHT)

    assert verdict.recommendation == "fight"
    assert verdict.confidence > 0.7
    assert verdict.draft_rebuttal is None


def test_evaluate_recommends_accept_on_the_clear_accept_sample():
    verdict = evaluate(DISPUTE_CLEAR_ACCEPT)

    assert verdict.recommendation == "accept"
    assert verdict.confidence > 0.7
    assert verdict.draft_rebuttal is None
