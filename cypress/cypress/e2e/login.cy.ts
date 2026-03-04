import { LoginPage } from '../pages/LoginPage';

const loginPage = new LoginPage();

/**
 * testIsolation: false — Cypress does NOT clear cookies/localStorage/sessionStorage
 * between tests in this suite. This lets us visit '/' exactly once (in `before`)
 * and share the browser session across all five tests, avoiding repeated
 * cy.visit('/') calls that trigger saucedemo.com rate-limiting in CI.
 *
 * Test order matters:
 *   1–3  Error-state tests: stay on the login page, so no re-navigation needed.
 *   4    Valid login: navigates to /inventory.html.
 *   5    Logout: starts on /inventory.html (from test 4), ends back on login page.
 */
describe('Login', { testIsolation: false }, () => {
  before(() => {
    // Single visit to the login page for the entire suite.
    cy.visit('/');
  });

  beforeEach(() => {
    // If the login form is present, clear any residual text from the previous test.
    cy.get('body').then(($body) => {
      if ($body.find('#user-name').length) {
        cy.get('#user-name').clear();
        cy.get('#password').clear();
      }
    });
  });

  // ── Smoke — error states (stay on login page) ──────────────────────────────

  it('@smoke invalid password shows error message', () => {
    cy.fixture('users').then((users) => {
      loginPage.loginAs(users.standard.username, 'wrong_password');
      loginPage.assertErrorContains('Username and password do not match');
    });
  });

  it('@smoke empty username shows validation error', () => {
    cy.get('#login-button').click();
    loginPage.assertErrorContains('Username is required');
  });

  // ── Regression — error states ───────────────────────────────────────────────

  it('@regression locked-out user sees specific error', () => {
    cy.fixture('users').then((users) => {
      loginPage.loginAs(users.locked.username, users.locked.password);
      loginPage.assertErrorContains('Sorry, this user has been locked out');
    });
  });

  // ── Regression — navigation (must come after the error tests) ───────────────

  it('@regression valid credentials navigate to inventory', () => {
    cy.fixture('users').then((users) => {
      loginPage.loginAs(users.standard.username, users.standard.password);
      cy.url().should('include', '/inventory.html');
      cy.get('.inventory_list').should('be.visible');
    });
  });

  it('@regression logout returns to login page', () => {
    // Starts on /inventory.html — left there by the previous test.
    cy.get('#react-burger-menu-btn').click();
    cy.get('#logout_sidebar_link').click();
    loginPage.assertOnLoginPage();
  });
});
