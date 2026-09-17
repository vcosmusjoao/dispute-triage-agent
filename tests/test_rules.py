from fastapi.testclient import TestClient

from app.data.samples import DISPUTE_CLEAR_ACCEPT, DISPUTE_CLEAR_FIGHT
from app.main import app
from app.models import Verdict
from app.rules import evaluate

client = TestClient(app)


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


def test_analyze_endpoint_returns_a_well_formed_verdict():
    response = client.post(
        "/disputes/analyze",
        json=DISPUTE_CLEAR_FIGHT.model_dump(mode="json"),
    )

    assert response.status_code == 200
    verdict = Verdict.model_validate(response.json())
    assert verdict.recommendation == "fight"
