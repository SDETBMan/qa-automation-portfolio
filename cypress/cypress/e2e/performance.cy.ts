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
 */

const BUDGETS = {
  performance:     50,
  accessibility:   60,
  'best-practices': 75,
  seo:             60,
};

describe('Performance Audits — Lighthouse', () => {
  before(function () {
    // Lighthouse relies on Chrome DevTools Protocol — skip on other browsers
    if (Cypress.browser.name !== 'chrome' && Cypress.browser.name !== 'chromium') {
      this.skip();
    }
  });

  it('@regression — login page meets performance budget', () => {
    cy.visit('/');
    cy.lighthouse(BUDGETS);
  });

  it('@regression — inventory page meets performance budget', () => {
    cy.login('standard_user', 'secret_sauce');
    cy.lighthouse(BUDGETS);
  });

  it('@regression — checkout step 1 meets performance budget', () => {
    cy.login('standard_user', 'secret_sauce');
    cy.addToCart('Sauce Labs Backpack');
    cy.get('.shopping_cart_link').click();
    cy.get('[data-test="checkout"]').click();
    cy.lighthouse(BUDGETS);
  });
});
