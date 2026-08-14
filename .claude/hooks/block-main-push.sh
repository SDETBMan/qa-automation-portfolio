#!/usr/bin/env bash
# ── Pre-push hook: block pushes to main ──────────────────────────────────────
# Receives Claude Code hook input JSON on stdin (PreToolUse for Bash).
# Exits 0 (allow) for anything that is not a push to main.
# Exits 2 (block) when the command would push to the main branch.
set -euo pipefail

# Read the hook input JSON from stdin
INPUT=$(cat)

# Extract the command field using Python (jq not available)
COMMAND=$(echo "$INPUT" | python -c "
import sys, json
data = json.load(sys.stdin)
# The Bash tool input has the command under tool_input.command
print(data.get('tool_input', {}).get('command', ''))
" 2>/dev/null || echo "")

# Fast-path: not a git push command — allow immediately
if [[ ! "$COMMAND" =~ ^[[:space:]]*git[[:space:]]+push ]]; then
    exit 0
fi

# Use Python to parse the push target robustly (handles all flag styles)
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
RESULT=$(echo "$COMMAND" | python -c "
import sys, shlex
cmd = sys.stdin.read().strip()
tokens = shlex.split(cmd)
# Find 'push' index, extract non-flag args after it
idx = tokens.index('push') + 1
args = [t for t in tokens[idx:] if not t.startswith('-')]
# args[0] = remote (if present), args[1] = refspec (if present)
if len(args) >= 2:
    # Explicit refspec — check if it targets main/master
    refspec = args[1].split(':')[-1]  # handle src:dst syntax
    print(refspec)
else:
    # No explicit branch — will push current branch
    print('__CURRENT__')
" 2>/dev/null || echo "__CURRENT__")

if [[ "$RESULT" == "main" || "$RESULT" == "master" ]]; then
    echo "BLOCKED: Pushing directly to main is not allowed."
    echo "Create a feature branch and open a pull request instead."
    echo "See CLAUDE.md: 'Never push directly to main.'"
    exit 2
fi

if [[ "$RESULT" == "__CURRENT__" ]]; then
    if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
        echo "BLOCKED: You are on '$CURRENT_BRANCH' and this push would go to main."
        echo "Switch to a feature branch before pushing."
        echo "See CLAUDE.md: 'Never push directly to main.'"
        exit 2
    fi
fi

# All other pushes are allowed
exit 0
