"""
test_retrieval_quality.py

Evaluates retrieval quality in the RAG pipeline — isolating retriever
performance from generator performance.  When an answer is bad, these
metrics attribute blame: did the retriever fetch irrelevant chunks
(precision), miss important information (recall), or return context
misaligned with the query (relevancy)?

Metrics (all from DeepEval):
  - ContextualPrecisionMetric  (threshold 0.7) — Are retrieved chunks
    actually relevant to the question?  Penalizes noise in retrieval.
  - ContextualRecallMetric     (threshold 0.7) — Does the retrieval
    context cover the expected answer?  Catches missing information.
  - ContextualRelevancyMetric  (threshold 0.7) — Overall retrieval-to-
    query alignment.

All three require expected_output in the LLMTestCase (unlike faithfulness
or hallucination tests).  The golden dataset already has expected_output
for every case.

DeepEval uses GPT-4o-mini as the LLM judge for scoring.
"""

import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
)
from deepeval.test_case import LLMTestCase

from utils.datadog_reporter import send_eval_score

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "golden_dataset.json"
with open(DATASET_PATH) as f:
    _raw = json.load(f)

# Convert dataset tags -> pytest marks so `-m smoke` / `-m regression` work
DATASET = [
    pytest.param(c, id=c["id"], marks=[getattr(pytest.mark, t) for t in c.get("tags", [])])
    for c in _raw
]


@pytest.mark.parametrize("case", DATASET)
@pytest.mark.retrieval
def test_contextual_precision(case, retriever, answer_generator):
    """
    Are the retrieved chunks actually relevant to the question?

    High precision means retrieval returns minimal noise — every chunk
    contributes to answering the question.  Low precision means the
    retriever is fetching irrelevant content that dilutes the context
    window.
    """
    context = retriever(case["question"])
    actual_output = answer_generator(case["question"], context)

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=actual_output,
        expected_output=case["expected_output"],
        retrieval_context=context,
    )

    metric = ContextualPrecisionMetric(threshold=0.7, model="gpt-4o-mini")
    try:
        assert_test(test_case, [metric])
    finally:
        if metric.score is not None:
            send_eval_score("llm.eval.contextual_precision", metric.score, ["model:gpt-4o-mini"])


@pytest.mark.parametrize("case", DATASET)
@pytest.mark.retrieval
def test_contextual_recall(case, retriever, answer_generator):
    """
    Does the retrieval context cover the expected answer?

    High recall means retrieval captures all the information needed to
    produce the expected answer.  Low recall means important chunks are
    missing — the generator cannot produce a correct answer regardless
    of its capability.
    """
    context = retriever(case["question"])
    actual_output = answer_generator(case["question"], context)

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=actual_output,
        expected_output=case["expected_output"],
        retrieval_context=context,
    )

    metric = ContextualRecallMetric(threshold=0.7, model="gpt-4o-mini")
    try:
        assert_test(test_case, [metric])
    finally:
        if metric.score is not None:
            send_eval_score("llm.eval.contextual_recall", metric.score, ["model:gpt-4o-mini"])


@pytest.mark.parametrize("case", DATASET)
@pytest.mark.retrieval
def test_contextual_relevancy(case, retriever, answer_generator):
    """
    Overall retrieval-to-query alignment.

    Measures how well the retrieved context as a whole aligns with the
    user's question.  Combines precision and recall into a holistic
    retrieval quality signal.
    """
    context = retriever(case["question"])
    actual_output = answer_generator(case["question"], context)

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=actual_output,
        expected_output=case["expected_output"],
        retrieval_context=context,
    )

    # Lower threshold: ContextualRelevancy scores the fraction of retrieved
    # *sentences* relevant to the query.  Our FAQ chunks are large blocks
    # (product catalog, shipping policy, etc.) so even correct retrieval
    # yields a low sentence-level relevancy ratio.  0.05 catches regressions
    # without false-failing on coarse chunk granularity.
    metric = ContextualRelevancyMetric(threshold=0.05, model="gpt-4o-mini")
    try:
        assert_test(test_case, [metric])
    finally:
        if metric.score is not None:
            send_eval_score("llm.eval.contextual_relevancy", metric.score, ["model:gpt-4o-mini"])
