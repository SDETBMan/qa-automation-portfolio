#!/usr/bin/env bash
# ── Headless PR audit ─────────────────────────────────────────────────────────
# Analyzes a pull request diff against CLAUDE.md rules and produces a structured
# review. Can run locally or in CI. Uses --bare for deterministic output in
# pipelines.
#
# Usage:
#   ./audit-pr.sh                          # audits current branch vs main
#   ./audit-pr.sh --pr 42                  # audits a specific GitHub PR number
#   ./audit-pr.sh --base main --head dev   # audits diff between two refs
#   ./audit-pr.sh -o review.json           # writes to file
#   ./audit-pr.sh --ci                     # deterministic mode for CI (--bare)
#
# Prerequisites: claude CLI authenticated, git
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

# ── Parse arguments ──────────────────────────────────────────────────────────
PR_NUMBER=""
BASE_REF="main"
HEAD_REF=""
OUTPUT=""
CI_MODE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --pr)       PR_NUMBER="$2"; shift 2 ;;
        --base)     BASE_REF="$2"; shift 2 ;;
        --head)     HEAD_REF="$2"; shift 2 ;;
        -o|--output) OUTPUT="$2"; shift 2 ;;
        --ci)       CI_MODE=true; shift ;;
        -h|--help)
            echo "Usage: audit-pr.sh [--pr <number>] [--base <ref>] [--head <ref>] [-o output.json] [--ci]"
            exit 0 ;;
        *)
            echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

# ── Get the diff ─────────────────────────────────────────────────────────────
if [[ -n "$PR_NUMBER" ]]; then
    DIFF=$(gh pr diff "$PR_NUMBER" 2>/dev/null || {
        echo "Error: Could not fetch PR #$PR_NUMBER. Is gh CLI authenticated?" >&2
        exit 1
    })
    PR_TITLE=$(gh pr view "$PR_NUMBER" --json title -q '.title' 2>/dev/null || echo "")
    PR_FILES=$(gh pr view "$PR_NUMBER" --json files -q '.files[].path' 2>/dev/null || echo "")
else
    if [[ -z "$HEAD_REF" ]]; then
        HEAD_REF=$(git branch --show-current 2>/dev/null || echo "HEAD")
    fi
    DIFF=$(git diff "$BASE_REF"..."$HEAD_REF" 2>/dev/null || git diff "$BASE_REF".."$HEAD_REF" 2>/dev/null || {
        echo "Error: Could not compute diff between $BASE_REF and $HEAD_REF." >&2
        exit 1
    })
    PR_TITLE=""
    PR_FILES=$(git diff --name-only "$BASE_REF"..."$HEAD_REF" 2>/dev/null || echo "")
fi

if [[ -z "$DIFF" ]]; then
    echo "No changes found." >&2
    exit 0
fi

# Truncate very large diffs to avoid token limits
DIFF_LINES=$(echo "$DIFF" | wc -l)
if [[ $DIFF_LINES -gt 2000 ]]; then
    DIFF=$(echo "$DIFF" | head -2000)
    DIFF="$DIFF
... (truncated at 2000 lines, full diff has $DIFF_LINES lines)"
fi

# ── Read CLAUDE.md rules ─────────────────────────────────────────────────────
CLAUDE_MD=""
if [[ -f "$REPO_ROOT/CLAUDE.md" ]]; then
    CLAUDE_MD=$(cat "$REPO_ROOT/CLAUDE.md")
fi

# ── Build prompt ─────────────────────────────────────────────────────────────
TITLE_CTX=""
if [[ -n "$PR_TITLE" ]]; then
    TITLE_CTX="PR title: $PR_TITLE
"
fi

PROMPT="You are a senior QA engineer reviewing a pull request for a polyglot monorepo with 26 test frameworks.

${TITLE_CTX}Changed files:
$PR_FILES

Below are the repository coding standards (CLAUDE.md) followed by the diff. Review the diff against these standards.

Check for:
1. CLAUDE.md compliance: POM pattern violations, hardcoded test data, missing .env.example, selectors in test files, BasePage modifications
2. Framework isolation: changes in one framework shouldn't affect others
3. Test quality: proper grouping/tagging, data separation, no raw driver calls in tests
4. Security: no credentials, API keys, or secrets in the diff
5. General code quality: DRY violations, over-engineering, missing error handling at boundaries

CLAUDE.md:
$CLAUDE_MD

Diff:
$DIFF"

SCHEMA='{
  "type": "object",
  "properties": {
    "risk_level": {
      "type": "string",
      "enum": ["low", "medium", "high"],
      "description": "Overall risk level of merging this PR"
    },
    "affected_frameworks": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Frameworks touched by the changes"
    },
    "summary": {
      "type": "string",
      "description": "One-paragraph summary of what the PR does"
    },
    "review_items": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "file": { "type": "string" },
          "line": { "type": "string", "description": "Line number or range" },
          "concern": { "type": "string" },
          "severity": { "type": "string", "enum": ["info", "warning", "error"] }
        },
        "required": ["file", "concern", "severity"]
      }
    },
    "claude_md_compliance": {
      "type": "object",
      "properties": {
        "compliant": { "type": "boolean" },
        "violations": {
          "type": "array",
          "items": { "type": "string" }
        }
      },
      "required": ["compliant", "violations"]
    },
    "recommendation": {
      "type": "string",
      "enum": ["approve", "request_changes", "needs_discussion"],
      "description": "Recommended PR action"
    }
  },
  "required": ["risk_level", "affected_frameworks", "summary", "review_items", "claude_md_compliance", "recommendation"]
}'

# ── Run headless Claude ──────────────────────────────────────────────────────
CLAUDE_FLAGS="--output-format json --json-schema"

if [[ "$CI_MODE" == true ]]; then
    # --bare for deterministic CI output
    RESULT=$(echo "$PROMPT" | claude -p --bare \
        --output-format json \
        --json-schema "$SCHEMA" \
        2>/dev/null)
else
    RESULT=$(echo "$PROMPT" | claude -p \
        --output-format json \
        --json-schema "$SCHEMA" \
        2>/dev/null)
fi

REVIEW=$(echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(json.dumps(data.get('structured_output', data), indent=2))
" 2>/dev/null || echo "$RESULT")

# ── Output ───────────────────────────────────────────────────────────────────
if [[ -n "$OUTPUT" ]]; then
    echo "$REVIEW" > "$OUTPUT"
    echo "PR audit written to $OUTPUT" >&2
else
    echo "$REVIEW"
fi
