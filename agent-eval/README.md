[![agent-eval CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/agent-eval.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/agent-eval.yml)

# agent-eval

A production-grade **agentic AI evaluation framework** built with **DeepEval + Pytest**, testing an OpenAI function-calling agent (`SwagAgent`) that orchestrates multiple tools to answer Swag Labs customer support queries. Demonstrates how to evaluate AI quality at the agentic level, shifting from "did it say the right thing" to "did it call the right tools and complete the task."

## Key Features

* **Four DeepEval metrics:** `ToolCorrectnessMetric` (did the agent invoke the correct tools with correct arguments?), `TaskCompletionMetric` (did the agent fully satisfy the user's request?), `BiasMetric` (is the agent's output free of demographic bias?), and `ToxicityMetric` (is the output free of harmful language?).
* **Function-calling agent under test:** `SwagAgent` runs a multi-step tool-use loop. The model decides which tools to call and with what arguments, executes them, observes results, and synthesizes a grounded final response. The loop is capped at 6 iterations as a runaway guard.
* **Four deterministic tools:** `lookup_product`, `check_return_eligibility`, `calculate_shipping_cost`, and `get_account_status` are backed by in-memory Swag Labs data. The agent's tool-selection decisions are evaluated; the tools themselves always return correct, known data.
* **Scenario dataset:** `datasets/agent_scenarios.json` contains 7 scenarios covering single-tool queries (product lookup, shipping, account status) and multi-tool orchestration (return eligibility requiring both product and policy data). Each scenario carries `smoke` or `regression` tags.
* **Pytest markers:** `smoke` (single-tool, push-safe), `regression` (full suite including multi-tool orchestration, nightly), and `safety` (bias and toxicity checks).
* **DataDog observability:** Suite-level metrics plus per-step `llm.agent.*` scores and per-API-call latency/token usage (every step in the agent loop) sent after each test teardown. Skips gracefully without `DD_API_KEY`.
* **Transient-failure resilience:** `pytest-rerunfailures` retries up to 3× with 60 s delay to tolerate transient OpenAI API timeouts in CI.

## Tech Stack

| Layer | Technology |
|---|---|
| LLM evaluation | DeepEval 1.0+ |
| LLM / judge | OpenAI GPT-4o-mini |
| Function calling | OpenAI tool-use API (`tool_choice="auto"`) |
| Data models | Pydantic v2 |
| Test runner | Pytest 8+ |
| Observability | DataDog CI Visibility + custom GAUGE metrics |
| CI/CD | GitHub Actions |

## Architectural Difference from ai-eval and conv-eval

| Dimension | ai-eval | conv-eval | agent-eval |
|---|---|---|---|
| System under test | Stateless RAG pipeline | Stateful chatbot | Function-calling agent |
| Decision-making | Retrieval then generation | Chat completion with history | Multi-step tool orchestration |
| Core question | Is the answer relevant and faithful? | Is the conversation coherent and on-brand? | Were the right tools called? Was the task completed? |
| Fixture scope | Session-scoped `answer_generator` | Function-scoped `bot` | Function-scoped `agent` |

## Test Coverage

| File | Metric | What is evaluated |
|---|---|---|
| `test_tool_correctness.py` | `ToolCorrectnessMetric` | Agent called the expected tool(s) with correct argument values for each scenario |
| `test_task_completion.py` | `TaskCompletionMetric` | Agent's final response fully satisfies the user's stated intent |
| `test_safety.py` | `BiasMetric` · `ToxicityMetric` | Agent output is free of demographic bias and toxic language, even under adversarial prompts |

The tool correctness and task completion files are parametrized over the scenario dataset. The safety file uses 8 inline cases (4 bias probes + 4 toxicity probes) with a single parametrized test that dispatches to the correct metric based on each case's tag.

## Tools

| Tool | Description |
|---|---|
| `lookup_product` | Returns price, SKU, and description for a Swag Labs product by name |
| `check_return_eligibility` | Checks return eligibility given product name, days since purchase, and receipt status |
| `calculate_shipping_cost` | Returns cost and delivery window for standard, expedited, or overnight shipping |
| `get_account_status` | Returns login status and restrictions for a Swag Labs username |

## How to Run

**Prerequisite:** [Python 3.11+](https://python.org) · `OPENAI_API_KEY` in `agent-eval/.env`

```bash
# Install dependencies
pip install -r requirements.txt

# Smoke tests — single-tool scenarios (fast)
pytest -m smoke -v

# Safety tests — bias and toxicity checks
pytest -m safety -v

# Full suite — includes multi-tool orchestration scenarios
pytest -v
```

> Copy `.env.example` to `.env` and add your `OPENAI_API_KEY` before running locally.

## CI/CD Pipeline

The `agent-eval.yml` workflow triggers on every push/PR to `main` that touches `agent-eval/**`, on a nightly schedule (`07:00 UTC`), and via `workflow_dispatch`.

**Manual dispatch input:**

| Input | Description |
|---|---|
| `marker` | pytest marker filter: `smoke`, `regression`, or `safety`. Leave blank to run `smoke` (CI default). |

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
agent-eval/
├── agent/
│   ├── swag_agent.py               # SwagAgent — function-calling loop (max 6 iterations)
│   └── tools.py                    # TOOL_DEFINITIONS (OpenAI format) · implementations · execute_tool()
├── datasets/
│   └── agent_scenarios.json        # 7 scenarios with smoke/regression tags
├── evals/
│   ├── test_tool_correctness.py    # ToolCorrectnessMetric
│   ├── test_task_completion.py     # TaskCompletionMetric
│   └── test_safety.py             # BiasMetric + ToxicityMetric (safety)
├── utils/
│   └── datadog_reporter.py         # GAUGE metrics: test suite + per-eval scores + token/latency
├── conftest.py                     # Session fixtures: OpenAI client · function-scoped agent with teardown
├── pytest.ini                      # markers: smoke · regression · safety
└── requirements.txt
```

## DataDog Metrics

| Metric | Description |
|---|---|
| `test.suite.passed/failed/skipped` | Suite-level counts tagged `framework:agent-eval` |
| `test.suite.duration_ms` | Total session wall-clock duration |
| `llm.agent.tool_correctness` | Per-scenario ToolCorrectnessMetric score (0–1) |
| `llm.agent.task_completion` | Per-scenario TaskCompletionMetric score (0–1) |
| `llm.agent.bias` | Per-scenario BiasMetric score (0–1) |
| `llm.agent.toxicity` | Per-scenario ToxicityMetric score (0–1) |
| `llm.api.latency_ms` | Per-API-call latency (every step in the agent loop) |
| `llm.api.prompt_tokens` | Per-call prompt token count |
| `llm.api.completion_tokens` | Per-call completion token count |
| `llm.api.total_tokens` | Per-call total token count |
