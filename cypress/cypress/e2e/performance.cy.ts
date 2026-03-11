/**
 * Performance Audits — Lighthouse
 *
 * Uses @cypress-audit/lighthouse to run Google Lighthouse against key pages
 * and assert scores meet defined budgets.
 *
 * IMPORTANT: Lighthouse requires Chrome (DevTools Protocol).
 * These tests are automatically skipped when running in Firefox or Edge.
 *
 * Thresholds are set conservatively for SauceDemo — a demo app not optimised
 * for production performance. Raise them when testing a real production SUT.
 *
 * ── Known CI limitation ────────────────────────────────────────────────────
 * These tests fail in CI with a "multiple tabs open to the same origin" error.
 * This is an irreconcilable conflict between two constraints imposed by the
 * external demo site:
 *
 *   1. saucedemo.com's CDN rate-limits repeated asset downloads in CI, which
 *      requires testIsolation: false to preserve the browser cache across tests.
 *
 *   2. Lighthouse uses Chrome DevTools Protocol and throws if it detects more
 *      than one top-level Chrome target at the same origin. testIsolation: false
 *      causes Cypress to open the AUT as a separate top-level target, which
 *      triggers this check.
 *
 * These requirements cannot be satisfied simultaneously against an external
 * site we do not control. Against a local dev server or staging environment
 * (standard in production QA), both would be satisfied and these tests would
 * pass. See the README CI design decisions section for full context.
 */

const BUDGETS = {
  performance:      50,
  accessibility:    60,
  'best-practices': 75,
  seo:              60,
};

describe('Performance Audits — Lighthouse', { testIsolation: false, retries: 0 }, () => {
  before(function () {
    // Lighthouse relies on Chrome DevTools Protocol — skip on other browsers.
    if (Cypress.browser.name !== 'chrome' && Cypress.browser.name !== 'chromium') {
      this.skip();
    }
    cy.visit('/');
  });

  it('@regression — login page meets performance budget', () => {
    cy.lighthouse(BUDGETS);
  });

  it('@regression — inventory page meets performance budget', () => {
    cy.get('#user-name').type('standard_user');
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.url().should('include', '/inventory.html');
    cy.lighthouse(BUDGETS);
  });

  it('@regression — checkout step 1 meets performance budget', () => {
    cy.addToCart('Sauce Labs Backpack');
    cy.get('.shopping_cart_link').click();
    cy.get('[data-test="checkout"]').click();
    cy.lighthouse(BUDGETS);
  });
});
