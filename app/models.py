"""Data contracts for the dispute-triage-agent API.

These are the source of truth (docs/architecture.md §3) — the agent graph,
the FastAPI routes, and the frontend all build on these shapes.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Transaction(BaseModel):
    amount: float
    currency: str  # "USD", "BRL", ...
    date: datetime
    card_country: str  # ISO-2, e.g. "US"
    ip_country: str | None
    avs_match: bool | None  # address verification
    cvv_match: bool | None


class CustomerHistory(BaseModel):
    prior_purchases: int
    prior_chargebacks: int
    account_age_days: int


class EvidenceAvailable(BaseModel):
    proof_of_delivery: bool = False
    tracking_number: str | None = None
    terms_accepted: bool = False
    ip_logs: bool = False


class Dispute(BaseModel):
    dispute_id: str
    reason_code: str  # e.g. "13.1", "10.4"
    transaction: Transaction
    customer_history: CustomerHistory
    evidence_available: EvidenceAvailable


class Verdict(BaseModel):
    recommendation: Literal["fight", "accept"]
    confidence: float  # 0.0-1.0
    reason_code_meaning: str  # human-readable interpretation
    why: str  # plain-English rationale
    required_evidence: list[str]  # what would win this
    draft_rebuttal: str | None  # the representment letter (None if accept)
