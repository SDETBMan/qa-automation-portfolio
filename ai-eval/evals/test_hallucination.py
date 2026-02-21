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
    DATASET = json.load(f)


@pytest.mark.parametrize("case", DATASET, ids=[c["id"] for c in DATASET])
def test_hallucination(case, retriever, answer_generator):
    """
    Asserts the generated answer does not state facts that directly
    contradict the retrieved FAQ content.
    """
    context = retriever(case["question"])
    actual_output = answer_generator(case["question"], context)

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=actual_output,
        context=context,  # HallucinationMetric uses `context`, not `retrieval_context`
    )

    assert_test(test_case, [
        HallucinationMetric(threshold=0.5, model="gpt-4o-mini"),
    ])
