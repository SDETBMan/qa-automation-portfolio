#!/usr/bin/env bash
# ── Headless failure triage ───────────────────────────────────────────────────
# Pipes JUnit XML test failures through Claude Code in headless mode to produce
# structured root-cause clusters. Designed for CI: run this after any test job
# that exits non-zero to get an actionable triage report.
#
# Usage:
#   ./triage-failures.sh <junit-xml-dir>                     # prints JSON to stdout
#   ./triage-failures.sh <junit-xml-dir> -o triage.json      # writes to file
#   ./triage-failures.sh <junit-xml-dir> --framework cypress  # adds framework context
#
# Prerequisites: claude CLI authenticated
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ── Parse arguments ──────────────────────────────────────────────────────────
XML_DIR=""
OUTPUT=""
FRAMEWORK=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)   OUTPUT="$2"; shift 2 ;;
        --framework)   FRAMEWORK="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: triage-failures.sh <junit-xml-dir> [-o output.json] [--framework name]"
            exit 0 ;;
        *)             XML_DIR="$1"; shift ;;
    esac
done

if [[ -z "$XML_DIR" ]]; then
    echo "Error: JUnit XML directory is required." >&2
    echo "Usage: triage-failures.sh <junit-xml-dir> [-o output.json] [--framework name]" >&2
    exit 1
fi

if [[ ! -d "$XML_DIR" ]]; then
    echo "Error: '$XML_DIR' is not a directory." >&2
    exit 1
fi

# ── Extract failure data from JUnit XML ──────────────────────────────────────
FAILURES=$(python3 -c "
import xml.etree.ElementTree as ET
import glob, json, os, sys

xml_dir = sys.argv[1]
files = glob.glob(os.path.join(xml_dir, '**/*.xml'), recursive=True)

if not files:
    print('NO_XML_FILES')
    sys.exit(0)

failures = []
total = 0
for f in files:
    try:
        tree = ET.parse(f)
    except ET.ParseError:
        continue
    for tc in tree.iter('testcase'):
        total += 1
        fail = tc.find('failure')
        err = tc.find('error')
        element = fail if fail is not None else err
        if element is not None:
            failures.append({
                'test': f\"{tc.get('classname', '')}.{tc.get('name', '')}\",
                'type': element.get('type', 'unknown'),
                'message': (element.get('message', '') or '')[:500],
                'file': os.path.basename(f),
            })

print(json.dumps({'total_tests': total, 'total_failures': len(failures), 'failures': failures}))
" "$XML_DIR" 2>/dev/null)

if [[ "$FAILURES" == "NO_XML_FILES" ]]; then
    echo "No JUnit XML files found in $XML_DIR" >&2
    exit 0
fi

# ── Build prompt ─────────────────────────────────────────────────────────────
FRAMEWORK_CTX=""
if [[ -n "$FRAMEWORK" ]]; then
    FRAMEWORK_CTX="These results are from the '$FRAMEWORK' framework. "
fi

PROMPT="You are a QA engineer analyzing test failures from a CI run.
${FRAMEWORK_CTX}Below is a JSON summary of all test failures extracted from JUnit XML reports.

Analyze the failures and cluster them by root cause. For each cluster:
- Identify the shared root cause (not just the symptom)
- Assign a category from: assertion_error, element_not_found, timeout, setup_failure, api_error, data_error, unknown
- Rate severity as critical (blocking release), high (major feature broken), medium (edge case), or low (cosmetic)
- Give a specific, actionable recommendation to fix the cluster

Test failure data:
$FAILURES"

SCHEMA='{
  "type": "object",
  "properties": {
    "summary": {
      "type": "string",
      "description": "One-paragraph executive summary of the test run health"
    },
    "total_tests": { "type": "integer" },
    "total_failures": { "type": "integer" },
    "clusters": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "root_cause": { "type": "string" },
          "category": {
            "type": "string",
            "enum": ["assertion_error", "element_not_found", "timeout", "setup_failure", "api_error", "data_error", "unknown"]
          },
          "severity": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low"]
          },
          "count": { "type": "integer" },
          "tests": { "type": "array", "items": { "type": "string" } },
          "recommendation": { "type": "string" }
        },
        "required": ["root_cause", "category", "severity", "count", "tests", "recommendation"]
      }
    }
  },
  "required": ["summary", "total_tests", "total_failures", "clusters"]
}'

# ── Run headless Claude ──────────────────────────────────────────────────────
RESULT=$(echo "$PROMPT" | claude -p \
    --output-format json \
    --json-schema "$SCHEMA" \
    2>/dev/null)

# Extract structured output
TRIAGE=$(echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(json.dumps(data.get('structured_output', data), indent=2))
" 2>/dev/null || echo "$RESULT")

# ── Output ───────────────────────────────────────────────────────────────────
if [[ -n "$OUTPUT" ]]; then
    echo "$TRIAGE" > "$OUTPUT"
    echo "Triage report written to $OUTPUT" >&2
else
    echo "$TRIAGE"
fi
