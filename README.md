# QA Automation Portfolio

[![playwright-dotnet CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/playwright-dotnet.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/playwright-dotnet.yml)
[![selenium-java CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/selenium-java.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/selenium-java.yml)
[![cucumber CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml)
[![ai-eval CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/ai-eval.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/ai-eval.yml)
[![conv-eval CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/conv-eval.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/conv-eval.yml)
[![agent-eval CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/agent-eval.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/agent-eval.yml)
[![k8s CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/k8s.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/k8s.yml)
[![postman-newman CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/postman-newman.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/postman-newman.yml)
[![job-agent CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/job-agent.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/job-agent.yml)

A monorepo housing eight independent, production-grade test automation frameworks, each showcasing a distinct testing approach used by senior SDETs in the industry.

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
| [`job-agent`](./job-agent/) | Python | Anthropic Claude · Tavily · Python 3.11 | [→](./job-agent/README.md) |

---

## Feature Coverage

| Capability | playwright-dotnet | selenium-java | cucumber | ai-eval | conv-eval | agent-eval | postman | job-agent |
|---|---|---|---|---|---|---|---|---|
| **Page Object Model** | ✅ C# + TypeScript | ✅ Java | ✅ Java | — | — | — | — | — |
| **Parallel execution** | ✅ `[Parallelizable]` · `fullyParallel` | ✅ `ThreadLocal` · `parallel="tests"` | ✅ `ThreadLocal` · `@DataProvider(parallel=true)` | — | — | — | — | — |
| **Fixtures / base classes** | ✅ `AuthenticatedTest` · `test.extend<>` | ✅ `BaseTest` | ✅ Cucumber `Hooks` | ✅ `conftest.py` session fixtures | ✅ `conftest.py` session + function fixtures | ✅ `conftest.py` session + function fixtures | — | — |
| **Retry on failure** | ✅ `[Retry]` · `retries: 2` in CI | ✅ `RetryAnalyzer` + `AnnotationTransformer` | ✅ `RetryAnalyzer` + `AnnotationTransformer` | — | — | — | — | — |
| **Cross-browser** | ✅ Chromium · Firefox · WebKit | ✅ Chrome · Firefox · Edge | ✅ Chrome · Firefox · Edge | — | — | — | — | — |
| **BDD / Gherkin** | — | — | ✅ 6 feature files · 19+ scenarios | — | — | — | — | — |
| **Data-driven tests** | ✅ `[TestCaseSource]` | ✅ `@DataProvider` | ✅ Scenario Outline | ✅ `golden_dataset.json` · `@pytest.mark.parametrize` | ✅ `conversations.json` · `@pytest.mark.parametrize` | ✅ `agent_scenarios.json` · `@pytest.mark.parametrize` | ✅ pre-request scripts · collection variables | — |
| **REST API testing** | ✅ `HttpClient` | ✅ RestAssured | ✅ RestAssured | — | — | — | ✅ Newman CLI · 10 requests · 4 test groups | — |
| **Mocking & Service Virtualization** | ✅ 4 patterns: block assets, mock API responses, inject headers, simulate failures · enables UI testing independent of backend readiness | — | — | — | — | — | — | — |
| **Observability & Analytics** | ✅ Allure · GitHub Pages · Trace Viewer (`retain-on-failure`): DOM snapshots, screenshots, network calls for fast MTTR | ✅ Allure | ✅ Allure · GitHub Pages | — | — | — | ✅ JUnit XML · htmlextra HTML report | — |
| **AI/ML Self-Healing Locators** | — | ✅ Healenium 3.4.8 | ✅ Healenium 3.4.8 | — | — | — | — | — |
| **LLM Evaluation (RAG pipeline)** | — | — | — | ✅ Answer Relevancy · Faithfulness · Hallucination · Safety · JSON Schema | — | — | — | — |
| **LLM Evaluation (Conversational)** | — | — | — | — | ✅ Turn Relevancy · Knowledge Retention · Role Adherence · Graceful Handling | — | — | — |
| **LLM Evaluation (Agentic / tool-use)** | — | — | — | — | — | ✅ Tool Correctness · Task Completion | — | — |
| **Function-calling agent** | — | — | — | — | — | ✅ Multi-step tool orchestration · deterministic tool implementations | — | — |
| **Agentic tool-use loop** | — | — | — | — | — | — | — | ✅ Claude claude-sonnet-4-6 · 5 tools · max 30 iterations · Tavily web search |
| **Automated job search** | — | — | — | — | — | — | — | ✅ 5 role queries · score_job_fit · draft_cover_letter · save_results |
| **JSON schema validation** | — | — | — | ✅ `JsonCorrectnessMetric` · Pydantic `BaseModel` schemas | — | — | — | — |
| **Cost & latency tracking** | — | — | — | ✅ per-call tokens · `latency_ms` → DataDog | ✅ per-turn tokens · `latency_ms` → DataDog | ✅ per-step tokens · `latency_ms` → DataDog | — | ✅ `latency_ms` · run counts → DataDog |
| **Mobile (Appium)** | — | ✅ Android · iOS | ✅ Android · iOS | — | — | — | — | — |
| **Performance (JMeter)** | — | ✅ Maven plugin | ✅ Maven plugin | — | — | — | — | — |
| **Database validation** | — | ✅ JDBC / MySQL | ✅ JDBC / MySQL | — | — | — | — | — |
| **Security testing (OWASP)** | ✅ 4 test cases | ✅ 4 test cases | ✅ 3 BDD scenarios | — | — | — | — | — |
| **OWASP ZAP passive scan** | ✅ CI pipeline | ✅ CI pipeline | ✅ CI pipeline | — | — | — | — | — |
| **Containerized infra** | — | ✅ Docker Compose · K8s | ✅ Docker Compose · K8s | — | — | — | — | — |
| **Slack notifications** | — | ✅ Webhook | ✅ Webhook | — | — | — | — | — |
| **DataDog observability** | ✅ CI Visibility (TRX) | ✅ CI Visibility · Custom metrics | ✅ CI Visibility · Custom metrics | ✅ CI Visibility · LLM eval scores | ✅ CI Visibility · LLM eval scores | ✅ CI Visibility · LLM eval scores | ✅ CI Visibility (JUnit XML) | ✅ Custom metrics · run counts · latency |
| **GitHub Actions CI** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ nightly 09:00 UTC |
| **Agentic AI Development** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

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
│       ├── postman-newman.yml      # triggers on: paths postman/**
│       ├── job-agent.yml           # nightly 09:00 UTC · workflow_dispatch (role_filter input)
│       └── k8s.yml                 # workflow_dispatch only: Kind cluster + grid smoke tests
├── ai-eval/                            # Python · Pytest · DeepEval · OpenAI · ChromaDB
│   ├── rag/                            # RAG pipeline: document, embedder, retriever
│   ├── datasets/golden_dataset.json    # Ground truth Q&A pairs (SauceDemo FAQ)
│   ├── evals/                          # test_answer_relevancy · faithfulness · hallucination · safety · json_correctness
│   ├── conftest.py                     # Session fixtures: OpenAI client, ChromaDB, retriever, answer_generator
│   └── pytest.ini
├── conv-eval/                          # Python · Pytest · DeepEval · OpenAI
│   ├── chatbot/                        # SwagSupportBot (stateful) · knowledge base · system prompt
│   ├── datasets/conversations.json     # 7 multi-turn conversation scenarios
│   ├── evals/                          # test_conversation_relevancy · knowledge_retention · role_adherence · graceful_handling
│   ├── conftest.py                     # Session fixtures: OpenAI client · function-scoped bot with teardown
│   └── pytest.ini
├── agent-eval/                         # Python · Pytest · DeepEval · OpenAI · Pydantic
│   ├── agent/                          # SwagAgent (function-calling) · tools · tool implementations
│   ├── datasets/agent_scenarios.json   # 7 scenarios: single-tool and multi-tool orchestration
│   ├── evals/                          # test_tool_correctness · test_task_completion
│   ├── conftest.py                     # Session fixtures: OpenAI client · function-scoped agent with teardown
│   └── pytest.ini
├── playwright-dotnet/              # Playwright · NUnit · C# · TypeScript
│   ├── tests/
│   │   ├── Framework.Tests/        # NUnit C# test project
│   │   └── playwright-ts/          # TypeScript Playwright project
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
├── k8s/                            # Kubernetes manifests (mirrors docker-compose.yaml)
│   ├── namespace.yaml              # selenium-grid namespace
│   ├── configmap.yaml              # Healenium DB credentials
│   ├── selenium-grid/              # Hub + Chrome/Firefox/Edge node deployments & services
│   └── healenium/                  # Postgres, hlm-backend, hlm-selector-imitator
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
| `ai-eval.yml` | push · PR · nightly 05:00 UTC | pytest marker filter (smoke · regression · safety) |
| `conv-eval.yml` | push · PR · nightly 06:00 UTC | pytest marker filter (smoke · regression · safety · retention) |
| `agent-eval.yml` | push · PR · nightly 07:00 UTC | pytest marker filter (smoke · regression) |
| `postman-newman.yml` | push · PR · nightly 08:00 UTC | folder filter (Smoke · Users · Posts · Integration Flow) |
| `job-agent.yml` | nightly 09:00 UTC · `workflow_dispatch` | role_filter keyword (e.g. SDET · QA Lead) |
| `k8s.yml` | `workflow_dispatch` only | framework (selenium-java · cucumber) |

All three browser-test workflows include an **OWASP ZAP Baseline Scan** step (`if: always()`, `continue-on-error: true`) that runs a passive scan against saucedemo.com after tests complete. ZAP findings never block green CI since we do not control the target site. The HTML scan report is uploaded as a workflow artifact.

> **Secrets required:** `OPENAI_API_KEY` must be added to **Settings → Secrets → Actions** for `ai-eval.yml`, `conv-eval.yml`, and `agent-eval.yml`. `ANTHROPIC_API_KEY` and `TAVILY_API_KEY` are required for `job-agent.yml`. `DD_API_KEY` (optional DataDog free trial) enables CI Visibility and custom metrics across all frameworks. All utilities skip gracefully without it.

### DataDog Observability

Two DataDog features run across all frameworks:

**CI Visibility**: the `datadog/datadog-ci-github-action@v2.5.0` step (`if: always()`) uploads JUnit/TRX XML results to DataDog's Test Optimization dashboard after every run. Enables pass/fail trend charts, flaky-test detection, and duration tracking without leaving the DataDog UI.

**Custom metrics**: a `DataDogUtils` utility (Java, C#, Python) sends four GAUGE metrics to the v2 HTTP API at suite finish: `test.suite.passed`, `test.suite.failed`, `test.suite.skipped`, `test.suite.duration_ms`. Tagged with `framework:<name>`, `service:qa-automation-portfolio`, `env:ci`.

**AI evaluation frameworks bonus**: `datadog_reporter.send_eval_score()` sends LLM evaluation scores after each DeepEval assertion, connecting AI model quality directly to observability dashboards:

| Framework | DataDog metrics |
|---|---|
| `ai-eval` | `llm.eval.answer_relevancy` · `llm.eval.faithfulness` · `llm.eval.hallucination` · `llm.eval.safety` · `llm.eval.json_correctness` |
| `conv-eval` | `llm.conv.turn_relevancy` · `llm.conv.knowledge_retention` · `llm.conv.role_adherence` · `llm.conv.graceful_handling` |
| `agent-eval` | `llm.agent.tool_correctness` · `llm.agent.task_completion` |
| `job-agent` | `llm.job_agent.jobs_found` · `llm.job_agent.jobs_scored` · `llm.job_agent.cover_letters_drafted` · `llm.job_agent.duration_ms` |
| all four + job-agent | `llm.api.latency_ms` |

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
