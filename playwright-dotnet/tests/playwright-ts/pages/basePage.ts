import { Page, Locator } from '@playwright/test';

/**
 * Abstract base class for all page objects.
 *
 * Wraps Playwright locator interactions with auto-wait built in —
 * no explicit waits needed (mirrors C# BasePage.cs approach).
 *
 * Note: `page` is protected. Tests access the raw `page` via the built-in
 * Playwright `page` fixture — no need to expose it publicly here.
 */
export abstract class BasePage {
  protected readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  protected locator(selector: string): Locator {
    return this.page.locator(selector);
  }

  protected async click(selector: string): Promise<void> {
    await this.page.locator(selector).click();
  }

  protected async fill(selector: string, value: string): Promise<void> {
    await this.page.locator(selector).fill(value);
  }

  protected async getText(selector: string): Promise<string> {
    return await this.page.locator(selector).innerText();
  }

  protected async isVisible(selector: string): Promise<boolean> {
    return await this.page.locator(selector).isVisible();
  }
}
