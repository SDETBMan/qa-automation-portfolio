# PlaywrightDotNetFramework

[![playwright CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/playwright.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/playwright.yml)
[![.NET 8](https://img.shields.io/badge/.NET-8.0%20LTS-512BD4?logo=dotnet)](https://dotnet.microsoft.com/)
[![Playwright](https://img.shields.io/badge/Playwright-1.44-45ba4b?logo=playwright)](https://playwright.dev/dotnet/)
[![NUnit](https://img.shields.io/badge/NUnit-3.x-22c55e)](https://nunit.org/)
[![Allure](https://img.shields.io/badge/Allure-Report-F7941E)](https://docs.qameta.io/allure/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.4-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Playwright TS](https://img.shields.io/badge/Playwright%20TS-1.44-45ba4b?logo=playwright)](https://playwright.dev/)

A professional Playwright + .NET 8 + NUnit test automation framework targeting [SauceDemo](https://www.saucedemo.com/). This is the C# counterpart to the Java [SeleniumPOMFramework](../SeleniumPOMFramework).

---

## Features

- **Page Object Model**: clean separation of page logic from test logic
- **Playwright built-in auto-wait**: no `WebDriverWait` / `ExpectedConditions` boilerplate
- **Full parallel execution**: `[Parallelizable(ParallelScope.Self)]` with isolated `IPage` per test
- **Cross-browser**: Chromium, Firefox, WebKit via `.runsettings` files (C#) and `projects` config (TypeScript)
- **Trace Viewer**: `Context.Tracing` captures screenshots + DOM snapshots on failure; viewable via `playwright show-trace`
- **Network interception**: `RouteAsync` patterns: block assets, mock responses, inject headers, simulate failures
- **Fixtures (C#)**: `AuthenticatedTest` base class pre-logs in via NUnit `[SetUp]` chain; zero login boilerplate in tests
- **Fixtures (TypeScript)**: `test.extend<AppFixtures, WorkerFixtures>` with `authenticatedPage` (storageState) and worker-scoped `dbClient`; setup/teardown via `use()` callback
- **storageState authentication**: global `auth.setup.ts` logs in once, saves cookies/localStorage; browser projects reuse the saved state — eliminates per-test login overhead
- **Semantic locators**: page objects use Playwright's recommended priority: `getByRole` → `getByPlaceholder` / `getByText` → `getByTestId` (via `testIdAttribute: 'data-test'`) → scoped CSS
- **TypeScript project**: full Playwright TypeScript suite in `tests/playwright-ts/` with strict mode, page objects, and fixtures
- **Data-driven tests**: `[TestCaseSource]` for persona-based login scenarios
- **AI-assisted test data**: OpenAI integration via `AiHelper`
- **REST API tests**: `HttpClient` + `System.Text.Json` (mirrors REST Assured)
- **Database utilities**: `MySqlConnector` async ADO.NET helpers
- **Slack notifications**: post suite results to a webhook
- **BrowserStack upload**: app binary upload for mobile (Phase 2)
- **Visual regression**: `toHaveScreenshot()` with configurable thresholds, baseline update workflow, dynamic content masking
- **GraphQL API testing**: 5 patterns via Playwright `request` fixture (direct query, variables, mock by operationName, error handling, operation auditing)
- **Database-to-UI assertions**: `dbClient` + `dbAssertions` utilities — 5 validation patterns (scalar match, row count, field match, input pre-fill, column values in list)
- **Shopify E2E testing**: 8 storefront tests + 4 visual baselines with dedicated page objects and fixtures
- **Deploy validation + rollback**: Vercel health-check → Playwright smoke → auto-rollback CI pipeline
- **Allure reporting**: rich HTML reports with screenshots and traces on failure (`allure-playwright` v3)
- **GitHub Actions CI**: nightly regression pipeline with C# + TypeScript artifact upload, PR smoke gate
- **NUnit `[Retry]`**: built-in retry replaces Java's `AnnotationTransformer` + `RetryAnalyzer`

---

## Tech Stack

| Component | Technology |
|---|---|
| Browser automation (C#) | Microsoft.Playwright 1.44 |
| Browser automation (TS) | @playwright/test 1.44 |
| Test framework (C#) | NUnit 3.x |
| Test framework (TS) | Playwright Test runner |
| Language (C#) | C# / .NET 8 |
| Language (TS) | TypeScript 5.4 (strict mode) |
| Test runner | `dotnet test` + NUnit3TestAdapter / `npx playwright test` |
| Reporting | Allure.NUnit 2.x + allure-playwright v3 + Playwright HTML report |
| Configuration | `appsettings.json` + `IConfigurationBuilder` / `playwright.config.ts` |
| HTTP client | `System.Net.Http.HttpClient` |
| GraphQL | Playwright `request` fixture + `graphqlClient.ts` |
| JSON | `System.Text.Json` |
| Database | MySqlConnector 2.x (async ADO.NET) / `dbClient.ts` (MySQL · PostgreSQL) |
| Visual regression | Playwright `toHaveScreenshot()` with baseline management |
| CI/CD | GitHub Actions (nightly full + PR smoke gate + deploy validation) |
| Target apps | [SauceDemo](https://www.saucedemo.com/) · Shopify storefronts |

---

## Configuration

All settings live in `config/appsettings.json`. Override any key with an environment variable
(use `__` double-underscore as the hierarchy separator, e.g. `app__username`).

| Key | Default | Description |
|---|---|---|
| `url` | `https://www.saucedemo.com` | Application under test |
| `browser` | `chromium` | Browser (chromium/firefox/webkit) |
| `headless` | `false` | Headless mode |
| `timeout:explicit` | `10000` | Playwright timeout (ms) |
| `retry:max` | `1` | Test retry count |
| `app:username` | `standard_user` | Standard test user |
| `app:password` | `secret_sauce` | Test user password |
| `locked_out_username` | `locked_out_user` | Locked-out user for negative tests |
| `persona:standard` | `standard_user` | Data-driven persona |
| `persona:problem` | `problem_user` | Data-driven persona |
| `persona:performance` | `performance_glitch_user` | Data-driven persona |
| `api:base_url` | `https://jsonplaceholder.typicode.com` | REST API base URL |
| `ai:model` | `gpt-4o-mini` | OpenAI model |
| `openai:api_key` | _(empty)_ | OpenAI API key |
| `slack:webhook_url` | _(empty)_ | Slack incoming webhook |
| `db:url` | `localhost` | MySQL connection string |
| `db:user` | `root` | Database user |
| `db:password` | _(empty)_ | Database password |
| `hub:url` | _(empty)_ | Remote hub / BrowserStack URL |
| `browserstack:android_app_id` | _(empty)_ | BS Android app ID |
| `browserstack:ios_app_id` | _(empty)_ | BS iOS app ID |

---

## Quick Start

### One-Command Run (Recruiters / Hiring Managers)

Install the two prerequisites, clone, and run the entire suite with a single command:

**Prerequisites:** [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8) · [Node.js 20 LTS](https://nodejs.org)

```bash
# Linux / macOS / Git Bash on Windows
git clone https://github.com/SDETBMan/PlaywrightDotNetFramework.git
cd PlaywrightDotNetFramework
bash run-all.sh
```

```bash
# Any environment with make installed (Linux / macOS / WSL)
git clone https://github.com/SDETBMan/PlaywrightDotNetFramework.git
cd PlaywrightDotNetFramework
make all
```

`run-all.sh` / `make all` both:
1. Restore .NET packages and build the solution
2. Install Playwright browsers for the C# suite
3. Install npm dependencies and Playwright browsers for the TypeScript suite
4. Run the full C# / NUnit test suite (headless Chromium, 4 parallel workers)
5. Run the full TypeScript Playwright suite (Chromium)
6. Print a pass/fail summary with a link to the HTML report

**Available `make` targets:**

| Target | Description |
|---|---|
| `make all` | Full pipeline: setup + both test suites |
| `make setup` | Install all dependencies and browsers |
| `make test` | Run both suites (assumes setup done) |
| `make test-cs` | C# / NUnit tests only |
| `make test-ts` | TypeScript Playwright tests only |
| `make report` | Open TypeScript HTML report |
| `make clean` | Remove build artefacts and test output |

---

### Step-by-Step Setup

#### Prerequisites

- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8) (`dotnet --version` ≥ 8.0)
- [Node.js 20 LTS](https://nodejs.org) (`node --version` ≥ 20) for the TypeScript suite
- PowerShell (`pwsh`) for Playwright browser install (C# only)

### 1. Clone and restore

```bash
git clone https://github.com/SDETBMan/PlaywrightDotNetFramework.git
cd PlaywrightDotNetFramework
dotnet restore
```

### 2. Build

```bash
dotnet build
```

### 3. Install Playwright browsers (one-time)

```bash
pwsh tests/Framework.Tests/bin/Debug/net8.0/playwright.ps1 install
```

### 4. Run sanity checks

```bash
dotnet test --filter "Category=sanity"
```

### 5. Run unit tests

```bash
dotnet test --filter "Category=unit"
```

### 6. Run smoke tests (headed Chromium)

```bash
dotnet test --settings default.runsettings --filter "Category=smoke"
```

### 7. Run full regression (headless CI)

```bash
dotnet test --settings ci.runsettings
```

### 8. Cross-browser smoke

```bash
# Firefox
dotnet test --settings grid-firefox.runsettings --filter "Category=smoke"

# WebKit (Safari engine)
dotnet test --settings grid-webkit.runsettings --filter "Category=smoke"
```

### 9. Allure report

```bash
dotnet test --logger "allure-nunit"
allure serve allure-results
```

### 10. TypeScript Playwright tests

```bash
cd tests/playwright-ts
npm install
npx playwright install chromium

# Run all tests (Chromium — setup project runs auth first)
npx playwright test --project=setup --project=chromium

# Run smoke tests only
npx playwright test --grep "@smoke" --project=setup --project=chromium

# Run headed (for debugging)
npx playwright test --project=setup --project=chromium --headed

# Run all browsers (local only)
npx playwright install
npx playwright test

# Open HTML report
npx playwright show-report
```

### 11. View a trace (C# or TypeScript)

```bash
# C# trace saved on failure to traces/<TestName>.zip
npx playwright show-trace traces/<TestName>.zip

# TypeScript traces saved to tests/playwright-ts/test-results/ on failure
npx playwright show-trace tests/playwright-ts/test-results/**/*.zip
```

---

## Project Structure

```
PlaywrightDotNetFramework/
├── PlaywrightDotNetFramework.sln
├── src/
│   └── Framework.Core/                    # Class library — pages + utilities
│       ├── Config/
│       │   └── ConfigReader.cs            # IConfiguration wrapper
│       ├── Pages/
│       │   ├── BasePage.cs                # Async locator helpers
│       │   ├── LoginPage.cs
│       │   ├── DashboardPage.cs
│       │   ├── InventoryPage.cs
│       │   └── CartPage.cs
│       └── Utils/
│           ├── AiHelper.cs                # OpenAI integration
│           ├── BrowserStackUtils.cs       # App upload
│           ├── DatabaseUtils.cs           # MySQL async helpers
│           ├── DateHelper.cs
│           ├── SlackUtils.cs              # Webhook notifications
│           ├── StringFormatter.cs
│           └── StringUtils.cs
├── tests/
│   ├── Framework.Tests/                   # NUnit test project (C#)
│   │   ├── Base/
│   │   │   ├── BaseTest.cs                # Extends PageTest; trace viewer + screenshots
│   │   │   └── AuthenticatedTest.cs       # Fixture base: pre-logged-in IPage + page objects
│   │   ├── Listeners/
│   │   │   └── TestHooks.cs               # SetUpFixture — Slack on suite finish
│   │   ├── Tests/
│   │   │   ├── LoginTest.cs               # smoke + regression
│   │   │   ├── DashboardTest.cs           # data-driven + smoke + regression
│   │   │   ├── AddToCartTest.cs           # smoke + regression
│   │   │   ├── CartFixtureTest.cs         # fixture pattern demo (extends AuthenticatedTest)
│   │   │   ├── NetworkInterceptionTest.cs # 4 network interception patterns
│   │   │   ├── SecurityTest.cs            # security + regression: SQL injection, XSS, repeated logins, headers
│   │   │   ├── AiDrivenTest.cs            # ai category
│   │   │   └── SanityTest.cs              # sanity (bare-metal Playwright)
│   │   ├── Api/
│   │   │   └── UserApiTest.cs             # integration
│   │   └── Unit/
│   │       ├── FrameworkUnitTest.cs       # unit
│   │       └── StringUtilsTest.cs         # unit
│   └── playwright-ts/                     # Playwright TypeScript project
│       ├── package.json
│       ├── tsconfig.json
│       ├── playwright.config.ts           # 6 projects: setup, chromium, firefox, webkit, api, shopify
│       ├── pages/
│       │   ├── basePage.ts                # Abstract base: protected page for child page objects
│       │   ├── loginPage.ts
│       │   ├── inventoryPage.ts
│       │   ├── cartPage.ts
│       │   └── shopify/                   # Shopify storefront page objects
│       │       ├── shopifyStorefrontPage.ts
│       │       ├── shopifyProductPage.ts
│       │       └── shopifyCartPage.ts
│       ├── fixtures/
│       │   ├── fixtures.ts                # test.extend<AppFixtures, WorkerFixtures> — storageState auth + worker-scoped dbClient
│       │   └── shopifyFixtures.ts         # Shopify test fixtures
│       ├── utils/
│       │   ├── dbClient.ts                # Async MySQL/PostgreSQL with connection pooling
│       │   ├── dbAssertions.ts            # 5 DB-to-UI assertion patterns
│       │   ├── graphqlClient.ts           # GraphQL query client
│       │   └── allureHelper.ts            # Allure v3 metadata (suite, feature, story, severity)
│       ├── helpers/
│       │   ├── visual-config.ts           # Visual regression threshold config
│       │   └── freeze-animations.css      # CSS injection for deterministic screenshots
│       ├── scripts/
│       │   └── health-check.ts            # Deploy validation health-check script
│       └── tests/
│           ├── auth.setup.ts              # Global auth: login once → save storageState for all browser projects
│           ├── login.spec.ts              # @smoke + @regression login tests
│           ├── inventory.spec.ts          # @smoke + @regression cart tests (fixture)
│           ├── network.spec.ts            # 4 network interception patterns
│           ├── visual-regression.spec.ts  # 5 visual baseline tests
│           ├── db-assertions.spec.ts      # 7 DB-to-UI assertion patterns
│           ├── graphql.spec.ts            # 5 GraphQL patterns (pure API, no browser)
│           ├── smoke-health.spec.ts       # Deploy validation smoke tests
│           └── shopify/                   # Shopify E2E + visual tests
│               ├── storefront.spec.ts     # 8 storefront E2E tests
│               └── storefront-visual.spec.ts  # 4 Shopify visual baselines
├── config/
│   └── appsettings.json
├── default.runsettings                    # Local: chromium headed, 4 workers
├── ci.runsettings                         # CI: chromium headless, 4 workers
├── grid-firefox.runsettings               # Firefox cross-browser
├── grid-webkit.runsettings                # WebKit cross-browser
└── .github/
    └── workflows/
        └── regression.yml                 # C# + TypeScript CI pipeline
```

---

## Test Categories

| Category | Description | C# Command | TS Command |
|---|---|---|---|
| `sanity` | Bare-metal Playwright + config checks | `--filter "Category=sanity"` | — |
| `unit` | Pure C# logic, no browser | `--filter "Category=unit"` | — |
| `smoke` | Critical happy-path flows | `--filter "Category=smoke"` | `--grep "@smoke"` |
| `regression` | Full negative + edge cases | `--filter "Category=regression"` | `--grep "@regression"` |
| `security` | OWASP-aware login surface checks | `--filter "Category=security"` | — |
| `fixture` | Fixture / authenticated base class demos | `--filter "Category=fixture"` | — |
| `network` | Network interception patterns | `--filter "Category=network"` | — |
| `integration` | REST API tests | `--filter "Category=integration"` | — |
| `ai` | AI-assisted test data generation | `--filter "Category=ai"` | — |
| `visual` | Visual regression snapshot tests | — | `--grep "@visual"` |
| `graphql` | GraphQL API patterns (no browser) | — | `--project=api` |
| `database` | Database-to-UI assertion patterns | — | `--grep "@database"` |
| `shopify` | Shopify storefront E2E + visual | — | `--project=shopify` |

---

## Visual Regression Testing

Playwright's `toHaveScreenshot()` captures pixel-level baselines and diffs them on subsequent runs. Baseline images live in `tests/*-snapshots/` directories, checked into source control.

| Test | Page |
|---|---|
| Login page baseline | Login form at default state |
| Inventory page baseline | Product grid after login |
| Cart page baseline | Cart with items |
| Product detail baseline | Single product view |
| Error state baseline | Login error message |

**Configuration** (`playwright.config.ts`):
- `maxDiffPixelRatio: 0.01` — tolerates up to 1% pixel variance
- `threshold: 0.2` — per-pixel color distance tolerance
- `freeze-animations.css` injected to eliminate flaky animation diffs

**Baseline update workflow** (`visual-regression-update.yml`): manually triggered, runs `--update-snapshots`, commits to a branch, and opens a PR for human review. Baselines are never auto-updated.

---

## GraphQL API Testing

Five patterns tested via Playwright's `request` fixture (no browser launched):

| Pattern | What it validates |
|---|---|
| Direct query | Simple query execution against GraphQL endpoint |
| Variables | Parameterized queries with variable injection |
| Mock by operationName | `page.route()` intercepts GraphQL by operation name |
| Error handling | Graceful handling of malformed queries |
| Operation auditing | Intercept and log all GraphQL operations (N+1 detection) |

Default endpoint: `https://countries.trevorblades.com/` (public demo).
Override via `GRAPHQL_URL` env var for production targets.

---

## Database-to-UI Assertions

The `dbClient.ts` utility provides async connection pooling for MySQL and PostgreSQL, worker-scoped via `test.extend` to share one pool per worker process. The `dbAssertions.ts` module implements five reusable assertion patterns with `expect.poll()` for auto-retry:

| Pattern | What it validates |
|---|---|
| Scalar match | Single DB value matches UI element text |
| Row count | DB record count matches UI list length |
| Field match | DB row fields match UI detail view |
| Input pre-fill | DB defaults pre-populate form fields |
| Column values in list | DB column values appear in UI dropdown/list |

---

## Shopify E2E Testing

A dedicated `shopify` project in `playwright.config.ts` runs against a live Shopify storefront. Tests skip gracefully when `SHOPIFY_STORE_URL` is not set.

**E2E tests** (8): homepage load, collection browsing, product detail, add-to-cart, cart verification, search, empty cart, checkout flow.

**Visual baselines** (4): homepage, collection page, product page, cart page.

Page objects: `ShopifyStorefrontPage`, `ShopifyProductPage`, `ShopifyCartPage`.

---

## Deploy Validation Pipeline

The `deploy-validate-rollback.yml` workflow implements a three-stage deployment gate:

```
Deploy URL → Health Check (HTTP + Playwright smoke) → PASS → done
                                                    → FAIL → Rollback (Vercel API) → Summary
```

- Accepts any Vercel deployment URL via `workflow_dispatch`
- Runs `health-check.ts` script + `smoke-health.spec.ts` Playwright tests
- On failure: finds previous successful deployment via Vercel API and triggers rollback
- Posts a summary table to the GitHub Actions job summary
- Also available as `workflow_call` for composing into other pipelines

---

## Architecture Decisions

### No DriverManager needed
`PageTest` (from `Microsoft.Playwright.NUnit`) provides a fresh `IBrowser`, `IBrowserContext`,
and `IPage` per test. Combined with `[Parallelizable(ParallelScope.Self)]`, this gives full
isolation without any thread-local driver management.

### Auto-wait replaces Healenium
Playwright's built-in auto-waiting on every `ClickAsync` / `FillAsync` / `WaitForAsync` makes
Healenium's self-healing driver unnecessary. Locators are stable CSS/ARIA selectors.

### ConfigReader priority chain
`ENV VAR` → `appsettings.json` → supplied default. Environment variables use `__` as
hierarchy separator (e.g. `app__username=standard_user`).

### Trace Viewer: retain-on-failure
Both the C# and TypeScript projects discard traces for passing tests and save full traces
(screenshots + DOM snapshots + network) only on failure. This mirrors the `retain-on-failure`
strategy and avoids disk waste on clean runs.

- **C#:** `Context.Tracing.StopAsync(new TracingStopOptions { Path = tracePath })` on failure; `StopAsync()` (no path) on pass.
- **TypeScript:** `trace: 'retain-on-failure'` in `playwright.config.ts`.

### Fixtures: C# vs TypeScript
The fixture pattern is implemented identically in both languages, though the idiom differs:

| Concept | C# | TypeScript |
|---|---|---|
| Fixture base | `AuthenticatedTest : BaseTest` | `test.extend<AppFixtures, WorkerFixtures>` |
| Auth strategy | `[SetUp] LoginBeforeEach()` (per-test UI login) | `storageState` — global `auth.setup.ts` logs in once, browser projects reuse saved cookies |
| Fixture scoping | NUnit `[SetUp]` / `[OneTimeSetUp]` | Test-scoped (page objects) + worker-scoped (`dbClient`) |
| Teardown | `[TearDown]` inherited from `BaseTest` | Playwright disposes page automatically |
| Guard | `Assert.That(Page.Url, Does.Contain("inventory"))` | `await page.waitForURL(/inventory/)` |
| Locator strategy | CSS selectors via `BasePage` helpers | Semantic: `getByRole` → `getByPlaceholder` → `getByTestId` (`data-test`) |

---

## Security Testing

`SecurityTest.cs` adds four OWASP-aware test cases (categories: `security`, `regression`). The class extends `BaseTest` and reuses `LoginPage` from `Framework.Core.Pages`. `HttpClient` mirrors the pattern already used in `UserApiTest.cs`.

| Test | OWASP category |
|---|---|
| `SqlInjectionIsRejected` | A03 Injection: injects `' OR '1'='1' --`; asserts error visible and message contains no `sql`/`exception` leakage |
| `XssInjectionIsHandledSafely` | A03 Injection: injects `<script>document.title='xss'</script>`; asserts `Page.TitleAsync()` is not `"xss"` |
| `RepeatedFailedLoginAttemptsHandledGracefully` | A07 Auth Failures: 5 bad logins then valid login; asserts URL contains `inventory` |
| `SecurityResponseHeadersPresent` | A05 Security Misconfiguration: `HttpClient.GetAsync` to saucedemo.com; `Assert.Multiple` (soft) checks `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy` |

Run security tests only:
```bash
dotnet test --settings ci.runsettings --filter "Category=security"
```

The CI pipeline also runs an **OWASP ZAP Baseline Scan** after every test run (`if: always()`). Passive scan against `https://www.saucedemo.com` with `continue-on-error: true` so findings never block a green build.

---

## CI Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `playwright.yml` | push · PR · nightly 02:00 UTC | Full regression: C# + TypeScript + Shopify + visual + OWASP ZAP |
| `playwright-smoke-pr.yml` | PR to `main` (paths: `playwright/**`) | Fast @smoke gate: Chromium only, 5-min timeout, fail-fast |
| `azure-pipelines.yml` | PR to `main` (paths: `playwright/*`) | Azure DevOps equivalent of the GHA smoke gate |
| `deploy-validate-rollback.yml` | `workflow_dispatch` · `workflow_call` | Health-check → smoke → auto-rollback pipeline |
| `visual-regression-update.yml` | `workflow_dispatch` | Update visual baselines → commit → open PR for review |

### Azure DevOps Pipeline

`azure-pipelines.yml` is a direct port of the GitHub Actions PR smoke gate to Azure DevOps YAML. It mirrors the same functionality — TypeScript `@smoke` tests, Chromium only, 5-minute timeout, fail-fast — using ADO equivalents:

- `pr:` trigger with `autoCancel: true` (replaces GHA `concurrency.cancel-in-progress`)
- `NodeTool@0` + `Cache@2` (replaces `actions/setup-node` + `actions/cache`)
- `PublishTestResults@2` for JUnit XML (surfaces in the ADO Test tab)
- `PublishBuildArtifacts@1` conditioned on `failed()` for HTML report + traces
- Variable group `playwright-secrets` for credentials (replaces GitHub Secrets)

---

## Contributing

1. Fork the repo and create a feature branch.
2. Follow existing naming conventions (one test per method, `[Category]` on every test).
3. Run `dotnet test --filter "Category=unit"` before pushing.
4. Open a PR; the CI pipeline runs automatically.
