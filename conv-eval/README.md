[![conv-eval CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/conv-eval.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/conv-eval.yml)

# conv-eval

A production-grade **conversational AI evaluation framework** built with **DeepEval + Pytest**, testing a stateful multi-turn chatbot (`SwagSupportBot`) that simulates a Swag Labs customer support agent. Demonstrates how to evaluate AI quality across a full conversation, not just single-turn answers. Covering: turn relevancy, knowledge retention, role adherence, and graceful handling of out-of-scope requests.

## Key Features

* **Six DeepEval conversational metrics:** `ConversationRelevancyMetric`, `KnowledgeRetentionMetric`, `RoleAdherenceMetric`, `ConversationalGEval` (graceful handling), `BiasMetric` (per-turn bias), and `ToxicityMetric` (per-turn toxicity). Each evaluating conversation quality from a different safety or quality dimension.
* **Stateful chatbot under test:** `SwagSupportBot` accumulates the full message history across turns so the model resolves pronouns, follows topic switches, and acknowledges corrections, exactly like a real support bot. Each test gets a fresh bot instance via a function-scoped fixture.
* **Conversation dataset:** `datasets/conversations.json` contains 7 multi-turn scenarios covering normal support queries, implicit reference resolution, context corrections, off-domain deflection, and adversarial prompt injection. Each scenario carries `smoke`, `regression`, `safety`, or `retention` tags.
* **Pytest markers:** `smoke` (push-safe), `regression` (nightly), `safety`, and `retention`. Filter with `-m smoke`, `-m retention`, etc.
* **DataDog observability:** Suite-level metrics plus per-turn `llm.conv.*` scores and per-API-call latency/token usage sent after every test teardown. Skips gracefully without `DD_API_KEY`.
* **Transient-failure resilience:** `pytest-rerunfailures` retries up to 3× with 60 s delay to tolerate transient OpenAI API timeouts in CI.

## Tech Stack

| Layer | Technology |
|---|---|
| LLM evaluation | DeepEval 1.0+ |
| LLM / judge | OpenAI GPT-4o-mini |
| Test runner | Pytest 8+ |
| Observability | DataDog CI Visibility + custom GAUGE metrics |
| CI/CD | GitHub Actions |

## Architectural Difference from ai-eval

| Dimension | ai-eval | conv-eval |
|---|---|---|
| System under test | Stateless RAG pipeline | Stateful chatbot (`SwagSupportBot`) |
| Input | Single question + retrieved context | Multi-turn conversation history |
| Metrics | Single-turn answer quality | Conversational coherence and role fidelity |
| Fixture scope | Session-scoped `answer_generator` | Function-scoped `bot` (fresh per test) |

## Test Coverage

| File | Metric | What is evaluated |
|---|---|---|
| `test_conversation_relevancy.py` | `ConversationRelevancyMetric` | Each bot turn directly addresses the user's message in context |
| `test_knowledge_retention.py` | `KnowledgeRetentionMetric` | Bot correctly recalls facts mentioned in earlier turns (implicit references, corrections) |
| `test_role_adherence.py` | `RoleAdherenceMetric` | Bot stays in character as a Swag Labs support agent across all turns |
| `test_graceful_handling.py` | `ConversationalGEval` | Bot politely deflects out-of-domain queries and resists prompt injection without breaking character |
| `test_safety.py` | `BiasMetric` · `ToxicityMetric` | Each response in a multi-turn conversation is free of bias and toxicity, even as adversarial context accumulates |

All five test files are parametrized over the conversation dataset or inline safety conversations. Each scenario's tags map directly to pytest markers.

## How to Run

**Prerequisite:** [Python 3.11+](https://python.org) · `OPENAI_API_KEY` in `conv-eval/.env`

```bash
# Install dependencies
pip install -r requirements.txt

# Smoke tests — turn relevancy + role adherence across normal scenarios (fast)
pytest -m smoke -v

# Knowledge retention tests — implicit reference and correction scenarios
pytest -m retention -v

# Safety tests — out-of-scope deflection and prompt injection
pytest -m safety -v

# Full suite
pytest -v
```

> Copy `.env.example` to `.env` and add your `OPENAI_API_KEY` before running locally.

## CI/CD Pipeline

The `conv-eval.yml` workflow triggers on every push/PR to `main` that touches `conv-eval/**`, on a nightly schedule (`06:00 UTC`), and via `workflow_dispatch`.

**Manual dispatch input:**

| Input | Description |
|---|---|
| `marker` | pytest marker filter: `smoke`, `regression`, `safety`, `retention`. Leave blank to run `smoke` (CI default). |

**Pipeline steps:**

1. Checkout code
2. Set up Python 3.11 with pip cache
3. `pip install -r requirements.txt`
4. Run pytest (`--reruns 3 --reruns-delay 60`, `DEEPEVAL_DISABLE_TIMEOUTS=true`)
5. Upload JUnit XML to DataDog CI Visibility (`if: always()`, `continue-on-error: true`)
6. Upload `.deepeval/` artifact (retained 30 days)

> **Secret required:** `OPENAI_API_KEY` must be set in repository secrets. `DD_API_KEY` (optional) enables DataDog CI Visibility and custom metrics.

## Project Structure

```
conv-eval/
├── chatbot/
│   ├── knowledge.py                # SYSTEM_PROMPT and Swag Labs knowledge base
│   └── swag_support_bot.py         # SwagSupportBot — stateful multi-turn chatbot
├── datasets/
│   └── conversations.json          # 7 multi-turn scenarios with smoke/regression/safety/retention tags
├── evals/
│   ├── test_conversation_relevancy.py  # ConversationRelevancyMetric
│   ├── test_knowledge_retention.py     # KnowledgeRetentionMetric
│   ├── test_role_adherence.py          # RoleAdherenceMetric
│   ├── test_graceful_handling.py       # ConversationalGEval (safety)
│   └── test_safety.py                 # BiasMetric + ToxicityMetric (per-turn)
├── utils/
│   └── datadog_reporter.py         # GAUGE metrics: test suite + per-eval scores + token/latency
├── conftest.py                     # Session fixtures: OpenAI client · function-scoped bot with teardown
├── pytest.ini                      # markers: smoke · regression · safety · retention
└── requirements.txt
```

## DataDog Metrics

| Metric | Description |
|---|---|
| `test.suite.passed/failed/skipped` | Suite-level counts tagged `framework:conv-eval` |
| `test.suite.duration_ms` | Total session wall-clock duration |
| `llm.conv.turn_relevancy` | Per-scenario ConversationRelevancyMetric score (0–1) |
| `llm.conv.knowledge_retention` | Per-scenario KnowledgeRetentionMetric score (0–1) |
| `llm.conv.role_adherence` | Per-scenario RoleAdherenceMetric score (0–1) |
| `llm.conv.graceful_handling` | Per-scenario GEval graceful handling score (0–1) |
| `llm.conv.bias` | Per-turn BiasMetric score (0–1) |
| `llm.conv.toxicity` | Per-turn ToxicityMetric score (0–1) |
| `llm.api.latency_ms` | Per-API-call latency (every chat turn) |
| `llm.api.prompt_tokens` | Per-call prompt token count |
| `llm.api.completion_tokens` | Per-call completion token count |
| `llm.api.total_tokens` | Per-call total token count |
