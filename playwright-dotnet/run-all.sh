#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run-all.sh — One-command full suite runner for PlaywrightDotNetFramework
#
# Runs: C# / NUnit tests  +  TypeScript Playwright tests
#
# Usage:
#   chmod +x run-all.sh && ./run-all.sh          (Linux / macOS / Git Bash)
#   bash run-all.sh                               (any bash environment)
#
# Prerequisites: .NET 8 SDK  (dotnet --version ≥ 8.0)
#                Node.js 20+ (node --version)
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

step()  { echo -e "\n${CYAN}${BOLD}>>> $*${RESET}"; }
ok()    { echo -e "${GREEN}    ✔  $*${RESET}"; }
fail()  { echo -e "${RED}    ✘  $*${RESET}"; }

# ── Banner ────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}╔══════════════════════════════════════════════════════╗"
echo    "║   PlaywrightDotNetFramework — Full Suite Runner      ║"
echo -e "╚══════════════════════════════════════════════════════╝${RESET}"

# ── Prerequisite checks ───────────────────────────────────────────────────────
step "Checking prerequisites..."

if ! command -v dotnet &> /dev/null; then
  fail ".NET SDK not found. Install from https://dotnet.microsoft.com/download/dotnet/8"
  exit 1
fi
ok ".NET SDK: $(dotnet --version)"

if ! command -v node &> /dev/null; then
  fail "Node.js not found. Install from https://nodejs.org (v20 LTS recommended)"
  exit 1
fi
ok "Node.js: $(node --version)"

if ! command -v npx &> /dev/null; then
  fail "npx not found. Run: npm install -g npm"
  exit 1
fi
ok "npx: $(npx --version)"

# ── .NET setup ────────────────────────────────────────────────────────────────
step "[1/6] Restoring .NET dependencies..."
dotnet restore PlaywrightDotNetFramework.sln
ok "Restore complete."

step "[2/6] Building solution (Release)..."
dotnet build PlaywrightDotNetFramework.sln --configuration Release --no-restore
ok "Build complete."

step "[3/6] Installing Playwright browsers for C# suite..."
npx --yes playwright@1.44.0 install chromium
ok "C# Playwright browsers installed."

# ── TypeScript setup ──────────────────────────────────────────────────────────
step "[4/6] Installing TypeScript dependencies..."
cd tests/playwright-ts
npm install
ok "npm install complete."

step "[5/6] Installing Playwright browsers for TypeScript suite..."
npx playwright install chromium
ok "TypeScript Playwright browsers installed."
cd ../..

# ── C# tests ─────────────────────────────────────────────────────────────────
step "[6a/6] Running C# / NUnit tests (headless Chromium, 4 workers)..."
CS_EXIT=0
dotnet test PlaywrightDotNetFramework.sln \
  --settings ci.runsettings \
  --configuration Release \
  --no-build \
  --logger "console;verbosity=normal" \
  --results-directory TestResults || CS_EXIT=$?

if [ $CS_EXIT -eq 0 ]; then
  ok "C# tests passed."
else
  fail "C# tests finished with exit code $CS_EXIT (see output above)."
fi

# ── TypeScript tests ──────────────────────────────────────────────────────────
step "[6b/6] Running TypeScript Playwright tests (Chromium)..."
TS_EXIT=0
cd tests/playwright-ts
npx playwright test --project=chromium || TS_EXIT=$?
cd ../..

if [ $TS_EXIT -eq 0 ]; then
  ok "TypeScript tests passed."
else
  fail "TypeScript tests finished with exit code $TS_EXIT (see output above)."
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}──────────────────── Summary ────────────────────────${RESET}"

if [ $CS_EXIT -eq 0 ]; then
  echo -e "  ${GREEN}✔  C# / NUnit suite        PASSED${RESET}"
else
  echo -e "  ${RED}✘  C# / NUnit suite        FAILED (exit $CS_EXIT)${RESET}"
fi

if [ $TS_EXIT -eq 0 ]; then
  echo -e "  ${GREEN}✔  TypeScript Playwright    PASSED${RESET}"
else
  echo -e "  ${RED}✘  TypeScript Playwright    FAILED (exit $TS_EXIT)${RESET}"
fi

echo ""
echo -e "  TypeScript HTML report:"
echo    "    cd tests/playwright-ts && npx playwright show-report"
echo ""

# Exit non-zero if either suite failed
if [ $CS_EXIT -ne 0 ] || [ $TS_EXIT -ne 0 ]; then
  exit 1
fi

echo -e "${GREEN}${BOLD}All tests passed.${RESET}\n"
