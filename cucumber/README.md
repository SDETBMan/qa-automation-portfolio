# Enterprise Scalable BDD Test Automation Framework

![Java](https://img.shields.io/badge/Language-Java-orange)
![Cucumber](https://img.shields.io/badge/BDD-Cucumber-brightgreen)
![JaCoCo](https://img.shields.io/badge/Coverage-JaCoCo-blue)
![Mockito](https://img.shields.io/badge/Mocks-Mockito-yellow)

A production-grade, thread-safe BDD testing framework built from scratch to demonstrate modern SDET architecture. Designed for high scalability, this framework leverages **Java**, **Selenium 4**, and **Cucumber 7** with **TestNG** for parallel execution across web, mobile, and cloud platforms.

[![cucumber CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cucumber.yml)

## Key Features

* **Hybrid BDD Architecture:** Clear separation of concerns using Feature files, Step Definitions, and Page Object Model (POM).
* **Parallel Execution:** Implemented `ThreadLocal<WebDriver>` to ensure thread safety, allowing multiple scenarios to run simultaneously.
* **Self-Healing Tests:** Integrated **Healenium** to automatically recover from broken locators — no manual maintenance when the UI shifts.
* **Multi-Platform Driver:** Single `DriverManager` supports Local, Selenium Grid, BrowserStack, Android (Appium), and iOS (Appium) with a single `-Dtarget=` flag.
* **Containerized Infrastructure:** `Dockerfile` and `docker-compose.yaml` orchestrate the full stack — Selenium Grid (Chrome/Firefox/Edge nodes), Healenium backend, and PostgreSQL.
* **Retry Analyzer:** `AnnotationTransformer` globally applies `RetryAnalyzer` to every scenario — flaky network tests auto-retry without any per-test annotation.
* **Dual Reporting:** **Allure** (interactive dashboard, GitHub Pages deployment) and **Extent Reports** (Spark HTML) generated on every run.
* **API Testing Layer:** **RestAssured** step definitions and feature files validate backend endpoints alongside UI tests.
* **Database Validation:** `DatabaseUtils` enables frontend-to-backend data integrity checks via JDBC.
* **Slack Notifications:** `TestListener` dispatches suite summaries to a Slack channel via webhook on every execution.
* **Performance Testing:** **JMeter** load test included — triggered optionally from the CI/CD pipeline.
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
| API Testing | RestAssured 5.4 |
| Database | MySQL Connector 9.0 |
| Performance | JMeter (Maven Plugin 3.8) |
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

## Project Structure

```
src/
├── main/java/com/saucedemo/
│   └── utils/
│       ├── ConfigReader.java          # Priority-based config (sys props > env vars > file)
│       ├── AnnotationTransformer.java # Globally applies RetryAnalyzer to every scenario
│       ├── RetryAnalyzer.java         # Auto-retries flaky tests up to retry.max times
│       ├── SlackUtils.java            # Posts suite summary to Slack via webhook
│       └── DatabaseUtils.java         # JDBC helpers for backend data validation
├── test/java/com/saucedemo/
│   ├── pages/
│   │   ├── BasePage.java              # Fluent wrapper methods (click, sendKeys, waits)
│   │   ├── LoginPage.java
│   │   ├── DashboardPage.java
│   │   ├── InventoryPage.java
│   │   ├── CartPage.java
│   │   └── ProductsPage.java
│   ├── stepDefinitions/
│   │   ├── LoginSteps.java
│   │   ├── DashboardSteps.java
│   │   ├── InventorySteps.java
│   │   ├── CartSteps.java
│   │   ├── ApiSteps.java
│   │   ├── SecuritySteps.java         # OWASP step defs: error leakage, XSS title, response headers
│   │   └── Hooks.java                 # Screenshot on failure, driver teardown
│   ├── runners/
│   │   └── TestRunner.java            # Parallel DataProvider, Allure + Extent plugins
│   ├── listeners/
│   │   └── TestListener.java          # Slack notification on suite finish
│   └── utils/
│       └── DriverManager.java         # ThreadLocal factory: local/grid/BS/android/iOS + Healenium
└── test/resources/
    ├── features/
    │   ├── login.feature
    │   ├── dashboard.feature
    │   ├── inventory.feature
    │   ├── cart.feature
    │   ├── api.feature
    │   └── security.feature           # @security: SQL injection, XSS, response headers
    ├── config.properties
    ├── extent.properties
    └── healenium.properties
```
