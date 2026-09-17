"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import DisputeForm from "@/components/DisputeForm";
import VerdictResult from "@/components/VerdictResult";
import { analyzeDispute, fetchSamples } from "@/lib/api";
import type { Dispute, Verdict } from "@/lib/types";

export default function Home() {
  const [samples, setSamples] = useState<Dispute[]>([]);
  const [jsonText, setJsonText] = useState("");
  const [verdict, setVerdict] = useState<Verdict | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSamples()
      .then((loaded) => {
        setSamples(loaded);
        setJsonText(JSON.stringify(loaded[0], null, 2));
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  function handleSelectSample(sample: Dispute) {
    setJsonText(JSON.stringify(sample, null, 2));
    setVerdict(null);
    setError(null);
  }

  async function handleSubmit() {
    setError(null);
    setVerdict(null);

    let dispute: Dispute;
    try {
      dispute = JSON.parse(jsonText);
    } catch {
      setError("That's not valid JSON. Check for a missing comma or bracket.");
      return;
    }

    setLoading(true);
    try {
      const result = await analyzeDispute(dispute);
      setVerdict(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="py-8">
      <header className="mb-8">
        <h1 className="text-2xl">Try the agent</h1>
        <p className="mt-1 text-sm text-text/60">
          Paste a chargeback dispute, or load a sample, to see the agent&apos;s fight/accept
          recommendation and, when it recommends fighting, the drafted representment letter.
          New to the domain? See{" "}
          <Link href="/how-it-works" className="text-highlight underline hover:text-highlight/80">
            how it works
          </Link>
          {" "}first.
        </p>
      </header>

      <div className="grid gap-8 md:grid-cols-2">
        <DisputeForm
          samples={samples}
          jsonText={jsonText}
          onSelectSample={handleSelectSample}
          onJsonTextChange={setJsonText}
          onSubmit={handleSubmit}
          loading={loading}
        />

        <div>
          {error && (
            <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
              {error}
            </p>
          )}
          {verdict && <VerdictResult verdict={verdict} />}
          {!verdict && !error && (
            <p className="text-sm text-text/40">Analyze a dispute to see the verdict here.</p>
          )}
        </div>
      </div>
    </main>
  );
}
