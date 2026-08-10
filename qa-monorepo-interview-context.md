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
- **UI Automation:** Selenium WebDriver, Playwright, Cucumber/BDD
- **API Testing:** REST Assured, Karate 1.5, Postman/Newman, pytest
- **AI / LLM Testing:** DeepEval, Anthropic Claude (tool-use, agentic loops, `@beta_tool` auto-schema, multi-agent orchestration, AI test generation for Cypress), OpenAI function-calling, ChromaDB, RAG evaluation, conversation evaluation, agent evaluation
- **CI/CD:** GitHub Actions, Azure DevOps Pipelines, Jenkins, Docker, Kubernetes (k8s health checks)
- **Performance Testing:** k6 (load testing with scenario executors), JMeter (Maven plugin)
- **Monitoring / Observability:** DataDog (custom metrics via v2 API, CI Visibility, dashboard JSON, Allure reporting)
- **Build tools:** Maven, pip, npm, .NET CLI
- **Other:** Git, JIRA, TestRail, Testiny, Page Object Model, Factory pattern, BDD, parallel execution, retry analyzers, OWASP ZAP, Sauce Labs

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

## QA Operating Model

The repo includes two quality governance documents:
- **`QA-OPERATING-MODEL.md`** — Defines quality assurance standards, processes, and coverage strategy. Single source of truth for regression planning, release readiness, defect triage, and device/browser coverage across three tiers (Must Pass, Should Pass, Best Effort).
- **`ISO-9001-QUALITY-MANUAL.md`** — Maps portfolio quality practices to ISO 9001:2015 clause structure (sections 4-10), with cross-references to SOC 2 CC-series controls and ISO/IEC 17025:2017 (Testing and Calibration Laboratories). Supplements the operating model with formal compliance clause references.

---

## Portfolio at a Glance

**Repo:** github.com/SDETBMan/qa-automation-portfolio
**Structure:** 25 independent, production-grade frameworks in a single monorepo with 28 GitHub Actions workflows. Each framework has its own CI workflow, dependencies, and DataDog integration.

**Standalone repos:** 3 additional projects outside the monorepo — `legal-funding-qa-agent`, `agentic-p2p-auditor`, `ai-pr-reviewer` — for a total of 28 projects.

| # | Framework | Stack | Description |
|---|---|---|---|
| 1 | `ai-eval` | Python · DeepEval · OpenAI · ChromaDB | RAG pipeline quality evaluation with 10 DeepEval metrics |
| 2 | `conv-eval` | Python · DeepEval · OpenAI | Multi-turn conversation quality testing (4 metrics) |
| 3 | `agent-eval` | Python · DeepEval · OpenAI · Pydantic | AI agent tool-use evaluation (function-calling) |
| 4 | `playwright` | C# · TypeScript · Playwright · NUnit · .NET 8 | Cross-browser UI testing + GraphQL + visual regression + DB assertions |
| 5 | `selenium-java` | Java · Selenium 4 · TestNG · Maven | Production-grade UI regression suite with Healenium self-healing |
| 6 | `cucumber` | Java · Cucumber 7 · Karate 1.5 · TestNG | BDD feature tests + standalone Karate API testing (13 features) |
| 7 | `postman` | Postman · Newman 6 · Node.js 20 | REST API contract tests against JSONPlaceholder |
| 8 | `job-agent` | Python · Claude · Tavily | Agentic job search, scoring, and cover letter drafting |
| 9 | `coding-agent` | Python · Claude · `@beta_tool` | 5-demo AI coding agent (rewrite, execute, git, multi-agent, test gen) |
| 10 | `cucumber_python` | Python · Behave · Selenium 4 | Python BDD framework with 4 scaling strategies |
| 11 | `claims-diff` | Python · Pydantic · Pandas · BigQuery | Healthcare claims adjudication data diff engine |
| 12 | `pact-consumer` | TypeScript · Pact v13 · Vitest | Consumer-driven contract testing (8 interactions) |
| 13 | `flakiness-detector` | Python · JUnit XML · Click · DataDog | Flaky test detection, scoring, and quarantine recommendations |
| 14 | `vulnerability-aggregator` | Python · GitHub API · Dependabot · CodeQL · ZAP | Unified security scanning aggregation |
| 15 | `cypress` | TypeScript · Cypress 13 · React 18 · Claude | E2E + component tests + AI test generator |
| 16 | `quality-dashboard` | Python · JUnit XML · DataDog v2 · GH Actions API | Portfolio-wide quality KPI aggregation |
| 17 | `failure-triage` | Python · Claude · `@beta_tool` · JUnit XML | AI-powered failure root cause clustering |
| 18 | `fastapi-service` | Python · FastAPI · Redis · Pytest · k6 | REST API + Redis caching + full test suite + load tests |
| 19 | `terraform` | HCL · Terraform 1.6 · AWS · DataDog | IaC for S3 artifacts, OIDC IAM, DataDog observability |
| 20 | `langchain-rag` | Python · LangChain 0.3 · Chroma · OpenAI | Multi-turn conversational RAG assistant over monorepo docs |
| 21 | `langgraph-agent` | Python · LangGraph 0.4 · Claude Haiku | BDD test case generator with 4-node StateGraph pipeline |
| 22 | `dspy-optimizer` | Python · DSPy 2.6 · BootstrapFewShot · OpenAI | Bug severity classifier with prompt optimization |
| 23 | `dspy-vertex` | Python · DSPy 2.6 · Vertex AI Gemini 1.5 | Same classifier, Vertex AI backend (multi-LLM portability) |
| 24 | `site-monitor` | Python · BeautifulSoup · Click · DataDog · Requests | Website drift detection across 23 selectors for 5 frameworks |
| 25 | `qms-evidence-collector` | Python · Click · DataDog | Maps CI artifacts to ISO 9001, SOC 2, and ISO/IEC 17025 clauses |

---

## Deep Dives

### Framework 1: `ai-eval` — RAG Pipeline Quality Evaluation
**Stack:** Python 3.11 · DeepEval · OpenAI (GPT-4o-mini) · ChromaDB · pytest
**What it does:** Evaluates a full RAG (Retrieval-Augmented Generation) pipeline built on SauceDemo FAQ content. ChromaDB stores embedded FAQ chunks; OpenAI generates grounded answers; DeepEval scores those answers across 10 metrics in 8 test files.

**10 DeepEval metrics evaluated:**
- Answer Relevancy (0.7 threshold)
- Faithfulness via GEval (0.7 threshold) — custom rubric instead of built-in FaithfulnessMetric to stay within gpt-4o-mini output token limits
- Hallucination (lower is better)
- Hallucination Benchmark — aggregate sentinel across 10 test cases
- Toxicity / safety
- Bias — probes across gender, age, race, socioeconomic, adversarial stereotype
- JSON Schema Correctness (Pydantic models)
- Contextual Precision (0.7 threshold) — retrieval chunk relevance
- Contextual Recall (0.7 threshold) — retrieval context coverage
- Contextual Relevancy (0.05 threshold) — retrieval-to-query alignment (low threshold because coarse FAQ chunks yield low sentence-level ratios)

**Key architecture decisions:**
- `conftest.py` session fixtures: ChromaDB embedded once per session, shared across all tests
- `golden_dataset.json` — 10 Q&A pairs tagged `smoke` / `regression` / `safety` for marker-based filtering
- `pytest.mark.parametrize` drives all test cases from the dataset
- `DEEPEVAL_DISABLE_TIMEOUTS=true` in CI to prevent false failures from slow OpenAI responses
- `--reruns 5 --reruns-delay 60` handles transient OpenAI API timeouts

**DataDog metrics sent:**
- `llm.eval.answer_relevancy`, `llm.eval.faithfulness`, `llm.eval.hallucination`, `llm.eval.safety`, `llm.eval.json_correctness`, `llm.eval.contextual_precision`, `llm.eval.contextual_recall`, `llm.eval.contextual_relevancy`
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

### Framework 4: `playwright` — Cross-Browser UI Testing
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
- **Sauce Labs configuration** (`.sauce/config.yml`) — 3 suites (Chromium, Firefox, WebKit) via `saucectl`; runs Playwright natively on Sauce Labs infrastructure with `us-west-1` region and concurrency 4
- Allure reporting + GitHub Pages deployment
- Trace Viewer artifacts on failure (DOM snapshots, screenshots, network calls)
- DataDog CI Visibility via TRX upload
- **Testiny test management sync** — CI uploads JUnit XML results to Testiny via `@testiny/cli automation`

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
- Triggers exclusively on `pull_request` to `main` (push/nightly handled by `playwright.yml`)
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

### Framework 6: `cucumber` — BDD Feature Tests + Karate API Testing
**Stack:** Java 17 · Cucumber 7 · Karate 1.5.2 · TestNG · Selenium 4 · Maven
**What it does:** BDD-style feature coverage of SauceDemo with Gherkin scenarios, plus a standalone Karate API testing layer with 13 feature files (~42 scenarios).

**Key features (Cucumber):**
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

**Key features (Karate 1.5.2):**
- 13 feature files, ~42 scenarios across 4 domains:
  - **Core API** (3 features): Full CRUD on /users, /posts, /comments with nested resources, query filtering, request chaining
  - **Advanced patterns** (4 features): JSON schema validation with type markers (`#string`, `#number`, `#regex`), Scenario Outline + Examples for data-driven tests, header/auth/cookie management, error handling with retry logic
  - **Financial domain** (3 features): Stateful mock payment gateway (PENDING→AUTHORIZED→CAPTURED→REFUNDED state machine), pricing engine with tax/discount calculations
  - **Infrastructure** (3 features): Reusable callable features (`@ignore`), auth helper, response time SLAs, parallel API calls
- Karate's built-in mock server for financial domain tests (no external dependencies)
- Maven profile coexistence: `mvn test` runs only Cucumber, `mvn test -Pkarate` runs only Karate
- JUnit5 runner (`KarateRunner.java`) with karate-config.js for env switching
- DataDog integration via `DataDogHook.java` (reuses existing `DataDogUtils`)

**Run commands:**
- `mvn clean test` — Cucumber only (unchanged)
- `mvn clean test -Pkarate` — all Karate tests
- `mvn clean test -Pkarate -Dkarate.env=staging` — Karate against staging
- `mvn clean test -Pkarate -Dkarate.options="--tags @smoke"` — tagged subset

**CI:** Two workflows — `cucumber.yml` (Cucumber, nightly 04:00 UTC) and `karate.yml` (Karate, same triggers + dispatch inputs for `karate_env` and `karate_tags`). Both upload to DataDog CI Visibility with distinct `framework:` tags.

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

**Five demos:**

1. **Codebase Reader & Rewriter (`demo1`)** — Explores `cucumber_python/steps/` and `pages/`, identifies Page Object architecture violations in `auth_steps.py` (inline Selenium, magic strings), produces a compliant rewrite at `output/auth_steps_rewritten.py`, and validates it with `python -m py_compile`. Iterates on any compile error.

2. **Code Execution Feedback Loop (`demo2`)** — Writes `output/validate_saucedemo.py`, runs it via bash, reads stdout/stderr, and iterates until all assertions pass and exit code is 0. Uses only the Python standard library — the agent discovers this constraint and adapts. Demonstrates the write → run → observe → fix loop underpinning reliable AI-generated code.

3. **Git & PR Automation (`demo3`)** — Reads feature files, identifies highest-value scenarios, adds `@performance` tags, creates branch `agent/add-performance-tags`, commits with a conventional commit message, dry-runs `git push`, and produces a full PR description (Summary + Motivation + Test Plan). No remote state modified in demo mode.

4. **Multi-Agent: Planner → Executor → Validator (`demo4`)** — Three specialised agents with role-scoped tools collaborate to add a new Behave cart scenario end-to-end:
   - **Planner**: `read_file` + `list_files` only — explores codebase, outputs structured JSON implementation plan
   - **Executor**: `read_file` + `write_file` + `run_bash` — implements the plan, runs `py_compile` on modified files
   - **Validator**: `run_bash` only — runs `behave --dry-run` + `grep`, issues `VERDICT: PASS | FAIL` with evidence
   - Orchestrator passes each agent's output as the next agent's input — clean, auditable context handoff

5. **AI Test Generator (`demo5`)** — Translates a manual QA tester's plain-English test description into a runnable pytest test. The agent reads existing tests (`claims-diff/tests/`) and source code (`claims-diff/differ/`) to learn project patterns (class structure, factory fixtures, assertion style), generates a test file, and iterates through compile + pytest until the test passes. Demonstrates the core value proposition of AI tooling for QA — enabling manual testers to generate automated tests by describing what they want to verify.

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

**CLI:** `python run_demo.py --demo {1-5}` or `--all`; `--quiet` for summary-only output

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

### Framework 11: `claims-diff` — Claims Adjudication Data Diff Engine
**Stack:** Python 3.11 · Pydantic · Pandas · BigQuery (optional) · pytest
**What it does:** Compares two sets of healthcare claim records to detect discrepancies in adjudication results — added claims, removed claims, and field-level modifications. Demonstrates healthcare data validation patterns relevant to claims processing QA.

**Healthcare validation rules (Pydantic model):**
- `claim_id`: `^CLM-\d{3,}$` — standardised claim ID format
- `patient_id`: `^PAT-\d{3,}$` — standardised patient ID format
- `procedure_code`: `^\d{5}$` — CPT codes are 5-digit numeric
- `billed_cents`, `allowed_cents`, `paid_cents`: `>= 0` — monetary amounts cannot be negative
- `status`: `Literal["paid", "denied", "pending"]` — only valid adjudication statuses

**Test suite (30 tests across 3 files):**
- `test_models.py` (12 tests) — Pydantic schema enforcement: CPT format, status enum, negative amounts, extra fields, serialization round-trip
- `test_diff_engine.py` (12 tests) — core diff logic: added/removed/modified detection, multi-field changes, empty datasets, real CSV integration test
- `test_loader.py` (6 tests) — CSV loading: field types, missing columns, empty files, non-numeric values, file-not-found

**Data generation utility (`datasets/generate.py`):**
- CLI tool generating synthetic claim datasets at configurable scale (`--count 500 --diffs 25 --seed 42`)
- Realistic data: weighted CPT code distribution, payer discount chains (billed → allowed → paid), weighted status distribution (75% paid, 15% denied, 10% pending)
- Controlled diff injection: ~40% amount reprocessing, ~20% status changes, ~20% new claims (late filing), ~20% removed claims (voided/reversed)
- Outputs `baseline_generated.csv` / `current_generated.csv` — never overwrites hand-crafted datasets
- Demonstrates "data engineering for QA" — complex data generation utilities for test environments

**Parallel test execution:**
- `pytest-xdist` with `-n auto --dist=loadscope` configured in `pytest.ini`
- Auto-detects CPU cores, groups tests by class (matches existing class-organised structure)
- No global state or autouse fixtures — the suite is an ideal candidate for parallel execution

**Key architecture decisions:**
- `conftest.py` factory fixtures: `sample_claim()` with keyword overrides, `tmp_csv()` for temp file generation
- Frozen Pydantic models with `extra="forbid"` — immutable records, no silent data corruption
- `diff_claims()` returns a structured `DiffReport` with field-level `FieldDiff` objects
- BigQuery loader available for warehouse-scale validation when credentials are configured

**CI (`claims-diff.yml`):**
- Triggers: push to `main` (path: `claims-diff/**`), PR, `workflow_dispatch`
- Pipeline: Python 3.11 → install deps → pytest with JUnit XML + coverage → CLI verification → DataDog CI Visibility → artifact upload

---

### Framework 12: `pact-consumer` — Consumer-Driven Contract Testing
**Stack:** TypeScript · Pact v13 (pact-js) · Vitest · pact-python provider verifier
**What it does:** Validates the contract between a TypeScript API consumer and the FastAPI provider using Pact's consumer-driven approach.

**Consumer contracts (8 interactions):**
- `GET /health` → 200 `{ status: "ok" }`
- `GET /products` → 200 array of Product
- `GET /products/{id}` → 200 single Product; 404 when not found
- `POST /products` → 201 + Product with `id`
- `GET /users` → 200 array of User
- `GET /users/{id}` → 200 single User; 404 when not found

**Provider verification:** `fastapi-service/tests/test_pact_provider.py` launches the FastAPI app, points the Pact verifier at consumer pact files, and verifies all interactions pass against the real provider.

**CI (`pact.yml`):** Two-job workflow — consumer tests generate pact files, provider job downloads and verifies them. Triggers on push/PR to `pact-consumer/**` or `fastapi-service/**`.

---

### Framework 13: `flakiness-detector` — Flaky Test Detection & Quarantine
**Stack:** Python 3.11 · JUnit XML · Click · DataDog
**What it does:** Parses JUnit XML test results across multiple CI runs, computes per-test flakiness scores, and generates a severity-ranked report with quarantine recommendations.

**Architecture:**
- `parser.py` — Parse JUnit XML files using `xml.etree.ElementTree` (stdlib)
- `analyzer.py` — Aggregate outcomes, compute `flakiness_score = min(passes, failures) / total_non_skipped`
- `reporter.py` — Generate markdown with QUARANTINE/MONITOR recommendations
- `datadog.py` — Send `flakiness.score`, `flakiness.quarantined_count`, `flakiness.total_flaky` metrics

**CLI:** `python run.py --xml-dir ./results/ --threshold 0.20 --output report.md`

**CI (`flakiness-detector.yml`):** Runs tests and demo analysis on push/PR to `flakiness-detector/**`.

---

### Framework 14: `vulnerability-aggregator` — Unified Security Scanning
**Stack:** Python 3.11 · GitHub API (gh CLI) · Dependabot · CodeQL · OWASP ZAP
**What it does:** Aggregates vulnerability findings from Dependabot, CodeQL, and ZAP into a unified severity-prioritized markdown report.

**Security scanning setup:**
- `dependabot.yml` — Weekly pip/npm/GitHub Actions dependency updates across all projects
- `codeql.yml` — Weekly CodeQL analysis for Python and JavaScript/TypeScript
- 5 existing ZAP workflows updated to export JSON reports (`-J zap-report.json`)

**CI:** Dependabot and CodeQL run automatically. Aggregator can be run manually via `make vuln-report`.

---

### Framework 15: `cypress` — TypeScript E2E + Component Testing + AI Test Generator
**Stack:** TypeScript · Cypress 13 · React 18 · Vite · Anthropic Claude (AI test generator) · Node.js 20
**What it does:** End-to-end tests against SauceDemo plus isolated React component tests, all in TypeScript. Includes an AI test generator that takes plain-English user stories and produces runnable `.cy.ts` files using Claude with full framework context as RAG input.

**Key features:**
- Page Object Model: abstract `BasePage` + 4 concrete pages (Login, Inventory, Cart, Checkout)
- Custom commands: `cy.login()`, `cy.addToCart()`, `cy.clearCart()` with TypeScript type declarations
- `cy.intercept()` patterns: spy, stub, failure simulation (network.cy.ts)
- React component testing: `ProductCard.cy.tsx` via Cypress component runner
- Accessibility testing: `cypress-axe` WCAG 2.1 AA checks
- Lighthouse performance audits (Chrome only)
- `testIsolation: false` strategy for external site rate-limiting
- DataDog GAUGE metrics + JUnit XML CI Visibility
- 43 E2E + 4 component = 47 tests
- **Testiny test management sync** — CI uploads JUnit XML results to Testiny via `@testiny/cli automation`

**AI Test Generator (`ai-generator/generate-test.ts`):**
- CLI tool: `npm run ai:generate "User story here"` → writes `cypress/e2e/generated/<name>.cy.ts`
- Reads 5 page objects, custom commands, 2 fixtures, and 3 example tests at runtime
- Builds a RAG prompt injecting full codebase context into Claude's system prompt
- Generated tests follow exact framework conventions: POM imports, `testIsolation: false`, fixture-driven data, `@smoke`/`@regression` tags
- `--dry-run` flag for preview without file creation
- Demonstrates AI + test automation integration — the bridge between manual QA descriptions and automated test coverage

**Run commands:**
- `npm test` — all E2E tests (headless Chrome)
- `npm run test:smoke` — smoke tests only
- `npm run test:component` — React component tests
- `npm run ai:generate "user story"` — AI-generated test from plain English

**CI (`cypress.yml`):** push · PR · nightly 05:00 UTC. Dispatch inputs: browser, test type.

---

### Framework 16: `quality-dashboard` — Portfolio-Wide Quality KPI Dashboard
**Stack:** Python 3.11 · JUnit XML · DataDog v2 API · GitHub Actions API (gh CLI)
**What it does:** Aggregates test results across all frameworks, computes derived quality KPIs (pass rate, failure density, MTTD, suite stability, flakiness rate), sends metrics to DataDog, and includes a VP-level dashboard JSON.

**KPIs computed:**
- Pass Rate — passed / total (primary quality signal)
- Failure Density — failed / total (severity ranking)
- Avg Duration / p95 Duration — test execution time tracking
- Suite Stability — pass rate trend over last N runs
- Flakiness Rate — from flakiness-detector data
- MTTD (Mean Time to Detect) — seconds from code push to CI failure notification

**Key architecture decisions:**
- Reuses `flakiness-detector/flakiness/parser.py` for JUnit XML parsing — no duplication
- GitHub Actions API via `gh api` subprocess (same pattern as vulnerability-aggregator)
- DataDog dashboard JSON with conditional formatting (green/yellow/red thresholds)
- Two modes: `--xml-dir` for local results, `--from-github` for CI history

**DataDog metrics:** `kpi.pass_rate`, `kpi.failure_density`, `kpi.avg_duration_s`, `kpi.p95_duration_s`, `kpi.total_tests`, `kpi.suite_stability`, `kpi.flakiness_rate`, `kpi.mttd_seconds`

**Run:** `python run.py --xml-dir ../flakiness-detector/fixtures/ --output report.json`

---

### Framework 17: `failure-triage` — AI-Powered Failure Root Cause Clustering
**Stack:** Python 3.11 · Anthropic Claude (tool use, `@beta_tool`) · JUnit XML · DataDog
**What it does:** An Anthropic tool-use agent that reads JUnit XML test results, uses Claude to cluster failures by root cause, and produces a structured triage report with severity rankings and suggested fix actions.

**Root cause categories:** assertion_error, element_not_found, timeout, setup_failure, api_error, data_error, unknown

**Key architecture decisions:**
- 4 `@beta_tool`-decorated tools: read_test_results, search_failure_patterns, read_source_file, write_triage_report
- `client.beta.messages.tool_runner` SDK-managed agent loop (same pattern as coding-agent)
- Structured JSON output with severity levels (CRITICAL/HIGH/MEDIUM/LOW) and priority ordering
- Reuses flakiness-detector's JUnit XML parser

**DataDog metrics:** `triage.total_failures`, `triage.cluster_count`, `triage.root_cause` (per category)

**Run:** `python run.py --xml-dir ../flakiness-detector/fixtures/ --output triage_report.json`

---

### Framework 18: `fastapi-service` — REST API + Full Test Suite + Redis Caching Layer
**Stack:** Python 3.11 · FastAPI · Pydantic v2 · Redis 7 · Pytest · k6
**What it does:** A self-contained REST API built with FastAPI + Pydantic v2, paired with a full contract and integration test suite in pytest. A Redis caching layer sits between endpoints and the in-memory store as a transparent read-through cache with graceful fallback when Redis is unavailable. Closes the full-stack loop in the portfolio: instead of testing someone else's API, this service is built here and tested here.

**API endpoints:**
- `GET /health` — liveness check
- `GET /products`, `GET /products/{id}`, `POST /products`, `PUT /products/{id}`, `DELETE /products/{id}` — full CRUD
- `GET /users`, `GET /users/{id}` — read-only

**Redis caching (`app/cache.py`):**
- Transparent read-through cache — GET endpoints check cache first, populate on miss
- Mutation endpoints (POST/PUT/DELETE) invalidate affected keys
- Cache key scheme: `fastapi:products:list`, `fastapi:products:{id}`, `fastapi:users:list`, `fastapi:users:{id}`
- Graceful degradation: app starts and works normally without Redis; cache ops become no-ops with `[WARN]` logged if Redis goes down mid-flight
- `docker-compose.yml` provides `redis:7-alpine` for local development

**Test suite (38 tests across 6 files):**
- `test_health.py` (2 tests) — liveness endpoint
- `test_products.py` (11 tests) — full CRUD: list, get, create, update, delete
- `test_users.py` (5 tests) — read-only user endpoints + 405 guard
- `test_api_contract.py` (4 tests) — OpenAPI schema validation
- `test_cache.py` (15 tests) — cache hit/miss, invalidation, TTL, graceful degradation, utilities
- `test_pact_provider.py` (1 test) — Pact provider verification (contract compliance)
- All tests fully deterministic — `reset_store` autouse fixture restores seed data, `_reset_cache` injects fresh `fakeredis` instance per test for order-independent execution

**k6 load tests with SLO thresholds:**
- 4 scenarios: `health_baseline` (constant-vus), `read_heavy` (ramping-vus), `crud_workflow` (per-vu-iterations), `error_handling` (constant-vus)
- `k6/slo.json` — single source of truth for all performance thresholds
- Dynamic threshold generation — `load-test.js` reads `slo.json` instead of hardcoding values
- `handleSummary(data)` — produces per-scenario pass/fail SLO report (`k6-slo-report.json`)
- `k6/datadog-summary.js` — sends `k6.slo.pass`, `k6.slo.margin_ms`, `k6.slo.error_rate` metrics to DataDog

**DataDog metrics:** `test.suite.*`, `cache.hits`, `cache.misses`, `k6.slo.pass`, `k6.slo.margin_ms`, `k6.slo.error_rate`

**CI:** `fastapi-service.yml` (nightly 10:00 UTC + dispatch) for pytest; `k6-load-test.yml` (nightly 11:00 UTC + dispatch) for k6

---

### Framework 19: `terraform` — Infrastructure as Code
**Stack:** HCL · Terraform >= 1.6 · AWS · DataDog
**What it does:** Provisions the cloud infrastructure that supports the monorepo.

**Three modules:**
- `s3-artifacts` — S3 bucket for permanent test artifact storage (Allure reports, JUnit XML, screenshots) with versioning, AES-256 encryption, public-access block, and lifecycle rules
- `iam-ci` — Keyless GitHub Actions → AWS IAM role via OIDC (no long-lived AWS keys in CI)
- `datadog-observability` — DataDog dashboard, two monitors, and a CI pass-rate SLO

**CI (`terraform.yml`):** push/PR (paths: `terraform/**`) + dispatch. Plan on PR, apply on merge to main, OIDC AWS auth.

---

### Framework 20: `langchain-rag` — Multi-Turn Conversational RAG Assistant
**Stack:** Python 3.11 · LangChain 0.3 LCEL · Chroma (in-memory) · OpenAI gpt-4o-mini · text-embedding-3-small · Langfuse tracing
**What it does:** A Retrieval-Augmented Generation pipeline that loads the monorepo's own `.md` and `.feature` files as its knowledge corpus, then answers natural-language questions about the test frameworks. Supports multi-turn conversation with chat memory.

**Key architecture:**
- **LCEL chain composition** — `rag/chain.py`: dict fan-out, `RunnablePassthrough`, `StrOutputParser`
- **In-memory Chroma vector store** — `rag/vectorstore.py`: `RecursiveCharacterTextSplitter` + `OpenAIEmbeddings`
- **Multi-source document loader** — `rag/loader.py`: walks monorepo, skips noise dirs
- **Conversation history** — `RunnableWithMessageHistory` + `InMemoryHistory` for multi-turn chat memory
- **Cost-efficient models** — gpt-4o-mini + text-embedding-3-small (< $0.01 per demo run)
- **Langfuse observability** — `rag/observability.py`: LLM tracing, token/cost tracking, retriever spans

**CLI modes:** `--question` (single), `--demo` (3 built-in questions), `--interactive` (REPL)

**CI (`langchain-rag.yml`):** push/PR lint (free) + `workflow_dispatch` full demo (< $0.01)

---

### Framework 21: `langgraph-agent` — BDD Test Case Generator Pipeline
**Stack:** Python 3.11 · LangGraph 0.4 · LangChain Anthropic · claude-haiku-4-5 · Langfuse tracing
**What it does:** A stateful multi-agent graph that turns a plain-English feature description into reviewed, production-quality BDD Gherkin scenarios — with an automated review/revise cycle.

**Graph topology (StateGraph with 4 nodes):**
```
parse_requirements → generate_tests → review_quality
    review_quality ├── (REVISE, count < 2) → revise_tests → review_quality  [loop]
                   └── (PASS or count >= 2) → END
```

**Key architecture:**
- **StateGraph + TypedDict state** — `graph/state.py`, `graph/pipeline.py`
- **4 nodes as pure functions** — `graph/nodes.py`: parse_requirements, generate_tests, review_quality, revise_tests
- **Conditional edges** — `graph/edges.py`: `review_router` routes to revise or END
- **Bounded revision cycles** — max 2 revisions to prevent runaway loops
- **Provider-agnostic LLM** — `ChatAnthropic` shows LangGraph works beyond OpenAI
- **Real-time streaming** — `graph.stream()` prints node-by-node progress
- **Langfuse observability** — span-per-node tracing with graceful-skip pattern

**Cost:** ~$0.02 per run

**CLI:** `--demo` (built-in feature) or `--feature "User can reset their password via email"`

**CI (`langgraph-agent.yml`):** push/PR lint (free) + `workflow_dispatch` full demo (~$0.02)

---

### Framework 22: `dspy-optimizer` — Bug Severity Classifier
**Stack:** Python 3.11 · DSPy 2.6 · BootstrapFewShot · OpenAI gpt-4o-mini
**What it does:** A systematic prompt optimization demo that classifies bug reports by severity (Critical / High / Medium / Low) and compares zero-shot baseline accuracy against a BootstrapFewShot-optimized classifier on a held-out test set.

**Key architecture:**
- **DSPy Signatures** — `classifier/signatures.py`: `InputField` / `OutputField` with docstring instructions
- **ChainOfThought module** — `classifier/modules.py`: reasoning before classification
- **BootstrapFewShot optimizer** — `classifier/optimizer.py`: auto-selects few-shot demos from trainset
- **Offline dataset** — `datasets/bug_reports.py`: 30 synthetic examples (20 train, 10 dev), zero API cost for data
- **Before/after accuracy** — `run.py --mode compare`: prints delta on 10-item held-out split
- **Compiled program export** — `output/compiled_classifier.json`: saved after optimization

**Cost:** ~$0.02 per run

**CLI modes:** `--mode baseline` (zero-shot), `--mode optimized` (Bootstrap + evaluate), `--mode compare` (side-by-side)

**CI (`dspy-optimizer.yml`):** push/PR lint (free) + `workflow_dispatch` compare run (~$0.02)

---

### Framework 23: `dspy-vertex` — Bug Severity Classifier (Vertex AI Backend)
**Stack:** Python 3.11 · DSPy 2.6 · BootstrapFewShot · Vertex AI Gemini 1.5 Flash
**What it does:** Same DSPy BootstrapFewShot optimization pipeline as `dspy-optimizer`, but using Google Vertex AI (Gemini 1.5 Flash) as the LLM backend instead of OpenAI. Demonstrates multi-LLM flexibility — the classifier, datasets, and optimizer logic are identical; only the LLM configuration changes.

**Proves:**
- Cloud-native ML pipeline skills (Vertex AI / GCP)
- Backend portability — same optimization, different provider
- Graceful degradation — exits cleanly when GCP credentials are unavailable

**Auth:** `GCP_PROJECT` + `gcloud auth application-default login`

**CI (`dspy-vertex.yml`):** push/PR lint (free) + `workflow_dispatch` compare run

---

### Framework 24: `site-monitor` — Website Drift Detection
**Stack:** Python 3.11 · BeautifulSoup · Click · DataDog · Requests
**What it does:** Monitors saucedemo.com for DOM selector changes that could break the 5 browser automation frameworks in the portfolio (Cypress, Selenium Java, Cucumber Java, Cucumber Python, Playwright). SauceDemo has no changelog — when they push updates, selectors can change without warning, causing test failures discovered only after the fact in CI.

**Pipeline:**
1. **Fetch** — Downloads the HTML page and Vite JS bundle from saucedemo.com
2. **Extract** — Parses all DOM selectors (IDs, classes, data-test attributes) using BeautifulSoup + regex
3. **Compare** — Diffs current state against a committed baseline snapshot (`baseline.json`)
4. **Report** — Generates markdown report identifying removed/added selectors and affected frameworks
5. **Alert** — Optionally auto-creates a GitHub issue on critical drift and sends metrics to DataDog

**Architecture:**
- `monitor/fetcher.py` — HTTP fetch of HTML + JS bundle
- `monitor/extractor.py` — Parse selectors from HTML + JS
- `monitor/comparator.py` — Diff current vs baseline
- `monitor/reporter.py` — Markdown report + GitHub issue creation
- `monitor/datadog.py` — DataDog drift metrics
- `selectors.json` — Monitored selector registry (23 selectors mapped to 5 frameworks)
- `baseline.json` — Committed selector baseline (auto-generated)

**CLI:** `python run.py [--update-baseline] [--output drift-report.md] [--auto-issue]`

**CI (`site-monitor.yml`):** Daily 06:00 UTC + push/PR (paths: `site-monitor/**`) + dispatch. Auto-creates GitHub issues on critical drift.

---

### Framework 25: `qms-evidence-collector` — Compliance Evidence Mapping
**Stack:** Python 3.11 · Click · DataDog · Requests
**What it does:** Scans the monorepo for CI artifacts (JUnit XML, ZAP reports, coverage files, Pact contracts, k6 results, flakiness reports, drift baselines, Allure reports, triage reports, dependency scans) and maps each artifact type to specific compliance clauses across three standards: ISO 9001:2015, SOC 2 CC-series, and ISO/IEC 17025:2017. Generates a structured evidence report with gap analysis for audit preparation.

**10 artifact types mapped:**
- JUnit/TRX XML → ISO 9001 8.6 (Release), 9.1.1 (Monitoring), 7.1.5.1 (Measuring resources)
- Coverage reports → ISO 9001 8.5.1 (Control of production), 9.1.3 (Analysis)
- ZAP reports → ISO 9001 6.1 (Risk), SOC 2 CC6.1 (Logical access)
- Flakiness reports → ISO 9001 7.1.5.2 (Measurement traceability), 10.2 (Corrective action)
- Pact contracts → ISO 9001 8.4.2 (External provision control)
- k6 SLO results → ISO 9001 9.1.1 (Monitoring), ISO/IEC 17025 7.2.2 (Validation)
- Drift baselines → ISO 9001 8.5.6 (Control of changes), ISO/IEC 17025 7.7.1 (Validity)
- Allure reports → ISO 9001 7.5.1 (Documented information)
- Dependency scans → SOC 2 CC3.1 (Risk assessment), CC6.1 (Logical access)
- Triage reports → ISO 9001 10.2 (Corrective action), SOC 2 CC7.2 (Incident management)

**Architecture:**
- `collector/scanner.py` — Walks the repo, matches files against known artifact patterns
- `collector/mapper.py` — Maps artifact types to clause registry entries
- `collector/reporter.py` — Generates markdown or JSON evidence reports with gap analysis
- `collector/datadog.py` — Sends coverage metrics (graceful-skip pattern)
- `mappings/clause_registry.json` — Artifact-to-clause definitions with rationale

**Test suite:** 48 tests across 3 files (scanner, mapper, reporter)

**CLI:** `python run.py [--repo-dir ..] [--output evidence.json] [--standard iso9001] [--format json]`

**DataDog metrics:** `qms.clauses_covered`, `qms.evidence_files`, `qms.iso9001_clauses`, `qms.soc2_controls`, `qms.iso17025_clauses`

**CI (`qms-evidence-collector.yml`):** push/PR (paths: `qms-evidence-collector/**`) + nightly 12:00 UTC + dispatch. Runs tests and full repo evidence scan.

---

## GenAI Workflow: `.claude/commands/`
Three Claude Code custom slash commands for daily QA workflow integration:
- `/project:triage-failures <xml-dir>` — AI failure triage from JUnit XML
- `/project:review-tests <test-dir>` — QA best practice review (POM, waits, isolation, assertions, data, fixtures)
- `/project:gen-test <description>` — Generate tests matching project conventions from plain-English descriptions

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
| `cucumber` | test suite results + duration (Cucumber + Karate) |
| `cucumber-python` | test suite results + duration |
| `playwright` | test suite results + duration |
| `job-agent` | jobs_found · jobs_scored · cover_letters_drafted · duration · latency |
| `coding-agent` | (no DataDog integration — demo artefacts written to `output/`) |
| `fastapi-service` | test suite + cache.hits · cache.misses + k6 SLO metrics |
| `site-monitor` | site_monitor.drift_detected · site_monitor.selectors_removed · site_monitor.selectors_added |
| `langchain-rag` | Langfuse tracing (token/cost/latency per retrieval + generation) |
| `langgraph-agent` | Langfuse tracing (span-per-node, token/cost tracking) |
| `dspy-optimizer` | baseline_accuracy · optimized_accuracy · delta |
| `quality-dashboard` | kpi.pass_rate · kpi.failure_density · kpi.avg_duration_s · kpi.p95_duration_s · kpi.total_tests · kpi.suite_stability · kpi.flakiness_rate · kpi.mttd_seconds |
| `failure-triage` | triage.total_failures · triage.cluster_count · triage.root_cause (per category) |
| `qms-evidence-collector` | qms.clauses_covered · qms.evidence_files · qms.iso9001_clauses · qms.soc2_controls · qms.iso17025_clauses |

---

## CI Strategy

Each framework has its own workflow with **path filters** — a push to `selenium-java/` only triggers `selenium-java.yml`. Path filters prevent cross-framework interference.

| Workflow | Trigger | Key dispatch inputs |
|---|---|---|
| `playwright-smoke-pr.yml` | PR only · 5-min hard cap | — (Chromium · @smoke · retries=0 always) |
| `playwright.yml` | push · PR · nightly 02:00 UTC | browser · execution mode · JMeter toggle |
| `selenium-java.yml` | push · PR · nightly 03:00 UTC | browser · suite XML · JMeter toggle |
| `cucumber.yml` | push · PR · nightly 04:00 UTC | browser · execution mode · JMeter toggle |
| `karate.yml` | push · PR · nightly 04:00 UTC | karate_env (dev · staging) · karate_tags filter |
| `cypress.yml` | push · PR · nightly 05:00 UTC | browser · test type (e2e · component · all) |
| `cucumber-python.yml` | push · PR · nightly 05:00 UTC | execution_mode · browser · test_tags |
| `ai-eval.yml` | push · PR · nightly 05:00 UTC | pytest marker (smoke · regression · safety) |
| `conv-eval.yml` | push · PR · nightly 06:00 UTC | pytest marker (smoke · regression · safety · retention) |
| `agent-eval.yml` | push · PR · nightly 07:00 UTC | pytest marker (smoke · regression) |
| `postman-newman.yml` | push · PR · nightly 08:00 UTC | folder filter |
| `job-agent.yml` | nightly 09:00 UTC · workflow_dispatch | role_filter keyword |
| `coding-agent.yml` | push · PR · workflow_dispatch | demo number (1-5 or all) |
| `fastapi-service.yml` | nightly 10:00 UTC · workflow_dispatch | — |
| `k6-load-test.yml` | nightly 11:00 UTC · workflow_dispatch | — |
| `site-monitor.yml` | daily 06:00 UTC · push · PR · workflow_dispatch | auto-issue on drift |
| `terraform.yml` | push · PR (paths: `terraform/**`) · workflow_dispatch | plan on PR · apply on merge · OIDC AWS auth |
| `claims-diff.yml` | push · PR (paths: `claims-diff/**`) · workflow_dispatch | — |
| `pact.yml` | push · PR (paths: `pact-consumer/**`, `fastapi-service/**`) | consumer → provider verification |
| `flakiness-detector.yml` | push · PR (paths: `flakiness-detector/**`) · workflow_dispatch | — |
| `langchain-rag.yml` | push · PR (lint only, free) · workflow_dispatch (demo) | — |
| `langgraph-agent.yml` | push · PR (lint only, free) · workflow_dispatch (demo) | — |
| `dspy-optimizer.yml` | push · PR (lint only, free) · workflow_dispatch (compare) | — |
| `dspy-vertex.yml` | push · PR (lint only, free) · workflow_dispatch (compare) | — |
| `qms-evidence-collector.yml` | push · PR (paths: `qms-evidence-collector/**`) · nightly 12:00 UTC | — |
| `visual-regression-update.yml` | workflow_dispatch | browser project (chromium · firefox · webkit) |
| `deploy-validate-rollback.yml` | workflow_dispatch · workflow_call | deployment URL · Vercel project ID · auto-rollback toggle |
| `codeql.yml` | push to main · weekly Monday 14:00 UTC | Python, JavaScript/TypeScript |
| `k8s.yml` | workflow_dispatch only | framework (selenium-java · cucumber) |

**Secrets required:**
- `OPENAI_API_KEY` — ai-eval, conv-eval, agent-eval, langchain-rag, dspy-optimizer
- `ANTHROPIC_API_KEY` — job-agent, coding-agent, langgraph-agent, cypress AI generator
- `TAVILY_API_KEY` — job-agent
- `CANDIDATE_PROFILE` — job-agent (injects git-ignored profile.md into CI runner)
- `DD_API_KEY` — optional, all frameworks (graceful skip if absent)
- `TESTINY_API_TOKEN` — optional, Playwright + Cypress (test management sync)
- `SAUCE_USERNAME` / `SAUCE_ACCESS_KEY` — optional, Playwright Sauce Labs runs
- `VERCEL_TOKEN` — deploy-validate-rollback workflow
- `GOOGLE_APPLICATION_CREDENTIALS` — dspy-vertex (GCP auth)

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

## Standalone Repos (Outside the Monorepo)

These three repos live outside `qa-automation-portfolio` as independent public projects. They demonstrate adversarial AI agent architecture, domain-specific financial QA, and AI-powered code review.

---

### Standalone 1: `legal-funding-qa-agent` — Adversarial QA Agent with BLOCK/WARN/PASS Release Gate
**Repo:** github.com/SDETBMan/legal-funding-qa-agent
**Stack:** Python 3.11 · LangGraph · DSPy · Hypothesis · Anthropic Claude · FastAPI · Pydantic v2 · Presidio (PII) · AgentOps
**What it does:** An autonomous adversarial QA agent that attacks 12 financial and legal invariants in a pre-settlement funding API. Produces an auditable JSON report and a severity-tiered BLOCK/WARN/PASS release gate signal for CI/CD. Not a test suite — an agent that reasons about why a payoff calculation is wrong and explains it.

**Architecture:** Explorer → Adversarial Agent → Judge Agent → Report + Release Gate

**12 invariants under attack:**
- INV-01: No duplicate active funding on same case (HIGH)
- INV-04: Interest accrues from disbursement_date, not application_date (CRITICAL)
- INV-06: Jurisdiction usury rate cap enforced — 51 state caps in basis points (CRITICAL)
- INV-07: Medicare/Medicaid super-priority in settlement waterfall (CRITICAL)
- INV-09: Plaintiff remainder >= 0 after waterfall (CRITICAL)
- INV-11: All money fields are integer cents — never floats (CRITICAL)
- Plus 6 more covering attorney acknowledgment, lien caps, capacity release, day count basis

**Release gate tiers:**
| Tier | CI impact |
|---|---|
| CRITICAL | Hard block — deploy does not proceed |
| HIGH | Block unless overridden with ticket |
| MEDIUM | Warning — deploy proceeds, alert created |
| EVAL | Logged — quality dashboard, no block |

**Key technical decisions:**
- DSPy-optimized judge module with float-money guardrail (INV-17)
- Integer cents throughout (`money.py` — `validate_cents()` rejects floats)
- Presidio PII redaction strips SSN/email before LLM context
- Mock API with 8 intentionally seeded invariant violations
- SHA-256 versioned prompt templates
- Structured JSON logging via structlog (no `print()`)

**Demo output:** 8 breaches detected, 4 invariants held. Exit code 1 (BLOCK).

**CI:** `qa-pipeline.yml` — runs all 12 attacks against mock API, produces `artifacts/report.json`

---

### Standalone 2: `agentic-p2p-auditor` — Three-Agent Financial Controls Auditor
**Repo:** github.com/SDETBMan/agentic-p2p-auditor
**Stack:** Python 3.11 · Anthropic Claude (tool use) · Decimal math · AgentOps
**What it does:** A domain-agnostic three-agent QA pipeline for auditing financial and compliance systems. Exploration agent runs happy-path workflow, adversarial agent attacks declared control rules, judge agent reads both transcripts and emits a structured JSON verdict grounded in tool evidence.

**Three production domains:**

*P2P (Purchase-to-Pay) — 6 control rules:*
- Overpayment protection, 3-way match gate, partial receipt flag, inactive vendor gate, GL balance, duplicate invoice detection

*Medical Lien — 6 control rules:*
- Lien priority enforcement (federal super-priority), balance cap, duplicate lien detection, provider status gate, settlement waterfall order, reduction negotiation cap

*Private Markets (PE Distribution Waterfall) — 6 control rules:*
- Waterfall sequence enforcement, hurdle rate gate, overcall protection, recycling cap, LP/GP split accuracy, management fee offset

**Key architecture:**
- Pluggable domain packages: add `domains/your_domain/` with tools, prompts, mock store, controls
- `DomainSpec` interface contract for adding new audit domains without changing the framework
- Live HTTP adapter: `--live` flag to run against real API instead of mock
- Decimal-based money — float contamination is a control violation, not a rounding error
- Evidence-grounded verdicts: judge validates HELD/BREACHED claims against actual tool response JSON
- Wall-clock and iteration limits prevent runaway agent loops

**Run:** `python run_pipeline.py --mode full --domain p2p --output-dir pipeline_output`

---

### Standalone 3: `ai-pr-reviewer` — AI Code Reviewer for Test Automation PRs
**Repo:** github.com/SDETBMan/ai-pr-reviewer (Private)
**Stack:** JavaScript · Anthropic Claude · promptfoo · Docker · FastAPI (ephemeral env)
**What it does:** Framework-agnostic AI code reviewer for test automation pull requests. Uses Claude as the reasoning engine, a 22-rule catalog to enforce QA engineering best practices, and promptfoo as the eval harness to measure reviewer accuracy.

**Supported frameworks:** Playwright (TypeScript, C#), Cypress (TypeScript), Selenium (Java, C#, Python)

**22 rules across 7 categories:**
- Locator Strategy (LOC-01–03): non-semantic selectors, locator leaks, index fragility
- Wait Strategy (WAIT-01–03): unjustified hard waits, manual polling, silent timeouts
- Page Object Model (POM-01–04): raw element exposure, assertions in POs, naming, constructors
- Test Isolation (ISO-01–03): order dependency, shared mutable state, unreliable cleanup
- Assertion Patterns (ASRT-01–03): snapshot vs retrying, weak messages, assertion sprawl
- Fixture/Data (FIX/DATA): duplicated setup, hard-coded data, UI-based data creation
- Migration Fidelity (MIG-01–04): contract drift, carried-over anti-patterns, dropped tests

**Eval suite:** 11 test cases x 2 models = 22 evaluations. 100% pass rate. Categories: true positives (3), true negatives (2), false positive traps (2), migration fidelity (3), judgment calls (1).

**Key design decisions:**
- Hybrid: static analysis (ESLint, Semgrep) handles deterministic checks; AI handles judgment calls
- Dual-audience output: technical `findings[]` for engineers + plain-English `verification_checklist` for offshore QA testers
- Calibrated confidence: below 0.6 phrased as questions, below 0.4 omitted entirely
- Ephemeral PR environments: Docker Compose spins up PostgreSQL + FastAPI per PR, torn down on merge
- Silence is acceptable: `findings: []` on clean PRs (false positives erode trust faster than missed issues)

**CI:** `eval-reviewer.yml` runs promptfoo eval on prompt/corpus changes; `pr-environment.yml` manages ephemeral environments

---

## How to Use This File

Paste this entire file into a new Claude conversation, then ask:

- "Help me prep for a QA Lead interview at [Company]"
- "Evaluate this JD against my background" (paste the JD)
- "Write a cover letter for [role] at [company]"
- "What questions should I expect for a role requiring [skill]?"
- "How would I explain [framework] to a non-technical hiring manager?"
- "What are the strongest talking points from my portfolio for this JD?"
