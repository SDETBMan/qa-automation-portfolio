"""
parser.py — Parse JUnit XML test results.

Uses xml.etree.ElementTree (stdlib) to extract test case outcomes
from standard JUnit XML files (<testsuite>/<testcase> schema).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TestResult:
    """A single test case outcome from a JUnit XML file."""
    suite: str
    name: str
    classname: str
    time_s: float
    status: str  # "passed" | "failed" | "skipped" | "error"
    message: str = ""


@dataclass
class RunResults:
    """All test results from a single JUnit XML file (one CI run)."""
    run_id: str
    results: list[TestResult] = field(default_factory=list)


def parse_junit_xml(path: Path) -> RunResults:
    """Parse a JUnit XML file and return structured test results."""
    tree = ET.parse(path)
    root = tree.getroot()

    run_id = path.stem
    results: list[TestResult] = []

    # Handle both <testsuites><testsuite>... and <testsuite>... roots
    suites = root.findall(".//testsuite") if root.tag == "testsuites" else [root]

    for suite in suites:
        suite_name = suite.get("name", "unknown")
        for tc in suite.findall("testcase"):
            name = tc.get("name", "unknown")
            classname = tc.get("classname", "")
            time_s = float(tc.get("time", "0"))

            failure = tc.find("failure")
            error = tc.find("error")
            skipped = tc.find("skipped")

            if failure is not None:
                status = "failed"
                message = failure.get("message", "")
            elif error is not None:
                status = "error"
                message = error.get("message", "")
            elif skipped is not None:
                status = "skipped"
                message = skipped.get("message", "")
            else:
                status = "passed"
                message = ""

            results.append(TestResult(
                suite=suite_name,
                name=name,
                classname=classname,
                time_s=time_s,
                status=status,
                message=message,
            ))

    return RunResults(run_id=run_id, results=results)


def parse_directory(xml_dir: Path) -> list[RunResults]:
    """Parse all JUnit XML files in a directory."""
    runs = []
    for xml_file in sorted(xml_dir.glob("*.xml")):
        runs.append(parse_junit_xml(xml_file))
    return runs
