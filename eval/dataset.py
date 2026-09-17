"""~10 synthetic labeled disputes for eval/run.py.

`expected` is None for genuinely ambiguous cases on purpose - there is no
single "correct" answer to assert on, so eval/run.py prints the agent's
reasoning for a human to eyeball instead of failing the run over it.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from app.data.samples import (
    DISPUTE_AMBIGUOUS,
    DISPUTE_CANCELLED_SERVICE,
    DISPUTE_CLEAR_ACCEPT,
    DISPUTE_CLEAR_FIGHT,
    DISPUTE_UNRECOGNIZED_CHARGE,
)
from app.models import CustomerHistory, Dispute, EvidenceAvailable, Transaction


@dataclass
class EvalCase:
    dispute: Dispute
    expected: Literal["fight", "accept"] | None  # None = ambiguous, don't assert
    note: str


# New cases, written for this eval set specifically (not reused elsewhere).

_FRAUD_BUT_CLEARLY_AUTHORIZED = Dispute(
    dispute_id="EVAL-001",
    reason_code="10.4",  # cardholder claims fraud
    transaction=Transaction(
        amount=210.00,
        currency="USD",
        date=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
        card_country="US",
        ip_country="US",
        avs_match=True,
        cvv_match=True,
    ),
    customer_history=CustomerHistory(
        prior_purchases=22,
        prior_chargebacks=0,
        account_age_days=980,
    ),
    evidence_available=EvidenceAvailable(
        proof_of_delivery=True,
        tracking_number="1Z999TESTFRAUD01",
        terms_accepted=True,
        ip_logs=True,
    ),
)

_BRAND_NEW_ACCOUNT_NO_EVIDENCE = Dispute(
    dispute_id="EVAL-002",
    reason_code="13.3",  # not as described
    transaction=Transaction(
        amount=340.00,
        currency="USD",
        date=datetime(2026, 7, 5, 22, 40, tzinfo=timezone.utc),
        card_country="US",
        ip_country="RU",
        avs_match=False,
        cvv_match=None,
    ),
    customer_history=CustomerHistory(
        prior_purchases=0,
        prior_chargebacks=1,
        account_age_days=2,
    ),
    evidence_available=EvidenceAvailable(
        proof_of_delivery=False,
        tracking_number=None,
        terms_accepted=False,
        ip_logs=False,
    ),
)

_PARTIAL_EVIDENCE_MISMATCHED_CVV = Dispute(
    dispute_id="EVAL-003",
    reason_code="13.1",  # not received
    transaction=Transaction(
        amount=88.00,
        currency="USD",
        date=datetime(2026, 7, 10, 16, 0, tzinfo=timezone.utc),
        card_country="US",
        ip_country="US",
        avs_match=True,
        cvv_match=False,
    ),
    customer_history=CustomerHistory(
        prior_purchases=6,
        prior_chargebacks=1,
        account_age_days=150,
    ),
    evidence_available=EvidenceAvailable(
        proof_of_delivery=True,
        tracking_number=None,  # delivered per merchant, but no tracking to prove it
        terms_accepted=False,
        ip_logs=False,
    ),
)

_STRONG_SIGNALS_CLEAR_FIGHT = Dispute(
    dispute_id="EVAL-004",
    reason_code="10.4",
    transaction=Transaction(
        amount=64.00,
        currency="USD",
        date=datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc),
        card_country="US",
        ip_country="US",
        avs_match=True,
        cvv_match=True,
    ),
    customer_history=CustomerHistory(
        prior_purchases=50,
        prior_chargebacks=0,
        account_age_days=1800,
    ),
    evidence_available=EvidenceAvailable(
        proof_of_delivery=True,
        tracking_number="1Z999TESTSTRONG04",
        terms_accepted=True,
        ip_logs=True,
    ),
)

_NO_POLICY_SHOWN_CLEAR_ACCEPT = Dispute(
    dispute_id="EVAL-005",
    reason_code="13.7",  # cancelled merchandise/services
    transaction=Transaction(
        amount=120.00,
        currency="USD",
        date=datetime(2026, 7, 18, 8, 0, tzinfo=timezone.utc),
        card_country="US",
        ip_country="US",
        avs_match=None,
        cvv_match=None,
    ),
    customer_history=CustomerHistory(
        prior_purchases=1,
        prior_chargebacks=3,
        account_age_days=4,
    ),
    evidence_available=EvidenceAvailable(
        proof_of_delivery=False,
        tracking_number=None,
        terms_accepted=False,  # cancellation policy was never shown/accepted
        ip_logs=False,
    ),
)

EVAL_CASES: list[EvalCase] = [
    EvalCase(DISPUTE_CLEAR_FIGHT, "fight", "strong delivery proof + clean auth"),
    EvalCase(DISPUTE_CLEAR_ACCEPT, "accept", "fraud signals + mismatched AVS/CVV + foreign IP"),
    EvalCase(DISPUTE_AMBIGUOUS, None, "clean long-standing customer, but CVV mismatch + no delivery proof"),
    EvalCase(DISPUTE_CANCELLED_SERVICE, None, "cancellation claim, terms accepted but no other evidence"),
    EvalCase(DISPUTE_UNRECOGNIZED_CHARGE, None, "mastercard fraud claim, mixed signals"),
    EvalCase(_FRAUD_BUT_CLEARLY_AUTHORIZED, "fight", "fraud claim contradicted by every auth signal"),
    EvalCase(_BRAND_NEW_ACCOUNT_NO_EVIDENCE, "accept", "day-2 account, foreign IP, zero evidence"),
    EvalCase(_PARTIAL_EVIDENCE_MISMATCHED_CVV, None, "merchant says delivered but has no tracking to prove it"),
    EvalCase(_STRONG_SIGNALS_CLEAR_FIGHT, "fight", "every signal points the same clean direction"),
    EvalCase(_NO_POLICY_SHOWN_CLEAR_ACCEPT, "accept", "cancellation policy never shown, thin/bad history"),
]
