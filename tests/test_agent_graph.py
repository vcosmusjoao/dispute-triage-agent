"""Graph tests never make a real network call - `classify`'s Claude client
is monkeypatched with a fake that returns a canned tool-use response. This
is how you keep a test suite green without an ANTHROPIC_API_KEY in CI: swap
the *seam* (`_get_client`), not the Anthropic SDK internals.
"""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.agent.graph import build_graph
from app.agent.nodes import classify as classify_module
from app.data.samples import SAMPLE_DISPUTES
from app.main import app


class _FakeToolUseBlock:
    type = "tool_use"

    def __init__(self, input_: dict):
        self.input = input_


class _FakeMessages:
    def create(self, **kwargs) -> SimpleNamespace:
        return SimpleNamespace(
            content=[_FakeToolUseBlock({"meaning": "Mocked meaning", "required_evidence": ["Mocked evidence"]})]
        )


class _FakeAnthropicClient:
    messages = _FakeMessages()


def test_graph_runs_end_to_end_on_every_sample(monkeypatch):
    monkeypatch.setattr(classify_module, "_get_client", lambda: _FakeAnthropicClient())
    graph = build_graph()

    for dispute in SAMPLE_DISPUTES:
        result = graph.invoke({"dispute": dispute})

        assert result["recommendation"] in {"fight", "accept"}
        assert result["reason_code_meaning"] == "Mocked meaning"
        assert result["required_evidence"] == ["Mocked evidence"]
        if result["recommendation"] == "fight":
            assert result["draft_rebuttal"] is not None
        else:
            assert result.get("draft_rebuttal") is None


def test_classify_falls_back_when_claude_is_unavailable(monkeypatch):
    def _boom():
        raise RuntimeError("no api key configured")

    monkeypatch.setattr(classify_module, "_get_client", _boom)

    update = classify_module.classify({"dispute": SAMPLE_DISPUTES[0]})

    assert update["reason_code_meaning"]
    assert update["required_evidence"]


def test_analyze_endpoint_uses_the_graph(monkeypatch):
    monkeypatch.setattr(classify_module, "_get_client", lambda: _FakeAnthropicClient())
    client = TestClient(app)

    response = client.post(
        "/disputes/analyze",
        json=SAMPLE_DISPUTES[0].model_dump(mode="json"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reason_code_meaning"] == "Mocked meaning"
