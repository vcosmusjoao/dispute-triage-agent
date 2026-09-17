"""Shared Claude client + model id for the LLM nodes (classify/assess/draft).

Centralized so the model version and client setup live in one place instead
of three copies drifting apart. The client is lazily created and cached at
module scope so a process reuses one client instead of opening a new one per
node call.
"""

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-5"

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    return _client
