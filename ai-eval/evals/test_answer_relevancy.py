"""
test_answer_relevancy.py

Evaluates whether the RAG pipeline's generated answers actually address
the user's question — regardless of factual accuracy.

Metric: AnswerRelevancyMetric
  - Scores how directly the actual_output responds to the input question.
  - An answer that is factually correct but off-topic will score low.
  - Threshold: 0.7 (70% relevancy required to pass).

DeepEval uses GPT-4o-mini as the LLM judge for scoring.
"""

import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "golden_dataset.json"
with open(DATASET_PATH) as f:
    _raw = json.load(f)

# Convert dataset tags → pytest marks so `-m smoke` / `-m regression` work
DATASET = [
    pytest.param(c, id=c["id"], marks=[getattr(pytest.mark, t) for t in c.get("tags", [])])
    for c in _raw
]


@pytest.mark.parametrize("case", DATASET)
def test_answer_relevancy(case, retriever, answer_generator):
    """
    RAG pipeline flow:
      1. Retrieve top-3 FAQ chunks semantically closest to the question.
      2. Generate an answer grounded in those chunks (GPT-4o-mini).
      3. Assert the answer is relevant to the original question.
    """
    context = retriever(case["question"])
    actual_output = answer_generator(case["question"], context)

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=actual_output,
        retrieval_context=context,
    )

    assert_test(test_case, [
        AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini"),
    ])
