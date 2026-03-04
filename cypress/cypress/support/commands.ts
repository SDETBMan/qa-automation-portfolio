// ─── Custom Cypress Commands ────────────────────────────────────────────────
// Declared globally below so TypeScript recognises cy.login(), etc.

declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Cypress {
    interface Chainable {
      /**
       * Log in with username / password and assert landing on inventory page.
       */
      login(username: string, password: string): Chainable<void>;

      /**
       * Add a product to the cart by its display name.
       */
      addToCart(productName: string): Chainable<void>;

      /**
       * Remove all items currently in the cart and return to the inventory page.
       */
      clearCart(): Chainable<void>;
    }
  }
}

Cypress.Commands.add('login', (username: string, password: string) => {
  // SauceDemo auth is in-memory React state only — cy.session() cannot capture
  // it because nothing meaningful is written to cookies or localStorage.
  // A direct login is the only reliable approach.
  cy.visit('/');
  cy.get('#user-name').type(username);
  cy.get('#password').type(password);
  cy.get('#login-button').click();
  cy.url().should('include', '/inventory.html');
});

Cypress.Commands.add('addToCart', (productName: string) => {
  cy.contains('.inventory_item', productName)
    .find('button[id^="add-to-cart"]')
    .click();
});

Cypress.Commands.add('clearCart', () => {
  cy.get('.shopping_cart_link').click();
  cy.get('body').then(($body) => {
    if ($body.find('.cart_item').length) {
      cy.get('.cart_item').each(($el) => {
        cy.wrap($el).find('button[id^="remove"]').click();
      });
    }
  });
  // SauceDemo's server only serves '/'; '/inventory.html' returns 404.
  // Use the "Continue Shopping" button for client-side navigation back to inventory.
  cy.get('[data-test="continue-shopping"]').click();
});
