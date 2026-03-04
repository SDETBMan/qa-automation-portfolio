/**
 * network.cy.ts — cy.intercept() showcase
 *
 * Demonstrates the three most common cy.intercept() patterns:
 *   1. Spy on real network traffic
 *   2. Stub a response with custom data
 *   3. Simulate an API failure / error state
 *
 * SauceDemo is a static site rendered server-side, so there are no
 * XHR/fetch calls during normal navigation. We therefore intercept
 * the HTML page load itself (route aliasing) and the login POST.
 */

describe('Network — cy.intercept() showcase', () => {
  // ── @regression: spy on page load ─────────────────────────────────────────

  it('@regression spies on document request during page load', () => {
    cy.intercept('GET', '/').as('homePage');
    cy.visit('/');
    cy.wait('@homePage').then((interception) => {
      expect(interception.response?.statusCode).to.eq(200);
    });
  });

  // ── @regression: stub inventory HTML to inject custom content ─────────────

  it('@regression stubs inventory page to inject custom product heading', () => {
    cy.intercept('GET', '/inventory.html', (req) => {
      req.reply((res) => {
        // Replace the page title in the HTML body to prove the stub ran
        res.body = (res.body as string).replace(
          'Swag Labs',
          'Cypress Stub — Swag Labs',
        );
      });
    }).as('stubbedInventory');

    cy.fixture('users').then((users) => {
      cy.visit('/');
      cy.get('#user-name').type(users.standard.username);
      cy.get('#password').type(users.standard.password);
      cy.get('#login-button').click();
    });

    cy.wait('@stubbedInventory');
    cy.title().should('contain', 'Cypress Stub — Swag Labs');
  });

  // ── @regression: intercept login POST and assert request body ─────────────

  it('@regression intercepts login form POST and asserts request', () => {
    cy.intercept('POST', '/').as('loginPost');

    cy.fixture('users').then((users) => {
      cy.visit('/');
      cy.get('#user-name').type(users.standard.username);
      cy.get('#password').type(users.standard.password);
      cy.get('#login-button').click();
    });

    // SauceDemo submits as form-encoded POST; wait and inspect
    cy.wait('@loginPost').then((interception) => {
      // The form body is URL-encoded; confirm it contains the username field
      const body = interception.request.body as string;
      expect(body).to.include('user-name');
    });
  });

  // ── @regression: simulate API failure → graceful error handling ───────────

  it('@regression simulates 500 error on inventory page and stays on app', () => {
    cy.intercept('GET', '/inventory.html', {
      statusCode: 500,
      body: '<html><body><h1>Internal Server Error</h1></body></html>',
    }).as('inventoryError');

    cy.fixture('users').then((users) => {
      cy.visit('/');
      cy.get('#user-name').type(users.standard.username);
      cy.get('#password').type(users.standard.password);
      cy.get('#login-button').click();
    });

    cy.wait('@inventoryError').then((interception) => {
      expect(interception.response?.statusCode).to.eq(500);
    });

    // App is still in a rendered state (not a hard crash) — body exists
    cy.get('body').should('exist');
  });
});
