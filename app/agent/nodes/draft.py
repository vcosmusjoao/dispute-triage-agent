"""draft: generates the representment letter for a "fight" verdict.

Only reached via the conditional edge in app/agent/graph.py, when
`recommendation == "fight"`. Uses the same tool-use pattern as classify/assess
so the reply comes back as a clean `letter` field instead of a chatty
completion with wrapper text ("Sure, here's the letter:...") around it. If
Claude is unavailable, falls back to a templated letter built straight from
the available evidence, mirroring the fallback in the other two LLM nodes.
"""

import logging

import anthropic
from dotenv import load_dotenv

from app.agent.state import DisputeState

logger = logging.getLogger(__name__)

load_dotenv()

MODEL = "claude-sonnet-5"

_DRAFT_TOOL = {
    "name": "draft_rebuttal",
    "description": "Write a formal representment letter contesting a card network chargeback.",
    "input_schema": {
        "type": "object",
        "properties": {
            "letter": {
                "type": "string",
                "description": (
                    "The full representment letter as a formal business letter: a header "
                    "with the dispute ID, transaction amount, and reason code; then 2-4 "
                    "persuasive body paragraphs; then a closing paragraph requesting the "
                    "chargeback be reversed. No email greeting or sign-off."
                ),
            },
        },
        "required": ["letter"],
    },
}

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def _evidence_lists(state: DisputeState) -> tuple[list[str], list[str]]:
    """Split the evidence catalog into what the merchant has vs. doesn't -
    handing the prompt an explicit contrast is what lets us tell Claude
    "don't invent the second list" instead of just saying "don't lie" in
    the abstract.
    """
    evidence = state["dispute"].evidence_available
    catalog = [
        ("proof of delivery", evidence.proof_of_delivery),
        ("tracking number", bool(evidence.tracking_number)),
        ("accepted terms of service", evidence.terms_accepted),
        ("IP/session logs", evidence.ip_logs),
    ]
    available = [name for name, present in catalog if present]
    unavailable = [name for name, present in catalog if not present]
    return available, unavailable


def _prompt(state: DisputeState) -> str:
    dispute = state["dispute"]
    available, unavailable = _evidence_lists(state)

    return (
        "You are a merchant's chargeback analyst writing a representment letter to contest "
        "a dispute with the card issuer. Write a formal business letter: a header with the "
        "dispute ID, transaction amount/currency, and reason code; then 2-4 persuasive body "
        "paragraphs tailored to the reason code; then a closing paragraph requesting the "
        "chargeback be reversed. Professional tone, no email greeting or sign-off.\n\n"
        f"Dispute ID: {dispute.dispute_id}\n"
        f"Amount: {dispute.transaction.amount} {dispute.transaction.currency}\n"
        f"Reason code {dispute.reason_code}: {state.get('reason_code_meaning', 'n/a')}\n"
        f"Why we're contesting: {state.get('why', 'n/a')}\n\n"
        f"Evidence AVAILABLE (you may cite these): {', '.join(available) or 'none'}\n"
        f"Evidence NOT AVAILABLE (do not claim these exist): {', '.join(unavailable) or 'none'}\n\n"
        "Only cite evidence listed as AVAILABLE. Do not mention anything from the NOT "
        "AVAILABLE list as if the merchant has it - if something there would normally "
        "strengthen this argument, acknowledge that gap honestly instead of inventing it."
    )


def _fallback(state: DisputeState) -> dict:
    dispute = state["dispute"]
    available, _ = _evidence_lists(state)
    letter = (
        f"Re: Dispute {dispute.dispute_id} - Reason Code {dispute.reason_code}\n"
        f"Amount: {dispute.transaction.amount} {dispute.transaction.currency}\n\n"
        f"We contest this chargeback. {state.get('why', '')}\n"
        f"Supporting evidence on file: {', '.join(available) or 'none available'}.\n\n"
        "We request that this chargeback be reversed."
    )
    return {"draft_rebuttal": letter}


def draft(state: DisputeState) -> dict:
    try:
        client = _get_client()
        response = client.messages.create(
            model=MODEL,
            max_tokens=1536,
            tools=[_DRAFT_TOOL],
            tool_choice={"type": "tool", "name": "draft_rebuttal"},
            messages=[{"role": "user", "content": _prompt(state)}],
        )
        tool_use = next(block for block in response.content if block.type == "tool_use")
        return {"draft_rebuttal": tool_use.input["letter"]}
    except Exception:
        logger.exception("draft: Claude call failed, falling back to templated letter")
        return _fallback(state)
