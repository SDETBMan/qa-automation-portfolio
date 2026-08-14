#!/usr/bin/env bash
# ── Post-edit auto-format ─────────────────────────────────────────────────────
# Event: PostToolUse (matcher: Edit|Write)
# After every Write or Edit, formats the file by extension and invalidates
# the .verified marker when test-related files are edited.
# Exit: Always 0. PostToolUse can't block (tool already ran).
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Read the hook input JSON from stdin
INPUT=$(cat)

# Extract the file path from tool_input.file_path
FILE_PATH=$(echo "$INPUT" | python -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('file_path', ''))
" 2>/dev/null || echo "")

if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

# ── Format by extension ──────────────────────────────────────────────────────
EXT="${FILE_PATH##*.}"

case "$EXT" in
    tf)
        if command -v terraform &>/dev/null; then
            terraform fmt "$FILE_PATH" 2>&1 >&2 || true
        fi
        ;;
    py)
        if command -v ruff &>/dev/null; then
            ruff format "$FILE_PATH" 2>&1 >&2 || true
        elif command -v black &>/dev/null; then
            black --quiet "$FILE_PATH" 2>&1 >&2 || true
        fi
        ;;
    *)
        # No formatter for this extension
        ;;
esac

# ── Invalidate .verified marker for test-related files ────────────────────────
# Convert to repo-relative path for pattern matching
REL_PATH="${FILE_PATH#"$REPO_ROOT"/}"
# Also try normalizing Windows-style paths
REL_PATH="${REL_PATH//\\//}"

MARKER="$REPO_ROOT/.claude/hooks/.verified"

is_test_related() {
    local path="$1"
    # Page objects
    [[ "$path" == */pages/* ]] && return 0
    # Cypress e2e tests
    [[ "$path" == */e2e/*.cy.ts ]] && return 0
    # Java tests
    [[ "$path" == */tests/*Test.java ]] && return 0
    # Playwright TS specs
    [[ "$path" == */tests/*.spec.ts ]] && return 0
    # C# NUnit tests
    [[ "$path" == */Tests/*Test.cs ]] && return 0
    # Python Behave steps
    [[ "$path" == */steps/*.py ]] && return 0
    # Java/Cucumber step definitions
    [[ "$path" == */stepDefinitions/* ]] && return 0
    # CI workflows
    [[ "$path" == .github/workflows/*.yml ]] && return 0
    # Python pytest tests
    [[ "$path" == */tests/test_*.py ]] && return 0
    return 1
}

if is_test_related "$REL_PATH"; then
    if [[ -f "$MARKER" ]]; then
        rm -f "$MARKER"
        echo "Verification marker invalidated — test-related file changed: $REL_PATH" >&2
    fi
fi

exit 0
