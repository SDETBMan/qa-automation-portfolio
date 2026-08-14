#!/usr/bin/env bash
# ── Compaction state preserver ────────────────────────────────────────────────
# Event: SessionStart (matcher: compact)
# Prints ephemeral working state to stdout after compaction so it gets
# re-injected into Claude's context. CLAUDE.md is reloaded automatically;
# this covers git state and verification status that compaction loses.
# Exit: Always 0 (SessionStart ignores blocking; stdout is what matters).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== Post-compaction working state ==="
echo ""

# Current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "(detached)")
echo "Branch: $BRANCH"
echo ""

# Last 5 commits
echo "Recent commits:"
git log --oneline -5 2>/dev/null || echo "  (no commits)"
echo ""

# Staged files
STAGED=$(git diff --cached --name-only 2>/dev/null || true)
if [[ -n "$STAGED" ]]; then
    echo "Staged files:"
    echo "$STAGED" | sed 's/^/  /'
    echo ""
fi

# Uncommitted changes (unstaged + untracked)
DIFF_STAT=$(git diff --stat HEAD 2>/dev/null || true)
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null || true)

if [[ -n "$DIFF_STAT" || -n "$UNTRACKED" ]]; then
    echo "Uncommitted changes:"
    if [[ -n "$DIFF_STAT" ]]; then
        echo "$DIFF_STAT" | sed 's/^/  /'
    fi
    if [[ -n "$UNTRACKED" ]]; then
        echo "  Untracked files:"
        echo "$UNTRACKED" | sed 's/^/    /'
    fi
    echo ""
fi

# Verification marker status
MARKER="$REPO_ROOT/.claude/hooks/.verified"
if [[ -f "$MARKER" ]]; then
    MARKER_AGE=""
    if command -v stat &>/dev/null; then
        # Get modification time — works on both GNU and BSD stat
        if stat --version &>/dev/null 2>&1; then
            MARKER_TIME=$(stat -c %Y "$MARKER" 2>/dev/null || echo "")
        else
            MARKER_TIME=$(stat -f %m "$MARKER" 2>/dev/null || echo "")
        fi
        if [[ -n "$MARKER_TIME" ]]; then
            NOW=$(date +%s)
            AGE_MINS=$(( (NOW - MARKER_TIME) / 60 ))
            MARKER_AGE=" (${AGE_MINS}m ago)"
        fi
    fi
    echo "Verification: PASSED${MARKER_AGE}"
else
    echo "Verification: NOT VERIFIED (run verify-changes before finishing)"
fi

echo ""
echo "=== End working state ==="
