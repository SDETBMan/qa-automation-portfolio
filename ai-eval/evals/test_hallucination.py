"""
test_hallucination.py

Evaluates whether the RAG pipeline's answers contradict the source context —
the stricter complement to faithfulness.

Metric: HallucinationMetric
  - Detects factual contradictions between actual_output and context.
  - Where FaithfulnessMetric asks "is the output supported by context?",
    HallucinationMetric asks "does the output contradict context?"
  - Threshold: 0.5 (less than 50% hallucination rate required to pass).
  - Uses `context` (not `retrieval_context`) per DeepEval's API contract.

Together, test_faithfulness + test_hallucination give full coverage of the
retrieval → generation accuracy contract.
"""

import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import HallucinationMetric
from deepeval.test_case import LLMTestCase

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "golden_dataset.json"
with open(DATASET_PATH) as f:
    _raw = json.load(f)

DATASET = [
    pytest.param(c, id=c["id"], marks=[getattr(pytest.mark, t) for t in c.get("tags", [])])
    for c in _raw
]


@pytest.mark.parametrize("case", DATASET)
def test_hallucination(case, retriever, answer_generator):
    """
    Asserts the generated answer does not state facts that directly
    contradict the most relevant FAQ chunk. Using n_results=1 scopes the
    check to the single most relevant source — the metric judges contradiction,
    not completeness, so a focused context avoids false positives.
    """
    context = retriever(case["question"], n_results=1)
    actual_output = answer_generator(case["question"], context)

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=actual_output,
        context=context,  # HallucinationMetric uses `context`, not `retrieval_context`
    )

    assert_test(test_case, [
        HallucinationMetric(threshold=0.5, model="gpt-4o-mini"),
    ])
