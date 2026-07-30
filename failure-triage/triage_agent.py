"""
triage_agent.py — Failure triage agent loop.

Uses Anthropic's tool_runner to orchestrate Claude through a tool-use
loop that reads JUnit XML results, clusters failures by root cause,
and produces a structured triage report.

Follows the coding-agent pattern (client.beta.messages.tool_runner).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from anthropic import Anthropic

from tools import read_source_file, read_test_results, search_failure_patterns, write_triage_report

MODEL = "claude-sonnet-4-20250514"

_SYSTEM = """\
You are a senior QA engineer performing failure triage on test results.

Your job is to read JUnit XML test results, analyze all failures and errors,
cluster them by root cause, and produce a structured triage report.

ROOT CAUSE CATEGORIES:
  - assertion_error:    expected vs actual value mismatch
  - element_not_found:  Selenium/Playwright locator failures (NoSuchElement, locator timeout)
  - timeout:            wait/network timeouts, connection timeouts
  - setup_failure:      fixture/environment/setup errors (before hooks, DB connection)
  - api_error:          HTTP status code errors, connection refused, REST API failures
  - data_error:         test data issues (missing data, wrong format, stale data)
  - unknown:            cannot be categorized into the above

SEVERITY LEVELS:
  - CRITICAL: Blocks release — core functionality broken (login, checkout, payment)
  - HIGH:     Major feature impacted — needs fix before next release
  - MEDIUM:   Non-critical path affected — can ship with known issue
  - LOW:      Cosmetic or edge case — fix in next sprint

INSTRUCTIONS:
1. Use read_test_results to parse all JUnit XML files in the input directory.
2. Identify all failures and errors from the results.
3. Use search_failure_patterns to search for common patterns across failures.
4. Optionally use read_source_file to inspect test source code for context.
5. Cluster failures by root cause category.
6. For each cluster: count affected tests, assess severity, list affected suites,
   provide a suggested action, and include 1-2 example failure messages.
7. Rank clusters by severity (CRITICAL > HIGH > MEDIUM > LOW) then by count.
8. Use write_triage_report to output the final JSON report.

OUTPUT JSON SCHEMA:
{
  "summary": {
    "total_tests": <int>,
    "total_failures": <int>,
    "clusters": <int>
  },
  "clusters": [
    {
      "root_cause": "<category>",
      "count": <int>,
      "severity": "<CRITICAL|HIGH|MEDIUM|LOW>",
      "affected_suites": ["suite1", "suite2"],
      "suggested_action": "<what to do to fix>",
      "examples": [
        { "test": "<test_name>", "message": "<failure_message>" }
      ]
    }
  ],
  "priority_order": ["<root_cause_1>", "<root_cause_2>"],
  "timestamp": "<ISO 8601>"
}
"""


def get_client() -> Anthropic:
    """Return a configured Anthropic client.

    Reads ANTHROPIC_API_KEY from the environment or a .env file.
    """
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            pass

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set.\n"
            "Export ANTHROPIC_API_KEY=<key> or create a .env file."
        )
    return Anthropic(api_key=api_key)


def run_triage(
    xml_dir: str,
    output_path: str = "triage_report.json",
    verbose: bool = True,
) -> dict:
    """Run the failure triage agent on JUnit XML results.

    Args:
        xml_dir: Path to directory containing JUnit XML files.
        output_path: Path to write the triage report JSON.
        verbose: If True, print agent messages to stdout.

    Returns:
        The triage report as a dict, or empty dict on failure.
    """
    client = get_client()
    tools = [read_test_results, search_failure_patterns, read_source_file, write_triage_report]

    timestamp = datetime.now(timezone.utc).isoformat()
    task_message = (
        f"Triage the test results in this directory: {xml_dir}\n\n"
        f"Write the triage report to: {output_path}\n\n"
        f"Use timestamp: {timestamp}\n\n"
        f"Start by reading all test results, then analyze failures, "
        f"cluster by root cause, and produce the final report."
    )

    if verbose:
        print(f"Starting failure triage agent...")
        print(f"  XML directory: {xml_dir}")
        print(f"  Output: {output_path}")
        print()

    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=8192,
        system=_SYSTEM,
        tools=tools,
        messages=[{"role": "user", "content": task_message}],
    )

    final_text = ""
    for message in runner:
        if verbose:
            for block in message.content:
                if block.type == "text" and block.text.strip():
                    print(f"[AGENT] {block.text}")
                elif block.type == "tool_use":
                    print(f"[TOOL -> {block.name}]")

        for block in message.content:
            if block.type == "text":
                final_text = block.text

    # Read the report if it was written
    report_path = Path(output_path)
    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            if verbose:
                summary = report.get("summary", {})
                print(f"\nTriage complete:")
                print(f"  Total tests: {summary.get('total_tests', '?')}")
                print(f"  Total failures: {summary.get('total_failures', '?')}")
                print(f"  Root cause clusters: {summary.get('clusters', '?')}")
            return report
        except (json.JSONDecodeError, Exception):
            pass

    if verbose:
        print(f"\n[RESULT] {final_text}")

    return {}
