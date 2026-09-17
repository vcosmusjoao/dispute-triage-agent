from fastapi.testclient import TestClient

from app.data.samples import SAMPLE_DISPUTES
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_samples_endpoint_returns_the_sample_disputes():
    response = client.get("/disputes/samples")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == len(SAMPLE_DISPUTES)
    assert {d["dispute_id"] for d in body} == {d.dispute_id for d in SAMPLE_DISPUTES}
