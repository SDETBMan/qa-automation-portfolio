"""
server.py — QA MCP Server.

Exposes five QA tools over the Model Context Protocol (stdio transport):
  1. parse_junit_xml   — Parse JUnit XML files into structured results
  2. analyze_flakiness — Detect flaky tests across multiple CI runs
  3. compute_quality_kpis — Compute pass rate, failure density, duration KPIs
  4. diff_claims       — Compare two claims CSV files field-by-field
  5. inspect_db        — Read-only Postgres queries with safety guardrails

Transport: stdio (default for Claude Code).
All logging goes to stderr to keep stdout reserved for MCP protocol wire.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

# Load .env from this directory
load_dotenv(Path(__file__).parent / ".env")

# ── sys.path setup for sibling framework imports ────────────────────────────
# Same pattern used by quality-dashboard/kpi_calculator.py and failure-triage/tools.py
_REPO_ROOT = Path(__file__).resolve().parent.parent
for _d in [
    _REPO_ROOT / "flakiness-detector",
    _REPO_ROOT / "quality-dashboard",
    _REPO_ROOT / "claims-diff",
]:
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

# ── MCPServer server ──────────────────────────────────────────────────────────
mcp = MCPServer(
    "qa-tools",
    description="QA automation tools: JUnit parsing, flakiness detection, "
    "quality KPIs, claims diffing, and database inspection.",
)

# ── Register tools ──────────────────────────────────────────────────────────
from tools.junit_parser import parse_junit_xml  # noqa: E402
from tools.flakiness import analyze_flakiness  # noqa: E402
from tools.quality_kpi import compute_quality_kpis  # noqa: E402
from tools.claims_diff import diff_claims  # noqa: E402
from tools.db_inspector import inspect_db  # noqa: E402

mcp.tool()(parse_junit_xml)
mcp.tool()(analyze_flakiness)
mcp.tool()(compute_quality_kpis)
mcp.tool()(diff_claims)
mcp.tool()(inspect_db)


if __name__ == "__main__":
    mcp.run(transport="stdio")
