// Mirrors app/models.py on the backend - same field names, since we send
// this straight back as the POST body and there's no mapping layer.

export interface Transaction {
  amount: number;
  currency: string;
  date: string;
  card_country: string;
  ip_country: string | null;
  avs_match: boolean | null;
  cvv_match: boolean | null;
}

export interface CustomerHistory {
  prior_purchases: number;
  prior_chargebacks: number;
  account_age_days: number;
}

export interface EvidenceAvailable {
  proof_of_delivery: boolean;
  tracking_number: string | null;
  terms_accepted: boolean;
  ip_logs: boolean;
}

export interface Dispute {
  dispute_id: string;
  reason_code: string;
  transaction: Transaction;
  customer_history: CustomerHistory;
  evidence_available: EvidenceAvailable;
}

export interface Verdict {
  recommendation: "fight" | "accept";
  confidence: number;
  reason_code_meaning: string;
  why: string;
  required_evidence: string[];
  draft_rebuttal: string | null;
}
