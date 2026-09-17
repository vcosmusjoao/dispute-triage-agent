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
        <p className="mb-2 font-fira-code text-sm text-text/60">Load a sample dispute</p>
        <div className="flex flex-wrap gap-2">
          {samples.map((sample) => (
            <button
              key={sample.dispute_id}
              type="button"
              onClick={() => onSelectSample(sample)}
              className="rounded-full border border-highlight/40 px-3 py-1 font-fira-code text-xs text-highlight transition hover:bg-highlight/10"
            >
              {sample.dispute_id} · {sample.reason_code}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label htmlFor="dispute-json" className="mb-2 block font-fira-code text-sm text-text/60">
          Dispute JSON (editable)
        </label>
        <textarea
          id="dispute-json"
          value={jsonText}
          onChange={(e) => onJsonTextChange(e.target.value)}
          spellCheck={false}
          className="h-72 w-full resize-y rounded-md border border-text/20 bg-text/5 p-3 font-mono text-xs text-text focus:border-highlight focus:outline-none"
        />
      </div>

      <button
        type="button"
        onClick={onSubmit}
        disabled={loading}
        className="self-start rounded-md border border-highlight bg-highlight/10 px-5 py-2.5 font-fira-code font-medium text-highlight transition hover:bg-highlight/20 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Analyzing…" : "Analyze dispute"}
      </button>
    </div>
  );
}
