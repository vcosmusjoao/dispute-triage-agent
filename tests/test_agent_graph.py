"""Graph tests never hit the network. Both nodes that call Claude
(`classify` and `assess`) have their client seam (`_get_client`)
monkeypatched with a fake that returns a canned tool-use response. This is
how the suite stays green — and free — even though a real ANTHROPIC_API_KEY
now sits in .env: we swap the seam, not the SDK internals.
"""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.agent.graph import build_graph
from app.agent.nodes import assess as assess_module
from app.agent.nodes import classify as classify_module
from app.agent.nodes.decide import decide
from app.data.samples import SAMPLE_DISPUTES
from app.main import app


class _FakeToolUseBlock:
    type = "tool_use"

    def __init__(self, input_: dict):
        self.input = input_


def _fake_client(payload: dict):
    class _Messages:
        def create(self, **kwargs):
            return SimpleNamespace(content=[_FakeToolUseBlock(payload)])

    class _Client:
        messages = _Messages()

    return lambda: _Client()


def _mock_llm_nodes(monkeypatch, *, win_probability: float = 0.8):
    monkeypatch.setattr(
        classify_module,
        "_get_client",
        _fake_client({"meaning": "Mocked meaning", "required_evidence": ["Mocked evidence"]}),
    )
    monkeypatch.setattr(
        assess_module,
        "_get_client",
        _fake_client({"win_probability": win_probability, "reasoning": "Mocked reasoning."}),
    )


def test_graph_runs_end_to_end_and_fights_on_high_probability(monkeypatch):
    _mock_llm_nodes(monkeypatch, win_probability=0.85)
    graph = build_graph()

    for dispute in SAMPLE_DISPUTES:
        result = graph.invoke({"dispute": dispute})

        assert result["recommendation"] == "fight"
        assert result["reason_code_meaning"] == "Mocked meaning"
        assert result["win_probability"] == 0.85
        assert result["draft_rebuttal"] is not None  # fight path reaches draft


def test_graph_accepts_and_skips_draft_on_low_probability(monkeypatch):
    _mock_llm_nodes(monkeypatch, win_probability=0.15)
    graph = build_graph()

    result = graph.invoke({"dispute": SAMPLE_DISPUTES[0]})

    assert result["recommendation"] == "accept"
    assert result.get("draft_rebuttal") is None  # accept path skips draft


def test_classify_falls_back_when_claude_is_unavailable(monkeypatch):
    def _boom():
        raise RuntimeError("no api key configured")

    monkeypatch.setattr(classify_module, "_get_client", _boom)

    update = classify_module.classify({"dispute": SAMPLE_DISPUTES[0]})

    assert update["reason_code_meaning"]
    assert update["required_evidence"]


def test_assess_falls_back_when_claude_is_unavailable(monkeypatch):
    def _boom():
        raise RuntimeError("no api key configured")

    monkeypatch.setattr(assess_module, "_get_client", _boom)

    update = assess_module.assess({"dispute": SAMPLE_DISPUTES[0]})

    assert 0.0 <= update["win_probability"] <= 1.0
    assert update["assess_reasoning"]


def test_decide_fights_when_probability_is_high():
    out = decide({"win_probability": 0.8, "assess_reasoning": "x"})
    assert out["recommendation"] == "fight"
    assert out["confidence"] == 0.8  # 0.5 + |0.8 - 0.5|


def test_decide_accepts_when_probability_is_low():
    out = decide({"win_probability": 0.2, "assess_reasoning": "x"})
    assert out["recommendation"] == "accept"
    assert out["confidence"] == 0.8  # 0.5 + |0.2 - 0.5|


def test_analyze_endpoint_uses_the_graph(monkeypatch):
    _mock_llm_nodes(monkeypatch, win_probability=0.9)
    client = TestClient(app)

    response = client.post(
        "/disputes/analyze",
        json=SAMPLE_DISPUTES[0].model_dump(mode="json"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reason_code_meaning"] == "Mocked meaning"
    assert body["recommendation"] == "fight"
