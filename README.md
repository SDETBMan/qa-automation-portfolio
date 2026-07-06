# QA Automation Portfolio

[![playwright-dotnet CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/playwright-dotnet.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/playwright-dotnet.yml)
[![selenium-java CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/selenium-java.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/selenium-java.yml)
[![cucumber CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml)
[![cypress CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cypress.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cypress.yml)
[![ai-eval CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/ai-eval.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/ai-eval.yml)
[![conv-eval CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/conv-eval.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/conv-eval.yml)
[![agent-eval CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/agent-eval.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/agent-eval.yml)
[![k8s CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/k8s.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/k8s.yml)
[![postman-newman CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/postman-newman.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/postman-newman.yml)
[![job-agent CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/job-agent.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/job-agent.yml)
[![cucumber-python CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber-python.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber-python.yml)
[![coding-agent CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/coding-agent.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/coding-agent.yml)
[![fastapi-service CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/fastapi-service.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/fastapi-service.yml)
[![Terraform CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/terraform.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/terraform.yml)
[![langchain-rag CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/langchain-rag.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/langchain-rag.yml)
[![langgraph-agent CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/langgraph-agent.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/langgraph-agent.yml)
[![dspy-optimizer CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/dspy-optimizer.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/dspy-optimizer.yml)

A monorepo housing eighteen independent, production-grade frameworks spanning test automation, AI agents, API services, and cloud infrastructure — each showcasing a distinct engineering discipline used by senior SDETs and platform engineers.

---

## Frameworks

| Framework | Language | Stack | README |
|---|---|---|---|
| [`ai-eval`](./ai-eval/) | Python | DeepEval · Pytest · OpenAI · ChromaDB · Python 3.11 | [→](./ai-eval/README.md) |
| [`conv-eval`](./conv-eval/) | Python | DeepEval · Pytest · OpenAI · Python 3.11 | [→](./conv-eval/README.md) |
| [`agent-eval`](./agent-eval/) | Python | DeepEval · Pytest · OpenAI · Pydantic · Python 3.11 | [→](./agent-eval/README.md) |
| [`playwright-dotnet`](./playwright-dotnet/) | C# · TypeScript | Playwright 1.44 · NUnit · .NET 8 · TypeScript 5.4 | [→](./playwright-dotnet/README.md) |
| [`selenium-java`](./selenium-java/) | Java | Selenium 4 · TestNG · Maven · Java 17 | [→](./selenium-java/README.md) |
| [`cucumber`](./cucumber/) | Java | Cucumber 7 · TestNG · Selenium 4 · Maven · Java 17 | [→](./cucumber/README.md) |
| [`postman`](./postman/) | JSON · JavaScript | Postman Collection v2.1 · Newman 6 · Node.js 20 | [→](./postman/README.md) |
| [`job-agent`](./job-agent/) | Python | Anthropic Claude · Tavily · AgentOps · Python 3.11 | [→](./job-agent/README.md) |
| [`cypress`](./cypress/) | TypeScript | Cypress 13 · React 18 · Vite · Node.js 20 | [→](./cypress/README.md) |
| [`cucumber-python`](./cucumber_python/) | Python | Behave · Selenium 4 · Python 3.11 | [→](./cucumber_python/README.md) |
| [`coding-agent`](./coding-agent/) | Python | Anthropic Claude · AgentOps · Python 3.11 | [→](./coding-agent/README.md) |
| [`fastapi-service`](./fastapi-service/) | Python · JavaScript | FastAPI · Redis · Pytest · k6 · Python 3.11 | [→](./fastapi-service/README.md) |
| [`terraform`](./terraform/) | HCL | Terraform ≥ 1.6 · AWS · DataDog | [→](./terraform/README.md) |
| [`langchain-rag`](./langchain-rag/) | Python | LangChain 0.3 · LCEL · Chroma · OpenAI `gpt-4o-mini` · Python 3.11 | [→](./langchain-rag/README.md) |
| [`langgraph-agent`](./langgraph-agent/) | Python | LangGraph 0.4 · LangChain Anthropic · `claude-haiku-4-5` · Python 3.11 | [→](./langgraph-agent/README.md) |
| [`dspy-optimizer`](./dspy-optimizer/) | Python | DSPy 2.6 · BootstrapFewShot · OpenAI `gpt-4o-mini` · Python 3.11 | [→](./dspy-optimizer/README.md) |
| [`dspy-vertex`](./dspy-vertex/) | Python | DSPy 2.6 · BootstrapFewShot · Vertex AI Gemini 1.5 · Python 3.11 | [→](./dspy-vertex/README.md) |
| [`claims-diff`](./claims-diff/) | Python | Pandas · Pydantic · BigQuery (optional) · Python 3.11 | [→](./claims-diff/README.md) |

---

## Feature Coverage

| Capability | playwright-dotnet | selenium-java | cucumber | cypress | ai-eval | conv-eval | agent-eval | postman | job-agent |
|---|---|---|---|---|---|---|---|---|---|
| **Page Object Model** | ✅ C# + TypeScript | ✅ Java | ✅ Java | ✅ TypeScript | — | — | — | — | — |
| **Custom commands** | — | — | — | ✅ `cy.login()` · `cy.addToCart()` · `cy.clearCart()` | — | — | — | — | — |
| **Network interception** | ✅ `page.route()` mock/stub | — | — | ✅ `cy.intercept()` spy + stub + failure sim | — | — | — | — | — |
| **Component testing** | — | — | — | ✅ React `ProductCard` via Cypress component runner | — | — | — | — | — |
| **Parallel execution** | ✅ `[Parallelizable]` · `fullyParallel` | ✅ `ThreadLocal` · `parallel="tests"` | ✅ `ThreadLocal` · `@DataProvider(parallel=true)` | ✅ `--parallel` (Cypress Cloud) | — | — | — | — | — |
| **Fixtures / base classes** | ✅ `AuthenticatedTest` · `test.extend<>` | ✅ `BaseTest` | ✅ Cucumber `Hooks` | ✅ `BasePage` abstract class · JSON fixtures | ✅ `conftest.py` session fixtures | ✅ `conftest.py` session + function fixtures | ✅ `conftest.py` session + function fixtures | — | — |
| **Retry on failure** | ✅ `[Retry]` · `retries: 2` in CI | ✅ `RetryAnalyzer` + `AnnotationTransformer` | ✅ `RetryAnalyzer` + `AnnotationTransformer` | ✅ `retries: { runMode: 2 }` | — | — | — | — | — |
| **Cross-browser** | ✅ Chromium · Firefox · WebKit | ✅ Chrome · Firefox · Edge | ✅ Chrome · Firefox · Edge | ✅ Chrome · Firefox · Edge · Electron | — | — | — | — | — |
| **Screenshot/video on failure** | ✅ Trace Viewer | — | — | ✅ `screenshotOnRunFailure` · `video: true` | — | — | — | — | — |
| **BDD / Gherkin** | — | — | ✅ 6 feature files · 19+ scenarios | — | — | — | — | — | — |
| **Data-driven tests** | ✅ `[TestCaseSource]` | ✅ `@DataProvider` | ✅ Scenario Outline | ✅ `cy.fixture()` JSON datasets | ✅ `golden_dataset.json` · `@pytest.mark.parametrize` | ✅ `conversations.json` · `@pytest.mark.parametrize` | ✅ `agent_scenarios.json` · `@pytest.mark.parametrize` | ✅ pre-request scripts · collection variables | — |
| **Visual regression** | ✅ `toHaveScreenshot()` · snapshot baselines · CI update workflow | — | — | — | — | — | — | — | — |
| **GraphQL API testing** | ✅ Playwright `request` fixture · 5 patterns (query, variables, mock, error, auditing) | — | — | — | — | — | — | — | — |
| **Database-to-UI assertions** | ✅ 5 patterns: scalar match, row count, field match, pre-fill, column values | — | — | — | — | — | — | — | — |
| **Shopify E2E testing** | ✅ 8 storefront tests · 4 visual baselines · Page Objects | — | — | — | — | — | — | — | — |
| **Deploy validation + rollback** | ✅ Vercel health-check → Playwright smoke → auto-rollback pipeline | — | — | — | — | — | — | — | — |
| **REST API testing** | ✅ `HttpClient` · Playwright `request` | ✅ RestAssured | ✅ RestAssured | — | — | — | — | ✅ Newman CLI · 10 requests · 4 test groups | — |
| **Mocking & Service Virtualization** | ✅ 4 patterns: block assets, mock API responses, inject headers, simulate failures · enables UI testing independent of backend readiness | — | — | ✅ `cy.intercept()` response stub + failure sim | — | — | — | — | — |
| **Observability & Analytics** | ✅ Allure · GitHub Pages · Trace Viewer (`retain-on-failure`): DOM snapshots, screenshots, network calls for fast MTTR | ✅ Allure | ✅ Allure · GitHub Pages | ✅ JUnit XML · videos · screenshots | — | — | — | ✅ JUnit XML · htmlextra HTML report | — |
| **AI/ML Self-Healing Locators** | — | ✅ Healenium 3.4.8 | ✅ Healenium 3.4.8 | — | — | — | — | — | — |
| **LLM Evaluation (RAG pipeline)** | — | — | — | — | ✅ Answer Relevancy · Faithfulness · Hallucination · Safety · Bias · JSON Schema | — | — | — | — |
| **LLM Evaluation (Conversational)** | — | — | — | — | — | ✅ Turn Relevancy · Knowledge Retention · Role Adherence · Graceful Handling · Bias · Toxicity | — | — | — |
| **LLM Evaluation (Agentic / tool-use)** | — | — | — | — | — | — | ✅ Tool Correctness · Task Completion · Bias · Toxicity | — | — |
| **Function-calling agent** | — | — | — | — | — | — | ✅ Multi-step tool orchestration · deterministic tool implementations | — | — |
| **Agentic tool-use loop** | — | — | — | — | — | — | — | — | ✅ Claude claude-sonnet-4-6 · 5 tools · max 30 iterations · Tavily web search |
| **Automated job search** | — | — | — | — | — | — | — | — | ✅ 5 role queries · score_job_fit · draft_cover_letter · save_results |
| **JSON schema validation** | — | — | — | — | ✅ `JsonCorrectnessMetric` · Pydantic `BaseModel` schemas | — | — | — | — |
| **Cost & latency tracking** | — | — | — | — | ✅ per-call tokens · `latency_ms` → DataDog | ✅ per-turn tokens · `latency_ms` → DataDog | ✅ per-step tokens · `latency_ms` → DataDog | — | ✅ `latency_ms` · run counts → DataDog |
| **Mobile (Appium)** | — | ✅ Android · iOS | ✅ Android · iOS | — | — | — | — | — | — |
| **Performance (JMeter)** | — | ✅ Maven plugin | ✅ Maven plugin | — | — | — | — | — | — |
| **Database validation** | ✅ dbClient + dbAssertions (MySQL · PostgreSQL) | ✅ JDBC / MySQL | ✅ JDBC / MySQL | — | — | — | — | — | — |
| **Security testing (OWASP)** | ✅ 4 test cases | ✅ 4 test cases | ✅ 3 BDD scenarios | — | — | — | — | — | — |
| **OWASP ZAP passive scan** | ✅ CI pipeline | ✅ CI pipeline | ✅ CI pipeline | ✅ CI pipeline | — | — | — | — | — |
| **Containerized infra** | — | ✅ Docker Compose · K8s | ✅ Docker Compose · K8s | — | — | — | — | — | — |
| **Slack notifications** | — | ✅ Webhook | ✅ Webhook | — | — | — | — | — | — |
| **DataDog observability** | ✅ CI Visibility (TRX) | ✅ CI Visibility · Custom metrics | ✅ CI Visibility · Custom metrics | ✅ CI Visibility · Custom GAUGE metrics | ✅ CI Visibility · LLM eval scores | ✅ CI Visibility · LLM eval scores | ✅ CI Visibility · LLM eval scores | ✅ CI Visibility (JUnit XML) | ✅ Custom metrics · run counts · latency |
| **RAG pipeline (LCEL)** | — | — | — | — | — | — | — | — | — |
| **Stateful multi-agent graph** | — | — | — | — | — | — | — | — | — |
| **Conditional edges + cycles** | — | — | — | — | — | — | — | — | — |
| **DSPy prompt optimization** | — | — | — | — | — | — | — | — | — |
| **Conversation history (RunnableWithMessageHistory)** | — | — | — | — | — | — | — | — | — |
| **GitHub Actions CI** | ✅ | ✅ | ✅ | ✅ nightly 05:00 UTC | ✅ | ✅ | ✅ | ✅ | ✅ nightly 09:00 UTC |
| **Agentic AI Development** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Quick Start

### ai-eval

**Prerequisites:** [Python 3.11+](https://python.org) · OpenAI API key in `ai-eval/.env`

```bash
# From the repo root
make ai-eval

# Or manually
cd ai-eval
pip install -r requirements.txt

# Run all evaluations
pytest -v

# Smoke tests only (fast)
pytest -m smoke -v

# Safety tests only
pytest -m safety -v
```

### conv-eval

**Prerequisites:** [Python 3.11+](https://python.org) · OpenAI API key in `conv-eval/.env`

```bash
cd conv-eval
pip install -r requirements.txt

# Smoke tests only (fast): turn relevancy + role adherence across normal scenarios
pytest -m smoke -v

# Retention tests: knowledge retention across implicit reference and correction scenarios
pytest -m retention -v

# Safety tests: graceful handling of out-of-scope queries and prompt injection
pytest -m safety -v

# Full suite
pytest -v
```

### agent-eval

**Prerequisites:** [Python 3.11+](https://python.org) · OpenAI API key in `agent-eval/.env`

```bash
cd agent-eval
pip install -r requirements.txt

# Smoke tests only (fast): tool correctness + task completion across single-tool scenarios
pytest -m smoke -v

# Full suite (includes multi-tool orchestration scenarios)
pytest -v
```

### cypress (TypeScript E2E + Component)

**Prerequisites:** [Node.js 20 LTS](https://nodejs.org)

```bash
# From the repo root
make cypress-test

# Or manually
cd cypress
npm install

# All E2E tests (headless Chrome)
npm test

# React component tests only
npm run test:component

# Interactive Cypress Test Runner
npm run test:headed
```

### playwright-dotnet (C# + TypeScript)

**Prerequisites:** [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8) · [Node.js 20 LTS](https://nodejs.org)

```bash
cd playwright-dotnet

# One command: installs all deps, browsers, runs C# and TypeScript suites
bash run-all.sh

# Or with make
make all
```

### selenium-java

**Prerequisites:** [Java 17](https://adoptium.net) · [Maven 3.9+](https://maven.apache.org)

```bash
# From the repo root
make selenium

# Or manually
cd selenium-java

# Headless Chrome (default)
mvn clean test -Dheadless=true

# Specific browser
mvn clean test -Dheadless=true -Dbrowser=firefox

# Selenium Grid (start Docker first)
docker compose up -d selenium-hub chrome firefox edge
mvn clean test -PGrid -Dheadless=true

# Performance tests
mvn jmeter:jmeter
```

### cucumber

**Prerequisites:** [Java 17](https://adoptium.net) · [Maven 3.9+](https://maven.apache.org)

```bash
# From the repo root
make cucumber

# Or manually
cd cucumber

# Headless Chrome (default)
mvn clean test -Dheadless=true

# Tag filter
mvn clean test -Dheadless=true -Dcucumber.filter.tags="@smoke"

# Full stack with Selenium Grid + Healenium
docker compose up -d
mvn clean test -Dtarget=grid -Dheadless=true

# Performance tests
mvn jmeter:jmeter
```

### postman (Newman API tests)

**Prerequisites:** [Node.js 20 LTS](https://nodejs.org)

```bash
# From the repo root
make postman

# Or manually
cd postman

# Install Newman and reporters
npm install

# Run full collection (all 4 folders)
npm test

# Smoke folder only (fast connectivity check)
npm run test:smoke

# Verbose output with request/response details
npm run test:verbose

# HTML report (opens in browser)
npm run test:html
```

### job-agent

**Prerequisites:** [Python 3.11+](https://python.org) · Anthropic API key · Tavily API key in `job-agent/.env`

```bash
# From the repo root
make job-agent

# Or manually
cd job-agent
pip install -r requirements.txt

# Copy and fill in your profile
cp profile/profile.example.md profile/profile.md

# Run full job search (all 5 role queries)
python run.py

# Narrow to a specific role
python run.py --role "SDET"
python run.py --role "QA Lead"
```

### cucumber-python

**Prerequisites:** [Python 3.11+](https://python.org) · Chrome/Chromium installed

```bash
# From the repo root
make cucumber-python

# Or manually
cd cucumber_python
pip install -r requirements.txt

# All scenarios (headless Chrome)
HEADLESS=true behave --no-capture

# Tag filter (e.g. security scenarios only)
HEADLESS=true behave --tags=security

# Specific feature file
HEADLESS=true behave features/inventory.feature
```

### coding-agent

**Prerequisites:** [Python 3.11+](https://python.org) · Anthropic API key in `coding-agent/.env`

```bash
# From the repo root
make coding-agent

# Or manually
cd coding-agent
pip install -r requirements.txt

# Demo 2 — HTTP validation script (default, no browser needed)
python run_demo.py --demo 2

# All demos (1–4)
python run_demo.py --demo all
```

### fastapi-service

**Prerequisites:** [Python 3.11+](https://python.org) · Docker (optional, for Redis)

```bash
# Start the API server on :8001
make fastapi-service

# Run the Pytest suite with coverage (37 tests, no Redis needed)
make fastapi-service-test

# Or manually
cd fastapi-service
pip install -r requirements.txt
pytest tests/ -v --cov=app --cov-report=term-missing

# Start with Redis caching (optional)
docker compose up -d
uvicorn app.main:app --reload --port 8001
```

### terraform

**Prerequisites:** [Terraform ≥ 1.6](https://developer.hashicorp.com/terraform/downloads) · AWS credentials · DataDog API + App keys

```bash
# Copy example vars and fill in your values
cp terraform/terraform.tfvars.example terraform/terraform.tfvars

make terraform-init      # download providers
make terraform-validate  # check HCL syntax
make terraform-plan      # preview changes (requires creds)
make terraform-apply     # apply (requires creds)
```

See [`terraform/README.md`](./terraform/README.md) for the full bootstrap guide, CI integration notes, and the chicken-and-egg OIDC setup instructions.

### langchain-rag

**Prerequisites:** [Python 3.11+](https://python.org) · OpenAI API key in `langchain-rag/.env`

```bash
# From the repo root
make langchain-rag

# Or manually
cd langchain-rag
pip install -r requirements.txt
cp .env.example .env  # add OPENAI_API_KEY

# Run 3 built-in demo questions
python run.py --demo

# Ask a single question
python run.py --question "Which frameworks use Selenium?"

# Interactive REPL
python run.py --interactive
```

### langgraph-agent

**Prerequisites:** [Python 3.11+](https://python.org) · Anthropic API key in `langgraph-agent/.env`

```bash
# From the repo root
make langgraph-agent

# Or manually
cd langgraph-agent
pip install -r requirements.txt
cp .env.example .env  # add ANTHROPIC_API_KEY

# Run built-in demo feature
python run.py --demo

# Provide your own feature description
python run.py --feature "User can reset their password via email"
```

### dspy-optimizer

**Prerequisites:** [Python 3.11+](https://python.org) · OpenAI API key in `dspy-optimizer/.env`

```bash
# From the repo root
make dspy-optimizer

# Or manually
cd dspy-optimizer
pip install -r requirements.txt
cp .env.example .env  # add OPENAI_API_KEY

# Side-by-side baseline vs optimized accuracy (default)
python run.py

# Zero-shot baseline only
python run.py --mode baseline

# BootstrapFewShot optimized only
python run.py --mode optimized
```

### dspy-vertex

**Prerequisites:** [Python 3.11+](https://python.org) · GCP credentials (`gcloud auth application-default login`)

```bash
cd dspy-vertex
pip install -r requirements.txt
cp .env.example .env  # add GCP_PROJECT

# Side-by-side baseline vs optimized accuracy (default)
python run.py

# Zero-shot baseline only
python run.py --mode baseline

# BootstrapFewShot optimized only
python run.py --mode optimized
```

### claims-diff

**Prerequisites:** [Python 3.11+](https://python.org)

```bash
cd claims-diff
pip install -r requirements.txt

# Run diff against included synthetic datasets
python run.py
```

---

## Repo Structure

```
qa-automation-portfolio/
├── .github/
│   └── workflows/
│       ├── ai-eval.yml             # triggers on: paths ai-eval/**
│       ├── conv-eval.yml           # triggers on: paths conv-eval/**
│       ├── agent-eval.yml          # triggers on: paths agent-eval/**
│       ├── playwright-dotnet.yml   # triggers on: paths playwright-dotnet/**
│       ├── selenium-java.yml       # triggers on: paths selenium-java/**
│       ├── cucumber.yml            # triggers on: paths cucumber/**
│       ├── cypress.yml             # triggers on: paths cypress/** · nightly 05:00 UTC
│       ├── postman-newman.yml      # triggers on: paths postman/**
│       ├── job-agent.yml           # nightly 09:00 UTC · workflow_dispatch (role_filter input)
│       ├── cucumber-python.yml     # nightly 05:00 UTC · workflow_dispatch (browser · execution mode)
│       ├── coding-agent.yml        # push/PR paths: coding-agent/** · workflow_dispatch (demo number)
│       ├── fastapi-service.yml     # nightly 10:00 UTC · workflow_dispatch
│       ├── terraform.yml           # push/PR paths: terraform/** · workflow_dispatch (plan + apply)
│       ├── k8s.yml                 # workflow_dispatch only: Kind cluster + grid smoke tests
│       ├── langchain-rag.yml       # push/PR lint (free) · workflow_dispatch demo (< $0.01)
│       ├── langgraph-agent.yml     # push/PR lint (free) · workflow_dispatch demo (< $0.02)
│       ├── dspy-optimizer.yml      # push/PR lint (free) · workflow_dispatch compare (~$0.02)
│       ├── playwright-smoke-pr.yml # PR gate: @smoke Chromium only, 5-min timeout, fail-fast
│       ├── k6-load-test.yml       # nightly k6 load test against fastapi-service
│       ├── deploy-validate-rollback.yml  # Vercel health-check → smoke → auto-rollback
│       └── visual-regression-update.yml  # Manual baseline update → PR for review
├── ai-eval/                            # Python · Pytest · DeepEval · OpenAI · ChromaDB
│   ├── rag/                            # RAG pipeline: document, embedder, retriever
│   ├── datasets/golden_dataset.json    # Ground truth Q&A pairs (SauceDemo FAQ)
│   ├── evals/                          # test_answer_relevancy · faithfulness · hallucination · safety · bias · json_correctness
│   ├── conftest.py                     # Session fixtures: OpenAI client, ChromaDB, retriever, answer_generator
│   └── pytest.ini
├── conv-eval/                          # Python · Pytest · DeepEval · OpenAI
│   ├── chatbot/                        # SwagSupportBot (stateful) · knowledge base · system prompt
│   ├── datasets/conversations.json     # 7 multi-turn conversation scenarios
│   ├── evals/                          # test_conversation_relevancy · knowledge_retention · role_adherence · graceful_handling · safety
│   ├── conftest.py                     # Session fixtures: OpenAI client · function-scoped bot with teardown
│   └── pytest.ini
├── agent-eval/                         # Python · Pytest · DeepEval · OpenAI · Pydantic
│   ├── agent/                          # SwagAgent (function-calling) · tools · tool implementations
│   ├── datasets/agent_scenarios.json   # 7 scenarios: single-tool and multi-tool orchestration
│   ├── evals/                          # test_tool_correctness · test_task_completion · test_safety
│   ├── conftest.py                     # Session fixtures: OpenAI client · function-scoped agent with teardown
│   └── pytest.ini
├── playwright-dotnet/              # Playwright · NUnit · C# · TypeScript
│   ├── tests/
│   │   ├── Framework.Tests/        # NUnit C# test project
│   │   └── playwright-ts/          # TypeScript Playwright project
│   │       ├── tests/              # login · inventory · network · visual-regression · db-assertions · graphql
│   │       │   └── shopify/        # storefront E2E + visual baselines (Shopify)
│   │       ├── pages/shopify/      # ShopifyStorefront · Product · Cart page objects
│   │       ├── utils/              # dbClient · dbAssertions · graphqlClient · allureHelper
│   │       └── scripts/            # health-check.ts (deploy validation)
│   ├── Makefile
│   └── run-all.sh
├── selenium-java/                  # Selenium 4 · TestNG · Java · Maven
│   ├── src/main/java/              # Page objects, driver factory, utilities
│   ├── src/test/java/              # Tests, listeners, unit tests
│   ├── testng.xml                  # Web · API · Unit suites
│   └── testng_mobile.xml           # Android & iOS Appium suites
├── cucumber/                       # Cucumber 7 · TestNG · Selenium 4 · Java
│   ├── src/main/java/              # Utilities: ConfigReader, RetryAnalyzer, SlackUtils
│   ├── src/test/java/              # Step definitions, runners, page objects
│   ├── src/test/resources/features/  # login · dashboard · inventory · cart · api · security
│   └── docker-compose.yaml
├── cypress/                            # Cypress 13 · TypeScript · React 18 · Vite · Node.js 20
│   ├── cypress/
│   │   ├── component/                  # ProductCard.cy.tsx — React component tests
│   │   ├── e2e/                        # login · inventory · checkout · network (cy.intercept)
│   │   ├── fixtures/                   # users.json · products.json
│   │   ├── pages/                      # BasePage · LoginPage · InventoryPage · CartPage · CheckoutPage
│   │   └── support/                    # commands.ts (cy.login · cy.addToCart · cy.clearCart) · e2e.ts
│   ├── src/components/ProductCard.tsx  # React component under test
│   ├── utils/datadog_reporter.ts       # GAUGE metrics reporter
│   └── cypress.config.ts
├── postman/                            # Postman Collection v2.1 · Newman · Node.js 20
│   ├── collections/                   # jsonplaceholder.postman_collection.json: 10 requests, 4 folders
│   ├── environments/                  # jsonplaceholder.postman_environment.json
│   ├── results/                       # JUnit XML · HTML report (git-ignored)
│   └── package.json                   # Newman + htmlextra reporter
├── job-agent/                          # Python · Anthropic Claude · Tavily
│   ├── agent/                          # job_hunter.py (agentic loop) · tools.py (5 tool defs)
│   ├── profile/                        # profile.example.md (template) · profile.md (git-ignored)
│   ├── utils/                          # datadog_reporter.py
│   ├── output/                         # jobs_YYYY-MM-DD.md · cover_letters/ (git-ignored)
│   └── run.py                          # CLI entry: python run.py [--role SDET]
├── cucumber_python/                    # Python · Behave · Selenium 4
│   ├── features/                       # login · dashboard · inventory · cart · api · security
│   │   ├── steps/                      # auth_steps · inventory_steps · api_steps · security_steps
│   │   └── environment.py              # before/after_scenario hooks · DataDog metrics · Slack
│   ├── pages/                          # BasePage · LoginPage · InventoryPage · CartPage · DashboardPage
│   ├── utils/                          # driver_manager · config_reader · tasks · datadog_utils
│   └── config.ini
├── coding-agent/                       # Python · Anthropic Claude · multi-demo AI coding agent
│   ├── agents/                         # agent loop · tool implementations
│   ├── shared/                         # shared utilities
│   └── run_demo.py                     # CLI entry: python run_demo.py --demo 2
├── fastapi-service/                    # Python · FastAPI · Redis · Pytest · k6
│   ├── app/                            # FastAPI application + Redis cache layer
│   ├── tests/                          # 37 tests: CRUD, contract, cache (fakeredis)
│   ├── k6/                             # k6 load tests (4 scenarios: health, read, CRUD, error)
│   ├── utils/                          # datadog_reporter (test + cache metrics)
│   └── docker-compose.yml             # redis:7-alpine for local dev
├── terraform/                          # HCL · Terraform ≥ 1.6 · AWS · DataDog IaC
│   ├── modules/
│   │   ├── s3-artifacts/               # S3 bucket: versioning, SSE, lifecycle rules
│   │   ├── iam-ci/                     # GitHub OIDC provider + keyless CI IAM role
│   │   └── datadog-observability/      # dashboard, 2 monitors, CI pass-rate SLO
│   ├── main.tf · variables.tf · outputs.tf
│   ├── backend.tf                      # local (default) + S3 backend (commented out)
│   └── terraform.tfvars.example
├── k8s/                            # Kubernetes manifests (mirrors docker-compose.yaml)
│   ├── namespace.yaml              # selenium-grid namespace
│   ├── configmap.yaml              # Healenium DB credentials
│   ├── selenium-grid/              # Hub + Chrome/Firefox/Edge node deployments & services
│   └── healenium/                  # Postgres, hlm-backend, hlm-selector-imitator
├── langchain-rag/                      # Python · LangChain LCEL · Chroma · OpenAI
│   ├── rag/                            # loader · vectorstore · LCEL chain + RunnableWithMessageHistory
│   └── run.py                          # CLI: --question · --demo · --interactive
├── langgraph-agent/                    # Python · LangGraph · LangChain Anthropic · Haiku
│   ├── graph/                          # state · nodes · edges · pipeline (StateGraph)
│   └── run.py                          # CLI: --feature · --demo (streams node events)
├── dspy-optimizer/                     # Python · DSPy · BootstrapFewShot · OpenAI
│   ├── classifier/                     # signatures · ChainOfThought module · optimizer
│   ├── datasets/bug_reports.py         # 30 synthetic examples (hardcoded, offline)
│   └── run.py                          # CLI: --mode baseline|optimized|compare
├── dspy-vertex/                        # Python · DSPy · BootstrapFewShot · Vertex AI Gemini
│   ├── classifier/                     # identical pipeline, Vertex AI backend
│   ├── datasets/bug_reports.py         # 30 synthetic examples (shared with dspy-optimizer)
│   └── run.py                          # CLI: --mode baseline|optimized|compare
├── claims-diff/                        # Python · Pandas · Pydantic · BigQuery (optional)
│   ├── differ/                         # models · loader · diff_engine
│   ├── datasets/                       # baseline_claims.csv · current_claims.csv
│   └── run.py                          # CLI: structured JSON diff report
├── Makefile                            # One-command runner for all suites
├── .gitignore
└── README.md
```

---

## CI Strategy

Each workflow has **path filters** so a push to `selenium-java/` only triggers the `selenium-java.yml` pipeline, the other frameworks are unaffected. A nightly `cron` schedule keeps the full portfolio green without cross-framework interference.

| Workflow | Trigger | dispatch inputs |
|---|---|---|
| `playwright-dotnet.yml` | push · PR · nightly 02:00 UTC | execution mode · browser · JMeter toggle |
| `selenium-java.yml` | push · PR · nightly 03:00 UTC | browser · suite XML · JMeter toggle |
| `cucumber.yml` | push · PR · nightly 04:00 UTC | execution mode · browser · JMeter toggle |
| `cypress.yml` | push · PR · nightly 05:00 UTC | browser (chrome · firefox · edge · electron) · test type (e2e · component · all) |
| `ai-eval.yml` | push · PR · nightly 05:00 UTC | pytest marker filter (smoke · regression · safety) |
| `conv-eval.yml` | push · PR · nightly 06:00 UTC | pytest marker filter (smoke · regression · safety · retention) |
| `agent-eval.yml` | push · PR · nightly 07:00 UTC | pytest marker filter (smoke · regression · safety) |
| `postman-newman.yml` | push · PR · nightly 08:00 UTC | folder filter (Smoke · Users · Posts · Integration Flow) |
| `job-agent.yml` | nightly 09:00 UTC · `workflow_dispatch` | role_filter keyword (e.g. SDET · QA Lead) |
| `cucumber-python.yml` | push · PR · nightly 05:00 UTC | execution mode (local · grid · browserstack) · browser · tag filter |
| `coding-agent.yml` | push · PR · `workflow_dispatch` | demo number (1–4 or all) |
| `fastapi-service.yml` | nightly 10:00 UTC · `workflow_dispatch` | — |
| `k6-load-test.yml` | nightly 11:00 UTC · `workflow_dispatch` | k6 load test against fastapi-service (4 scenarios) |
| `terraform.yml` | push · PR · `workflow_dispatch` (paths: `terraform/**`) | plan on PR · apply on merge to main · OIDC AWS auth |
| `k8s.yml` | `workflow_dispatch` only | framework (selenium-java · cucumber) |
| `langchain-rag.yml` | push · PR (lint only, free) · `workflow_dispatch` (full demo) | — |
| `langgraph-agent.yml` | push · PR (lint only, free) · `workflow_dispatch` (full demo) | — |
| `dspy-optimizer.yml` | push · PR (lint only, free) · `workflow_dispatch` (compare run) | — |
| `playwright-smoke-pr.yml` | PR to `main` (paths: `playwright-dotnet/**`) | Chromium-only @smoke gate, 5-min timeout, fail-fast |
| `azure-pipelines.yml` | PR (Azure DevOps) | ADO YAML equivalent of GHA smoke gate (playwright-dotnet) |
| `deploy-validate-rollback.yml` | `workflow_dispatch` · `workflow_call` | deployment URL · Vercel project ID · auto-rollback toggle |
| `visual-regression-update.yml` | `workflow_dispatch` | browser project (chromium · firefox · webkit) |

All three browser-test workflows include an **OWASP ZAP Baseline Scan** step (`if: always()`, `continue-on-error: true`) that runs a passive scan against saucedemo.com after tests complete. ZAP findings never block green CI since we do not control the target site. The HTML scan report is uploaded as a workflow artifact.

> **Secrets required:** `OPENAI_API_KEY` must be added to **Settings → Secrets → Actions** for `ai-eval.yml`, `conv-eval.yml`, `agent-eval.yml`, `langchain-rag.yml`, and `dspy-optimizer.yml`. `ANTHROPIC_API_KEY` and `TAVILY_API_KEY` are required for `job-agent.yml`; `ANTHROPIC_API_KEY` alone is required for `langgraph-agent.yml`. `dspy-vertex` requires GCP credentials (`GOOGLE_APPLICATION_CREDENTIALS` or `gcloud auth`). `VERCEL_TOKEN` is required for `deploy-validate-rollback.yml`. `SHOPIFY_STORE_URL` is required for Shopify E2E tests. `DD_API_KEY` (optional DataDog free trial) enables CI Visibility and custom metrics across all frameworks. All utilities skip gracefully without it. The three new AI framework workflows (`langchain-rag`, `langgraph-agent`, `dspy-optimizer`) only call APIs on `workflow_dispatch` — lint runs for free on every push/PR.

### DataDog Observability

Two DataDog features run across all frameworks:

**CI Visibility**: the `datadog/datadog-ci-github-action@v2.5.0` step (`if: always()`) uploads JUnit/TRX XML results to DataDog's Test Optimization dashboard after every run. Enables pass/fail trend charts, flaky-test detection, and duration tracking without leaving the DataDog UI.

**Custom metrics**: a `DataDogUtils` utility (Java, C#, Python) sends four GAUGE metrics to the v2 HTTP API at suite finish: `test.suite.passed`, `test.suite.failed`, `test.suite.skipped`, `test.suite.duration_ms`. Tagged with `framework:<name>`, `service:qa-automation-portfolio`, `env:ci`.

**AI evaluation frameworks bonus**: `datadog_reporter.send_eval_score()` sends LLM evaluation scores after each DeepEval assertion, connecting AI model quality directly to observability dashboards:

| Framework | DataDog metrics |
|---|---|
| `ai-eval` | `llm.eval.answer_relevancy` · `llm.eval.faithfulness` · `llm.eval.hallucination` · `llm.eval.safety` · `llm.eval.bias` · `llm.eval.json_correctness` |
| `conv-eval` | `llm.conv.turn_relevancy` · `llm.conv.knowledge_retention` · `llm.conv.role_adherence` · `llm.conv.graceful_handling` · `llm.conv.bias` · `llm.conv.toxicity` |
| `agent-eval` | `llm.agent.tool_correctness` · `llm.agent.task_completion` · `llm.agent.bias` · `llm.agent.toxicity` |
| `job-agent` | `llm.job_agent.jobs_found` · `llm.job_agent.jobs_scored` · `llm.job_agent.cover_letters_drafted` · `llm.job_agent.duration_ms` |
| all four + job-agent | `llm.api.latency_ms` |
| `fastapi-service` | `cache.hits` · `cache.misses` |

All utilities follow the same graceful-skip pattern as SlackUtils: if `DD_API_KEY` is absent, a `[WARN]` is logged and execution continues, while the CI stays green.

---

## Target Application

All three browser frameworks test [SauceDemo](https://www.saucedemo.com/), a purpose-built e-commerce demo with stable, publicly documented test credentials. No back-end setup is required. The three AI evaluation frameworks (`ai-eval`, `conv-eval`, `agent-eval`) also use the SauceDemo domain as their knowledge base, simulating a real customer support system.

| Page | Coverage |
|---|---|
| Login | Valid login · invalid credentials · locked-out user · data-driven multi-user |
| Dashboard | Cart icon · logout flow · direct-URL security check |
| Inventory | Add item · add multiple · remove item · badge count |
| Cart | Item verification · checkout navigation |
| API | Health check · data integrity (JSONPlaceholder) |
| Security | SQL injection · XSS payload · repeated failed logins · HTTP security headers |

---

## Security Testing

All three frameworks include an OWASP-aware security test suite targeting the SauceDemo login surface. Security tests reuse existing page objects and utilities. No new infrastructure is required.

### Test cases (all 3 frameworks)

| Test | What it verifies | OWASP category |
|---|---|---|
| SQL injection rejected | `' OR '1'='1' --` in username triggers an error; error message contains no `sql` / `exception` leakage | A03 Injection |
| XSS handled safely | `<script>document.title='xss'</script>` in username triggers an error; page title is not changed to `xss` | A03 Injection |
| Repeated failed logins | 5 consecutive bad logins followed by a valid login. Valid login must still succeed | A07 Identification & Authentication Failures |
| Security response headers | `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy` checked via HTTP GET | A05 Security Misconfiguration |

The headers test uses soft assertions (`SoftAssert` in Java, `Assert.Multiple` in C#) so it documents the site's security posture without blocking CI on a target we do not control.

### Framework-specific notes

| Framework | File | Groups / Tags |
|---|---|---|
| selenium-java | `src/test/java/com/framework/tests/SecurityTest.java` | `security`, `regression`, `web` picked up by `testng.xml` |
| playwright-dotnet | `tests/Framework.Tests/Tests/SecurityTest.cs` | `[Category("security")]`, `[Category("regression")]` |
| cucumber | `src/test/resources/features/security.feature` + `SecuritySteps.java` | `@security` runs with all features by default |

### OWASP ZAP Baseline Scan (CI)

Each workflow runs a passive ZAP scan after tests complete:

```yaml
- name: OWASP ZAP Baseline Scan
  if: always()
  uses: zaproxy/action-baseline@v0.12.0
  continue-on-error: true
  with:
    target: 'https://www.saucedemo.com'
    allow_issue_writing: false
    cmd_options: '-I'
```

- `continue-on-error: true`: ZAP findings never block green CI
- `allow_issue_writing: false`: no GitHub issues created automatically
- `-I`: informational mode; suppresses non-zero exit on warnings
- The HTML scan report (`zap_baseline_scan.html`) is auto-uploaded as a workflow artifact

---

## Kubernetes Infrastructure

The `k8s/` directory contains Kubernetes manifests that mirror the existing `docker-compose.yaml` providing an alternative deployment target for the Selenium Grid and Healenium stack.

### Directory layout

```
k8s/
├── namespace.yaml                  # selenium-grid namespace
├── configmap.yaml                  # Healenium DB credentials
├── selenium-grid/
│   ├── hub-deployment.yaml         # selenium/hub:4.16.1
│   ├── hub-service.yaml            # ClusterIP: ports 4444, 4442, 4443
│   ├── chrome-deployment.yaml      # selenium/node-chrome:4.16.1
│   ├── firefox-deployment.yaml     # selenium/node-firefox:4.16.1
│   └── edge-deployment.yaml        # selenium/node-edge:4.16.1
└── healenium/
    ├── postgres-deployment.yaml    # postgres:12-alpine
    ├── postgres-service.yaml
    ├── hlm-backend-deployment.yaml # healenium/hlm-backend:3.3.0
    ├── hlm-backend-service.yaml
    ├── hlm-imitator-deployment.yaml# healenium/hlm-selector-imitator:1.0.2
    └── hlm-imitator-service.yaml
```

### Design decisions

| Decision | Detail |
|---|---|
| Image versions | Pinned to the same tags as `docker-compose.yaml` (e.g. `selenium/hub:4.16.1`) |
| Shared memory | Chrome/Firefox/Edge nodes mount `/dev/shm` via `emptyDir: {medium: Memory, sizeLimit: 2Gi}`: matches `shm_size: 2gb` in Docker Compose |
| Postgres storage | `emptyDir` (non-persistent) sufficient for portfolio/demo; swap for a `PersistentVolumeClaim` in production |
| Healenium config | Credentials stored in `configmap.yaml`; referenced by `configMapKeyRef` in each dependent deployment |
| DNS resolution | Browser nodes set `SE_EVENT_BUS_HOST: selenium-hub` Kubernetes DNS resolves this to the hub `ClusterIP` Service |

### Deploy manually

```bash
# Namespace + config
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml

# Selenium Hub
kubectl apply -f k8s/selenium-grid/hub-deployment.yaml
kubectl apply -f k8s/selenium-grid/hub-service.yaml

# Browser nodes (add firefox / edge as needed)
kubectl apply -f k8s/selenium-grid/chrome-deployment.yaml

# Healenium stack
kubectl apply -f k8s/healenium/

# Wait for hub to be ready
kubectl wait deployment/selenium-hub --for=condition=Available --timeout=120s -n selenium-grid

# Port-forward and run tests
kubectl port-forward svc/selenium-hub 4444:4444 -n selenium-grid &
cd selenium-java && mvn clean test -Dtarget=grid -Dgrid_url=http://localhost:4444/wd/hub -Dheadless=true
```

### k8s CI workflow (`k8s.yml`)

Triggered via `workflow_dispatch` only (avoids heavy image pulls on every push). Spins up a [Kind](https://kind.sigs.k8s.io/) cluster, deploys the hub + Chrome node, port-forwards, and runs the smoke suite:

```
Input: framework → selenium-java | cucumber
Steps: checkout → Kind cluster → JDK 17 → apply k8s manifests → wait for Available
       → port-forward → health check → mvn smoke tests → upload surefire reports
```
