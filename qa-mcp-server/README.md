# qa-mcp-server

MCP (Model Context Protocol) server that exposes five QA automation tools to Claude Code over stdio transport. Wraps four existing frameworks from the monorepo and adds read-only Postgres inspection.

## Tech Stack

| Component | Version |
|---|---|
| Python | 3.11+ |
| MCPServer | mcp[cli] >= 1.0.0 |
| psycopg2-binary | >= 2.9.9 |
| Pydantic | >= 2.0.0 |
| Pandas | >= 2.0.0 |
| Pytest | >= 8.0.0 |

## Tools

| Tool | Description | Source |
|---|---|---|
| `parse_junit_xml` | Parse JUnit XML files into structured JSON (summary + per-test results) | flakiness-detector/flakiness/parser.py |
| `analyze_flakiness` | Detect flaky tests across multiple CI runs from JUnit XML | flakiness-detector/flakiness/analyzer.py |
| `compute_quality_kpis` | Compute pass rate, failure density, duration KPIs | quality-dashboard/kpi_calculator.py |
| `diff_claims` | Compare two claims CSV files with field-level diffs | claims-diff/differ/diff_engine.py |
| `inspect_db` | Read-only Postgres queries with 5 safety guardrail layers | New (psycopg2) |

## Architecture

```
Claude Code ──(stdio)──> server.py (MCPServer)
                              |
                              ├── parse_junit_xml     -> flakiness.parser
                              ├── analyze_flakiness   -> flakiness.analyzer
                              ├── compute_quality_kpis -> kpi_calculator
                              ├── diff_claims          -> differ.diff_engine
                              └── inspect_db           -> psycopg2 (read-only)
```

Transport: stdio (default for Claude Code). All logging goes to stderr to keep stdout reserved for the MCP protocol wire.

## Database Inspector Guardrails

The `inspect_db` tool enforces 5 safety layers:

1. **SQL keyword validation** — only `SELECT`, `WITH`, `EXPLAIN` allowed as first keyword
2. **DML/DDL blocking** — 16 keywords blocked via word-boundary regex (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `GRANT`, `REVOKE`, `COMMIT`, `ROLLBACK`, `BEGIN`, `SAVEPOINT`, `COPY`, `EXECUTE`, `LOCK`)
3. **Multi-statement prevention** — semicolons between statements rejected
4. **Read-only transaction** — `connection.set_session(readonly=True, autocommit=True)`
5. **Row limit cap** — clamped to [1, 1000], fetched via `cursor.fetchmany()`

## How to Run

### Prerequisites

- Python 3.11+
- (Optional) PostgreSQL for `inspect_db`

### Install

```bash
cd qa-mcp-server
pip install -r requirements.txt
```

### Claude Code Integration

The root `.mcp.json` auto-registers this server with Claude Code:

```json
{
  "mcpServers": {
    "qa-tools": {
      "type": "stdio",
      "command": "python",
      "args": ["qa-mcp-server/server.py"]
    }
  }
}
```

### MCP Inspector (manual testing)

```bash
cd qa-mcp-server
mcp dev server.py
```

### Run Tests

```bash
cd qa-mcp-server
pip install -r requirements.txt
pytest tests/ -v

# From repo root
make mcp-server-test
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | For `inspect_db` | PostgreSQL connection string (`postgresql://user:pass@host:port/db`) |
| `DD_API_KEY` | No | DataDog API key (metrics skip silently when absent) |
| `DD_SITE` | No | DataDog site (default: `datadoghq.com`) |

## DataDog Metrics

All metrics tagged with `tool:<name>`, `service:qa-automation-portfolio`, `env:ci`:

| Metric | Description |
|---|---|
| `mcp.tool_invocations` | Count of tool calls |
| `mcp.tool_errors` | Count of tool errors |
| `mcp.tool_duration_ms` | Tool execution time in milliseconds |

## Repo Structure

```
qa-mcp-server/
├── server.py                  # MCPServer server, sys.path setup, tool registration
├── tools/
│   ├── __init__.py
│   ├── junit_parser.py        # Wraps flakiness.parser
│   ├── flakiness.py           # Wraps flakiness.analyzer
│   ├── quality_kpi.py         # Wraps kpi_calculator
│   ├── claims_diff.py         # Wraps differ.diff_engine + differ.loader
│   └── db_inspector.py        # Read-only Postgres with 5 guardrail layers
├── utils/
│   ├── __init__.py
│   └── datadog_reporter.py    # Optional DD metrics
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Shared fixtures (sample XML, sample CSV)
│   ├── test_junit_parser.py
│   ├── test_flakiness.py
│   ├── test_quality_kpi.py
│   ├── test_claims_diff.py
│   └── test_db_inspector.py
├── requirements.txt
├── .env.example
├── pytest.ini
└── README.md
```
