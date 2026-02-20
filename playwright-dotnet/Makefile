# ─────────────────────────────────────────────────────────────────────────────
# PlaywrightDotNetFramework — Makefile
#
# Usage:
#   make          → print available targets
#   make all      → setup + C# tests + TypeScript tests (full suite)
#   make setup    → install all dependencies + Playwright browsers
#   make test     → run C# + TypeScript tests (skip setup)
#   make test-cs  → run C# tests only
#   make test-ts  → run TypeScript tests only (Chromium)
#   make report   → open TypeScript Playwright HTML report
#   make clean    → remove build artefacts and test output
#
# Prerequisites: .NET 8 SDK   (dotnet --version)
#                Node.js 20+  (node --version)
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help all setup install-browsers test test-cs test-ts report clean

# Print help when `make` is called with no target
help:
	@echo ""
	@echo "  PlaywrightDotNetFramework — available targets"
	@echo "  ─────────────────────────────────────────────"
	@echo "  make all       Full suite: setup → C# tests → TypeScript tests"
	@echo "  make setup     Install .NET deps, npm deps, and Playwright browsers"
	@echo "  make test      Run both C# and TypeScript tests (assumes setup done)"
	@echo "  make test-cs   Run C# / NUnit tests only"
	@echo "  make test-ts   Run TypeScript Playwright tests (Chromium)"
	@echo "  make report    Open TypeScript HTML report"
	@echo "  make clean     Remove build artefacts and test output"
	@echo ""

# ── Full pipeline ─────────────────────────────────────────────────────────────

all: setup test

# ── Setup ─────────────────────────────────────────────────────────────────────

setup:
	@echo "\n>>> [1/4] Restoring .NET dependencies..."
	dotnet restore PlaywrightDotNetFramework.sln

	@echo "\n>>> [2/4] Building solution..."
	dotnet build PlaywrightDotNetFramework.sln --configuration Release --no-restore

	@echo "\n>>> [3/4] Installing Playwright browsers for C# suite..."
	npx --yes playwright@1.44.0 install chromium

	@echo "\n>>> [4/4] Installing TypeScript dependencies and Playwright browsers..."
	cd tests/playwright-ts && npm install
	cd tests/playwright-ts && npx playwright install chromium

	@echo "\n>>> Setup complete.\n"

# ── Tests ─────────────────────────────────────────────────────────────────────

test: test-cs test-ts

test-cs:
	@echo "\n>>> Running C# / NUnit tests (headless Chromium, 4 workers)..."
	dotnet test PlaywrightDotNetFramework.sln \
		--settings ci.runsettings \
		--configuration Release \
		--no-build \
		--logger "console;verbosity=normal" \
		--results-directory TestResults
	@echo "\n>>> C# tests complete.\n"

test-ts:
	@echo "\n>>> Running TypeScript Playwright tests (Chromium)..."
	cd tests/playwright-ts && npx playwright test --project=chromium
	@echo "\n>>> TypeScript tests complete.\n"

# ── Report ────────────────────────────────────────────────────────────────────

report:
	@echo "\n>>> Opening TypeScript Playwright HTML report..."
	cd tests/playwright-ts && npx playwright show-report

# ── Clean ─────────────────────────────────────────────────────────────────────

clean:
	@echo "\n>>> Cleaning build artefacts..."
	dotnet clean PlaywrightDotNetFramework.sln --configuration Release
	rm -rf TestResults allure-results allure-report traces
	rm -rf tests/playwright-ts/playwright-report
	rm -rf tests/playwright-ts/test-results
	@echo "\n>>> Clean complete.\n"
