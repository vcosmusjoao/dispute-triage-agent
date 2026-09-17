const STEPS = [
  {
    name: "classify",
    detail: "Reads the reason code, asks Claude what it means and what evidence typically wins it.",
  },
  {
    name: "assess",
    detail: "Weighs the merchant's actual signals against each other — Claude reasons about conflicts, not a lookup table.",
  },
  {
    name: "decide",
    detail: "A transparent, deterministic policy over assess's win-probability: fight above the threshold, accept below it.",
  },
  {
    name: "draft",
    detail: "Only reached on \"fight\" — Claude writes the representment letter, citing only evidence the merchant actually has.",
  },
];

export default function PipelineDiagram() {
  return (
    <div>
      <div className="flex flex-col gap-3 md:flex-row md:items-stretch md:gap-2">
        {STEPS.map((step, i) => (
          <div key={step.name} className="flex items-stretch gap-2 md:flex-1">
            <div className="flex-1 rounded-lg border border-neutral-200 p-4 dark:border-neutral-800">
              <code className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">
                {step.name}
              </code>
              <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">{step.detail}</p>
            </div>
            {i < STEPS.length - 1 && (
              <div
                className="hidden items-center text-neutral-300 dark:text-neutral-700 md:flex"
                aria-hidden
              >
                →
              </div>
            )}
          </div>
        ))}
      </div>
      <p className="mt-4 text-xs text-neutral-500 dark:text-neutral-400">
        The step from <code>decide</code> to <code>draft</code> is a conditional edge: it only
        fires when the recommendation is &quot;fight&quot;. On &quot;accept&quot;, the graph ends
        right after <code>decide</code> — no letter is generated, no extra Claude call is spent.
      </p>
    </div>
  );
}
