import dotenv from 'dotenv';
import path from 'path';
import { defineConfig, devices } from '@playwright/test';

dotenv.config({ path: path.resolve(__dirname, '.env') });

/**
 * Playwright configuration for the TypeScript test suite.
 *
 * Key settings for portfolio / JD demonstration:
 *  - trace: 'retain-on-failure'  → Trace Viewer captures DOM + network on failure
 *  - fullyParallel: true          → Parallel execution across all spec files
 *  - retries: CI ? 2 : 0          → Retry on CI, fail-fast locally
 *  - projects: 3 browsers         → Cross-browser strategy (Chromium, Firefox, WebKit)
 *  - reporter: allure-playwright  → Allure report generation (mirrors C# Allure.NUnit)
 *
 * C# equivalent settings:
 *  - trace        → Context.Tracing.StartAsync / StopAsync in BaseTest.cs
 *  - parallel     → [Parallelizable(ParallelScope.Self)]
 *  - retries      → [Retry] attribute / retry:max in appsettings.json
 *  - cross-browser → grid-firefox.runsettings / grid-webkit.runsettings
 *  - allure       → [AllureNUnit] / [AllureSuite] / [AllureFeature] / [AllureStory]
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env['CI'],          // Block accidental test.only() in CI
  retries: process.env['CI'] ? 2 : 0,       // Retry on CI, fail-fast locally
  workers: process.env['CI'] ? 4 : undefined,
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
    ['allure-playwright', {
      resultsDir: 'allure-results',
      detail: true,
      suiteTitle: true,
    }],
  ],

  use: {
    baseURL: process.env['BASE_URL'] ?? 'https://www.saucedemo.com',
    testIdAttribute: 'data-test',            // SauceDemo uses data-test, not data-testid
    trace: 'retain-on-failure',              // ← Trace Viewer: saves on failure only
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10_000,
    navigationTimeout: 30_000,
  },

  projects: [
    /**
     * Auth setup project — runs once before all browser projects.
     *
     * Logs in as standard_user, saves cookies/localStorage to a JSON file.
     * Browser projects depend on this and reuse the saved state, so tests
     * start authenticated without per-test UI login.
     *
     * Why: Login-per-test adds seconds × hundreds of tests = minutes of CI.
     * For MFA-protected apps (e.g. Juniper Square), it's the difference
     * between one auth ceremony and hundreds.
     */
    {
      name: 'setup',
      testMatch: /auth\.setup\.ts/,
    },

    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'test-results/.auth/user.json',
      },
      dependencies: ['setup'],
      testIgnore: ['**/shopify/**'],
    },
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        storageState: 'test-results/.auth/user.json',
      },
      dependencies: ['setup'],
      testIgnore: ['**/shopify/**'],
    },
    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
        storageState: 'test-results/.auth/user.json',
      },
      dependencies: ['setup'],
      testIgnore: ['**/shopify/**'],
    },

    /**
     * API project — GraphQL and REST API tests that do not require a browser.
     *
     * Runs graphql.spec.ts tests using Playwright's APIRequestContext (the `request`
     * fixture) without launching a browser process. This is faster and appropriate
     * for pure data layer tests. Tests that also use `page` (mock interception,
     * operation auditing) still run correctly — Playwright spins up a browser
     * only for those test functions.
     *
     * Target endpoint is controlled by GRAPHQL_URL env var:
     *   Default: https://countries.trevorblades.com/ (public demo)
     *   Production: https://api.instinct.vet/graphql (or equivalent)
     */
    {
      name: 'api',
      use: {
        baseURL: process.env['GRAPHQL_URL'] ?? 'https://countries.trevorblades.com/',
        extraHTTPHeaders: {
          'Accept': 'application/json',
          ...(process.env['API_TOKEN'] && {
            'Authorization': `Bearer ${process.env['API_TOKEN']}`,
          }),
        },
      },
      testMatch: ['**/graphql.spec.ts'],
    },

    /**
     * Shopify project — E2E tests against a live Shopify storefront.
     *
     * Requires SHOPIFY_STORE_URL env var (e.g. https://my-store.myshopify.com).
     * Tests skip gracefully when the URL is not set.
     */
    {
      name: 'shopify',
      use: {
        baseURL: process.env['SHOPIFY_STORE_URL'] ?? 'https://shopify.com',
        ...devices['Desktop Chrome'],
        actionTimeout: 15_000,
        navigationTimeout: 45_000,
      },
      testMatch: ['**/shopify/**'],
    },
  ],

  /** Visual comparison settings for toHaveScreenshot(). */
  expect: {
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.01,
      threshold: 0.2,
    },
  },
});
