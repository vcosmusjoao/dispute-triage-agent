"use client";

import type { Dispute } from "@/lib/types";

interface DisputeFormProps {
  samples: Dispute[];
  jsonText: string;
  onSelectSample: (dispute: Dispute) => void;
  onJsonTextChange: (text: string) => void;
  onSubmit: () => void;
  loading: boolean;
}

export default function DisputeForm({
  samples,
  jsonText,
  onSelectSample,
  onJsonTextChange,
  onSubmit,
  loading,
}: DisputeFormProps) {
  return (
    <div className="flex flex-col gap-4">
      <div>
        <p className="mb-2 text-sm font-medium text-neutral-600 dark:text-neutral-400">
          Load a sample dispute
        </p>
        <div className="flex flex-wrap gap-2">
          {samples.map((sample) => (
            <button
              key={sample.dispute_id}
              type="button"
              onClick={() => onSelectSample(sample)}
              className="rounded-full border border-neutral-300 px-3 py-1 text-sm text-neutral-700 transition hover:border-violet-400 hover:bg-violet-50 hover:text-violet-700 dark:border-neutral-700 dark:text-neutral-300 dark:hover:border-violet-500 dark:hover:bg-violet-950 dark:hover:text-violet-300"
            >
              {sample.dispute_id} · {sample.reason_code}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label htmlFor="dispute-json" className="mb-2 block text-sm font-medium text-neutral-600 dark:text-neutral-400">
          Dispute JSON (editable)
        </label>
        <textarea
          id="dispute-json"
          value={jsonText}
          onChange={(e) => onJsonTextChange(e.target.value)}
          spellCheck={false}
          className="h-72 w-full resize-y rounded-lg border border-neutral-300 bg-neutral-50 p-3 font-mono text-xs text-neutral-800 focus:border-violet-500 focus:outline-none dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-200"
        />
      </div>

      <button
        type="button"
        onClick={onSubmit}
        disabled={loading}
        className="self-start rounded-lg bg-violet-600 px-5 py-2.5 font-medium text-white transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Analyzing…" : "Analyze dispute"}
      </button>
    </div>
  );
}
