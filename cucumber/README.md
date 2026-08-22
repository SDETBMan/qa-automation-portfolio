# Enterprise Scalable BDD Test Automation Framework

![Java](https://img.shields.io/badge/Language-Java-orange)
![Cucumber](https://img.shields.io/badge/BDD-Cucumber-brightgreen)
![Karate](https://img.shields.io/badge/API-Karate-purple)
![JaCoCo](https://img.shields.io/badge/Coverage-JaCoCo-blue)
![Mockito](https://img.shields.io/badge/Mocks-Mockito-yellow)

A production-grade, thread-safe BDD testing framework built from scratch to demonstrate modern SDET architecture. Designed for high scalability, this framework leverages **Java**, **Selenium 4**, and **Cucumber 7** with **TestNG** for parallel execution across web, mobile, and cloud platforms. Includes a **Karate 1.5** API testing layer with 13 feature files covering CRUD operations, schema validation, mock servers, and financial domain workflows.

[![cucumber CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml)

## Key Features

* **Hybrid BDD Architecture:** Clear separation of concerns using Feature files, Step Definitions, and Page Object Model (POM).
* **Parallel Execution:** Implemented `ThreadLocal<WebDriver>` to ensure thread safety, allowing multiple scenarios to run simultaneously.
* **Self-Healing Tests:** Integrated **Healenium** to automatically recover from broken locators with no manual maintenance when the UI shifts.
* **Multi-Platform Driver:** Single `DriverManager` supports Local, Selenium Grid, BrowserStack, Android (Appium), and iOS (Appium) with a single `-Dtarget=` flag.
* **Containerized Infrastructure:** `Dockerfile` and `docker-compose.yaml` orchestrate the full stack: Selenium Grid (Chrome/Firefox/Edge nodes), Healenium backend, and PostgreSQL.
* **Retry Analyzer:** `AnnotationTransformer` globally applies `RetryAnalyzer` to every scenario; flaky network tests auto-retry without any per-test annotation.
* **Dual Reporting:** **Allure** (interactive dashboard, GitHub Pages deployment) and **Extent Reports** (Spark HTML) generated on every run.
* **API Testing Layer:** **RestAssured** step definitions and feature files validate backend endpoints alongside UI tests.
* **Database Validation:** `DatabaseUtils` enables frontend-to-backend data integrity checks via JDBC.
* **Slack Notifications:** `TestListener` dispatches suite summaries to a Slack channel via webhook on every execution.
* **Performance Testing (JMeter):** JMeter load test included, triggered optionally from the CI/CD pipeline.
* **Performance Testing (Gatling):** **Karate-Gatling** integration reuses existing Karate feature files as Gatling load test simulations with SLA assertions — zero test rewriting required.
* **CI/CD Integration:** **GitHub Actions** pipeline with dispatch inputs for execution mode, browser, and JMeter toggle. Allure report auto-deployed to GitHub Pages.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Java 17 |
| BDD | Cucumber 7 |
| Test Runner | TestNG 7.10 |
| Browser Automation | Selenium WebDriver 4.21 |
| Mobile Automation | Appium 9.3 (Android + iOS) |
| Self-Healing | Healenium 3.4.8 |
| API Testing (UI steps) | RestAssured 5.4 |
| API Testing (standalone) | Karate 1.5.2 |
| Database | MySQL Connector 9.0 |
| Performance | JMeter (Maven Plugin 3.8) · Karate-Gatling 1.5.2 |
| Reporting | Allure 2.27 + Extent Reports 5.1 |
| Code Coverage | JaCoCo 0.8.12 |
| CI/CD | GitHub Actions |
| Containerization | Docker + Docker Compose |
| Build Tool | Maven |

## Page Coverage

Both frameworks (CucumberFramework and SeleniumPOMFramework) cover the same five pages, each implemented in their respective stack's style:

| Page | Purpose |
|---|---|
| `LoginPage` | Login actions, error validation, mobile + web locators |
| `DashboardPage` | Cart icon visibility, logout flow, welcome header |
| `InventoryPage` | Add/remove products, cart badge, navigate to cart |
| `CartPage` | Item verification, checkout navigation |
| `ProductsPage` | Lightweight product page for quick cart interactions |

## Feature Coverage

| Feature File | Scenarios |
|---|---|
| `login.feature` | Valid login, invalid login, data-driven multi-user |
| `dashboard.feature` | Multi-user access, logout flow, security (direct URL access) |
| `inventory.feature` | Add item, add multiple, remove item, checkout navigation |
| `cart.feature` | Add item, verify cart badge, verify cart contents |
| `api.feature` | API health check, data integrity validation |
| `security.feature` | SQL injection rejected, XSS handled safely, security response headers present |

## How to Run

### Local (GUI)
```bash
mvn clean test
```

### Local (Headless)
```bash
mvn clean test -Dheadless=true
```

### Selenium Grid
```bash
docker compose up -d selenium-hub chrome firefox edge
mvn clean test -Dtarget=grid -Dgrid_url=http://localhost:4444/wd/hub -Dheadless=true
```

### Full Stack (Grid + Self-Healing via Docker Compose)
```bash
docker compose up -d
mvn clean test -Dtarget=grid -Dheadless=true
```

### BrowserStack
```bash
mvn clean test -Dtarget=browserstack -Dbs_user=YOUR_USER -Dbs_key=YOUR_KEY
```

### Mobile (Android)
```bash
mvn clean test -Dtarget=android
```

### Mobile (iOS)
```bash
mvn clean test -Dtarget=ios
```

### Performance Tests (JMeter)
```bash
mvn jmeter:jmeter
```

### Performance Tests (Karate-Gatling)
```bash
# Run Gatling load simulation reusing Karate feature files
mvn test -Pperf
```

Runs three Karate feature files (users, posts, comments) as concurrent Gatling load scenarios. Assertions fail the build if SLAs are violated (mean < 500ms, p95 < 2000ms, success > 95%). Gatling HTML report is generated in `target/gatling/`.

## CI/CD Pipeline

The GitHub Actions pipeline triggers automatically on every push and pull request to `main` (headless Chrome). A manual `workflow_dispatch` trigger exposes additional controls:

| Input | Options |
|---|---|
| Execution Environment | `local`, `grid`, `browserstack`, `android`, `ios` |
| Browser | `chrome`, `firefox`, `edge` |
| Run JMeter Performance | `true` / `false` |

On every run the pipeline: executes tests, generates an Allure report, deploys it to GitHub Pages, and sends a Slack notification.

## Reporting

| Report | Location |
|---|---|
| Allure Dashboard | GitHub Pages (auto-deployed by CI) |
| Extent Spark Report | `target/spark-reports/Spark.html` |
| Cucumber HTML | `target/cucumber-reports/cucumber.html` |
| JaCoCo Coverage | `target/site/jacoco/index.html` |
| Gatling Load Report | `target/gatling/*/index.html` |

## Security Testing

`security.feature` adds three OWASP-aware BDD scenarios tagged `@security`. The SQL injection and XSS scenarios reuse the four existing step definitions from `LoginSteps.java` with no changes. `SecuritySteps.java` provides only the three new assertion steps.

| Scenario | Reused steps | New step | OWASP category |
|---|---|---|---|
| SQL injection attempt is safely rejected | `Given I am on...` · `When I enter username...` · `When I click...` · `Then I should see an error message` | `Then the error message should not expose system internals` | A03 Injection |
| XSS payload in login field is handled safely | same 4 steps | `Then the page title should not be "xss"` | A03 Injection |
| Security response headers are present | `Given I am on...` | `Then the security response headers should be present` | A05 Security Misconfiguration |

The headers step uses `SoftAssert` and RestAssured so missing headers on the demo site document posture without failing the build.

Run security scenarios only:
```bash
mvn clean test -Dheadless=true -Dcucumber.filter.tags="@security"
```

The CI pipeline also runs an **OWASP ZAP Baseline Scan** after every test run (`if: always()`). Passive scan against `https://www.saucedemo.com` with `continue-on-error: true` so findings never block a green build.

---

## Karate API Testing

A standalone API testing layer using **Karate 1.5.2** that coexists with Cucumber in the same Maven project. Karate runs via JUnit5 under a dedicated Maven profile — `mvn test` continues to run only Cucumber, while `mvn test -Pkarate` runs only Karate.

### Karate Feature Coverage

| Category | Feature File | Scenarios |
|---|---|---|
| **Core API** | `users-crud.feature` | GET all/single, POST, PUT, PATCH, DELETE (7) |
| **Core API** | `posts.feature` | GET all/filtered, POST, read-modify-write (4) |
| **Core API** | `comments.feature` | Nested resources, query filtering, request chaining (3) |
| **Advanced** | `schema-validation.feature` | Type markers, each keyword, optional fields, regex (4) |
| **Advanced** | `data-driven.feature` | Scenario Outline + Examples, dynamic data (3) |
| **Advanced** | `headers-auth.feature` | Custom headers, Bearer token, cookies, configure (5) |
| **Advanced** | `error-handling.feature` | 404s, empty body, large payload, retry (6) |
| **Financial** | `transaction-lifecycle.feature` | PENDING→AUTHORIZED→CAPTURED→REFUNDED state machine (4) |
| **Financial** | `pricing-calculations.feature` | Tax rates, discount + tax combined (2 outlines) |
| **Infra** | `performance-hooks.feature` | Response time SLAs, parallel calls, auth helper (4) |
| | **Reusable (@ignore)** | `common.feature`, `auth.feature`, `payment-mock.feature` |

**Total: 13 runnable feature files, ~42 scenarios**

### How to Run Karate

```bash
# All Karate tests
mvn clean test -Pkarate

# Target a specific environment
mvn clean test -Pkarate -Dkarate.env=staging

# Run only smoke-tagged features
mvn clean test -Pkarate -Dkarate.options="--tags @smoke"

# Run only financial domain features
mvn clean test -Pkarate -Dkarate.options="--tags @financial"
```

### Karate Reports

| Report | Location |
|---|---|
| Karate HTML Summary | `target/karate-reports/karate-summary.html` |
| Surefire XML | `target/surefire-reports/TEST-karate.KarateRunner.xml` |
| Karate Log | `target/karate.log` |

---

## Project Structure

```
src/
├── main/java/com/saucedemo/
│   └── utils/
│       ├── ConfigReader.java          # Priority-based config (sys props > env vars > file)
│       ├── AnnotationTransformer.java # Globally applies RetryAnalyzer to every scenario
│       ├── RetryAnalyzer.java         # Auto-retries flaky tests up to retry.max times
│       ├── SlackUtils.java            # Posts suite summary to Slack via webhook
│       ├── DatabaseUtils.java         # JDBC helpers for backend data validation
│       └── DataDogUtils.java          # Sends test metrics to DataDog v2 API
├── test/java/
│   ├── karate-config.js               # Karate env switching, base URLs, timeouts
│   ├── com/saucedemo/
│   │   ├── pages/
│   │   │   ├── BasePage.java          # Fluent wrapper methods (click, sendKeys, waits)
│   │   │   ├── LoginPage.java
│   │   │   ├── DashboardPage.java
│   │   │   ├── InventoryPage.java
│   │   │   ├── CartPage.java
│   │   │   └── ProductsPage.java
│   │   ├── stepDefinitions/
│   │   │   ├── LoginSteps.java
│   │   │   ├── DashboardSteps.java
│   │   │   ├── InventorySteps.java
│   │   │   ├── CartSteps.java
│   │   │   ├── ApiSteps.java
│   │   │   ├── SecuritySteps.java     # OWASP step defs
│   │   │   └── Hooks.java            # Screenshot on failure, driver teardown
│   │   ├── runners/
│   │   │   └── TestRunner.java        # Cucumber + TestNG parallel runner
│   │   ├── listeners/
│   │   │   └── TestListener.java      # Slack + DataDog on suite finish
│   │   └── utils/
│   │       └── DriverManager.java     # ThreadLocal factory: local/grid/BS/android/iOS
│   ├── karate/                        # ── Karate API Testing ──
│       ├── KarateRunner.java          # JUnit5 runner (active with -Pkarate)
│       ├── logback-test.xml           # Karate logging config
│       ├── helpers/
│       │   └── DataDogHook.java       # Karate → DataDog metrics bridge
│       ├── api/
│       │   ├── users/users-crud.feature
│       │   ├── posts/posts.feature
│       │   └── comments/comments.feature
│       ├── advanced/
│       │   ├── schema/schema-validation.feature
│       │   ├── data-driven/data-driven.feature
│       │   ├── headers/headers-auth.feature
│       │   └── error-handling/error-handling.feature
│       ├── financial/
│       │   ├── mock/payment-mock.feature        # @ignore — mock server
│       │   ├── transactions/transaction-lifecycle.feature
│       │   └── pricing/pricing-calculations.feature
│       └── infra/
│           ├── reusable/common.feature          # @ignore — shared helpers
│           ├── reusable/auth.feature            # @ignore — auth helper
│           └── performance/performance-hooks.feature
├── test/scala/karate/perf/
│   └── KaratePerformanceSimulation.scala  # Gatling simulation (mvn test -Pperf)
└── test/resources/
    ├── features/                      # ── Cucumber features ──
    │   ├── login.feature
    │   ├── dashboard.feature
    │   ├── inventory.feature
    │   ├── cart.feature
    │   ├── api.feature
    │   └── security.feature
    ├── config.properties
    ├── extent.properties
    └── healenium.properties
```
