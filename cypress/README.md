# cypress — TypeScript E2E + Component Testing

[![cypress CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cypress.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/cypress.yml)

Cypress 13 · TypeScript 5 · React 18 · Vite · Node.js 20

End-to-end tests against [SauceDemo](https://www.saucedemo.com/) plus isolated
React component tests — all in TypeScript.

---

## What's unique here

| Feature | Detail |
|---|---|
| **`cy.intercept()`** | Network spy/stub in `network.cy.ts` — Cypress's most-asked-about interview topic |
| **Component testing** | Mounts `ProductCard` React component in isolation via the Cypress component runner |
| **Custom commands** | `cy.login()`, `cy.addToCart()`, `cy.clearCart()` — typed via `Chainable` declaration |
| **Page Object Model** | Abstract `BasePage` + 4 concrete pages |
| **DataDog GAUGE metrics** | TypeScript port of the Python reporter; posts 4 metrics after every run |
| **JUnit XML** | `mocha-junit-reporter` for DataDog CI Visibility upload |

---

## Structure

```
cypress/
├── cypress/
│   ├── component/
│   │   └── ProductCard.cy.tsx       # React component tests
│   ├── e2e/
│   │   ├── login.cy.ts              # @smoke + @regression
│   │   ├── inventory.cy.ts          # @smoke + @regression
│   │   ├── checkout.cy.ts           # @regression
│   │   └── network.cy.ts            # cy.intercept() — @regression
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
| `login.cy.ts` | 5 | `@smoke` `@regression` |
| `inventory.cy.ts` | 6 | `@smoke` `@regression` |
| `checkout.cy.ts` | 4 | `@regression` |
| `network.cy.ts` | 4 | `@regression` |

### Component (`cypress/component/`)

| File | Tests |
|---|---|
| `ProductCard.cy.tsx` | 4 |

**Total: 19 E2E + 4 component = 23 tests**

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
