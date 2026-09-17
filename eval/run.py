"""Eval harness for the dispute-triage agent.

NOT a pytest test - this makes real Claude calls (2 per case: classify +
assess), so it costs a little money and isn't hermetic. Run it by hand
after touching a prompt, the assess/decide policy, or the reason-code data:

    uv run python -m eval.run

Clear-cut cases (expected != None) are asserted: the agent must land on the
labeled recommendation, or the run fails (exit code 1) - this is the
regression safety net. Ambiguous cases (expected == None) have no single
right answer, so their reasoning is printed for a human to eyeball instead.
"""

import sys

from dotenv import load_dotenv

load_dotenv()

from app.agent.graph import dispute_graph  # noqa: E402  (must load .env first)
from eval.dataset import EVAL_CASES  # noqa: E402


def run() -> int:
    passed = 0
    failed = 0

    for case in EVAL_CASES:
        result = dispute_graph.invoke({"dispute": case.dispute})
        recommendation = result["recommendation"]

        if case.expected is None:
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
        print()

    print(f"--- {passed} passed, {failed} failed on clear-cut cases "
          f"({len(EVAL_CASES) - passed - failed} ambiguous cases printed above for review) ---")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run())
