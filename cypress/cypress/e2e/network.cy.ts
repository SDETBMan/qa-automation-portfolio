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
 * testIsolation is disabled so all tests share a single browser session.
 * Test 1 performs the only cold page load, priming the browser cache.
 * Subsequent tests use cy.reload(true) (hard reload) to bypass the browser's
 * disk cache for Vite's immutable-hashed ES module bundles, ensuring network
 * requests are always issued for cy.intercept() to observe.
 */

describe('Network — cy.intercept() showcase', { testIsolation: false, retries: 0 }, () => {
  // ── @regression: spy on initial HTML request ───────────────────────────────
  // This is the only cold load in the suite — it also primes the browser cache.

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
    // Hard reload (true) bypasses the disk cache — Vite's immutable-hashed
    // ES modules would otherwise be served from cache without a network request.
    cy.reload(true);
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

    // Navigate back to / from inventory, then hard-reload to force JS
    // re-fetch — Vite's immutable-hashed bundles are cached aggressively.
    cy.visit('/');
    cy.reload(true);

    cy.wait('@jsWithHeader').then((interception) => {
      expect(interception.response?.statusCode).to.be.oneOf([200, 304]);
      expect(interception.response?.headers?.['x-cypress-intercepted']).to.eq(
        'true',
      );
    });
  });
});
