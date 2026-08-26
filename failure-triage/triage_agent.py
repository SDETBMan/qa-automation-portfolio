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

from tools import (
    read_multi_framework_results,
    read_source_file,
    read_test_results,
    search_failure_patterns,
    write_triage_report,
)

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

CROSS-FRAMEWORK CORRELATION:
  When failures from multiple frameworks share the same error pattern, page,
  or component, cluster them together as a cross-framework incident. Flag
  cross-framework incidents with higher severity — simultaneous failures
  across frameworks indicate systemic issues (e.g., a UI change breaking
  Cypress, Selenium, and Playwright at the same time).

INSTRUCTIONS:
1. Use read_test_results (single directory) or read_multi_framework_results
   (multiple directories) to parse all JUnit XML files.
2. Identify all failures and errors from the results.
3. Use search_failure_patterns to search for common patterns across failures.
4. Optionally use read_source_file to inspect test source code for context.
5. Cluster failures by root cause category.
6. For each cluster: count affected tests, assess severity, list affected suites,
   list affected frameworks, provide a suggested action, and include 1-2 example
   failure messages.
7. Mark clusters as cross-framework (is_cross_framework: true) when 2+ frameworks
   are affected.
8. Rank clusters by severity (CRITICAL > HIGH > MEDIUM > LOW) then by count.
9. Use write_triage_report to output the final JSON report.

OUTPUT JSON SCHEMA:
{
  "summary": {
    "total_tests": <int>,
    "total_failures": <int>,
    "clusters": <int>,
    "cross_framework_incidents": <int>
  },
  "clusters": [
    {
      "root_cause": "<category>",
      "count": <int>,
      "severity": "<CRITICAL|HIGH|MEDIUM|LOW>",
      "affected_suites": ["suite1", "suite2"],
      "affected_frameworks": ["cypress", "selenium"],
      "is_cross_framework": <bool>,
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
    xml_sources: list[tuple[Path, str]] | None = None,
    output_path: str = "triage_report.json",
    verbose: bool = True,
    *,
    xml_dir: str | None = None,
) -> dict:
    """Run the failure triage agent on JUnit XML results.

    Args:
        xml_sources: List of (path, framework_name) tuples for multi-framework
                     correlation mode. Takes precedence over xml_dir.
        output_path: Path to write the triage report JSON.
        verbose: If True, print agent messages to stdout.
        xml_dir: Path to a single directory containing JUnit XML files
                 (backward-compatible mode). Used when xml_sources is None.

    Returns:
        The triage report as a dict, or empty dict on failure.
    """
    # Backward compatibility: convert single xml_dir to xml_sources
    if xml_sources is None:
        if xml_dir is None:
            raise ValueError("Either xml_sources or xml_dir must be provided.")
        xml_sources = [(Path(xml_dir), Path(xml_dir).name)]

    client = get_client()
    multi_framework = len(xml_sources) > 1
    tools = [read_test_results, read_multi_framework_results,
             search_failure_patterns, read_source_file, write_triage_report]

    timestamp = datetime.now(timezone.utc).isoformat()

    if multi_framework:
        dirs_json = json.dumps([
            {"path": str(p), "framework": fw} for p, fw in xml_sources
        ])
        framework_names = [fw for _, fw in xml_sources]
        task_message = (
            f"Triage the test results from multiple frameworks.\n\n"
            f"Use read_multi_framework_results with this JSON:\n{dirs_json}\n\n"
            f"Frameworks being correlated: {', '.join(framework_names)}\n\n"
            f"Write the triage report to: {output_path}\n\n"
            f"Use timestamp: {timestamp}\n\n"
            f"Start by reading all test results across all frameworks, then "
            f"analyze failures, look for cross-framework patterns (same error "
            f"across multiple frameworks), cluster by root cause, and produce "
            f"the final report with cross-framework correlation."
        )
    else:
        single_dir = str(xml_sources[0][0])
        task_message = (
            f"Triage the test results in this directory: {single_dir}\n\n"
            f"Write the triage report to: {output_path}\n\n"
            f"Use timestamp: {timestamp}\n\n"
            f"Start by reading all test results, then analyze failures, "
            f"cluster by root cause, and produce the final report."
        )

    if verbose:
        print(f"Starting failure triage agent...")
        if multi_framework:
            for p, fw in xml_sources:
                print(f"  [{fw}] {p}")
        else:
            print(f"  XML directory: {xml_sources[0][0]}")
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
                cross_fw = summary.get("cross_framework_incidents", 0)
                if cross_fw > 0:
                    print(f"  Cross-framework incidents: {cross_fw}")
            return report
        except (json.JSONDecodeError, Exception):
            pass

    if verbose:
        print(f"\n[RESULT] {final_text}")

    return {}
