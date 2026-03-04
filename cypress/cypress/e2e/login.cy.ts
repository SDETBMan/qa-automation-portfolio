import { LoginPage } from '../pages/LoginPage';

const loginPage = new LoginPage();

describe('Login', () => {
  beforeEach(() => {
    loginPage.open();
  });

  // ── Smoke ──────────────────────────────────────────────────────────────────

  it('@smoke valid credentials navigate to inventory', () => {
    cy.fixture('users').then((users) => {
      loginPage.loginAs(users.standard.username, users.standard.password);
      cy.url().should('include', '/inventory.html');
      cy.get('.inventory_list').should('be.visible');
    });
  });

  it('@smoke invalid password shows error message', () => {
    cy.fixture('users').then((users) => {
      loginPage.loginAs(users.standard.username, 'wrong_password');
      loginPage.assertErrorContains('Username and password do not match');
    });
  });

  // ── Regression ─────────────────────────────────────────────────────────────

  it('@regression locked-out user sees specific error', () => {
    cy.fixture('users').then((users) => {
      loginPage.loginAs(users.locked.username, users.locked.password);
      loginPage.assertErrorContains('Sorry, this user has been locked out');
    });
  });

  it('@regression empty username shows validation error', () => {
    cy.get('#login-button').click();
    loginPage.assertErrorContains('Username is required');
  });

  it('@regression logout returns to login page', () => {
    cy.fixture('users').then((users) => {
      loginPage.loginAs(users.standard.username, users.standard.password);
      cy.get('#react-burger-menu-btn').click();
      cy.get('#logout_sidebar_link').click();
      loginPage.assertOnLoginPage();
    });
  });
});
