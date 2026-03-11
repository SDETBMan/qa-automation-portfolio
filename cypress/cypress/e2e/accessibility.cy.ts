/**
 * Accessibility Audits — WCAG 2.1 AA
 *
 * Uses cypress-axe (axe-core) to assert no critical or serious violations
 * exist on each major page of the application.
 *
 * Scope: wcag2a + wcag2aa rules, critical and serious impact only.
 * Minor/moderate issues are intentionally excluded — the goal is to catch
 * blockers (keyboard traps, missing labels, broken ARIA) not cosmetic issues.
 *
 * testIsolation is disabled so all tests share a single browser session and
 * navigate through the login → inventory → cart → checkout journey with only
 * one cy.visit('/') call. Repeated visits to saucedemo.com in CI caused
 * consistent page-load hangs due to rate limiting on the demo site's assets.
 */

const A11Y_OPTIONS: Parameters<typeof cy.checkA11y>[1] = {
  runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] },
  includedImpacts: ['critical', 'serious'],
};

// The inventory page sort <select> has no accessible label (axe rule: select-name).
// Excluded from the main audit and documented as a known saucedemo.com defect below.
const INVENTORY_A11Y_OPTIONS: Parameters<typeof cy.checkA11y>[1] = {
  ...A11Y_OPTIONS,
  rules: { 'select-name': { enabled: false } },
};

describe('Accessibility Audits', { testIsolation: false, retries: 0 }, () => {
  before(() => {
    cy.visit('/');
  });

  it('@smoke — login page has no critical a11y violations', () => {
    cy.injectAxe();
    cy.checkA11y(undefined, A11Y_OPTIONS);
  });

  it('@regression — inventory page has no critical a11y violations', () => {
    cy.get('#user-name').type('standard_user');
    cy.get('#password').type('secret_sauce');
    cy.get('#login-button').click();
    cy.url().should('include', '/inventory.html');
    cy.injectAxe();
    cy.checkA11y(undefined, INVENTORY_A11Y_OPTIONS);
  });

  it('@known-defect — inventory sort dropdown is missing an accessible label', () => {
    // saucedemo.com defect: the product sort <select> has no associated <label>
    // or aria-label, making it unidentifiable to screen readers (axe: select-name).
    // Passes when the violation is present, confirming the defect is still tracked.
    cy.checkA11y(
      undefined,
      { runOnly: { type: 'rule', values: ['select-name'] } },
      (violations) => {
        expect(violations).to.have.length(1);
        expect(violations[0].id).to.equal('select-name');
      },
      true,
    );
  });

  it('@regression — cart page has no critical a11y violations', () => {
    cy.addToCart('Sauce Labs Backpack');
    cy.get('.shopping_cart_link').click();
    cy.injectAxe();
    cy.checkA11y(undefined, A11Y_OPTIONS);
  });

  it('@regression — checkout step 1 has no critical a11y violations', () => {
    cy.get('[data-test="checkout"]').click();
    cy.injectAxe();
    cy.checkA11y(undefined, A11Y_OPTIONS);
  });
});
