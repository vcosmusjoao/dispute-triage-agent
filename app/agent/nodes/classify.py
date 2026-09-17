"""classify: the only node in this milestone that actually calls Claude.

Given a reason_code, ask Claude for its human-readable meaning and the
evidence that tends to win it - using a tool (function-calling) schema so
the reply comes back as structured JSON instead of prose we'd have to
parse. If the call fails for any reason (no API key, network, rate limit,
malformed reply), fall back to the deterministic lookup from app/rules.py
so the graph still produces a usable result.
"""

import logging

import anthropic
from dotenv import load_dotenv

from app.agent.state import DisputeState
from app.rules import DEFAULT_REASON, REASON_CODES

logger = logging.getLogger(__name__)

load_dotenv()

MODEL = "claude-sonnet-5"

_CLASSIFY_TOOL = {
    "name": "classify_reason_code",
    "description": "Interpret a card network chargeback reason code.",
    "input_schema": {
        "type": "object",
        "properties": {
            "meaning": {
                "type": "string",
                "description": "A concise, one-sentence human-readable interpretation of the reason code.",
            },
            "required_evidence": {
                "type": "array",
                "items": {"type": "string"},
                "description": "The kinds of evidence a merchant would need to win this dispute.",
            },
        },
        "required": ["meaning", "required_evidence"],
    },
}

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    return _client


def classify(state: DisputeState) -> dict:
    dispute = state["dispute"]

    try:
        client = _get_client()
        response = client.messages.create(
            model=MODEL,
            # Enough headroom for the full tool-call JSON. Too small and the
            # structured output gets truncated mid-JSON (stop_reason ==
            # "max_tokens"), leaving required fields missing -> KeyError ->
            # fallback. Learned this the hard way with max_tokens=300.
            max_tokens=1024,
            tools=[_CLASSIFY_TOOL],
            tool_choice={"type": "tool", "name": "classify_reason_code"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Classify card network dispute reason code {dispute.reason_code!r} "
                        f"for a chargeback on a {dispute.transaction.amount} "
                        f"{dispute.transaction.currency} transaction."
                    ),
                }
            ],
        )
        tool_use = next(block for block in response.content if block.type == "tool_use")
        result = tool_use.input
        return {
            "reason_code_meaning": result["meaning"],
            "required_evidence": result["required_evidence"],
        }
    except Exception:
        # Broad on purpose: this is the one edge where the graph talks to an
        # external service, and anything from a missing API key to a network
        # blip to a malformed reply should degrade to the deterministic
        # lookup rather than take the whole request down. Logged so a real
        # failure (vs. "no key configured") is still visible in server logs.
        logger.exception("classify: Claude call failed, falling back to REASON_CODES lookup")
        meaning, required_evidence = REASON_CODES.get(dispute.reason_code, DEFAULT_REASON)
        return {
            "reason_code_meaning": meaning,
            "required_evidence": required_evidence,
        }
