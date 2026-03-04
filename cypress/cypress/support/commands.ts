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
  // cy.session() caches the authenticated browser state (cookies + localStorage)
  // after the first login. Subsequent calls restore that state without hitting
  // the login page again — avoiding CI rate-limiting from saucedemo.com.
  cy.session(
    [username, password],
    () => {
      cy.visit('/');
      cy.get('#user-name').type(username);
      cy.get('#password').type(password);
      cy.get('#login-button').click();
      cy.url().should('include', '/inventory.html');
    },
  );
  // After session setup or restore, visit '/'. SauceDemo's React app reads
  // the restored localStorage auth state and client-side navigates to
  // /inventory.html automatically. Visiting '/inventory.html' directly
  // returns 404 — the server only knows '/'.
  cy.visit('/');
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
  cy.visit('/inventory.html');
});
