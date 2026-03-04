# ─────────────────────────────────────────────────────────────────────────────
# QA Automation Portfolio — root Makefile
#
# Usage:
#   make              → print available targets
#   make all          → run all five frameworks sequentially
#   make playwright   → playwright-dotnet (C# + TypeScript, headless Chromium)
#   make selenium     → selenium-java (headless Chrome)
#   make cucumber     → cucumber (headless Chrome)
#   make ai-eval      → ai-eval (Python + Pytest + DeepEval)
#   make postman      → postman (Newman CLI, JSONPlaceholder API tests)
#   make clean        → remove build artefacts from all frameworks
#
# Prerequisites:
#   playwright — .NET 8 SDK (dotnet --version) · Node.js 20+ (node --version)
#   selenium   — Java 17 (java --version) · Maven 3.9+ (mvn --version)
#   cucumber   — Java 17 (java --version) · Maven 3.9+ (mvn --version)
#   ai-eval    — Python 3.11+ (python3 --version) · OPENAI_API_KEY in ai-eval/.env
#   postman    — Node.js 20+ (node --version)
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: help all playwright selenium cucumber ai-eval postman job-agent fastapi-service fastapi-service-test cypress-test cypress-open clean

# Print help when `make` is called with no target
help:
	@echo ""
	@echo "  QA Automation Portfolio — available targets"
	@echo "  ───────────────────────────────────────────"
	@echo "  make all                  Run all five frameworks sequentially"
	@echo "  make cypress-test         Run Cypress E2E suite (headless Chrome)"
	@echo "  make cypress-open         Open Cypress interactive Test Runner"
	@echo "  make job-agent            Run Claude-powered job search agent"
	@echo "  make playwright           Run playwright-dotnet suite (C# + TypeScript)"
	@echo "  make selenium             Run selenium-java suite (headless Chrome)"
	@echo "  make cucumber             Run cucumber suite (headless Chrome)"
	@echo "  make ai-eval              Run AI evaluation suite (Python + DeepEval)"
	@echo "  make postman              Run Postman/Newman API test suite"
	@echo "  make fastapi-service      Start FastAPI server on :8001"
	@echo "  make fastapi-service-test Run FastAPI pytest suite"
	@echo "  make clean                Remove build artefacts from all frameworks"
	@echo ""
	@echo "  Prerequisites:"
	@echo "    playwright       — .NET 8 SDK · Node.js 20+"
	@echo "    selenium         — Java 17 · Maven 3.9+"
	@echo "    cucumber         — Java 17 · Maven 3.9+"
	@echo "    ai-eval          — Python 3.11+ · OPENAI_API_KEY in ai-eval/.env"
	@echo "    postman          — Node.js 20+"
	@echo "    job-agent        — Python 3.11+ · ANTHROPIC_API_KEY · TAVILY_API_KEY in job-agent/.env"
	@echo "    fastapi-service  — Python 3.11+"
	@echo "    cypress          — Node.js 20+"
	@echo ""

# ── Full portfolio ─────────────────────────────────────────────────────────────

all: playwright selenium cucumber ai-eval postman
	@echo ""
	@echo ">>> All five suites complete."
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

postman:
	@echo ""
	@echo ">>> [postman] Installing Newman and running API test suite..."
	cd postman && npm install && npm test
	@echo ""
	@echo ">>> [postman] Done."
	@echo ""

job-agent:
	@echo ""
	@echo ">>> [job-agent] Running job search..."
	cd job-agent && pip install -r requirements.txt -q && python run.py
	@echo ""
	@echo ">>> [job-agent] Done. Results in job-agent/output/"
	@echo ""

fastapi-service:
	@echo ""
	@echo ">>> [fastapi-service] Starting API server..."
	cd fastapi-service && pip install -r requirements.txt -q && \
		uvicorn app.main:app --reload --port 8001
	@echo ""

fastapi-service-test:
	@echo ""
	@echo ">>> [fastapi-service] Running tests..."
	cd fastapi-service && pip install -r requirements.txt -q && \
		pytest tests/ -v --cov=app --cov-report=term-missing
	@echo ""

cypress-test:
	@echo ""
	@echo ">>> [cypress] Running Cypress tests..."
	cd cypress && npm ci --quiet && npm test
	@echo ""

cypress-open:
	@echo ""
	@echo ">>> [cypress] Opening Cypress Test Runner..."
	cd cypress && npm ci --quiet && npx cypress open
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
	@echo ">>> Cleaning postman artefacts..."
	rm -rf postman/node_modules postman/results/*.xml postman/results/*.html
	@echo ""
	@echo ">>> Clean complete."
	@echo ""
