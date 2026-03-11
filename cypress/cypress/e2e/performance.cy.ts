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
 * testIsolation: false is intentionally NOT used here. When enabled, Cypress
 * gives the AUT its own top-level Chrome target, causing Lighthouse to detect
 * two page targets at the same origin and throw "multiple tabs open to the
 * same origin." testIsolation: true (default) keeps the AUT in an iframe so
 * Lighthouse only sees one target.
 *
 * To avoid repeated cy.visit('/') calls that trigger saucedemo.com rate
 * limiting in CI, all three page audits run as checkpoints within a single
 * test, using SPA navigation (form interactions and button clicks) rather than
 * additional page loads after the initial cy.visit('/').
 */

const BUDGETS = {
  performance:      50,
  accessibility:    60,
  'best-practices': 75,
  seo:              60,
};

describe('Performance Audits — Lighthouse', () => {
  before(function () {
    // Lighthouse relies on Chrome DevTools Protocol — skip on other browsers.
    if (Cypress.browser.name !== 'chrome' && Cypress.browser.name !== 'chromium') {
      this.skip();
    }
  });

  it('@regression — login, inventory, and checkout pages meet performance budget', () => {
    // ── Login page ──────────────────────────────────────────────────────────
    cy.visit('/');
    cy.lighthouse(BUDGETS);

    // ── Inventory page — SPA navigation, no additional cy.visit() ───────────
    cy.get('#user-name').type('standard_user');
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.url().should('include', '/inventory.html');
    cy.lighthouse(BUDGETS);

    // ── Checkout step 1 — SPA navigation, no additional cy.visit() ──────────
    cy.addToCart('Sauce Labs Backpack');
    cy.get('.shopping_cart_link').click();
    cy.get('[data-test="checkout"]').click();
    cy.lighthouse(BUDGETS);
  });
});
