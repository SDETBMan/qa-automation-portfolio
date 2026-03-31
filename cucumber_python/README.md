# cucumber-python

Python BDD test framework using **Behave** (Python's Cucumber implementation) targeting [SauceDemo](https://www.saucedemo.com/). Built to mirror the Java Cucumber framework in this monorepo while applying four architectural strategies for scale.

---

## Architecture

### The Problem with Frameworks at 1,000+ Tests

Most frameworks collapse under scale because they treat automation as scripting rather than engineering. Four strategies are applied here to prevent that:

**Strategy 1 — Declarative Gherkin (the "What," not the "How")**

Imperative steps cause step definition explosion. Every button gets its own step. Instead, Gherkin describes *business intent* and the implementation details live in Page Objects and Tasks.

```gherkin
# Bad — imperative
When I type "standard_user" into the username field
And I type "secret_sauce" into the password field
And I click the blue login button

# Good — declarative
When I login with valid credentials
```

**Strategy 2 — Domain-Object Step Organization**

Steps are organized by *domain entity*, not by feature file. A new engineer knows exactly where to look.

| File | Domain |
|---|---|
| `steps/auth_steps.py` | Login, logout, session |
| `steps/inventory_steps.py` | Products, cart badge, checkout navigation |
| `steps/api_steps.py` | HTTP requests, response validation |
| `steps/security_steps.py` | Injection, XSS, headers |
| `steps/common_steps.py` | Shared cross-domain steps |

**Strategy 3 — Aggressive Parameterization**

One step handles every variant via Behave's `{type}` expressions. No separate step per product name, page, or status code.

```python
@then("the cart badge should show {count:d}")   # handles 1, 2, 3, ...
@then('"{product}" should be in the cart')       # handles any product name
@then("the response status code should be {expected_status:d}")
```

**Strategy 4 — Screenplay Pattern**

Complex multi-step flows become reusable **Tasks** rather than copy-pasted step sequences. Tasks separate the *Who* (Actor), *What* (Task), and *How* (Page Object Interaction).

```python
# Instead of 3 duplicated steps in every precondition:
LoginTask(driver).perform("standard_user", "secret_sauce")

# Add multiple products + assert badge in one call:
AddToCartTask(driver).perform(["Backpack", "Bike Light"], assert_badge=True)
```

---

## Project Structure

```
cucumber_python/
├── features/                  # Gherkin .feature files
│   ├── login.feature
│   ├── dashboard.feature
│   ├── inventory.feature
│   ├── cart.feature
│   ├── api.feature
│   ├── security.feature
│   └── environment.py         # Behave hooks (replaces Hooks.java)
│                              #   before_all, before_scenario,
│                              #   after_scenario, after_all
│
├── steps/                     # Step definitions — domain organized
│   ├── auth_steps.py          # Login, logout, session
│   ├── inventory_steps.py     # Products, add/remove, cart badge
│   ├── api_steps.py           # REST API validation
│   ├── security_steps.py      # SQL injection, XSS, headers
│   └── common_steps.py        # Shared reusable steps
│
├── pages/                     # Page Object Model
│   ├── base_page.py           # Shared wait/action wrappers
│   ├── login_page.py
│   ├── dashboard_page.py
│   ├── inventory_page.py
│   └── cart_page.py
│
├── utils/                     # Framework utilities
│   ├── config_reader.py       # Priority: env vars > config.ini
│   ├── driver_manager.py      # Thread-safe WebDriver factory
│   ├── tasks.py               # Screenplay Tasks (LoginTask, AddToCartTask)
│   ├── api_client.py          # Thin HTTP client for API steps
│   ├── datadog_utils.py       # Custom GAUGE metrics → DataDog v2 API
│   └── slack_utils.py         # Slack webhook notifications
│
├── k8s/                       # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── selenium-grid/         # Hub + Chrome/Firefox nodes
│   └── healenium/             # Postgres + hlm-backend + hlm-proxy
│
├── config.ini                 # Framework configuration
├── behave.ini                 # Behave runner configuration
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Multi-stage image (Python 3.11 + Chromium)
└── docker-compose.yaml        # Full stack: Grid + Healenium + test runner
```

---

## Healenium — Self-Healing Locators

Healenium reduces test maintenance caused by minor UI locator changes.

**How it works in Python (vs. Java):**

The Java framework uses `SelfHealingDriver.create(rawDriver)` — a native SDK wrapper. Python has no equivalent SDK. Instead, Healenium exposes an HTTP proxy (`hlm-proxy:8085`) that sits in front of Selenium Grid. The framework routes its `RemoteWebDriver` through this proxy; Healenium intercepts element lookups, applies ML-based healing, and forwards to the real Grid.

**Activation:**

```bash
# Via environment variable
HEALENIUM_ENABLED=true HEALENIUM_PROXY=http://localhost:8085 behave

# Via config.ini
[healenium]
enabled   = true
proxy_url = http://localhost:8085
```

When running `docker compose up`, Healenium is automatically active.

---

## Running the Tests

### Prerequisites

- Python 3.11+
- Chrome or Chromium installed
- `pip install -r requirements.txt`

### Local (headless Chrome)

```bash
cd cucumber_python
pip install -r requirements.txt
HEADLESS=true behave --no-capture
```

### Tag filter

```bash
behave --tags @security
behave --tags @smoke
```

### Selenium Grid (Docker Compose)

```bash
# Start the full stack: Grid + Healenium + test runner
docker compose up

# Or start just the infrastructure and run tests locally
docker compose up -d selenium-hub chrome firefox edge
TARGET=grid GRID_URL=http://localhost:4444/wd/hub HEADLESS=true behave
```

### Via root Makefile

```bash
make cucumber-python
```

### Kubernetes

```bash
# Apply manifests (reuses the shared k8s/ infra namespace)
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/selenium-grid/
kubectl apply -f k8s/healenium/

# Port-forward hub and run
kubectl port-forward -n selenium-grid svc/selenium-hub 4444:4444 &
TARGET=grid GRID_URL=http://localhost:4444/wd/hub HEADLESS=true behave
```

---

## Configuration

All settings live in `config.ini`. Environment variables take priority over the file.

| Key | Default | Env Var |
|---|---|---|
| Execution target | `local` | `TARGET` |
| Browser | `chrome` | `BROWSER` |
| Headless | `false` | `HEADLESS` |
| App URL | `https://www.saucedemo.com/` | `URL` |
| Grid URL | `http://localhost:4444/wd/hub` | `GRID_URL` |
| Healenium enabled | `false` | `HEALENIUM_ENABLED` |
| Healenium proxy | `http://localhost:8085` | `HEALENIUM_PROXY` |
| BrowserStack user | _(empty)_ | `BS_USER` |
| BrowserStack key | _(empty)_ | `BS_KEY` |

---

## Test Scenarios

| Feature | Scenarios | Tags |
|---|---|---|
| Login | Valid, invalid, 4-user Scenario Outline | — |
| Dashboard | 3-user outline, logout, direct URL auth | — |
| Inventory | Add single, add multiple (table), remove, checkout nav | — |
| Cart | Badge count, item persistence | — |
| API | 2 direct + 4-endpoint Scenario Outline | — |
| Security | SQL injection, XSS, brute-force resilience, headers | `@security` |

---

## Reporting

| Report | Location | Notes |
|---|---|---|
| Allure | `reports/allure-results/` | Deployed to GitHub Pages on CI |
| JUnit XML | `reports/junit/` | Uploaded to DataDog CI Visibility |
| Console | stdout | Pretty format, step timings enabled |

---

## CI/CD

`.github/workflows/cucumber-python.yml`

**Triggers:** push to `main` (path: `cucumber_python/**`), pull request, nightly 05:00 UTC, `workflow_dispatch`

**Dispatch inputs:**
- `execution_mode`: `local` / `grid` / `browserstack`
- `test_browser`: `chrome` / `firefox` / `edge`
- `test_tags`: Behave tag filter (e.g. `@smoke`)

**Pipeline steps:**
1. Set up Python 3.11 (pip cache)
2. Install dependencies
3. Run Behave (headless Chrome) — auto on push/PR/schedule
4. Start Selenium Grid + run (if `grid` mode dispatched)
5. Run BrowserStack (if `browserstack` mode dispatched)
6. OWASP ZAP Baseline Scan (`continue-on-error: true`)
7. Upload JUnit XML → DataDog CI Visibility
8. Upload Allure results artifact (7-day retention)
9. Build + deploy Allure report to GitHub Pages
10. Email notification on failure

---

## Observability

### DataDog Custom Metrics

Four GAUGE metrics sent after each suite run via `utils/datadog_utils.py`:

| Metric | Description |
|---|---|
| `test.suite.passed` | Passing scenario count |
| `test.suite.failed` | Failing scenario count |
| `test.suite.skipped` | Skipped scenario count |
| `test.suite.duration_ms` | Total wall-clock duration |

Tags applied: `framework:cucumber-python`, `service:qa-automation-portfolio`, `env:ci`

Requires `DD_API_KEY` environment variable. Gracefully skips if absent (local dev stays green).

### Slack Notifications

A Slack message is posted after any run with failures via `utils/slack_utils.py`.
Requires `SLACK_WEBHOOK_URL` environment variable. Gracefully skips if absent.
