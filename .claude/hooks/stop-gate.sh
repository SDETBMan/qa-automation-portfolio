#!/usr/bin/env bash
# ── Stop gate for verify-changes ──────────────────────────────────────────────
# Event: Stop (no matcher — Stop doesn't support matchers)
# Blocks Claude from finishing when test-related files were changed but
# verification hasn't run. Checks for a .verified marker file.
# Exit 0 = allow stop. Exit 2 = block stop (tell Claude to verify first).
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MARKER="$REPO_ROOT/.claude/hooks/.verified"

# Read the hook input JSON from stdin
INPUT=$(cat)

# Check stop_hook_active to prevent infinite loops
# (Claude Code also has a built-in 8-block cap)
STOP_HOOK_ACTIVE=$(echo "$INPUT" | python -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('stop_hook_active', False))
" 2>/dev/null || echo "False")

if [[ "$STOP_HOOK_ACTIVE" == "True" ]]; then
    exit 0
fi

# ── Gather changed files (staged + unstaged + untracked) ──────────────────────
CHANGED_FILES=""
DIFF_FILES=$(git diff --name-only HEAD 2>/dev/null || true)
UNTRACKED_FILES=$(git ls-files --others --exclude-standard 2>/dev/null || true)

if [[ -n "$DIFF_FILES" ]]; then
    CHANGED_FILES="$DIFF_FILES"
fi
if [[ -n "$UNTRACKED_FILES" ]]; then
    if [[ -n "$CHANGED_FILES" ]]; then
        CHANGED_FILES="$CHANGED_FILES"$'\n'"$UNTRACKED_FILES"
    else
        CHANGED_FILES="$UNTRACKED_FILES"
    fi
fi

if [[ -z "$CHANGED_FILES" ]]; then
    exit 0
fi

# ── Check for test-related patterns ───────────────────────────────────────────
TEST_RELATED=$(echo "$CHANGED_FILES" | python -c "
import sys, re

patterns = [
    r'.*/pages/.*',
    r'.*/e2e/.*\.cy\.ts$',
    r'.*/tests/.*Test\.java$',
    r'.*/tests/.*\.spec\.ts$',
    r'.*/Tests/.*Test\.cs$',
    r'.*/steps/.*\.py$',
    r'.*/stepDefinitions/.*',
    r'\.github/workflows/.*\.yml$',
    r'.*/tests/test_.*\.py$',
]

found = []
for line in sys.stdin:
    path = line.strip()
    if not path:
        continue
    for pattern in patterns:
        if re.search(pattern, path):
            found.append(path)
            break

if found:
    print('\n'.join(found))
" 2>/dev/null || echo "")

if [[ -z "$TEST_RELATED" ]]; then
    # No test-related changes — allow stop
    exit 0
fi

# ── Check .verified marker ────────────────────────────────────────────────────
if [[ -f "$MARKER" ]]; then
    # Check if marker is recent (< 4 hours = 14400 seconds)
    MARKER_TIME=""
    NOW=$(date +%s)

    if stat --version &>/dev/null 2>&1; then
        MARKER_TIME=$(stat -c %Y "$MARKER" 2>/dev/null || echo "")
    else
        MARKER_TIME=$(stat -f %m "$MARKER" 2>/dev/null || echo "")
    fi

    if [[ -n "$MARKER_TIME" ]]; then
        AGE=$(( NOW - MARKER_TIME ))
        if [[ $AGE -lt 14400 ]]; then
            # Marker exists and is recent — allow stop
            exit 0
        fi
        echo "Verification marker is stale ($(( AGE / 3600 ))h old). Re-run verification." >&2
    else
        # Can't determine age — treat as valid
        exit 0
    fi
fi

# ── Block: test-related changes without verification ──────────────────────────
echo "BLOCKED: Test-related files were changed but verification has not run." >&2
echo "" >&2
echo "Changed test-related files:" >&2
echo "$TEST_RELATED" | sed 's/^/  /' >&2
echo "" >&2
echo "Run the verify-changes skill before finishing:" >&2
echo "  Use /verify-changes to detect and test affected frameworks." >&2
echo "  The verification marker will be created on success." >&2
exit 2
