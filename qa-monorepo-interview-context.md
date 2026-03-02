# QA Automation Portfolio — Interview Context for Claude AI

Paste this file into a new Claude conversation to give it full context about the
candidate's background, monorepo, and experience for interview preparation, cover
letter review, or job-fit analysis.

---

## Candidate Overview

**Name:** Brian
**Title:** QA Leader / SDET
**Experience:** 9+ years building and leading test automation in SaaS and enterprise environments
**Location:** Utah (Salt Lake City / Utah County corridor — Lehi, South Jordan, Draper, West Valley)
**Work preference:** Fully remote strongly preferred; open to hybrid within the Utah corridor
**Employment type:** Full-time W2 preferred; contract-to-hire acceptable. Not interested in C2C / 1099.
**Salary target:** $120,000+ base
**Target roles:** SDET, QA Lead, Lead QA Engineer, Quality Engineering Manager, AI QA Engineer, LLM Testing Engineer

---

## Technical Skills

- **Languages:** Java (primary), Python, C#, TypeScript, JavaScript
- **UI Automation:** Selenium WebDriver, Playwright (C# + TypeScript), Cucumber/BDD
- **API Testing:** REST Assured, Postman/Newman, pytest
- **AI / LLM Testing:** DeepEval, Anthropic Claude (tool-use, agentic loops), OpenAI function-calling, ChromaDB, RAG evaluation, conversation evaluation, agent evaluation
- **CI/CD:** GitHub Actions, Jenkins, Docker, Kubernetes (k8s health checks)
- **Monitoring / Observability:** DataDog (custom metrics via v2 API, CI Visibility, dashboard JSON, Allure reporting)
- **Build tools:** Maven, pip, npm, .NET CLI
- **Other:** Git, JIRA, TestRail, Page Object Model, Factory pattern, BDD, parallel execution, retry analyzers, OWASP ZAP

---

## Work History

### Team Lead QA Engineer — Solutionreach | Lehi, UT (Hybrid)
*September 2024 – February 2026*
- Integration Testing: Led end-to-end testing for complex data exchange between third-party SaaS platforms and internal APIs, ensuring healthcare data integrity and compliance.
- Quality Gates: Collaborated with Engineering and Product to embed CI/CD quality gates detecting accuracy regressions in real-time, shifting quality validation left.
- Framework Architecture: Maintained scalable automation suites using Playwright, Selenium, REST Assured with parallel execution.
- Process Design: Architected QA documentation standards and release protocols that became organizational best practices.
- Team Mentorship: Mentored team on modern SDET practices, AI evaluation frameworks, and enterprise-grade test design patterns.

### Senior QA Engineer — Intuit Inc. | Washington, DC (Remote)
*January 2021 – September 2024*
- Selenium Grid Architecture: Designed and maintained production-grade Selenium Grid supporting cross-browser coverage (Chrome, Firefox, Safari, Edge).
- Parallel Execution: Implemented parallel test strategy reducing regression suite runtime from 4+ hours to 45 minutes.
- CI/CD Quality Gates: Integrated test suites into Jenkins, establishing immediate feedback loops for rapid release cycles.
- Test Selection Logic: Designed intelligent test selection running only affected tests based on code changes.
- Allure Integration: Implemented Allure Reporting for transparent execution visibility and failure analysis.
- Framework Modernization: Mentored team on POM design, CI/CD best practices, and Selenium 4 migration.
- Data Validation: Complex SQL validation across financial databases ensuring transactional integrity.

### QA Engineer — Farmers Insurance | San Diego, CA
*July 2018 – December 2020*
- Developed automated regression suites using Java, Selenium WebDriver, and TestNG in Agile/Scrum.
- SQL validation across PostgreSQL/MySQL ensuring data accuracy in financial systems.
- Identified and documented data-layer race conditions, establishing patterns for database validation testing.

### Jr. QA Engineer — Mastercard | San Diego, CA
*January 2017 – June 2018*
- Functional, smoke, and regression tests for payment processing workflows.
- Backend data validation using SQL across multiple database systems.
- Agile sprint planning and defect triage.

### Education
University of Utah | Salt Lake City, UT
Bachelor of Science | Expected Completion: 2026

---

## Portfolio: qa-automation-portfolio (GitHub Monorepo)

**Repo:** github.com/SDETBMan/qa-automation-portfolio
**Structure:** 8 independent, production-grade frameworks in a single monorepo.
Each framework has its own CI workflow, dependencies, and DataDog integration.
All run nightly on GitHub Actions.

---

### Framework 1: `ai-eval` — RAG Pipeline Quality Evaluation
**Stack:** Python 3.11 · DeepEval · OpenAI (GPT-4o-mini) · ChromaDB · pytest
**What it does:** Evaluates a full RAG (Retrieval-Augmented Generation) pipeline built on SauceDemo FAQ content. ChromaDB stores embedded FAQ chunks; OpenAI generates grounded answers; DeepEval scores those answers with 5 metrics.

**Metrics evaluated:**
- Answer Relevancy (0.7 threshold)
- Faithfulness (0.8 threshold)
- Hallucination (lower is better)
- Safety / toxicity
- JSON Schema Correctness (Pydantic models)

**Key architecture decisions:**
- `conftest.py` session fixtures: ChromaDB embedded once per session, shared across all tests
- `golden_dataset.json` — 10 Q&A pairs tagged `smoke` / `regression` / `safety` for marker-based filtering
- `pytest.mark.parametrize` drives all test cases from the dataset
- `DEEPEVAL_DISABLE_TIMEOUTS=true` in CI to prevent false failures from slow OpenAI responses
- `--reruns 5 --reruns-delay 60` handles transient OpenAI API timeouts

**DataDog metrics sent:**
- `llm.eval.answer_relevancy`, `llm.eval.faithfulness`, `llm.eval.hallucination`, `llm.eval.safety`, `llm.eval.json_correctness`
- `llm.api.latency_ms`, `llm.api.prompt_tokens`, `llm.api.completion_tokens`, `llm.api.total_tokens`
- `test.suite.passed`, `test.suite.failed`, `test.suite.skipped`, `test.suite.duration_ms`

---

### Framework 2: `conv-eval` — Multi-Turn Conversation Quality
**Stack:** Python 3.11 · DeepEval · OpenAI (GPT-4o-mini) · pytest
**What it does:** Tests a stateful customer support chatbot (SwagSupportBot) across 7 multi-turn conversation scenarios.

**Metrics evaluated:**
- Turn Relevancy — does each response address the current turn?
- Knowledge Retention — does the bot remember earlier facts within a conversation?
- Role Adherence — does it stay in character as a Swag Labs support agent?
- Graceful Handling — does it reject out-of-scope queries and prompt injection attempts safely?

**Key architecture decisions:**
- Function-scoped `bot` fixture: a fresh bot instance per test with teardown metrics reporting
- `conversations.json` drives parametrized test cases
- Markers: `smoke`, `regression`, `safety`, `retention`

**DataDog metrics:** `llm.conv.turn_relevancy`, `llm.conv.knowledge_retention`, `llm.conv.role_adherence`, `llm.conv.graceful_handling` + standard suite and API metrics

---

### Framework 3: `agent-eval` — AI Agent Tool-Use Evaluation
**Stack:** Python 3.11 · DeepEval · OpenAI function-calling · Pydantic · pytest
**What it does:** Tests SwagAgent, an OpenAI function-calling agent, across 7 scenarios ranging from single-tool calls to multi-step orchestration.

**Metrics evaluated:**
- Tool Correctness — did the agent call the right tool with correct arguments?
- Task Completion — did the agent successfully complete the assigned goal?

**Key architecture decisions:**
- Deterministic tool implementations (no live calls) for reproducible evals
- Pydantic models validate tool arguments and responses
- `agent_scenarios.json` drives parametrized scenarios
- Markers: `smoke` (single-tool), `regression` (multi-tool orchestration)

**DataDog metrics:** `llm.agent.tool_correctness`, `llm.agent.task_completion` + standard suite and API metrics

---

### Framework 4: `playwright-dotnet` — Cross-Browser UI Testing
**Stack:** C# · TypeScript · Playwright 1.44 · NUnit · .NET 8
**What it does:** Two parallel Playwright suites — one in C# (NUnit) and one in TypeScript — testing SauceDemo end-to-end.

**Key features:**
- Page Object Model in both C# and TypeScript
- `AuthenticatedTest` base class for shared login state
- `[Parallelizable]` + `fullyParallel: true` for concurrent execution
- `[Retry]` attribute + `retries: 2` in CI config
- 4 mocking patterns: block assets, mock API responses, inject headers, simulate failures
- 4 OWASP security test cases (SQL injection, XSS, auth failures, security headers)
- `Assert.Multiple` for soft assertions on security header checks
- OWASP ZAP passive baseline scan in CI (`continue-on-error: true`)
- Allure reporting + GitHub Pages deployment
- Trace Viewer artifacts on failure (DOM snapshots, screenshots, network calls)
- DataDog CI Visibility via TRX upload

---

### Framework 5: `selenium-java` — UI Regression Suite
**Stack:** Java 17 · Selenium 4 · TestNG · Maven
**What it does:** Production-grade Selenium Grid framework testing SauceDemo with full cross-browser support.

**Key features:**
- `DriverFactory` with `ThreadLocal<WebDriver>` for parallel-safe execution
- `BaseTest` with `@BeforeMethod` / `@AfterMethod` lifecycle
- `RetryAnalyzer` + `AnnotationTransformer` for automatic retry on failure
- Cross-browser: Chrome, Firefox, Edge (headless)
- Selenium Grid via Docker Compose + Kubernetes manifests
- **Healenium 3.4.8** — AI-powered self-healing locators (backed by PostgreSQL)
- Appium support for Android + iOS (testng_mobile.xml)
- JMeter performance testing via Maven plugin
- JDBC / MySQL database validation
- Slack webhook notifications on suite completion
- 4 OWASP security tests + ZAP passive scan
- Allure reporting
- DataDog CI Visibility + custom metrics

---

### Framework 6: `cucumber` — BDD Feature Tests
**Stack:** Java 17 · Cucumber 7 · TestNG · Selenium 4 · Maven
**What it does:** BDD-style feature coverage of SauceDemo with Gherkin scenarios.

**Key features:**
- 6 feature files, 19+ scenarios: login, dashboard, inventory, cart, API, security
- Scenario Outline for data-driven BDD cases
- Parallel execution via `@DataProvider(parallel=true)` and `ThreadLocal` driver management
- Healenium self-healing locators (same stack as selenium-java)
- Appium mobile support
- JMeter performance tests
- Slack notifications
- OWASP security scenarios (`@security` tag)
- Allure reporting + GitHub Pages
- DataDog CI Visibility + custom metrics

---

### Framework 7: `postman` — REST API Contract Tests
**Stack:** Postman Collection v2.1 · Newman 6 · Node.js 20
**What it does:** REST API contract testing against JSONPlaceholder (public REST API).

**Key features:**
- 10 requests across 4 folders: Smoke, Users, Posts, Integration Flow
- Pre-request scripts and collection variables
- `htmlextra` reporter for rich HTML output
- JUnit XML for DataDog CI Visibility upload
- Folder-level filtering via `npm run test:smoke`, `npm run test:verbose`, `npm run test:html`

---

### Framework 8: `job-agent` — Agentic Job Search Tool
**Stack:** Python 3.11 · Anthropic Claude (claude-sonnet-4-6) · Tavily API
**What it does:** A real autonomous agent — not an eval framework — that searches for QA/SDET job postings, scores them against a candidate profile, and drafts tailored cover letters. Differentiates the portfolio by demonstrating Anthropic Claude usage alongside the OpenAI-based eval frameworks.

**Architecture:**
- `agent/tools.py`: 5 Anthropic tool_use definitions:
  1. `search_jobs(query)` — Tavily web search, returns title/URL/snippet/score
  2. `fetch_job_posting(url)` — Tavily content extraction, returns full posting text
  3. `score_job_fit(job_title, company, job_description)` — focused Claude call, returns score 0-10 + strengths/gaps/recommendation
  4. `draft_cover_letter(job_title, company, job_description)` — returns polished markdown cover letter
  5. `save_results(jobs_json, cover_letters_json)` — writes `output/jobs_YYYY-MM-DD.md` and `output/cover_letters/Company_Title.md`
- `agent/job_hunter.py`: Agentic loop orchestrator (max 30 iterations, temperature=0)
  - Loads `profile/profile.md` → injected into system prompt
  - Runs 5 role-targeted search queries (remote + Utah-aware)
  - Filters to score >= 6, drafts cover letters for top matches
  - Scoring instructions penalise on-site roles outside Utah corridor and C2C/1099
- `run.py`: CLI entry point with `--role` filter and dotenv loading
- `profile/profile.md`: git-ignored; contains Brian's real resume/portfolio content
- `profile/profile.example.md`: template showing expected format

**5 search queries used:**
1. SDET remote OR "Salt Lake City" OR "Lehi Utah" job 2026
2. Lead QA Engineer remote OR Utah job 2026
3. Quality Engineering Manager remote OR Utah full time 2026
4. AI QA Engineer LLM testing remote OR Utah job 2026
5. QA Automation Lead Selenium Playwright remote OR Utah job 2026

**CI:** Nightly 09:00 UTC GitHub Actions. Uses `CANDIDATE_PROFILE` secret to inject the git-ignored `profile.md` into the CI runner. Outputs uploaded as 7-day artifacts.

**DataDog metrics:** `llm.job_agent.jobs_found`, `llm.job_agent.jobs_scored`, `llm.job_agent.cover_letters_drafted`, `llm.job_agent.duration_ms`, `llm.api.latency_ms`

**Successful local run results (2026-03-02):**
- AMH Software Development Engineer in Test III — score 9/10
- hackajob / Verisk SDET Team Lead — score 8/10
- 2 cover letters drafted

---

## DataDog Observability (All Frameworks)

**Two DataDog features run across all frameworks:**

**CI Visibility:** `datadog-ci junit upload` step uploads JUnit/TRX XML after every CI run. Enables pass/fail trend charts, flaky test detection, and duration tracking.

**Custom metrics:** A `DataDogUtils` utility (Java/C#/Python depending on framework) sends GAUGE metrics to the DataDog v2 HTTP API (`POST https://api.datadoghq.com/api/v2/series`). Tagged with `framework:<name>`, `service:qa-automation-portfolio`, `env:ci`.

**Graceful-skip pattern:** All utilities check for `DD_API_KEY` at startup. If absent, they log `[WARN]` and return — CI never fails due to missing DataDog credentials.

**Dashboard JSON files:** Each framework has a `datadog-dashboard.json` in its directory that can be imported directly into DataDog (Dashboards → New Dashboard → Import Dashboard).

| Framework | DataDog dashboard metrics |
|---|---|
| `ai-eval` | 5 eval scores + test suite + tokens + latency |
| `conv-eval` | test suite + tokens + API latency |
| `agent-eval` | test suite + tokens + API latency |
| `selenium-java` | test suite results + duration |
| `cucumber` | test suite results + duration |
| `playwright-dotnet` | test suite results + duration |
| `job-agent` | jobs_found · jobs_scored · cover_letters_drafted · duration · latency |

---

## CI Strategy

Each framework has its own workflow with **path filters** — a push to `selenium-java/` only triggers `selenium-java.yml`. Path filters prevent cross-framework interference.

| Workflow | Trigger | Key dispatch inputs |
|---|---|---|
| `playwright-dotnet.yml` | push · PR · nightly 02:00 UTC | browser · execution mode · JMeter toggle |
| `selenium-java.yml` | push · PR · nightly 03:00 UTC | browser · suite XML · JMeter toggle |
| `cucumber.yml` | push · PR · nightly 04:00 UTC | browser · execution mode · JMeter toggle |
| `ai-eval.yml` | push · PR · nightly 05:00 UTC | pytest marker (smoke · regression · safety) |
| `conv-eval.yml` | push · PR · nightly 06:00 UTC | pytest marker (smoke · regression · safety · retention) |
| `agent-eval.yml` | push · PR · nightly 07:00 UTC | pytest marker (smoke · regression) |
| `postman-newman.yml` | push · PR · nightly 08:00 UTC | folder filter |
| `job-agent.yml` | nightly 09:00 UTC · workflow_dispatch | role_filter keyword |
| `k8s.yml` | workflow_dispatch only | framework (selenium-java · cucumber) |

**Secrets required:**
- `OPENAI_API_KEY` — ai-eval, conv-eval, agent-eval
- `ANTHROPIC_API_KEY` — job-agent
- `TAVILY_API_KEY` — job-agent
- `CANDIDATE_PROFILE` — job-agent (injects git-ignored profile.md into CI runner)
- `DD_API_KEY` — optional, all frameworks (graceful skip if absent)

---

## Security Testing

All three browser frameworks include OWASP-aware security tests against SauceDemo:

| Test | What it verifies | OWASP category |
|---|---|---|
| SQL injection rejected | `' OR '1'='1' --` triggers error; no sql/exception leakage | A03 Injection |
| XSS handled safely | `<script>` payload in username; page title not changed | A03 Injection |
| Repeated failed logins | 5 bad logins + valid login still succeeds | A07 Auth Failures |
| Security response headers | X-Frame-Options, X-Content-Type-Options, CSP checked via HTTP GET | A05 Misconfiguration |

OWASP ZAP passive baseline scan runs in CI after tests (`continue-on-error: true`, `allow_issue_writing: false`). HTML report uploaded as workflow artifact.

---

## Kubernetes Infrastructure

`k8s/` directory mirrors `docker-compose.yaml` for Selenium Grid + Healenium:

- `selenium-grid/` — Hub + Chrome/Firefox/Edge node deployments and services
- `healenium/` — PostgreSQL, hlm-backend, hlm-selector-imitator

The `k8s.yml` workflow (workflow_dispatch only) spins up a Kind cluster, deploys the hub + Chrome node, port-forwards, and runs smoke tests. Avoids heavy image pulls on every push.

---

## Target Application

All browser and AI eval frameworks use **SauceDemo** (saucedemo.com) — a purpose-built e-commerce demo with stable, publicly documented test credentials. No backend setup required.

Test coverage: Login · Dashboard · Inventory · Cart · API · Security

---

## How to Use This File

Paste this entire file into a new Claude conversation, then ask:

- "Help me prep for a QA Lead interview at [Company]"
- "Evaluate this JD against my background" (paste the JD)
- "Write a cover letter for [role] at [company]"
- "What questions should I expect for a role requiring [skill]?"
- "How would I explain [framework] to a non-technical hiring manager?"
- "What are the strongest talking points from my portfolio for this JD?"
