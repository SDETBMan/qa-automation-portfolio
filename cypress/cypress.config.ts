import { defineConfig } from 'cypress';
import { sendTestMetrics } from './utils/datadog_reporter';

export default defineConfig({
  e2e: {
    baseUrl: process.env['BASE_URL'] ?? 'https://www.saucedemo.com',
    specPattern: 'cypress/e2e/**/*.cy.ts',
    supportFile: 'cypress/support/e2e.ts',
    video: true,
    screenshotOnRunFailure: true,
    retries: { runMode: 2, openMode: 0 },
    reporter: 'mocha-junit-reporter',
    reporterOptions: {
      mochaFile: 'test-results/cypress-[hash].xml',
      toConsole: true,
    },
    setupNodeEvents(on) {
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
    },
  },

  component: {
    devServer: { framework: 'react', bundler: 'vite' },
    specPattern: 'cypress/component/**/*.cy.tsx',
    supportFile: false,
  },
});
