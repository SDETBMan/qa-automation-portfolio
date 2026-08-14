#!/usr/bin/env bash
# ── Pre-tool secret redaction ─────────────────────────────────────────────────
# Event: PreToolUse (matcher: Bash)
# Scans every Bash command for secret patterns before execution.
# On match: denies with JSON permissionDecision (never echoes the actual secret).
# No match: exits 0 silently (allow).
# Coexists with block-main-push.sh — both run in parallel under PreToolUse/Bash.
set -euo pipefail

# Read the hook input JSON from stdin
INPUT=$(cat)

# Extract the command from tool_input.command
COMMAND=$(echo "$INPUT" | python -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('command', ''))
" 2>/dev/null || echo "")

if [[ -z "$COMMAND" ]]; then
    exit 0
fi

# Use Python for robust regex matching across all patterns at once
RESULT=$(echo "$COMMAND" | python -c "
import sys, re

command = sys.stdin.read()

patterns = [
    (r'sk_live_\w+',          'Stripe live key'),
    (r'sk_test_\w+',          'Stripe test key'),
    (r'AKIA[A-Z0-9]{16}',    'AWS access key ID'),
    (r'ghp_\w+',              'GitHub PAT'),
    (r'gho_\w+',              'GitHub OAuth token'),
    (r'glpat-\w+',            'GitLab PAT'),
    (r'xoxb-\w+',             'Slack bot token'),
    (r'xoxp-\w+',             'Slack user token'),
    (r'://[^/\s]+:[^/\s]+@',  'Credentials in URL'),
]

for pattern, label in patterns:
    if re.search(pattern, command):
        print(label)
        sys.exit(0)

print('')
" 2>/dev/null || echo "")

if [[ -n "$RESULT" ]]; then
    # Deny — output reason to stderr, exit 2
    echo "BLOCKED: Command contains what appears to be a secret ($RESULT)." >&2
    echo "Remove the secret from the command and use environment variables instead." >&2
    exit 2
fi

# No secrets detected — allow
exit 0
