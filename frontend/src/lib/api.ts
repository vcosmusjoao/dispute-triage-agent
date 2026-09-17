import type { Dispute, Verdict } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export async function fetchSamples(): Promise<Dispute[]> {
  const res = await fetch(`${API_URL}/disputes/samples`);
  if (!res.ok) {
    throw new Error(`Failed to load sample disputes (${res.status})`);
  }
  return res.json();
}

export async function analyzeDispute(dispute: Dispute): Promise<Verdict> {
  const res = await fetch(`${API_URL}/disputes/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dispute),
  });
  if (!res.ok) {
    throw new Error(`Analyze request failed (${res.status})`);
  }
  return res.json();
}
