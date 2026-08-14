#!/usr/bin/env bash
# ── Headless quality analysis ─────────────────────────────────────────────────
# Runs the quality-dashboard tool, then pipes its JSON output through Claude
# in headless mode to produce an actionable executive summary. Designed for
# scheduled runs: cron it daily or drop it into a GitHub Actions workflow.
#
# Usage:
#   ./analyze-quality.sh                                  # auto-detect XML dirs
#   ./analyze-quality.sh --xml-dir path/to/results        # specific XML dir
#   ./analyze-quality.sh --dashboard-json existing.json   # skip dashboard, analyze existing
#   ./analyze-quality.sh -o quality-insights.json         # write to file
#
# Prerequisites: claude CLI authenticated, Python 3.11+
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ── Parse arguments ──────────────────────────────────────────────────────────
XML_DIR=""
DASHBOARD_JSON=""
OUTPUT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --xml-dir)          XML_DIR="$2"; shift 2 ;;
        --dashboard-json)   DASHBOARD_JSON="$2"; shift 2 ;;
        -o|--output)        OUTPUT="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: analyze-quality.sh [--xml-dir <path>] [--dashboard-json <path>] [-o output.json]"
            exit 0 ;;
        *)
            echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

# ── Get quality dashboard data ───────────────────────────────────────────────
if [[ -n "$DASHBOARD_JSON" ]]; then
    if [[ ! -f "$DASHBOARD_JSON" ]]; then
        echo "Error: '$DASHBOARD_JSON' not found." >&2
        exit 1
    fi
    QUALITY_DATA=$(cat "$DASHBOARD_JSON")
else
    # Run the quality-dashboard tool
    QD_DIR="$REPO_ROOT/quality-dashboard"
    if [[ ! -f "$QD_DIR/run.py" ]]; then
        echo "Error: quality-dashboard/run.py not found." >&2
        exit 1
    fi

    pip install -r "$QD_DIR/requirements.txt" -q 2>/dev/null || true

    QD_ARGS=""
    if [[ -n "$XML_DIR" ]]; then
        QD_ARGS="--xml-dir $XML_DIR"
    fi

    QUALITY_DATA=$(python3 "$QD_DIR/run.py" $QD_ARGS --output /dev/stdout 2>/dev/null || echo "{}")
fi

if [[ -z "$QUALITY_DATA" || "$QUALITY_DATA" == "{}" ]]; then
    echo "No quality data available. Run tests first to generate JUnit XML." >&2
    exit 1
fi

# ── Build prompt ─────────────────────────────────────────────────────────────
PROMPT="You are a QA engineering lead reviewing the portfolio quality dashboard for a monorepo with 26 test frameworks.

Below is the JSON output from the quality-dashboard tool. It contains KPIs per framework: pass rate, failure density, average duration, p95 duration, suite stability, flakiness rate, and total test count.

Analyze this data and produce actionable insights:
- Identify frameworks that need immediate attention (low pass rates, high flakiness, degrading stability)
- Spot positive trends worth calling out
- Flag any anomalies (e.g., p95 duration >> average, suggesting intermittent slowness)
- Provide 3-5 prioritized recommendations

Quality dashboard data:
$QUALITY_DATA"

SCHEMA='{
  "type": "object",
  "properties": {
    "overall_health": {
      "type": "string",
      "enum": ["healthy", "degraded", "critical"],
      "description": "Portfolio-wide health rating"
    },
    "key_findings": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Top findings from the data"
    },
    "frameworks_needing_attention": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "framework": { "type": "string" },
          "issue": { "type": "string" },
          "metric": { "type": "string" },
          "value": { "type": "string" },
          "priority": { "type": "string", "enum": ["high", "medium", "low"] }
        },
        "required": ["framework", "issue", "metric", "value", "priority"]
      }
    },
    "positive_trends": {
      "type": "array",
      "items": { "type": "string" }
    },
    "recommendations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "action": { "type": "string" },
          "rationale": { "type": "string" },
          "priority": { "type": "string", "enum": ["high", "medium", "low"] }
        },
        "required": ["action", "rationale", "priority"]
      }
    }
  },
  "required": ["overall_health", "key_findings", "frameworks_needing_attention", "positive_trends", "recommendations"]
}'

# ── Run headless Claude ──────────────────────────────────────────────────────
RESULT=$(echo "$PROMPT" | claude -p \
    --output-format json \
    --json-schema "$SCHEMA" \
    2>/dev/null)

INSIGHTS=$(echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(json.dumps(data.get('structured_output', data), indent=2))
" 2>/dev/null || echo "$RESULT")

# ── Output ───────────────────────────────────────────────────────────────────
if [[ -n "$OUTPUT" ]]; then
    echo "$INSIGHTS" > "$OUTPUT"
    echo "Quality insights written to $OUTPUT" >&2
else
    echo "$INSIGHTS"
fi
