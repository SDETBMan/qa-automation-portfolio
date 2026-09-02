"""Shared test fixtures for qa-mcp-server tests.

Provides sample JUnit XML content, claims CSV content, and temporary
file/directory fixtures for tool wrapper tests.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

# ── sys.path setup (mirrors server.py) ──────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SERVER_DIR = Path(__file__).resolve().parent.parent

for _d in [
    _SERVER_DIR,
    _REPO_ROOT / "flakiness-detector",
    _REPO_ROOT / "quality-dashboard",
    _REPO_ROOT / "claims-diff",
]:
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))


# ── Sample JUnit XML ────────────────────────────────────────────────────────

SAMPLE_JUNIT_XML = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <testsuites>
      <testsuite name="test_login" tests="3" failures="1" errors="0" time="2.5">
        <testcase classname="tests.test_login" name="test_valid_login" time="0.8"/>
        <testcase classname="tests.test_login" name="test_invalid_creds" time="0.6">
          <failure message="Expected error message">Wrong message shown</failure>
        </testcase>
        <testcase classname="tests.test_login" name="test_locked_user" time="1.1">
          <skipped message="Known issue #42"/>
        </testcase>
      </testsuite>
    </testsuites>
""")

SAMPLE_JUNIT_XML_RUN2 = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <testsuites>
      <testsuite name="test_login" tests="3" failures="0" errors="0" time="2.3">
        <testcase classname="tests.test_login" name="test_valid_login" time="0.7"/>
        <testcase classname="tests.test_login" name="test_invalid_creds" time="0.5"/>
        <testcase classname="tests.test_login" name="test_locked_user" time="1.1">
          <skipped message="Known issue #42"/>
        </testcase>
      </testsuite>
    </testsuites>
""")

SAMPLE_JUNIT_XML_RUN3 = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <testsuites>
      <testsuite name="test_login" tests="3" failures="1" errors="0" time="2.6">
        <testcase classname="tests.test_login" name="test_valid_login" time="0.9"/>
        <testcase classname="tests.test_login" name="test_invalid_creds" time="0.7">
          <failure message="Timeout waiting for element">Element not found</failure>
        </testcase>
        <testcase classname="tests.test_login" name="test_locked_user" time="1.0">
          <skipped message="Known issue #42"/>
        </testcase>
      </testsuite>
    </testsuites>
""")


@pytest.fixture
def sample_xml_file(tmp_path: Path) -> Path:
    """Write a single JUnit XML file and return its path."""
    xml_file = tmp_path / "results.xml"
    xml_file.write_text(SAMPLE_JUNIT_XML, encoding="utf-8")
    return xml_file


@pytest.fixture
def sample_xml_dir(tmp_path: Path) -> Path:
    """Write multiple JUnit XML files to a directory and return the dir."""
    for name, content in [
        ("run-001.xml", SAMPLE_JUNIT_XML),
        ("run-002.xml", SAMPLE_JUNIT_XML_RUN2),
        ("run-003.xml", SAMPLE_JUNIT_XML_RUN3),
    ]:
        (tmp_path / name).write_text(content, encoding="utf-8")
    return tmp_path


# ── Sample Claims CSV ───────────────────────────────────────────────────────

SAMPLE_BASELINE_CSV = textwrap.dedent("""\
    claim_id,patient_id,procedure_code,billed_cents,allowed_cents,paid_cents,status,adjudication_date
    CLM-001,PAT-101,99213,15000,12000,9600,paid,2026-01-15
    CLM-002,PAT-102,99214,25000,20000,16000,paid,2026-01-16
    CLM-003,PAT-103,99215,35000,28000,22400,paid,2026-01-17
""")

SAMPLE_CURRENT_CSV = textwrap.dedent("""\
    claim_id,patient_id,procedure_code,billed_cents,allowed_cents,paid_cents,status,adjudication_date
    CLM-001,PAT-101,99213,15000,12000,9600,paid,2026-01-15
    CLM-002,PAT-102,99214,25000,20000,18000,paid,2026-01-16
    CLM-004,PAT-104,99203,18000,14400,11520,paid,2026-01-18
""")


@pytest.fixture
def claims_csv_pair(tmp_path: Path) -> tuple[Path, Path]:
    """Write baseline and current claims CSVs and return both paths."""
    baseline = tmp_path / "baseline.csv"
    current = tmp_path / "current.csv"
    baseline.write_text(SAMPLE_BASELINE_CSV, encoding="utf-8")
    current.write_text(SAMPLE_CURRENT_CSV, encoding="utf-8")
    return baseline, current
