import { Page } from '@playwright/test';

/**
 * Abstract base class for all page objects.
 *
 * Design principles:
 *   - `page` is protected: child pages use it to build locators, tests access
 *     the raw `page` via Playwright's built-in fixture when needed.
 *   - Locator strategy follows Playwright's recommended priority:
 *       1. getByRole     — tests the accessibility tree; free a11y validation
 *       2. getByLabel / getByPlaceholder / getByText — user-visible semantics
 *       3. getByTestId   — stable contract with developers (requires testIdAttribute config)
 *       4. Scoped CSS    — last resort, always scoped to a parent locator
 *   - No assertions in page objects — pages DO, tests ASSERT.
 *   - Business-verb methods (loginAs, addItemToCart), not click sequences.
 *
 * C# equivalent: BasePage.cs (mirrors protected helper approach with
 * Playwright auto-wait — no explicit waits needed in either binding).
 */
export abstract class BasePage {
  protected readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }
}
