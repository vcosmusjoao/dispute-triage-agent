"""Deterministic rules baseline for dispute triage — no LLM involved.

This exists so the API contract and tests are solid *before* any AI
complexity (docs/decisions.md ADR-002/ADR-004). `evaluate` is a pure
function: same `Dispute` in, same `Verdict` out, every time.
"""

from app.models import Dispute, Verdict

# reason_code -> (human-readable meaning, evidence that tends to win it)
REASON_CODES: dict[str, tuple[str, list[str]]] = {
    "10.4": (
        "Fraud - card-absent environment",
        [
            "AVS match",
            "CVV match",
            "Device/IP logs consistent with the cardholder",
            "Proof of delivery to a verified address",
        ],
    ),
    "13.1": (
        "Merchandise/services not received",
        [
            "Proof of delivery",
            "Tracking number showing delivery",
            "Terms accepted at purchase",
        ],
    ),
    "13.3": (
        "Not as described / defective",
        [
            "Proof of delivery",
            "Product/service description the customer agreed to",
            "Communication showing the issue was addressed",
        ],
    ),
    "13.7": (
        "Cancelled merchandise/services",
        [
            "Terms accepted, including the cancellation policy",
            "Evidence no cancellation request was received before fulfillment",
        ],
    ),
    "4863": (
        "Cardholder does not recognize the transaction",
        [
            "AVS match",
            "CVV match",
            "IP/device logs tying the session to the cardholder",
            "Purchase history consistent with the cardholder",
        ],
    ),
}

DEFAULT_REASON = (
    "Unrecognized reason code - manual review needed",
    ["General transaction records", "Any available proof of delivery or customer communication"],
)

# Points added/subtracted per signal. Tuned by hand for a sane baseline, not
# fit to data - the whole point is that this is the "boring" version.
_STRONG = 0.20
_MODERATE = 0.15
_MINOR = 0.10
_SMALL = 0.05


def evaluate(dispute: Dispute) -> Verdict:
    meaning, required_evidence = REASON_CODES.get(dispute.reason_code, DEFAULT_REASON)

    score = 0.0
    reasons: list[str] = []

    txn = dispute.transaction
    if txn.avs_match is True:
        score += _MODERATE
        reasons.append("AVS matched")
    elif txn.avs_match is False:
        score -= _STRONG
        reasons.append("AVS mismatch")

    if txn.cvv_match is True:
        score += _MODERATE
        reasons.append("CVV matched")
    elif txn.cvv_match is False:
        score -= _STRONG
        reasons.append("CVV mismatch")

    if txn.ip_country is not None:
        if txn.ip_country == txn.card_country:
            score += _MINOR
            reasons.append("IP country matches card country")
        else:
            score -= _MODERATE
            reasons.append(f"IP country ({txn.ip_country}) differs from card country ({txn.card_country})")

    history = dispute.customer_history
    if history.prior_chargebacks == 0:
        score += _MINOR
        reasons.append("no prior chargebacks")
    else:
        penalty = _MINOR * min(history.prior_chargebacks, 3)
        score -= penalty
        reasons.append(f"{history.prior_chargebacks} prior chargeback(s) on file")

    if history.account_age_days >= 365:
        score += _MINOR
        reasons.append("long-standing account")
    elif history.account_age_days < 30:
        score -= _MINOR
        reasons.append("very new account")

    evidence = dispute.evidence_available
    if evidence.proof_of_delivery:
        score += _STRONG
        reasons.append("proof of delivery available")
    if evidence.terms_accepted:
        score += _MINOR
        reasons.append("terms were accepted")
    if evidence.ip_logs:
        score += _SMALL
        reasons.append("IP/device logs available")

    score = max(-1.0, min(1.0, score))
    recommendation = "fight" if score >= 0 else "accept"
    confidence = round(min(0.95, max(0.5, 0.5 + abs(score) / 2)), 2)

    why = (
        f"Recommending {recommendation} with {confidence:.0%} confidence. "
        f"Signals considered: {', '.join(reasons)}."
        if reasons
        else f"Recommending {recommendation} with {confidence:.0%} confidence based on limited signal data."
    )

    return Verdict(
        recommendation=recommendation,
        confidence=confidence,
        reason_code_meaning=meaning,
        why=why,
        required_evidence=required_evidence,
        draft_rebuttal=None,
    )
