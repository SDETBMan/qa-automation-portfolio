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
- **AI / LLM Testing:** DeepEval, Anthropic Claude (tool-use, agentic loops, `@beta_tool` auto-schema, multi-agent orchestration), OpenAI function-calling, ChromaDB, RAG evaluation, conversation evaluation, agent evaluation
- **CI/CD:** GitHub Actions, Azure DevOps Pipelines, Jenkins, Docker, Kubernetes (k8s health checks)
- **Performance Testing:** k6 (load testing with scenario executors), JMeter (Maven plugin)
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
**Structure:** 10 independent, production-grade frameworks in a single monorepo.
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
- **Azure DevOps Pipeline** (`azure-pipelines.yml`) — ADO YAML equivalent of the GHA PR smoke gate
- Allure reporting + GitHub Pages deployment
- Trace Viewer artifacts on failure (DOM snapshots, screenshots, network calls)
- DataDog CI Visibility via TRX upload

**GraphQL testing layer (TypeScript suite):**
- `utils/graphqlClient.ts` — typed `GraphQLClient` class built on Playwright's built-in `APIRequestContext`; zero new npm dependencies; handles query/mutation, variables, operationName, auth headers
- `graphqlClient` fixture in `fixtures.ts` — reads `GRAPHQL_URL` + `API_TOKEN` from env; auto-injects Bearer token; follows same setup/yield/teardown pattern as `authenticatedPage`
- `api` project in `playwright.config.ts` — dedicated project for GraphQL/API tests; `testMatch` scoped to `graphql.spec.ts`
- 5 test patterns in `tests/graphql.spec.ts`:
  1. Direct query (happy path) — `data` and `errors` both asserted; documents HTTP 200 ≠ success
  2. Query with variables — parameterized filtering, validates list contents and exclusions
  3. Mock by `operationName` — `page.route()` + `page.evaluate()` intercepts fetch from browser context; veterinary mock data (Patient, VitalSigns); demonstrates how to test UI against controlled clinical data states
  4. GraphQL error contract — verifies `errors[]` populated on invalid query; documents that HTTP status alone is insufficient assertion
  5. Passive operation auditor — `page.on('request')` records every GraphQL operation fired during a flow; documents N+1 detection, mutation hygiene, and auth boundary patterns

**PR smoke gate (`playwright-smoke-pr.yml`):**
- Triggers exclusively on `pull_request` to `main` (push/nightly handled by `playwright-dotnet.yml`)
- `timeout-minutes: 5` hard cap — fails the job if exceeded, forcing deliberate scope control
- `concurrency: cancel-in-progress: true` — new commit immediately cancels stale run
- Chromium only · `--grep @smoke` · `--retries=0` (fail-fast, no flakiness masking)
- `--reporter=github` posts inline PR annotations on failing assertions
- `$GITHUB_STEP_SUMMARY` writes pass/fail table to the PR Checks tab
- Artifacts (HTML report + traces) uploaded only on failure — keeps storage clean on green runs

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

### Framework 9: `coding-agent` — AI Coding Agent Demo Suite
**Stack:** Python 3.11 · Anthropic Claude (`claude-opus-4-6`) · `@beta_tool` decorator · `tool_runner` agentic loop
**What it does:** Demonstrates four coding-agent capabilities — codebase rewriting, code execution feedback loops, git/PR automation, and multi-agent orchestration — all targeting the SauceDemo test suite in this monorepo.

**Four demos:**

1. **Codebase Reader & Rewriter (`demo1`)** — Explores `cucumber_python/steps/` and `pages/`, identifies Page Object architecture violations in `auth_steps.py` (inline Selenium, magic strings), produces a compliant rewrite at `output/auth_steps_rewritten.py`, and validates it with `python -m py_compile`. Iterates on any compile error.

2. **Code Execution Feedback Loop (`demo2`)** — Writes `output/validate_saucedemo.py`, runs it via bash, reads stdout/stderr, and iterates until all assertions pass and exit code is 0. Uses only the Python standard library — the agent discovers this constraint and adapts. Demonstrates the write → run → observe → fix loop underpinning reliable AI-generated code.

3. **Git & PR Automation (`demo3`)** — Reads feature files, identifies highest-value scenarios, adds `@performance` tags, creates branch `agent/add-performance-tags`, commits with a conventional commit message, dry-runs `git push`, and produces a full PR description (Summary + Motivation + Test Plan). No remote state modified in demo mode.

4. **Multi-Agent: Planner → Executor → Validator (`demo4`)** — Three specialised agents with role-scoped tools collaborate to add a new Behave cart scenario end-to-end:
   - **Planner**: `read_file` + `list_files` only — explores codebase, outputs structured JSON implementation plan
   - **Executor**: `read_file` + `write_file` + `run_bash` — implements the plan, runs `py_compile` on modified files
   - **Validator**: `run_bash` only — runs `behave --dry-run` + `grep`, issues `VERDICT: PASS | FAIL` with evidence
   - Orchestrator passes each agent's output as the next agent's input — clean, auditable context handoff

**Architecture:**
- `@beta_tool` decorator — auto-generates JSON schemas from function signatures + Google-style docstrings; no manual schema maintenance
- `client.beta.messages.tool_runner()` — SDK-managed agentic loop; each `BetaMessage` yielded for streaming display
- `thinking: {"type": "adaptive"}` — Opus 4.6 dynamically scales reasoning budget; low for trivial tasks, high for multi-file analysis
- Role-scoped tools in Demo 4 mirror real-world access control (Validator can't modify files it's verifying)
- All agent-generated files written to `output/` (git-ignored); no production code modified during demos

**Tool inventory (all `@beta_tool` decorated):**
- `file_tools.py`: `read_file`, `write_file`, `list_files`
- `bash_tools.py`: `run_bash` (stdout + stderr + exit code)
- `git_tools.py`: `git_status`, `git_diff`, `git_create_branch`, `git_add_and_commit`, `git_push`
- `github_tools.py`: `gh_create_pr`, `gh_list_pr_comments`, `gh_reply_to_pr`, `gh_pr_status`

**CLI:** `python run_demo.py --demo {1-4}` or `--all`; `--quiet` for summary-only output

**CI (`coding-agent.yml`):**
- Lint + import smoke test on every push to `coding-agent/**` (no API calls)
- Demo 2 runs on `workflow_dispatch` (requires `ANTHROPIC_API_KEY` secret); output uploaded as 7-day artifact
- Manual dispatch runs any demo or `--all`

---

### Framework 10: `cucumber_python` — Python BDD Framework
**Stack:** Python 3.11 · Behave (Python Cucumber) · Selenium 4 · requests · allure-behave
**What it does:** Python/Behave BDD framework mirroring the Java Cucumber framework, rebuilt with four architectural strategies specifically designed to prevent framework collapse at 1,000+ test scale.

**Four scaling strategies applied:**

1. **Declarative Gherkin** — Steps describe business intent (`When I login with valid credentials`), not UI mechanics. The "How" lives in Page Objects and Tasks, not Gherkin. Eliminates the step-definition explosion that kills frameworks at scale.

2. **Domain-Object Organization** — Step files organized by domain entity, not feature file: `auth_steps.py` (login/logout/session), `inventory_steps.py` (products/cart/checkout), `api_steps.py` (HTTP), `security_steps.py` (injection/XSS/headers), `common_steps.py` (shared). New engineers know exactly where to look.

3. **Aggressive Parameterization** — Behave `{type}` expressions make one step handle all variants: `{count:d}` covers every badge count, `{product}` covers every item name, `{expected_status:d}` covers every HTTP status. Avoids N steps for N values.

4. **Screenplay Pattern** — `utils/tasks.py` defines reusable `LoginTask` and `AddToCartTask` classes. Complex multi-step preconditions delegate to Tasks rather than duplicating step sequences. Separates Who (Actor), What (Task), How (Page Object Interaction). Prevents "God Object" page classes.

**Key features:**
- 6 feature files, 20+ scenarios: login, dashboard, inventory, cart, API, security
- `features/environment.py` — Behave hooks replacing Hooks.java: `before_all`, `before_scenario`, `after_scenario` (screenshot on failure), `after_all` (DataDog metrics + Slack)
- `pages/base_page.py` — shared wait/action wrappers (mirrors BasePage.java)
- `utils/driver_manager.py` — `threading.local()` thread-safe factory (mirrors ThreadLocal<WebDriver>); supports local, grid, BrowserStack targets
- `utils/config_reader.py` — priority: env vars > config.ini (mirrors ConfigReader.java)
- `utils/datadog_utils.py` / `utils/slack_utils.py` — same graceful-skip pattern as Java counterparts
- `utils/api_client.py` — thin `requests` wrapper for API test steps

**Healenium integration (Python-specific approach):**
Python has no native SelfHealingDriver SDK equivalent. Solution: Healenium's `hlm-proxy` image exposes a Selenium Grid-compatible HTTP proxy on port 8085. When `HEALENIUM_ENABLED=true`, `driver_manager.py` routes `RemoteWebDriver` through the proxy — Healenium intercepts element lookups and applies self-healing. Gracefully falls back to standard driver if proxy unreachable. Both `docker-compose.yaml` and `k8s/healenium/` include the `hlm-proxy` service.

**Infrastructure:**
- `Dockerfile` — multi-stage build (deps stage + runner stage with Chromium pre-installed)
- `docker-compose.yaml` — full stack: Selenium Grid (hub + Chrome/Firefox/Edge) + Healenium (postgres + hlm-backend + hlm-proxy)
- `k8s/` — 9 Kubernetes manifests: namespace, configmap, Grid hub/chrome/firefox, Healenium postgres/backend/proxy

**CI (`cucumber-python.yml`):**
- Triggers: push to `main` (path: `cucumber_python/**`), PR, nightly 05:00 UTC, `workflow_dispatch`
- Dispatch inputs: `execution_mode` (local/grid/browserstack), `test_browser`, `test_tags`
- Pipeline: Python 3.11 setup → install deps → run Behave → OWASP ZAP → DataDog CI Visibility → Allure → GitHub Pages → email on failure

**DataDog metrics:** `test.suite.passed`, `test.suite.failed`, `test.suite.skipped`, `test.suite.duration_ms` tagged `framework:cucumber-python`

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
| `cucumber-python` | test suite results + duration |
| `playwright-dotnet` | test suite results + duration |
| `job-agent` | jobs_found · jobs_scored · cover_letters_drafted · duration · latency |
| `coding-agent` | (no DataDog integration — demo artefacts written to `output/`) |

---

## CI Strategy

Each framework has its own workflow with **path filters** — a push to `selenium-java/` only triggers `selenium-java.yml`. Path filters prevent cross-framework interference.

| Workflow | Trigger | Key dispatch inputs |
|---|---|---|
| `playwright-smoke-pr.yml` | PR only · 5-min hard cap | — (Chromium · @smoke · retries=0 always) |
| `azure-pipelines.yml` | PR (Azure DevOps) | ADO equivalent of GHA smoke gate |
| `playwright-dotnet.yml` | push · PR · nightly 02:00 UTC | browser · execution mode · JMeter toggle |
| `selenium-java.yml` | push · PR · nightly 03:00 UTC | browser · suite XML · JMeter toggle |
| `cucumber.yml` | push · PR · nightly 04:00 UTC | browser · execution mode · JMeter toggle |
| `cucumber-python.yml` | push · PR · nightly 05:00 UTC | execution_mode · browser · test_tags |
| `ai-eval.yml` | push · PR · nightly 05:00 UTC | pytest marker (smoke · regression · safety) |
| `conv-eval.yml` | push · PR · nightly 06:00 UTC | pytest marker (smoke · regression · safety · retention) |
| `agent-eval.yml` | push · PR · nightly 07:00 UTC | pytest marker (smoke · regression) |
| `postman-newman.yml` | push · PR · nightly 08:00 UTC | folder filter |
| `job-agent.yml` | nightly 09:00 UTC · workflow_dispatch | role_filter keyword |
| `coding-agent.yml` | push · PR · workflow_dispatch | demo number (1-4 or all) |
| `k6-load-test.yml` | nightly 11:00 UTC · workflow_dispatch | — |
| `k8s.yml` | workflow_dispatch only | framework (selenium-java · cucumber) |

**Secrets required:**
- `OPENAI_API_KEY` — ai-eval, conv-eval, agent-eval
- `ANTHROPIC_API_KEY` — job-agent, coding-agent
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
