# Failure Triage Agent

An Anthropic tool-use agent that reads JUnit XML test results, uses Claude to cluster failures by root cause, and produces a structured triage report with severity rankings and suggested fix actions.

**Stack:** Python 3.11 · Anthropic Claude (tool use, `@beta_tool`) · JUnit XML · DataDog

---

## What It Does

Instead of manually reading through test failure logs, this agent:

1. **Reads** all JUnit XML files in a directory
2. **Extracts** failures and errors with their messages and stack traces
3. **Searches** for patterns across failure messages (regex-based)
4. **Clusters** failures by root cause category
5. **Ranks** clusters by severity and count
6. **Writes** a structured JSON triage report

---

## How It Works (Tool-Use Loop)

```
┌──────────────────┐
│   User provides  │
│   --xml-dir path │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────────┐
│  Claude reads    │────▶│  read_test_results   │
│  all XML files   │     │  (JUnit XML parser)  │
└────────┬─────────┘     └─────────────────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────────────┐
│  Claude searches │────▶│  search_failure_patterns │
│  for patterns    │     │  (regex grep)            │
└────────┬─────────┘     └─────────────────────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────────┐
│  Claude inspects │────▶│  read_source_file    │
│  source code     │     │  (optional)          │
└────────┬─────────┘     └─────────────────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────────┐
│  Claude writes   │────▶│  write_triage_report │
│  triage report   │     │  (JSON output)       │
└────────┬─────────┘     └─────────────────────┘
         │
         ▼
┌──────────────────┐
│  JSON report +   │
│  DataDog metrics │
└──────────────────┘
```

The agent uses `client.beta.messages.tool_runner` — the SDK manages the tool-use loop automatically, calling tools as Claude requests them.

---

## Root Cause Categories

| Category | Description | Example |
|----------|-------------|---------|
| `assertion_error` | Expected vs actual mismatch | `AssertionError: expected 5 but got 3` |
| `element_not_found` | Selenium/Playwright locator failure | `NoSuchElementException: #login-btn` |
| `timeout` | Wait/network timeout | `TimeoutError: waiting for selector` |
| `setup_failure` | Fixture/environment setup error | `ConnectionRefusedError: DB not ready` |
| `api_error` | HTTP status code / connection error | `HTTP 500 Internal Server Error` |
| `data_error` | Test data issues | `KeyError: 'expected_user' not in fixture` |
| `unknown` | Uncategorized | — |

---

## Sample Output

```json
{
  "summary": { "total_tests": 24, "total_failures": 4, "clusters": 2, "cross_framework_incidents": 1 },
  "clusters": [
    {
      "root_cause": "assertion_error",
      "count": 3,
      "severity": "HIGH",
      "affected_suites": ["test_inventory", "test_checkout"],
      "affected_frameworks": ["cypress", "selenium"],
      "is_cross_framework": true,
      "suggested_action": "Review recent product data changes — sort order and price assertions failing across frameworks",
      "examples": [
        { "test": "test_sort_products", "message": "AssertionError: sort order mismatch" }
      ]
    },
    {
      "root_cause": "timeout",
      "count": 1,
      "severity": "HIGH",
      "affected_suites": ["test_login"],
      "affected_frameworks": ["playwright"],
      "is_cross_framework": false,
      "suggested_action": "Check login page load time — may need increased wait timeout or server investigation",
      "examples": [
        { "test": "test_slow_login", "message": "TimeoutError: login page did not load within 10s" }
      ]
    }
  ],
  "priority_order": ["assertion_error", "timeout"],
  "timestamp": "2026-07-29T12:00:00+00:00"
}
```

---

## How to Run

```bash
# Basic triage from JUnit XML
python run.py --xml-dir ../flakiness-detector/fixtures/

# Custom output path
python run.py --xml-dir ./results/ --output triage_report.json

# Quiet mode (report only, no agent output)
python run.py --xml-dir ./results/ --quiet

# Multi-framework correlation (auto-derives framework names from paths)
python run.py --xml-dir ../cypress/results --xml-dir ../selenium-java/results

# Multi-framework with explicit labels
python run.py --xml-dir ./cypress-results --framework cypress \
              --xml-dir ./selenium-results --framework selenium \
              --xml-dir ./playwright-results --framework playwright
```

**Requirements:**
- Python 3.11+
- `anthropic` SDK (`pip install anthropic`)
- `ANTHROPIC_API_KEY` environment variable
- `requests` (for DataDog metrics, optional)
- `DD_API_KEY` environment variable (optional — gracefully skips if absent)

---

## GenAI Value Proposition

This agent demonstrates a concrete GenAI artifact beyond "I use Claude for coding":

- **Cross-framework correlation**: Multi-directory input detects systemic failures across Cypress, Selenium, Playwright simultaneously
- **Tool-use architecture**: 5 tools with `@beta_tool` decorator for auto JSON schema
- **SDK-managed loop**: `client.beta.messages.tool_runner` handles the agentic cycle
- **Structured output**: JSON report with typed root cause categories and severity levels
- **Operational integration**: DataDog metrics for triage trends over time
- **Reusable parser**: Same JUnit XML parser shared with flakiness-detector

---

## DataDog Metrics

| Metric | Description |
|--------|-------------|
| `triage.total_failures` | Total test failures triaged |
| `triage.cluster_count` | Number of root cause clusters identified |
| `triage.root_cause` | Failure count per root cause category (tagged `root_cause:<category>`) |
| `triage.cross_framework_incidents` | Number of clusters affecting 2+ frameworks |

All metrics tagged with `framework:failure-triage`, `service:qa-automation-portfolio`, `env:ci`.

---

## Architecture

```
failure-triage/
├── tools.py              # 5 @beta_tool functions (read_test_results, read_multi_framework_results, search, read_source, write_report)
├── triage_agent.py       # Agent loop using client.beta.messages.tool_runner
├── run.py                # CLI entry point
├── datadog_reporter.py   # Send triage metrics to DataDog v2 API
└── README.md
```
