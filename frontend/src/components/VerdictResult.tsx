import type { Verdict } from "@/lib/types";

export default function VerdictResult({ verdict }: { verdict: Verdict }) {
  const isFight = verdict.recommendation === "fight";

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center gap-3">
        <span
          className={`rounded-full px-3 py-1 text-sm font-semibold uppercase tracking-wide ${
            isFight
              ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300"
              : "bg-neutral-200 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300"
          }`}
        >
          {verdict.recommendation}
        </span>
        <span className="text-sm text-neutral-500 dark:text-neutral-400">
          {(verdict.confidence * 100).toFixed(0)}% confidence
        </span>
      </div>

      <div>
        <h3 className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Reason code</h3>
        <p className="mt-1 text-sm text-neutral-800 dark:text-neutral-200">{verdict.reason_code_meaning}</p>
      </div>

      <div>
        <h3 className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Why</h3>
        <p className="mt-1 text-sm text-neutral-800 dark:text-neutral-200">{verdict.why}</p>
      </div>

      <div>
        <h3 className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Evidence that would win this</h3>
        <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-neutral-800 dark:text-neutral-200">
          {verdict.required_evidence.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      <div>
        <h3 className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Representment letter</h3>
        {verdict.draft_rebuttal ? (
          <pre className="mt-2 whitespace-pre-wrap rounded-lg border border-neutral-200 bg-neutral-50 p-4 font-serif text-sm leading-relaxed text-neutral-800 dark:border-neutral-800 dark:bg-neutral-900 dark:text-neutral-200">
            {verdict.draft_rebuttal}
          </pre>
        ) : (
          <p className="mt-1 text-sm italic text-neutral-500 dark:text-neutral-400">
            No letter — we&apos;re recommending accepting this chargeback.
          </p>
        )}
      </div>
    </div>
  );
}
