# ─────────────────────────────────────────────────────────────────────────────
# QA Automation Portfolio — root Makefile
#
# Usage:
#   make              → print available targets
#   make all          → run all four frameworks sequentially
#   make playwright   → playwright-dotnet (C# + TypeScript, headless Chromium)
#   make selenium     → selenium-java (headless Chrome)
#   make cucumber     → cucumber (headless Chrome)
#   make ai-eval      → ai-eval (Python + Pytest + DeepEval)
#   make clean        → remove build artefacts from all frameworks
#
# Prerequisites:
#   playwright — .NET 8 SDK (dotnet --version) · Node.js 20+ (node --version)
#   selenium   — Java 17 (java --version) · Maven 3.9+ (mvn --version)
#   cucumber   — Java 17 (java --version) · Maven 3.9+ (mvn --version)
#   ai-eval    — Python 3.11+ (python3 --version) · OPENAI_API_KEY in ai-eval/.env
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help all playwright selenium cucumber ai-eval clean

# Print help when `make` is called with no target
help:
	@echo ""
	@echo "  QA Automation Portfolio — available targets"
	@echo "  ───────────────────────────────────────────"
	@echo "  make all          Run all four frameworks sequentially"
	@echo "  make playwright   Run playwright-dotnet suite (C# + TypeScript)"
	@echo "  make selenium     Run selenium-java suite (headless Chrome)"
	@echo "  make cucumber     Run cucumber suite (headless Chrome)"
	@echo "  make ai-eval      Run AI evaluation suite (Python + DeepEval)"
	@echo "  make clean        Remove build artefacts from all frameworks"
	@echo ""
	@echo "  Prerequisites:"
	@echo "    playwright — .NET 8 SDK · Node.js 20+"
	@echo "    selenium   — Java 17 · Maven 3.9+"
	@echo "    cucumber   — Java 17 · Maven 3.9+"
	@echo "    ai-eval    — Python 3.11+ · OPENAI_API_KEY in ai-eval/.env"
	@echo ""

# ── Full portfolio ─────────────────────────────────────────────────────────────

all: playwright selenium cucumber ai-eval
	@echo ""
	@echo ">>> All four suites complete."
	@echo ""

# ── Individual suites ─────────────────────────────────────────────────────────

playwright:
	@echo ""
	@echo ">>> [playwright-dotnet] Running C# + TypeScript suite..."
	$(MAKE) -C playwright-dotnet all
	@echo ""
	@echo ">>> [playwright-dotnet] Done."
	@echo ""

selenium:
	@echo ""
	@echo ">>> [selenium-java] Running headless Chrome suite..."
	cd selenium-java && mvn clean test -Dheadless=true
	@echo ""
	@echo ">>> [selenium-java] Done."
	@echo ""

cucumber:
	@echo ""
	@echo ">>> [cucumber] Running headless Chrome suite..."
	cd cucumber && mvn clean test -Dheadless=true
	@echo ""
	@echo ">>> [cucumber] Done."
	@echo ""

ai-eval:
	@echo ""
	@echo ">>> [ai-eval] Installing dependencies and running DeepEval suite..."
	cd ai-eval && pip install -r requirements.txt -q && pytest -v
	@echo ""
	@echo ">>> [ai-eval] Done."
	@echo ""

# ── Clean ─────────────────────────────────────────────────────────────────────

clean:
	@echo ""
	@echo ">>> Cleaning playwright-dotnet artefacts..."
	$(MAKE) -C playwright-dotnet clean
	@echo ""
	@echo ">>> Cleaning selenium-java artefacts..."
	cd selenium-java && mvn clean
	@echo ""
	@echo ">>> Cleaning cucumber artefacts..."
	cd cucumber && mvn clean
	@echo ""
	@echo ">>> Cleaning ai-eval artefacts..."
	rm -rf ai-eval/.pytest_cache ai-eval/.deepeval ai-eval/__pycache__
	@echo ""
	@echo ">>> Clean complete."
	@echo ""
