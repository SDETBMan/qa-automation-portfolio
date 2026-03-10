/**
 * Accessibility Audits — WCAG 2.1 AA
 *
 * Uses cypress-axe (axe-core) to assert no critical or serious violations
 * exist on each major page of the application.
 *
 * Scope: wcag2a + wcag2aa rules, critical and serious impact only.
 * Minor/moderate issues are intentionally excluded — the goal is to catch
 * blockers (keyboard traps, missing labels, broken ARIA) not cosmetic issues.
 */

const A11Y_OPTIONS: Parameters<typeof cy.checkA11y>[1] = {
  runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] },
  includedImpacts: ['critical', 'serious'],
};

describe('Accessibility Audits', () => {
  it('@smoke — login page has no critical a11y violations', () => {
    cy.visit('/');
    cy.injectAxe();
    cy.checkA11y(undefined, A11Y_OPTIONS);
  });

  it('@regression — inventory page has no critical a11y violations', () => {
    cy.login('standard_user', 'secret_sauce');
    cy.injectAxe();
    cy.checkA11y(undefined, A11Y_OPTIONS);
  });

  it('@regression — cart page has no critical a11y violations', () => {
    cy.login('standard_user', 'secret_sauce');
    cy.addToCart('Sauce Labs Backpack');
    cy.get('.shopping_cart_link').click();
    cy.injectAxe();
    cy.checkA11y(undefined, A11Y_OPTIONS);
  });

  it('@regression — checkout step 1 has no critical a11y violations', () => {
    cy.login('standard_user', 'secret_sauce');
    cy.addToCart('Sauce Labs Backpack');
    cy.get('.shopping_cart_link').click();
    cy.get('[data-test="checkout"]').click();
    cy.injectAxe();
    cy.checkA11y(undefined, A11Y_OPTIONS);
  });
});
