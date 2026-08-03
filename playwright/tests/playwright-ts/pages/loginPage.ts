import { Page, Locator } from '@playwright/test';
import { BasePage } from './basePage';

/**
 * LoginPage — wraps SauceDemo login form interactions.
 *
 * Locator strategy:
 *   - Username/Password: getByPlaceholder — user-visible, survives ID changes
 *   - Login button: getByRole('button') — tests the accessibility tree
 *   - Error message: getByTestId — data-test='error' is a stable contract
 *
 * C# equivalent: LoginPage.cs (uses CSS IDs to mirror the C# binding's
 * locator API; this TS version uses Playwright's recommended semantic locators).
 */
export class LoginPage extends BasePage {
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    super(page);
    this.usernameInput = page.getByPlaceholder('Username');
    this.passwordInput = page.getByPlaceholder('Password');
    this.loginButton = page.getByRole('button', { name: /login/i });
    this.errorMessage = page.getByTestId('error');
  }

  async loginAs(username: string, password: string): Promise<void> {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async getErrorMessage(): Promise<string> {
    return await this.errorMessage.innerText();
  }

  async isErrorDisplayed(): Promise<boolean> {
    return await this.errorMessage.isVisible();
  }

  async isLoginButtonVisible(): Promise<boolean> {
    return await this.loginButton.isVisible();
  }
}
