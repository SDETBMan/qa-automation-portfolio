/**
 * network.cy.ts — cy.intercept() showcase
 *
 * SauceDemo is a React SPA built with Vite. All post-login navigation (e.g.,
 * to /inventory.html) is handled client-side by React Router — the browser
 * never issues a new HTTP GET for those URLs. Likewise, the login form is
 * handled by JavaScript, not an HTML form POST. Intercepting those routes
 * will therefore never fire.
 *
 * Real HTTP requests the browser DOES make:
 *   1. GET /                    — initial HTML page
 *   2. GET /assets/index-*.js   — JavaScript bundle (ES module, on page load)
 *   3. GET /assets/*.jpg        — product images (when inventory renders)
 *   4. GET /assets/index-*.js   — JS bundle (response modifier demo)
 *
 * Note: SauceDemo ships a separate CSS file (/assets/index-*.css).
 * These four patterns drive the four cy.intercept() scenarios below.
 *
 * CACHING STRATEGY:
 *   testIsolation is disabled so all tests share a single browser session.
 *   Vite's immutable-hashed ES module bundles are aggressively cached by Chrome
 *   — even cy.reload(true) won't trigger a network request (the forceReload
 *   parameter to location.reload() was deprecated in Chrome 94+).
 *   We disable the HTTP cache via Chrome DevTools Protocol for this suite so
 *   cy.intercept() can observe all network requests reliably.
 */

describe('Network — cy.intercept() showcase', { testIsolation: false, retries: 0 }, () => {
  // Disable HTTP cache via CDP so cy.intercept() can observe Vite's
  // immutable-hashed ES module bundles, which would otherwise be served
  // from disk cache without any network request.
  before(() => {
    Cypress.automation('remote:debugger:protocol', {
      command: 'Network.setCacheDisabled',
      params: { cacheDisabled: true },
    });
  });

  after(() => {
    Cypress.automation('remote:debugger:protocol', {
      command: 'Network.setCacheDisabled',
      params: { cacheDisabled: false },
    });
  });

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
    cy.reload();
    cy.wait('@jsBundle').then((interception) => {
      expect(interception.response?.statusCode).to.be.oneOf([200, 304]);
    });
  });

  // ── @regression: stub product images with 404 ─────────────────────────────

  it('@regression stubs product images on inventory page with 404', () => {
    // Set up stub BEFORE login so it fires when inventory renders images.
    // SauceDemo (Vite) serves product images from /assets/ with content hashes.
    cy.intercept('GET', '/assets/*.jpg', {
      statusCode: 404,
      body: '',
    }).as('blockedImages');

    // Fill the login form directly — no cy.visit() needed since we are already
    // on the login page from the previous test's reload.
    cy.fixture('users').then((users) => {
      cy.get('#user-name').type(users.standard.username);
      cy.get('#password').type(users.standard.password);
      cy.get('#login-button').click();
      cy.url().should('include', '/inventory.html');
    });

    cy.wait('@blockedImages').then((interception) => {
      expect(interception.response?.statusCode).to.eq(404);
    });
  });

  // ── @regression: modify response headers via cy.intercept() ─────────────

  it('@regression modifies a JS bundle response to inject a custom header', () => {
    cy.intercept('GET', '**/*.js', (req) => {
      req.reply((res) => {
        res.headers['x-cypress-intercepted'] = 'true';
      });
    }).as('jsWithHeader');

    // Navigate back to / from inventory — cache is disabled via CDP so
    // JS bundles will be re-fetched on every navigation.
    cy.visit('/');

    cy.wait('@jsWithHeader').then((interception) => {
      expect(interception.response?.statusCode).to.be.oneOf([200, 304]);
      expect(interception.response?.headers?.['x-cypress-intercepted']).to.eq(
        'true',
      );
    });
  });
});
