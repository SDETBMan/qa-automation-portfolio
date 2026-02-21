"""
test_faithfulness.py

Evaluates whether the RAG pipeline's answers are grounded in the retrieved
context — i.e., the model isn't inventing facts beyond what was provided.

Metric: FaithfulnessMetric
  - Scores how well the actual_output is supported by the retrieval_context.
  - An answer that introduces facts not present in the retrieved chunks
    will score low, signaling a hallucination risk.
  - Threshold: 0.7 (70% faithfulness required to pass).

This is one of the most important metrics for RAG pipelines — it directly
measures whether the retrieval → generation chain is working as intended.
"""

import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "golden_dataset.json"
with open(DATASET_PATH) as f:
    DATASET = json.load(f)


@pytest.mark.parametrize("case", DATASET, ids=[c["id"] for c in DATASET])
def test_faithfulness(case, retriever, answer_generator):
    """
    Asserts the generated answer does not go beyond what the retrieved
    FAQ chunks contain — no fabricated policies, prices, or product details.
    """
    context = retriever(case["question"])
    actual_output = answer_generator(case["question"], context)

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=actual_output,
        retrieval_context=context,
    )

    assert_test(test_case, [
        FaithfulnessMetric(threshold=0.7, model="gpt-4o-mini"),
    ])
