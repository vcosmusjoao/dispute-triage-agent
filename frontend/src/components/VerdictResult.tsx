import type { Verdict } from "@/lib/types";

export default function VerdictResult({ verdict }: { verdict: Verdict }) {
  const isFight = verdict.recommendation === "fight";

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center gap-3">
        <span
          className={`rounded-full border px-3 py-1 font-fira-code text-sm font-semibold uppercase tracking-wide ${
            isFight
              ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-400"
              : "border-text/30 bg-text/5 text-text/70"
          }`}
        >
          {verdict.recommendation}
        </span>
        <span className="font-fira-code text-sm text-text/50">
          {(verdict.confidence * 100).toFixed(0)}% confidence
        </span>
      </div>

      <div>
        <h3 className="text-sm">Reason code</h3>
        <p className="mt-1 text-sm text-text/80">{verdict.reason_code_meaning}</p>
      </div>

      <div>
        <h3 className="text-sm">Why</h3>
        <p className="mt-1 text-sm text-text/80">{verdict.why}</p>
      </div>

      <div>
        <h3 className="text-sm">Evidence that would win this</h3>
        <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-text/80">
          {verdict.required_evidence.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      <div>
        <h3 className="text-sm">Representment letter</h3>
        {verdict.draft_rebuttal ? (
          <pre className="mt-2 whitespace-pre-wrap rounded-md border border-text/20 bg-text/5 p-4 font-serif text-sm leading-relaxed text-text/90">
            {verdict.draft_rebuttal}
          </pre>
        ) : (
          <p className="mt-1 text-sm italic text-text/50">
            No letter. We&apos;re recommending accepting this chargeback.
          </p>
        )}
      </div>
    </div>
  );
}
