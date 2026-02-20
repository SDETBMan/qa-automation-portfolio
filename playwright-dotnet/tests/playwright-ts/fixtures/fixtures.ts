import { test as base, expect } from '@playwright/test';
import { LoginPage } from '../pages/loginPage';
import { InventoryPage } from '../pages/inventoryPage';
import { CartPage } from '../pages/cartPage';

/**
 * Custom fixture types for the app under test.
 *
 * Fixture pattern explained:
 * ─────────────────────────────────────────────────────────────────────────────
 * Each fixture is a function: async ({ page }, use) => { ... }
 *
 *  1. Code BEFORE  `await use(value)` = SETUP   (runs before the test body)
 *  2. `await use(value)`              = YIELD    (test body receives `value`)
 *  3. Code AFTER   `await use(value)` = TEARDOWN (runs after the test body)
 *
 * Playwright disposes the `page` automatically — no explicit cleanup needed
 * in most fixtures. The `authenticatedPage` fixture demonstrates setup + yield
 * with an implicit teardown handled by the framework.
 *
 * C# equivalent comparison:
 * ─────────────────────────────────────────────────────────────────────────────
 * | Concept    | TypeScript                          | C#                          |
 * |------------|-------------------------------------|-----------------------------|
 * | Fixture    | test.extend<AppFixtures>            | AuthenticatedTest : BaseTest |
 * | Setup      | code before await use(...)          | [SetUp] LoginBeforeEach()   |
 * | Teardown   | code after await use(...)           | [TearDown] OnTearDown()     |
 * | Guard      | await page.waitForURL(/inventory/)  | Assert.That(Page.Url, ...)  |
 * | Page obj   | new InventoryPage(page)             | new InventoryPage(Page)     |
 */
type AppFixtures = {
  /** Login page object; browser is at baseURL (login screen). */
  loginPage: LoginPage;

  /** Inventory page object; browser is at baseURL. Tests must navigate/login themselves. */
  inventoryPage: InventoryPage;

  /** Cart page object; browser is at baseURL. Tests must navigate themselves. */
  cartPage: CartPage;

  /**
   * Pre-authenticated InventoryPage.
   * SETUP:    navigates to /, logs in as standard_user, waits for inventory.html
   * YIELD:    delivers InventoryPage to the test
   * TEARDOWN: Playwright disposes the page automatically
   *
   * Tests using this fixture begin already on inventory.html — zero login boilerplate.
   */
  authenticatedPage: InventoryPage;
};

export const test = base.extend<AppFixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  inventoryPage: async ({ page }, use) => {
    await use(new InventoryPage(page));
  },

  cartPage: async ({ page }, use) => {
    await use(new CartPage(page));
  },

  authenticatedPage: async ({ page }, use) => {
    // ── SETUP ────────────────────────────────────────────────────────────────
    await page.goto('/');
    await new LoginPage(page).loginAs(
      process.env['APP_USERNAME'] ?? 'standard_user',
      process.env['APP_PASSWORD'] ?? 'secret_sauce',
    );
    // Fixture guard: fail fast if login did not land on inventory.
    await page.waitForURL(/inventory/, { timeout: 10_000 });

    // ── YIELD — test body executes here ──────────────────────────────────────
    await use(new InventoryPage(page));

    // ── TEARDOWN — Playwright auto-disposes the page; nothing to clean up ────
  },
});

export { expect };
