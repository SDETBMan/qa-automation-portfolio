# CLAUDE.md — QA Automation Portfolio

## Repository overview

Polyglot monorepo with 26 independent QA/SDET frameworks across 6 languages (TypeScript, Java, C#, Python, JavaScript, HCL), plus 3 companion repos. Each sub-project is self-contained with its own dependencies, config, tests, and CI workflow. The repo targets SauceDemo, a Shopify test store, and custom FastAPI services as systems under test.

## Branching and commits

- **Never push directly to `main`.** Create a feature or fix branch (`dev`, `feature/*`, `fix/*`) and merge via PR.
- Write concise, conventional commit messages: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `ci:`.
- Never commit `.env` files, credentials, API keys, or secrets. Each framework provides a `.env.example` template — reference that pattern when adding new config.

## Monorepo structure

Each directory is an independent framework. Changes to one should not break another.

```
# Browser / E2E
cypress/               TypeScript — Cypress 15, React 18, Vite
playwright/            C# + TypeScript — Playwright 1.52, .NET 8, NUnit
selenium-java/         Java — Selenium 4, TestNG 7.10, Maven, Appium

# BDD
cucumber/              Java — Cucumber 7, Karate 1.5, TestNG, Selenium
cucumber_python/       Python — Behave, Selenium

# API / Service
postman/               JSON/JS — Newman 6.2.1
fastapi-service/       Python — FastAPI, Redis, Pytest, k6
pact-consumer/         TypeScript — Pact v13, Vitest, pact-python verifier

# LLM Evaluation
ai-eval/               Python — DeepEval, Pytest, OpenAI, ChromaDB
conv-eval/             Python — DeepEval, Pytest, OpenAI
agent-eval/            Python — DeepEval, Pytest, OpenAI, Pydantic

# AI Agents
job-agent/             Python — Anthropic Claude, Tavily, AgentOps
coding-agent/          Python — Anthropic Claude, AgentOps
failure-triage/        Python — Anthropic Claude (tool use), JUnit XML, DataDog

# LLM Frameworks
langchain-rag/         Python — LangChain 0.3, LCEL, ChromaDB, Langfuse
langgraph-agent/       Python — LangGraph 0.4, LangChain Anthropic
dspy-optimizer/        Python — DSPy 2.6, OpenAI
dspy-vertex/           Python — DSPy 2.6, Vertex AI Gemini

# Data & Analytics
claims-diff/           Python — Pandas, Pydantic, BigQuery (optional)
flakiness-detector/    Python — JUnit XML, Click, DataDog
quality-dashboard/     Python — JUnit XML, DataDog v2 API, GitHub Actions API
site-monitor/          Python — BeautifulSoup, Click, DataDog, Requests
vulnerability-aggregator/ Python — GitHub API, Dependabot, CodeQL, ZAP
dependency-audit/      Python — Click, npm/PyPI/NuGet/Maven registries
branch-collision-monitor/ Python — GitHub API (gh CLI), Anthropic Claude, DataDog

# MCP Server
qa-mcp-server/         Python — FastMCP, psycopg2, Pydantic, DataDog

# QMS & Compliance
qms-evidence-collector/ Python — Click, ISO 9001, SOC 2, ISO/IEC 17025, DataDog

# Infrastructure
terraform/             HCL — Terraform >= 1.6, AWS, DataDog
k8s/                   YAML — Kubernetes manifests, Selenium Grid, Healenium

# Automation (Claude Code)
automation/headless/   Bash — claude -p scripts for CI pipelines
automation/agent-sdk/  TypeScript — Agent SDK portfolio health orchestrator
automation/routines/   Markdown — Routine prompts for cloud-managed schedules

# Companion repos (external)
# legal-funding-qa-agent  — Python, LangGraph, DSPy, Hypothesis, Claude
# agentic-p2p-auditor     — Python, Claude (tool use), Decimal math
# ai-pr-reviewer          — JavaScript, Claude, promptfoo, Docker
```

## Architecture principles — follow these in all changes

### Page Object Model (POM)

Every browser framework uses POM with a shared `BasePage` superclass. Locators and page interactions live in page objects, never in test files. When adding or modifying UI interactions:

- Put locators and actions in the appropriate page class under `pages/`.
- Extend `BasePage` — use its `waitForVisibility`, `click`, `getText` utilities instead of raw driver calls.
- If a new page is needed, create a new class extending `BasePage`. One page class per logical page or major component.
- Tests call page methods; tests never reference selectors directly.

### Separation of test logic from test data

- **Cypress:** Fixtures in `cypress/fixtures/*.json`, loaded via `cy.fixture()`.
- **Java (Selenium/Cucumber):** `@DataProvider` for parametrized tests, `Examples` tables in `.feature` files, `config.properties` for env config.
- **Python (Pytest):** `@pytest.mark.parametrize` driven by JSON datasets in `datasets/`. Session-scoped fixtures in `conftest.py` for expensive resources (API clients, vector stores).
- **Python (Behave):** `Scenario Outline` with `Examples` in `.feature` files; `config.ini` for env config.
- Never hardcode test data in test methods. Extract to fixtures, data providers, or dataset files.

### Configuration management

- Environment-specific values (URLs, credentials, timeouts, browser choice) go in `.env` files or `config.properties`, never hardcoded.
- Always provide a `.env.example` when adding a new framework or new env vars.
- Follow the existing override hierarchy: defaults in config files → `.env` overrides → CLI/system env var overrides.
- DataDog integration is optional everywhere. All `datadog_reporter` utilities skip silently when `DD_API_KEY` is absent.

### DRY and reusable utilities

- **Custom commands** (Cypress): `cy.login()`, `cy.addToCart()`, `cy.clearCart()` in `support/commands.ts` with TypeScript declarations.
- **Tasks** (Python Behave): `LoginTask`, `AddToCartTask` in `utils/tasks.py` (Screenplay pattern) for composable multi-step actions.
- **BasePage utilities**: Waits, clicks, text retrieval — use inherited helpers, do not duplicate wait logic in tests or steps.
- **Service layer** (Selenium Java): Business logic in `services/` separates orchestration from page mechanics.
- Extract repeated patterns into helpers. If the same 3+ lines appear in multiple tests, create a shared utility or custom command.

### SOLID principles in practice

- **Single Responsibility:** Each page class owns one page. Each test file covers one feature area. Each fixture file serves one data domain.
- **Open/Closed:** `BasePage` is extended, not modified. Add new page classes for new pages instead of bloating existing ones.
- **Dependency Inversion:** Tests depend on page abstractions, not raw selectors. Fixtures and config inject data, not tests fetching it inline.

## Language and framework specifics

### TypeScript / Node.js (Cypress, Playwright TS, Postman)

- Node.js 22 LTS. Use `npm ci` for deterministic installs.
- Cypress: `cypress.config.ts` is the single config source. Custom commands must include `declare global` TypeScript augmentation.
- Linting: Follow existing ESLint/TSConfig conventions in each sub-project.

### Java (Selenium, Cucumber)

- Java 17, Maven 3.9+. Build with `mvn clean test`.
- TestNG for execution: test groups (`smoke`, `regression`, `web`, `mobile`), `testng.xml` / `testng_mobile.xml` for suite definitions, parallel via ThreadLocal driver.
- Allure for reporting: `@Step`, `@Description`, `@Severity` annotations on test methods.
- Retry: `RetryAnalyzer` applied globally via `AnnotationTransformer`. Tests auto-retry 2x on failure.

### C# / .NET (Playwright)

- .NET 8 LTS. Build with `dotnet test`.
- NUnit with `[Parallelizable]` attribute. Trace Viewer for debugging.

### Python (19 frameworks)

- Python 3.11+. Each framework has its own `requirements.txt`.
- Pytest: markers defined in `pytest.ini` (`smoke`, `regression`, `safety`). Use `conftest.py` for fixtures — session scope for expensive resources, function scope for stateful objects needing reset.
- Behave: `environment.py` for hooks, `behave.ini` for runner config. Steps organized by domain (`auth_steps.py`, `inventory_steps.py`).
- AI evals use `pytest-rerunfailures` for transient API timeouts.

### HCL (Terraform)

- Terraform >= 1.6. Modules in `terraform/modules/`. Always run `terraform fmt -recursive` before committing.

## CI/CD (GitHub Actions)

- 29 workflows in `.github/workflows/`.
- Each workflow triggers on push/PR **only for its own path** (e.g., `cypress/**`), plus nightly schedules staggered across UTC hours.
- All workflows support `workflow_dispatch` with framework-specific inputs (browser, markers, suite, demo number).
- All test results upload JUnit XML to DataDog CI Visibility when `DD_API_KEY` is set.
- OWASP ZAP baseline scan runs post-test in browser frameworks (`continue-on-error: true`).
- When modifying a workflow, only change the workflow for the affected framework. Do not cross-wire triggers.

## Running locally

Use the root `Makefile` as the entry point:

```bash
make help              # List all targets and prerequisites
make cypress-test      # Cypress E2E suite
make selenium          # Selenium Java (headless Chrome)
make cucumber          # Cucumber Java (headless Chrome)
make cucumber-python   # Behave (headless Chrome)
make ai-eval           # DeepEval RAG evaluation
make postman           # Newman API tests
make fastapi-service-test  # FastAPI pytest suite
```

Prerequisites vary by framework. Check `make help` for the full list.

## Reporting

- **JUnit XML**: All frameworks produce JUnit XML for CI consumption.
- **Allure**: Java, C#, and Cypress frameworks generate Allure results. Reports deploy to GitHub Pages (`gh-pages` branch) in CI.
- **DataDog**: Custom GAUGE metrics per framework (suite counts, AI eval scores, job agent stats). All utilities degrade gracefully without keys.
- When adding a new test framework, include JUnit XML output and a DataDog reporter that follows the existing `utils/datadog_reporter` pattern.

## What not to do

- Do not add dependencies to one framework that create coupling with another framework's code or config.
- Do not put selectors or UI interactions in test files — that belongs in page objects.
- Do not hardcode test data, credentials, or environment URLs in source code.
- Do not skip `.env.example` updates when introducing new environment variables.
- Do not modify `BasePage` to add page-specific logic — extend it in a new class instead.
- Do not create tests without proper tagging/grouping (`smoke`, `regression`, etc.).
- Do not add a new top-level directory or framework without updating `README.md` — add it to the Frameworks table, the Repo Structure tree, and the Quick Start section if it has a runnable entry point.
- When adding a significant capability to an existing framework (new dependency, new test type, new profile, new tool integration), update both the root `README.md` and the framework's own `README.md` to document the addition — including Tech Stack tables, Feature Coverage tables, How to Run sections, Quick Start blocks, and Repo Structure trees as applicable.
- **Do not make claims about what exists (or doesn't exist) in the repo without reading the source first.** Before stating what metrics, tests, features, or configs a framework has, read the actual files. Memory and summaries drift — the code is the source of truth.

