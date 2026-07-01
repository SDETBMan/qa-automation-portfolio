"""
test_hallucination_benchmark.py

Aggregate hallucination benchmark — runs all 10 golden-dataset cases through
HallucinationMetric and reports suite-level pass rate rather than failing on
individual cases.

How this differs from test_hallucination.py:
  - test_hallucination.py: per-case pass/fail with smoke/regression markers.
  - This module: all 10 cases always run, individual cases never fail pytest,
    and a sentinel test asserts the aggregate pass rate >= 80%.

Metrics reported to DataDog:
  - llm.eval.hallucination_benchmark.pass_rate   (0–100)
  - llm.eval.hallucination_benchmark.mean_score   (0–1)
  - llm.eval.hallucination_benchmark.sample_count  (integer)
"""

import json
from pathlib import Path

import pytest
from deepeval.metrics import HallucinationMetric
from deepeval.test_case import LLMTestCase

from utils.datadog_reporter import send_eval_score

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "golden_dataset.json"
with open(DATASET_PATH) as f:
    _raw = json.load(f)

# Module-level accumulator — each parametrized case appends its result here.
# The sentinel test reads this list after all cases have executed.
_benchmark_scores: list[dict] = []


@pytest.mark.parametrize("case", _raw, ids=[c["id"] for c in _raw])
@pytest.mark.regression
def test_hallucination_benchmark_case(case, retriever, answer_generator):
    """
    Runs a single golden-dataset case through HallucinationMetric and records
    the result. Individual cases intentionally do NOT fail — the aggregate
    sentinel test is the only failure point.
    """
    context = retriever(case["question"], n_results=1)
    actual_output = answer_generator(case["question"], context)

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=actual_output,
        context=context,
    )

    metric = HallucinationMetric(threshold=0.5, model="gpt-4o-mini")

    passed = False
    score = None
    try:
        metric.measure(test_case)
        score = metric.score
        passed = score <= metric.threshold if score is not None else False
    except Exception:
        passed = False

    _benchmark_scores.append({
        "case_id": case["id"],
        "score": score,
        "passed": passed,
    })


@pytest.mark.regression
def test_hallucination_benchmark_aggregate():
    """
    Sentinel test — runs after all parametrized cases. Computes aggregate
    metrics and asserts the overall pass rate meets the 80% threshold.

    This test must be collected after the parametrized cases. pytest runs
    tests in file order within a module, so placing it below the
    parametrized function guarantees correct ordering.
    """
    assert _benchmark_scores, (
        "No benchmark scores collected — parametrized cases must run first"
    )

    total = len(_benchmark_scores)
    passed_count = sum(1 for r in _benchmark_scores if r["passed"])
    pass_rate = (passed_count / total) * 100

    scores = [r["score"] for r in _benchmark_scores if r["score"] is not None]
    mean_score = sum(scores) / len(scores) if scores else 0.0

    # ── Report to DataDog ───────────────────────────────────────────
    tags = ["model:gpt-4o-mini", "framework:ai-eval"]
    send_eval_score("llm.eval.hallucination_benchmark.pass_rate", pass_rate, tags)
    send_eval_score("llm.eval.hallucination_benchmark.mean_score", mean_score, tags)
    send_eval_score("llm.eval.hallucination_benchmark.sample_count", total, tags)

    # ── Aggregate assertion ─────────────────────────────────────────
    assert pass_rate >= 80, (
        f"Hallucination benchmark pass rate {pass_rate:.1f}% is below the "
        f"80% threshold ({passed_count}/{total} cases passed)"
    )
