import { Page } from '@playwright/test';
import { BasePage } from './basePage';

/**
 * LoginPage — wraps SauceDemo login form interactions.
 * Selectors mirror C# LoginPage.cs.
 */
export class LoginPage extends BasePage {
  private readonly usernameInput = '#user-name';
  private readonly passwordInput = '#password';
  private readonly loginButton   = '#login-button';
  private readonly errorMessage  = "h3[data-test='error']";

  constructor(page: Page) {
    super(page);
  }

  async loginAs(username: string, password: string): Promise<void> {
    await this.fill(this.usernameInput, username);
    await this.fill(this.passwordInput, password);
    await this.click(this.loginButton);
  }

  async getErrorMessage(): Promise<string> {
    return await this.getText(this.errorMessage);
  }

  async isErrorDisplayed(): Promise<boolean> {
    return await this.isVisible(this.errorMessage);
  }

  async isLoginButtonVisible(): Promise<boolean> {
    return await this.isVisible(this.loginButton);
  }
}
