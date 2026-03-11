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
 * testIsolation is disabled so tests 2 and 3 can navigate via form interactions
 * rather than cy.visit('/'), keeping the total page load count to one and
 * avoiding saucedemo.com rate limiting in CI.
 *
 * cy.visit('/') stays in the test 1 body rather than a before hook — Lighthouse
 * uses Chrome DevTools Protocol and throws "multiple tabs" if it detects an
 * active CDP session to the same origin before the test starts.
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
  });

  it('@regression — login page meets performance budget', () => {
    cy.visit('/');
    cy.lighthouse(BUDGETS);
  });

  it('@regression — inventory page meets performance budget', () => {
    // Browser is still on the login page (testIsolation: false).
    // Log in via form — no cy.visit() needed.
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
