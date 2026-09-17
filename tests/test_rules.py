"""Tests for the deterministic rules baseline (app/rules.py). These stay
pure — no graph, no network. Endpoint/graph coverage lives in
test_agent_graph.py (with the Claude client mocked).
"""

from app.data.samples import DISPUTE_CLEAR_ACCEPT, DISPUTE_CLEAR_FIGHT
from app.rules import evaluate, recommend_from_score, score_signals


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


def test_score_signals_caps_the_prior_chargeback_penalty_at_three():
    # penalty = _MINOR * min(prior_chargebacks, 3), so 3 and 10 prior
    # chargebacks must score identically - this is the line that proves it.
    three = DISPUTE_CLEAR_FIGHT.model_copy(
        update={"customer_history": DISPUTE_CLEAR_FIGHT.customer_history.model_copy(update={"prior_chargebacks": 3})}
    )
    ten = DISPUTE_CLEAR_FIGHT.model_copy(
        update={"customer_history": DISPUTE_CLEAR_FIGHT.customer_history.model_copy(update={"prior_chargebacks": 10})}
    )

    score_at_three, _ = score_signals(three)
    score_at_ten, _ = score_signals(ten)

    assert score_at_three == score_at_ten


def test_recommend_from_score_fights_at_exactly_zero():
    recommendation, confidence = recommend_from_score(0.0)

    assert recommendation == "fight"
    assert confidence == 0.5
