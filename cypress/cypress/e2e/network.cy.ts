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
 *
 * testIsolation is disabled so all tests share a single browser session.
 * Test 1 performs the only cold page load, priming the browser cache.
 * Subsequent tests use cy.reload() or SPA form navigation so JS bundles are
 * served from cache (HTTP 304), avoiding saucedemo.com rate limiting in CI.
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
    // cy.reload() reuses the warm browser cache — JS assets return 304
    // immediately so the load event fires without hitting the CDN again.
    cy.reload();
    cy.wait('@jsBundle').then((interception) => {
      expect(interception.response?.statusCode).to.be.oneOf([200, 304]);
    });
  });

  // ── @regression: stub product images with 404 ─────────────────────────────

  it('@regression stubs product images on inventory page with 404', () => {
    // Set up stub BEFORE login so it fires when inventory renders images.
    cy.intercept('GET', '**/static/media/**', {
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

    // Navigate back to / from inventory — warm cache means JS bundles return
    // 304 instantly and the load event fires without stalling on the CDN.
    cy.visit('/');

    cy.wait('@jsWithHeader').then((interception) => {
      expect(interception.response?.statusCode).to.be.oneOf([200, 304]);
      expect(interception.response?.headers?.['x-cypress-intercepted']).to.eq(
        'true',
      );
    });
  });
});
