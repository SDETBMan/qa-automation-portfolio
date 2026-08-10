import { BasePage } from './BasePage';

const SELECTORS = {
  username:     '#user-name',
  password:     '#password',
  loginButton:  '#login-button',
  errorMessage: '[data-test="error"]',
} as const;

export class LoginPage extends BasePage {
  open(): void {
    this.visit('/');
  }

  loginAs(username: string, password: string): void {
    this.type(SELECTORS.username, username);
    this.type(SELECTORS.password, password);
    this.click(SELECTORS.loginButton);
  }

  getErrorMessage(): Cypress.Chainable<string> {
    return this.getText(SELECTORS.errorMessage);
  }

  isLoginButtonVisible(): Cypress.Chainable<boolean> {
    return cy.get(SELECTORS.loginButton).should('exist').then($el => $el.is(':visible'));
  }
}
