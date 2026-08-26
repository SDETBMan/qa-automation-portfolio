"""
tools.py — Tool definitions for the failure triage agent.

Four tools that Claude uses in a tool-use loop to read test results,
search for patterns, inspect source code, and write the final triage
report.  Uses the @beta_tool decorator for auto JSON schema generation.

Follows the coding-agent pattern (coding-agent/tools/).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from anthropic import beta_tool

# Add flakiness-detector to path for JUnit XML parser
_REPO_ROOT = Path(__file__).parent.parent
_FLAKINESS_DIR = _REPO_ROOT / "flakiness-detector"
if str(_FLAKINESS_DIR) not in sys.path:
    sys.path.insert(0, str(_FLAKINESS_DIR))

from flakiness.parser import parse_directory, parse_junit_xml  # noqa: E402


@beta_tool
def read_test_results(xml_path: str) -> str:
    """Parse JUnit XML file(s) and return a summary of all test results.

    If xml_path is a directory, all .xml files in it are parsed.
    If xml_path is a single file, only that file is parsed.

    Args:
        xml_path: Path to a JUnit XML file or directory containing XML files.
    """
    path = Path(xml_path)
    if not path.exists():
        return f"ERROR: path not found — {xml_path}"

    try:
        if path.is_dir():
            runs = parse_directory(path)
        else:
            runs = [parse_junit_xml(path)]
    except Exception as exc:
        return f"ERROR parsing XML: {exc}"

    if not runs:
        return "No test results found."

    lines: list[str] = []
    total_pass = 0
    total_fail = 0
    total_skip = 0
    total_error = 0

    for run in runs:
        lines.append(f"\n=== Run: {run.run_id} ({len(run.results)} tests) ===")
        for r in run.results:
            status_icon = {
                "passed": "PASS",
                "failed": "FAIL",
                "skipped": "SKIP",
                "error": "ERROR",
            }.get(r.status, r.status.upper())

            line = f"  [{status_icon}] {r.suite}::{r.name} ({r.time_s}s)"
            if r.message:
                line += f"\n         Message: {r.message}"
            lines.append(line)

            if r.status == "passed":
                total_pass += 1
            elif r.status == "failed":
                total_fail += 1
            elif r.status == "skipped":
                total_skip += 1
            elif r.status == "error":
                total_error += 1

    total = total_pass + total_fail + total_skip + total_error
    summary = (
        f"\n--- Summary ---\n"
        f"Total: {total}  |  Pass: {total_pass}  |  Fail: {total_fail}  "
        f"|  Skip: {total_skip}  |  Error: {total_error}"
    )
    lines.insert(0, summary)

    return "\n".join(lines)


@beta_tool
def read_multi_framework_results(xml_dirs_json: str) -> str:
    """Parse JUnit XML files from multiple framework directories.

    Each result line is prefixed with [framework_name] so failures can
    be correlated across frameworks.

    Args:
        xml_dirs_json: JSON array of objects with "path" and "framework" keys.
                       Example: [{"path": "/results/cypress", "framework": "cypress"}]
    """
    try:
        entries = json.loads(xml_dirs_json)
    except json.JSONDecodeError as exc:
        return f"ERROR: invalid JSON — {exc}"

    all_lines: list[str] = []
    total_pass = 0
    total_fail = 0
    total_skip = 0
    total_error = 0

    for entry in entries:
        dir_path = Path(entry["path"])
        framework = entry.get("framework", dir_path.name)

        if not dir_path.exists():
            all_lines.append(f"\n[{framework}] ERROR: path not found — {dir_path}")
            continue

        try:
            runs = parse_directory(dir_path) if dir_path.is_dir() else [parse_junit_xml(dir_path)]
        except Exception as exc:
            all_lines.append(f"\n[{framework}] ERROR parsing XML: {exc}")
            continue

        if not runs:
            all_lines.append(f"\n[{framework}] No test results found.")
            continue

        for run in runs:
            all_lines.append(f"\n=== [{framework}] Run: {run.run_id} ({len(run.results)} tests) ===")
            for r in run.results:
                status_icon = {
                    "passed": "PASS",
                    "failed": "FAIL",
                    "skipped": "SKIP",
                    "error": "ERROR",
                }.get(r.status, r.status.upper())

                line = f"  [{framework}] [{status_icon}] {r.suite}::{r.name} ({r.time_s}s)"
                if r.message:
                    line += f"\n         [{framework}] Message: {r.message}"
                all_lines.append(line)

                if r.status == "passed":
                    total_pass += 1
                elif r.status == "failed":
                    total_fail += 1
                elif r.status == "skipped":
                    total_skip += 1
                elif r.status == "error":
                    total_error += 1

    total = total_pass + total_fail + total_skip + total_error
    summary = (
        f"\n--- Multi-Framework Summary ---\n"
        f"Total: {total}  |  Pass: {total_pass}  |  Fail: {total_fail}  "
        f"|  Skip: {total_skip}  |  Error: {total_error}\n"
        f"Frameworks: {', '.join(e.get('framework', '?') for e in entries)}"
    )
    all_lines.insert(0, summary)

    return "\n".join(all_lines)


@beta_tool
def search_failure_patterns(results_text: str, pattern: str) -> str:
    """Search test failure messages for a specific pattern (regex).

    Lets you grep through failure messages to find related failures.

    Args:
        results_text: The text output from read_test_results.
        pattern: A regex pattern to search for in the results text.
    """
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as exc:
        return f"ERROR: invalid regex pattern — {exc}"

    matches: list[str] = []
    for line in results_text.splitlines():
        if regex.search(line):
            matches.append(line.strip())

    if not matches:
        return f"No matches found for pattern: {pattern}"

    return f"Found {len(matches)} match(es):\n" + "\n".join(matches)


@beta_tool
def read_source_file(path: str) -> str:
    """Read source code at a file path to understand test implementation.

    Args:
        path: Absolute or relative path to the source file.
    """
    try:
        content = Path(path).read_text(encoding="utf-8")
        # Truncate very large files to keep context manageable
        if len(content) > 10000:
            content = content[:10000] + "\n\n... (truncated at 10,000 characters)"
        return content
    except FileNotFoundError:
        return f"ERROR: file not found — {path}"
    except Exception as exc:
        return f"ERROR reading {path}: {exc}"


@beta_tool
def write_triage_report(report_json: str, output_path: str) -> str:
    """Write the final triage report as JSON.

    Args:
        report_json: The triage report as a JSON string.
        output_path: Path to write the JSON report file.
    """
    try:
        # Validate JSON
        parsed = json.loads(report_json)
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(parsed, indent=2),
            encoding="utf-8",
        )
        return f"Triage report written to {output_path} ({len(report_json)} bytes)"
    except json.JSONDecodeError as exc:
        return f"ERROR: invalid JSON — {exc}"
    except Exception as exc:
        return f"ERROR writing report: {exc}"
