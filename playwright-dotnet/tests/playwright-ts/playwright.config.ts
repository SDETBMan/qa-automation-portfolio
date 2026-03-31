import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for the TypeScript test suite.
 *
 * Key settings for portfolio / JD demonstration:
 *  - trace: 'retain-on-failure'  → Trace Viewer captures DOM + network on failure
 *  - fullyParallel: true          → Parallel execution across all spec files
 *  - retries: CI ? 2 : 0          → Retry on CI, fail-fast locally
 *  - projects: 3 browsers         → Cross-browser strategy (Chromium, Firefox, WebKit)
 *
 * C# equivalent settings:
 *  - trace        → Context.Tracing.StartAsync / StopAsync in BaseTest.cs
 *  - parallel     → [Parallelizable(ParallelScope.Self)]
 *  - retries      → [Retry] attribute / retry:max in appsettings.json
 *  - cross-browser → grid-firefox.runsettings / grid-webkit.runsettings
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env['CI'],          // Block accidental test.only() in CI
  retries: process.env['CI'] ? 2 : 0,       // Retry on CI, fail-fast locally
  workers: process.env['CI'] ? 4 : undefined,
  reporter: [['html', { open: 'never' }], ['list']],

  use: {
    baseURL: process.env['BASE_URL'] ?? 'https://www.saucedemo.com',
    trace: 'retain-on-failure',             // ← Trace Viewer: saves on failure only
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10_000,
    navigationTimeout: 30_000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
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
  ],
});
