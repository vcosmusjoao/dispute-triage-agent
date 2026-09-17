from app.data.samples import SAMPLE_DISPUTES
from app.models import Dispute


def test_sample_disputes_validate_against_the_dispute_contract():
    assert len(SAMPLE_DISPUTES) >= 4

    for sample in SAMPLE_DISPUTES:
        # Round-trips through the Pydantic contract to prove the samples are
        # valid Dispute payloads, not just Python objects that happen to work.
        revalidated = Dispute.model_validate(sample.model_dump())
        assert revalidated == sample
