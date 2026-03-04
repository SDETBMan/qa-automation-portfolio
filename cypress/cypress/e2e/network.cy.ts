/**
 * network.cy.ts — cy.intercept() showcase
 *
 * SauceDemo is a React SPA. All post-login navigation (e.g., to /inventory.html)
 * is handled client-side by React Router — the browser never issues a new HTTP
 * GET for those URLs. Likewise, the login form is handled by JavaScript, not an
 * HTML form POST. Intercepting those routes will therefore never fire.
 *
 * Real HTTP requests the browser DOES make:
 *   1. GET /                    — initial HTML page
 *   2. GET /static/js/...       — JavaScript bundles (on every page load)
 *   3. GET /static/media/...    — product images (when inventory renders)
 *   4. GET /static/js/...       — JS bundles (response modifier demo)
 *
 * Note: SauceDemo uses CSS-in-JS — no .css files are requested over the network.
 * These four patterns drive the four cy.intercept() scenarios below.
 */

describe('Network — cy.intercept() showcase', () => {
  // ── @regression: spy on initial HTML request ───────────────────────────────

  it('@regression spies on initial page request and asserts 200', () => {
    cy.intercept('GET', '/').as('homePage');
    cy.visit('/');
    cy.wait('@homePage').then((interception) => {
      expect(interception.response?.statusCode).to.eq(200);
    });
  });

  // ── @regression: spy on JavaScript bundle requests ────────────────────────

  it('@regression spies on JavaScript bundle requests during page load', () => {
    cy.intercept('GET', '**/*.js').as('jsBundle');
    cy.visit('/');
    // At least one JS chunk must load; status is 200 (or 304 from cache)
    cy.wait('@jsBundle').then((interception) => {
      expect(interception.response?.statusCode).to.be.oneOf([200, 304]);
    });
  });

  // ── @regression: stub product images with 404 ─────────────────────────────

  it('@regression stubs product images on inventory page with 404', () => {
    // Set up stub BEFORE login so it fires when inventory renders images
    cy.intercept('GET', '**/static/media/**', {
      statusCode: 404,
      body: '',
    }).as('blockedImages');

    cy.fixture('users').then((users) => {
      // cy.login() uses cy.session() — only one real login per run.
      // After session restore it navigates to /inventory.html, which
      // triggers the <img> requests that our stub intercepts.
      cy.login(users.standard.username, users.standard.password);
    });

    cy.wait('@blockedImages').then((interception) => {
      expect(interception.response?.statusCode).to.eq(404);
    });
  });

  // ── @regression: modify response headers via cy.intercept() ─────────────

  it('@regression modifies a JS bundle response to inject a custom header', () => {
    // Demonstrates cy.intercept() as a response modifier: intercept the first
    // JS chunk, add a custom header in the reply, then assert it's present.
    // SauceDemo uses CSS-in-JS so no .css files are requested; JS bundles
    // are always fetched on every page load and are the reliable intercept target.
    cy.intercept('GET', '**/*.js', (req) => {
      req.reply((res) => {
        res.headers['x-cypress-intercepted'] = 'true';
      });
    }).as('jsWithHeader');

    cy.visit('/');

    cy.wait('@jsWithHeader').then((interception) => {
      expect(interception.response?.statusCode).to.be.oneOf([200, 304]);
      expect(interception.response?.headers?.['x-cypress-intercepted']).to.eq(
        'true',
      );
    });
  });
});
