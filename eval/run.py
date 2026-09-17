"""Eval harness for the dispute-triage agent.

NOT a pytest test - this makes real Claude calls (2 per case: classify +
assess, plus a 3rd - draft - whenever the case reaches "fight"), so it costs
a little money and isn't hermetic. Run it by hand after touching a prompt,
the assess/decide policy, or the reason-code data:

    uv run python -m eval.run

Clear-cut cases (expected != None) are asserted: the agent must land on the
labeled recommendation, or the run fails (exit code 1) - this is the
regression safety net. Ambiguous cases (expected == None) have no single
right answer, so their reasoning is printed for a human to eyeball instead.

On every "fight" case, this also checks the real letter Claude wrote against
the dispute's actual evidence and fails the run if it mentions evidence
marked unavailable. Unlike the pytest suite (which mocks the Claude client
and can only test our own prompt-construction code), this is the one place
that can catch the model itself hallucinating, because it's the one place
still talking to the real model.
"""

import sys

from dotenv import load_dotenv

load_dotenv()

from app.agent.graph import dispute_graph  # noqa: E402  (must load .env first)
from app.agent.nodes.draft import _evidence_lists  # noqa: E402
from eval.dataset import EVAL_CASES  # noqa: E402


def _hallucinated_evidence(dispute, letter: str) -> list[str]:
    _, unavailable = _evidence_lists({"dispute": dispute})
    letter_lower = letter.lower()
    return [item for item in unavailable if item in letter_lower]


def run() -> int:
    passed = 0
    failed = 0
    ambiguous = 0
    hallucinations = 0

    for case in EVAL_CASES:
        result = dispute_graph.invoke({"dispute": case.dispute})
        recommendation = result["recommendation"]

        if case.expected is None:
            ambiguous += 1
            print(f"[AMBIGUOUS] {case.dispute.dispute_id} — {case.note}")
            print(
                f"  -> {recommendation} @ {result['confidence']:.0%} confidence "
                f"(win_probability={result['win_probability']:.2f})"
            )
            print(f"  reasoning: {result['assess_reasoning']}")
        else:
            ok = recommendation == case.expected
            passed += ok
            failed += not ok
            status = "PASS" if ok else "FAIL"
            print(
                f"[{status}] {case.dispute.dispute_id} — expected={case.expected} "
                f"got={recommendation} ({case.note})"
            )

        if recommendation == "fight":
            hallucinated = _hallucinated_evidence(case.dispute, result["draft_rebuttal"])
            if hallucinated:
                hallucinations += 1
                print(f"  [FAIL] draft_rebuttal claims unavailable evidence: {hallucinated}")
            else:
                print("  [PASS] draft_rebuttal cites no evidence marked unavailable")
        print()

    print(
        f"--- {passed} passed, {failed} failed on clear-cut cases "
        f"({ambiguous} ambiguous cases printed above for review); "
        f"{hallucinations} letter(s) with hallucinated evidence ---"
    )
    return 1 if failed or hallucinations else 0


if __name__ == "__main__":
    sys.exit(run())
