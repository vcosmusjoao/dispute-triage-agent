"""Synthetic sample disputes for local dev, tests, and demos.

All data below is fabricated — no real transactions, customers, or employer
data. See docs/decisions.md ADR-005.
"""

from datetime import datetime, timezone

from app.models import CustomerHistory, Dispute, EvidenceAvailable, Transaction

# Clear-fight: "not received" claim, but the merchant has strong delivery
# proof and clean auth signals — this should win.
DISPUTE_CLEAR_FIGHT = Dispute(
    dispute_id="DSP-1001",
    reason_code="13.1",  # Visa: Merchandise/Services Not Received
    transaction=Transaction(
        amount=129.90,
        currency="USD",
        date=datetime(2026, 8, 2, 14, 30, tzinfo=timezone.utc),
        card_country="US",
        ip_country="US",
        avs_match=True,
        cvv_match=True,
    ),
    customer_history=CustomerHistory(
        prior_purchases=14,
        prior_chargebacks=0,
        account_age_days=612,
    ),
    evidence_available=EvidenceAvailable(
        proof_of_delivery=True,
        tracking_number="1Z999AA10123456784",
        terms_accepted=True,
        ip_logs=True,
    ),
)

# Clear-accept: fraud claim with mismatched auth signals, foreign IP, and a
# customer history of prior chargebacks — not worth fighting.
DISPUTE_CLEAR_ACCEPT = Dispute(
    dispute_id="DSP-1002",
    reason_code="10.4",  # Visa: Other Fraud - Card-Absent Environment
    transaction=Transaction(
        amount=899.00,
        currency="USD",
        date=datetime(2026, 8, 10, 3, 12, tzinfo=timezone.utc),
        card_country="US",
        ip_country="NG",
        avs_match=False,
        cvv_match=False,
    ),
    customer_history=CustomerHistory(
        prior_purchases=1,
        prior_chargebacks=2,
        account_age_days=9,
    ),
    evidence_available=EvidenceAvailable(
        proof_of_delivery=False,
        tracking_number=None,
        terms_accepted=False,
        ip_logs=False,
    ),
)

# Ambiguous: long-standing, low-risk customer, but a CVV mismatch and no
# delivery proof — signals conflict, so this one needs real reasoning.
DISPUTE_AMBIGUOUS = Dispute(
    dispute_id="DSP-1003",
    reason_code="13.1",  # Visa: Merchandise/Services Not Received
    transaction=Transaction(
        amount=54.50,
        currency="USD",
        date=datetime(2026, 8, 15, 9, 5, tzinfo=timezone.utc),
        card_country="US",
        ip_country="US",
        avs_match=True,
        cvv_match=False,
    ),
    customer_history=CustomerHistory(
        prior_purchases=37,
        prior_chargebacks=0,
        account_age_days=1420,
    ),
    evidence_available=EvidenceAvailable(
        proof_of_delivery=False,
        tracking_number=None,
        terms_accepted=True,
        ip_logs=True,
    ),
)

# Cancelled-service dispute: customer says they cancelled, merchant has the
# accepted terms (cancellation policy) but no delivery/tracking angle applies.
DISPUTE_CANCELLED_SERVICE = Dispute(
    dispute_id="DSP-1004",
    reason_code="13.7",  # Visa: Cancelled Merchandise/Services
    transaction=Transaction(
        amount=249.00,
        currency="BRL",
        date=datetime(2026, 8, 20, 18, 45, tzinfo=timezone.utc),
        card_country="BR",
        ip_country="BR",
        avs_match=None,
        cvv_match=True,
    ),
    customer_history=CustomerHistory(
        prior_purchases=5,
        prior_chargebacks=0,
        account_age_days=210,
    ),
    evidence_available=EvidenceAvailable(
        proof_of_delivery=False,
        tracking_number=None,
        terms_accepted=True,
        ip_logs=False,
    ),
)

# Mastercard fraud claim: cardholder doesn't recognize the charge, but IP
# logs tie the session to the cardholder's usual location.
DISPUTE_UNRECOGNIZED_CHARGE = Dispute(
    dispute_id="DSP-1005",
    reason_code="4863",  # Mastercard: Cardholder Does Not Recognize
    transaction=Transaction(
        amount=76.20,
        currency="USD",
        date=datetime(2026, 8, 25, 21, 0, tzinfo=timezone.utc),
        card_country="US",
        ip_country="US",
        avs_match=True,
        cvv_match=True,
    ),
    customer_history=CustomerHistory(
        prior_purchases=8,
        prior_chargebacks=1,
        account_age_days=340,
    ),
    evidence_available=EvidenceAvailable(
        proof_of_delivery=False,
        tracking_number=None,
        terms_accepted=False,
        ip_logs=True,
    ),
)

SAMPLE_DISPUTES: list[Dispute] = [
    DISPUTE_CLEAR_FIGHT,
    DISPUTE_CLEAR_ACCEPT,
    DISPUTE_AMBIGUOUS,
    DISPUTE_CANCELLED_SERVICE,
    DISPUTE_UNRECOGNIZED_CHARGE,
]
