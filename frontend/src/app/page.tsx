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
      setError("That's not valid JSON — check for a missing comma or bracket.");
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
    <main className="mx-auto max-w-5xl px-6 py-12">
      <header className="mb-8">
        <h1 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
          Try the agent
        </h1>
        <p className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
          Paste a chargeback dispute, or load a sample, to see the agent&apos;s fight/accept
          recommendation and — when it recommends fighting — the drafted representment letter.
          New to the domain? See{" "}
          <Link href="/how-it-works" className="underline hover:text-neutral-700 dark:hover:text-neutral-300">
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
            <p className="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
              {error}
            </p>
          )}
          {verdict && <VerdictResult verdict={verdict} />}
          {!verdict && !error && (
            <p className="text-sm text-neutral-400 dark:text-neutral-500">
              Analyze a dispute to see the verdict here.
            </p>
          )}
        </div>
      </div>
    </main>
  );
}
