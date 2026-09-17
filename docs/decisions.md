# Decision Log — Dispute Triage Agent

Lightweight ADRs. Each: the decision, why, what we rejected, the tradeoff we accept.
Dated 2026-09-16 unless noted. Revisit any of these as we learn.

---

### ADR-001 — Python + FastAPI for the service
**Decision:** Build the backend in Python 3.12 with FastAPI.
**Why:** The live USD lead (Amplify/Chargeblast) and the AI-eng market ask for Python. FastAPI
gives typed endpoints, request/response validation, and auto Swagger docs for near-zero cost.
**Rejected:** Node/NestJS (João's comfort zone) — but the whole point is closing the *Python* gap.
**Tradeoff:** João is learning a new language while building. Mitigated by Angular/Nest bridges
in the docs and a rules-first milestone before any AI complexity.

---

### ADR-002 — LangGraph for the agent
**Decision:** Model the agent as a LangGraph state graph (classify → assess → decide → draft).
**Why:** The task is genuinely multi-step and stateful, with branching (skip drafting on
"accept"). LangGraph makes each step inspectable and testable, and it's a named, in-demand skill.
**Rejected:** (a) A single mega-prompt — no structure, hard to test/debug, no branching.
(b) A raw SDK tool-loop — works, but LangGraph is what job posts name and gives clearer state.
**Tradeoff:** A new library to learn. Worth it — it's half the résumé value of the project.

---

### ADR-003 — Claude API as the LLM
**Decision:** Use the Anthropic Claude API via the official SDK, with structured/tool-use output.
**Why:** João already knows Claude; strong structured-output support means responses parse
straight into Pydantic. One less unknown.
**Rejected:** OpenAI — no reason to add a second unfamiliar thing.
**Tradeoff:** Needs an API key + a few cents per run. Fine for a demo; keep sample runs small.

---

### ADR-004 — Full pipeline in v1, but built as vertical slices *(João's call)*
**Decision:** v1 includes the draft-rebuttal node (not deferred to v2). BUT we build
incrementally: rules baseline → agent skeleton → reasoning nodes → rebuttal → UI.
**Why:** João wants the impressive full demo. Incremental build keeps the repo shippable at
every step and directly counters the finishing-risk pattern.
**Rejected:** Big-bang full pipeline in one go (stall risk); decision-only v1 (less impressive).
**Tradeoff:** More total work. **Cut line:** if time runs short, ship without the React UI
(Milestone 5) — the API + Swagger is still a complete, demoable product.

---

### ADR-005 — Synthetic data only
**Decision:** All sample disputes are fabricated. No real PicPay data, customers, or codenames.
**Why:** Compliance and ethics. João's fraud *expertise* is portable; his employer's data is not.
**Tradeoff:** None worth mentioning. This is a hard rule.

---

### ADR-006 — Thin Next.js frontend for the demo *(João's call)*
**Decision:** Add a small Next.js page (paste a dispute → see the verdict + letter).
**Why:** Tells the fullstack + AI story, uses João's strength, makes the demo visual/screenshottable.
**Rejected:** API-only (Swagger as demo) — cheaper, but weaker portfolio moment.
**Tradeoff:** One extra milestone. It's the designated cut line if time is tight (see ADR-004).

---

### ADR-007 — Framed as decision-support on sample data, not a production platform
**Decision:** README + interview pitch state the honest scope explicitly.
**Why:** Overclaiming ("production chargeback platform") destroys credibility with anyone who
knows the space. Honesty about scope is itself a senior signal.
**Tradeoff:** Sounds less grand. Correct call — it's defensible.

---

### ADR-008 — No database in v1
**Decision:** Stateless service; sample disputes live in code.
**Why:** Persistence adds setup, migrations, and hosting cost for zero demo value right now.
**Revisit if:** we want a "case history" view or the UI needs to list past verdicts.

---

## Open decisions (defaults chosen; confirm or change later)

| # | Question | Default | Revisit when |
|---|----------|---------|--------------|
| O-1 | Deploy provider for the API | Render free tier | If cold starts / limits annoy → Railway/Fly. |
| O-2 | Package manager | `uv` | If setup friction on Windows → plain venv + pip. |
| O-3 | Add a small eval set for the agent? | Yes, lightweight (~10 disputes) in Milestone 3 | If it slows momentum, keep it tiny. |
| O-4 | Claude model id | Latest Sonnet (cost/latency balance) | Upgrade to Opus for the draft node if quality needs it. |
