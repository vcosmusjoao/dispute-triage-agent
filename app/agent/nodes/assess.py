"""assess: the LLM judgment node — the place where the agent beats the
rules baseline.

It receives every signal PLUS what `classify` found (the reason-code
meaning and the evidence that typically wins the case), and reasons over
how those signals *interact* to estimate a win-probability. If Claude is
unavailable it degrades to the deterministic rules score.
"""

import logging

import anthropic
from dotenv import load_dotenv

from app.agent.state import DisputeState
from app.rules import score_signals

logger = logging.getLogger(__name__)

load_dotenv()

MODEL = "claude-sonnet-5"

_ASSESS_TOOL = {
    "name": "assess_dispute",
    "description": "Estimate the merchant's probability of winning this dispute if they contest it.",
    "input_schema": {
        "type": "object",
        "properties": {
            "win_probability": {
                "type": "number",
                "description": "Estimated probability (0.0-1.0) that the merchant WINS if they contest the dispute.",
            },
            "reasoning": {
                "type": "string",
                "description": "A concise (2-4 sentence) explanation that weighs the conflicting signals against each other.",
            },
        },
        "required": ["win_probability", "reasoning"],
    },
}

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def _yn(value: bool | None) -> str:
    return "match" if value is True else "mismatch" if value is False else "unknown"


def _dispute_brief(state: DisputeState) -> str:
    """Turn the structured dispute + classify findings into a readable brief
    for Claude. We hand it BOTH the evidence that would win this code and
    the evidence the merchant actually has, so it can reason about the gap.
    """
    dispute = state["dispute"]
    txn = dispute.transaction
    history = dispute.customer_history
    evidence = dispute.evidence_available

    has = [
        name
        for name, present in [
            ("proof of delivery", evidence.proof_of_delivery),
            ("tracking number", bool(evidence.tracking_number)),
            ("terms accepted", evidence.terms_accepted),
            ("IP logs", evidence.ip_logs),
        ]
        if present
    ] or ["none"]

    return (
        f"Reason code {dispute.reason_code}: {state.get('reason_code_meaning', 'n/a')}\n"
        f"Evidence that typically wins this code: {', '.join(state.get('required_evidence', []))}\n\n"
        f"Transaction: {txn.amount} {txn.currency}; card country {txn.card_country}; "
        f"IP country {txn.ip_country or 'unknown'}; AVS {_yn(txn.avs_match)}; CVV {_yn(txn.cvv_match)}.\n"
        f"Customer: {history.prior_purchases} prior purchases; {history.prior_chargebacks} prior chargebacks; "
        f"account {history.account_age_days} days old.\n"
        f"Evidence the merchant actually has: {', '.join(has)}."
    )


def _fallback(state: DisputeState) -> dict:
    score, reasons = score_signals(state["dispute"])
    probability = round((score + 1) / 2, 2)  # map score [-1, 1] -> probability [0, 1]
    return {
        "win_probability": probability,
        "assess_reasoning": (
            "Estimated from deterministic signal scoring (Claude unavailable). "
            f"Signals: {', '.join(reasons)}."
        ),
    }


def assess(state: DisputeState) -> dict:
    try:
        client = _get_client()
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=[_ASSESS_TOOL],
            tool_choice={"type": "tool", "name": "assess_dispute"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        "You are a card chargeback analyst. Weigh the signals below and estimate "
                        "the merchant's probability of winning if they contest this dispute. "
                        "Reason about how signals INTERACT — for example, a long, clean customer "
                        "history can outweigh a single mismatched auth signal — not each signal in "
                        "isolation.\n\n" + _dispute_brief(state)
                    ),
                }
            ],
        )
        tool_use = next(block for block in response.content if block.type == "tool_use")
        result = tool_use.input
        probability = max(0.0, min(1.0, float(result["win_probability"])))
        return {"win_probability": probability, "assess_reasoning": result["reasoning"]}
    except Exception:
        logger.exception("assess: Claude call failed, falling back to rules score")
        return _fallback(state)
