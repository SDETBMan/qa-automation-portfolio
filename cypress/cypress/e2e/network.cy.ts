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
 *   Vite's immutable-hashed ES module bundles are aggressively cached by Chrome
 *   in both disk AND memory cache. Disk cache is disabled at browser launch via
 *   --disk-cache-size=1 (cypress.config.ts). Memory cache, however, persists
 *   for the lifetime of a browser tab — once a JS bundle is loaded, Chrome
 *   serves it from memory without any network request, making cy.intercept()
 *   invisible to it. For this reason:
 *
 *   - Tests that spy on/modify JS bundles use testIsolation: true so each
 *     test gets a fresh browser context with an empty memory cache.
 *   - Tests that spy on HTML or product images (which are always fetched fresh
 *     during login/navigation) use testIsolation: false for shared state.
 */

// ── Tests that rely on shared session state ─────────────────────────────────
// HTML page load and image stubbing don't hit the memory cache problem because
// cy.visit() always fetches HTML, and product images load fresh after login.
describe('Network — cy.intercept() showcase (shared session)', { testIsolation: false, retries: 0 }, () => {

  // ── @regression: spy on initial HTML request ───────────────────────────────

  it('@regression spies on initial page request and asserts 200', () => {
    cy.intercept('GET', '/').as('homePage');
    cy.visit('/');
    cy.wait('@homePage').then((interception) => {
      expect(interception.response?.statusCode).to.eq(200);
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

    // Fill the login form — we are already on the login page from the
    // previous test's cy.visit('/').
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
});

// ── Tests that require fresh browser context ────────────────────────────────
// JS bundle intercepts require testIsolation: true. Chrome's memory cache
// serves previously loaded JS bundles without any network request, so
// cy.intercept('**/*.js') never fires in a shared session. Each test here
// gets a fresh tab with an empty memory cache.
describe('Network — cy.intercept() showcase (JS bundles)', { retries: 0 }, () => {

  // Clear Chrome's HTTP cache (disk + memory) via CDP before each test.
  // cy.wrap() ensures the CDP promise resolves before the test proceeds.
  beforeEach(() => {
    cy.wrap(
      Cypress.automation('remote:debugger:protocol', {
        command: 'Network.clearBrowserCache',
        params: {},
      }),
      { log: false },
    );
    cy.wrap(
      Cypress.automation('remote:debugger:protocol', {
        command: 'Network.setCacheDisabled',
        params: { cacheDisabled: true },
      }),
      { log: false },
    );
  });

  // ── @regression: spy on JavaScript bundle requests ────────────────────────

  it('@regression spies on JavaScript bundle requests during page load', () => {
    cy.intercept('GET', '**/*.js').as('jsBundle');
    cy.visit('/');
    cy.wait('@jsBundle', { timeout: 10000 }).then((interception) => {
      expect(interception.response?.statusCode).to.be.oneOf([200, 304]);
    });
  });

  // ── @regression: modify response headers via cy.intercept() ─────────────

  it('@regression modifies a JS bundle response to inject a custom header', () => {
    cy.intercept('GET', '**/*.js', (req) => {
      req.reply((res) => {
        res.headers['x-cypress-intercepted'] = 'true';
      });
    }).as('jsWithHeader');

    cy.visit('/');

    cy.wait('@jsWithHeader', { timeout: 10000 }).then((interception) => {
      expect(interception.response?.statusCode).to.be.oneOf([200, 304]);
      expect(interception.response?.headers?.['x-cypress-intercepted']).to.eq(
        'true',
      );
    });
  });
});
