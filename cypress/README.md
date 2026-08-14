# cypress — TypeScript E2E + Component Testing

[![cypress CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cypress.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cypress.yml)

Cypress 15 · TypeScript 5 · React 18 · Vite · Node.js 22 · Claude AI Test Generator

End-to-end tests against [SauceDemo](https://www.saucedemo.com/) plus isolated
React component tests, all in TypeScript.

---

## What's unique here

| Feature | Detail |
|---|---|
| **`cy.intercept()`** | Network spy/stub in `network.cy.ts`: Cypress's most-asked-about interview topic |
| **Component testing** | Mounts `ProductCard` React component in isolation via the Cypress component runner |
| **Custom commands** | `cy.login()`, `cy.addToCart()`, `cy.clearCart()`: typed via `Chainable` declaration |
| **Page Object Model** | Abstract `BasePage` + 4 concrete pages |
| **DataDog GAUGE metrics** | TypeScript port of the Python reporter; posts 4 metrics after every run |
| **JUnit XML** | `mocha-junit-reporter` for DataDog CI Visibility upload |
| **AI test generator** | CLI tool that takes a plain-English user story and produces a runnable `.cy.ts` file using Claude, with full framework context (page objects, commands, fixtures) as RAG input |

---

## AI Test Generator

A CLI tool that bridges AI and test automation: give it a user story in plain English, and it produces a production-ready Cypress test file that follows every convention in the framework.

### How it works

1. **Reads framework context** — all 5 page objects, custom commands, fixtures, and 3 example tests
2. **Builds a RAG prompt** — injects the full codebase context into Claude's system prompt with explicit pattern rules
3. **Generates a `.cy.ts` file** — output follows existing conventions: `testIsolation: false`, POM imports, fixture-driven data, `@smoke`/`@regression` tags

### Usage

```bash
# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Generate a test file from a user story
npm run ai:generate "User adds multiple items to cart and verifies the cart badge updates"

# Preview without writing a file
npm run ai:dry-run "User sorts products by price low to high and verifies order"

# Custom output file name
npm run ai:generate -- --story "User completes checkout with valid info" --name happy-path-checkout
```

Generated tests are written to `cypress/e2e/generated/` and can be run immediately:

```bash
npx cypress run --spec "cypress/e2e/generated/user-adds-multiple-items.cy.ts"
```

### Why this matters

- Demonstrates **AI + test automation integration** — the key skill gap in modern QA
- Uses **retrieval-augmented generation (RAG)** — the LLM doesn't hallucinate selectors because it sees real page objects
- Produces **framework-consistent output** — generated tests are indistinguishable from hand-written ones
- **Zero-shot generation** — no fine-tuning, no training data; the framework context is the only input

---

## Structure

```
cypress/
├── ai-generator/
│   └── generate-test.ts             # AI test generator (Claude + RAG)
├── cypress/
│   ├── component/
│   │   └── ProductCard.cy.tsx       # React component tests
│   ├── e2e/
│   │   ├── generated/               # AI-generated test output directory
│   │   ├── login.cy.ts              # @smoke + @regression
│   │   ├── inventory.cy.ts          # @smoke + @regression
│   │   ├── checkout.cy.ts           # @regression
│   │   ├── network.cy.ts            # cy.intercept() — @regression
│   │   ├── accessibility.cy.ts      # WCAG 2.1 AA — @smoke + @regression + @known-defect
│   │   └── performance.cy.ts        # Lighthouse budgets — @regression (Chrome only)
│   ├── fixtures/
│   │   ├── users.json               # Credentials: standard, locked, problem, invalid
│   │   └── products.json            # SauceDemo product names, prices, stub data
│   ├── pages/
│   │   ├── BasePage.ts
│   │   ├── LoginPage.ts
│   │   ├── InventoryPage.ts
│   │   ├── CartPage.ts
│   │   └── CheckoutPage.ts
│   └── support/
│       ├── commands.ts              # Custom commands + TypeScript declarations
│       └── e2e.ts                   # Global import
├── src/
│   └── components/
│       └── ProductCard.tsx          # React component under test
├── utils/
│   └── datadog_reporter.ts          # GAUGE metrics reporter
├── cypress.config.ts
├── package.json
└── tsconfig.json
```

---

## Quick start

**Prerequisites:** [Node.js 20 LTS](https://nodejs.org)

```bash
cd cypress
npm install

# All E2E tests (headless Chrome)
npm test

# Smoke tests only
npm run test:smoke

# Regression suite
npm run test:regression

# Firefox
npm run test:firefox

# Component tests (React ProductCard)
npm run test:component

# Interactive mode (Cypress Test Runner)
npm run test:headed
```

Or from the repo root:

```bash
make cypress-test    # headless CI run
make cypress-open    # interactive runner
```

---

## Test inventory

### E2E (`cypress/e2e/`)

| File | Tests | Tags |
|---|---|---|
| `login.cy.ts` | 7 | `@smoke` `@regression` |
| `inventory.cy.ts` | 7 | `@smoke` `@regression` |
| `checkout.cy.ts` | 5 | `@regression` |
| `network.cy.ts` | 13 | `@regression` |
| `accessibility.cy.ts` | 7 | `@smoke` `@regression` `@known-defect` |
| `performance.cy.ts` | 4 | `@regression` (Chrome only) |

### Component (`cypress/component/`)

| File | Tests |
|---|---|
| `ProductCard.cy.tsx` | 4 |

**Total: 43 E2E + 4 component = 47 tests**

---

## cy.intercept() patterns (network.cy.ts)

```typescript
// 1. Spy — assert a real request was made
cy.intercept('GET', '/').as('homePage');
cy.wait('@homePage').its('response.statusCode').should('eq', 200);

// 2. Stub — replace the response body
cy.intercept('GET', '/inventory.html', (req) => {
  req.reply((res) => { res.body = res.body.replace('Swag Labs', 'Stubbed!'); });
}).as('stubbedPage');

// 3. Simulate failure — force a 500
cy.intercept('GET', '/inventory.html', { statusCode: 500, body: '...' });
```

---

## Custom commands

```typescript
// Typed in cypress/support/commands.ts
cy.login('standard_user', 'secret_sauce');
cy.addToCart('Sauce Labs Backpack');
cy.clearCart();
```

---

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `BASE_URL` | `https://www.saucedemo.com` | Cypress `baseUrl` |
| `DD_API_KEY` | — | DataDog metrics (skipped when absent) |
| `DD_SITE` | `datadoghq.com` | DataDog regional endpoint |
| `ANTHROPIC_API_KEY` | — | AI test generator (required for `npm run ai:generate`) |
| `MODEL` | `claude-sonnet-4-20250514` | AI model override for test generation |

Copy `.env.example` → `.env` and fill in values (never committed).

---

## DataDog observability

After every run the `after:run` hook fires `sendTestMetrics()`, posting:

| Metric | Tag |
|---|---|
| `test.suite.passed` | `framework:cypress` |
| `test.suite.failed` | `framework:cypress` |
| `test.suite.skipped` | `framework:cypress` |
| `test.suite.duration_ms` | `framework:cypress` |

JUnit XML files in `test-results/` are uploaded to DataDog CI Visibility by the CI workflow.

---

## CI design decisions

These are adaptations to the constraints of testing against an external demo
site, not patterns you would follow in a real production suite where you
control the environment.

### Root cause: saucedemo.com rate limiting

saucedemo.com is a free, unsupported demo site with no SLA. In CI its CDN
throttles repeated asset downloads from the same runner IP. After the first
page load, subsequent `cy.visit('/')` calls cause JS bundle requests to hang
indefinitely. The browser never fires the `load` event and Cypress times out.

This would never happen against a real SUT running on a local dev server or a
dedicated staging environment.

### Fix applied to most specs: `testIsolation: false`

By default (`testIsolation: true`) Cypress clears browser state, including
the in-memory asset cache, between each test. This forces every test to
re-download all JS bundles from the CDN, hitting the rate limit.

Setting `testIsolation: false` preserves the browser cache across tests within
a spec. After the first `cy.visit('/')` warms the cache, subsequent page loads
return HTTP 304 responses from the local cache instantly, and the `load` event
fires in milliseconds. Most specs adopt this pattern with a single `cy.visit()`
in a `before` hook and SPA navigation (form interactions, button clicks) for
subsequent tests.

Side effects of `testIsolation: false`:
- Tests are order-dependent within a spec (intentional — they model a user journey)
- `retries` is set to `0` per spec to prevent a failed mid-journey test from
  retrying with inconsistent browser state

### Known failure: `performance.cy.ts` in CI

The Lighthouse tests fail in CI with a "multiple tabs open to the same origin"
error. This is an irreconcilable conflict between two constraints:

- **saucedemo.com requires `testIsolation: false`** to preserve the browser
  cache. With `testIsolation: true`, Cypress resets Chrome's connection state
  between tests, causing saucedemo.com's CDN to hang every `cy.visit('/')`
  indefinitely, even the very first request of the entire run.

- **Lighthouse requires `testIsolation: true`** (or at least a single top-level
  Chrome target). When `testIsolation: false` is active, Cypress opens the AUT
  as its own top-level Chrome target, giving Lighthouse two page-type targets
  at `saucedemo.com` origin, which it refuses to run against.

These two requirements cannot be satisfied simultaneously when testing against
an external site we do not control. Against a local dev server or dedicated
staging environment, standard in any real QA setup, both would be satisfied
and the Lighthouse tests would pass without modification.
