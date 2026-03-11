import { defineConfig } from 'cypress';
import allureWriter from '@shelex/cypress-allure-plugin/writer';
import { lighthouse, prepareAudit } from '@cypress-audit/lighthouse';
import { sendTestMetrics } from './utils/datadog_reporter';

export default defineConfig({
  e2e: {
    baseUrl: process.env['BASE_URL'] ?? 'https://www.saucedemo.com',
    // performance.cy.ts runs first — Lighthouse requires testIsolation: true,
    // which means it cannot share the warm browser cache that other specs rely
    // on. Running it first ensures the CDN is fresh and cy.visit('/') succeeds
    // before the other specs have a chance to trigger saucedemo.com rate limiting.
    specPattern: [
      'cypress/e2e/performance.cy.ts',
      'cypress/e2e/accessibility.cy.ts',
      'cypress/e2e/checkout.cy.ts',
      'cypress/e2e/inventory.cy.ts',
      'cypress/e2e/login.cy.ts',
      'cypress/e2e/network.cy.ts',
    ],
    supportFile: 'cypress/support/e2e.ts',
    video: true,
    screenshotOnRunFailure: true,
    pageLoadTimeout: 120000,
    retries: { runMode: 2, openMode: 0 },
    reporter: 'mocha-junit-reporter',
    reporterOptions: {
      mochaFile: 'test-results/cypress-[hash].xml',
      toConsole: true,
    },

    setupNodeEvents(on, config) {
      // ── Task merge helper ───────────────────────────────────────────────────
      // Cypress honours only the LAST on('task', ...) registration.
      // Intercept every task registration, collect them all, then flush once
      // so Allure and Lighthouse tasks coexist without overriding each other.
      const tasks: Record<string, (...args: unknown[]) => unknown> = {
        lighthouse: lighthouse(), // Lighthouse performance audits (Chrome only)
      };

      const collectingOn: Cypress.PluginEvents = ((
        event: string,
        ...args: unknown[]
      ) => {
        if (event === 'task') {
          Object.assign(tasks, args[0] as Record<string, unknown>);
        } else {
          (on as (...a: unknown[]) => void)(event, ...args);
        }
      }) as Cypress.PluginEvents;

      // ── Allure CI reporting ─────────────────────────────────────────────────
      allureWriter(collectingOn, config);

      // Register the merged task map once
      on('task', tasks);

      // ── Lighthouse — prime Chrome with the DevTools flags the audit needs ───
      on('before:browser:launch', (_browser, launchOptions) => {
        prepareAudit(launchOptions);
        return launchOptions;
      });

      // ── DataDog custom metrics ──────────────────────────────────────────────
      on('after:run', async (results) => {
        if (results && 'totalPassed' in results) {
          await sendTestMetrics(
            results.totalPassed,
            results.totalFailed,
            results.totalPending,
            results.totalDuration,
            'cypress',
          );
        }
      });

      return config;
    },
  },

  component: {
    devServer: { framework: 'react', bundler: 'vite' },
    specPattern: 'cypress/component/**/*.cy.tsx',
    supportFile: false,
  },
});
