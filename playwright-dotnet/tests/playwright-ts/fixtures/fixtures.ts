import { test as base, expect } from '@playwright/test';
import { LoginPage } from '../pages/loginPage';
import { InventoryPage } from '../pages/inventoryPage';
import { CartPage } from '../pages/cartPage';
import { GraphQLClient } from '../utils/graphqlClient';

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

  /**
   * Pre-configured GraphQLClient backed by Playwright's APIRequestContext.
   *
   * SETUP:    reads GRAPHQL_URL and API_TOKEN from the environment, constructs
   *           a GraphQLClient with the correct endpoint and auth headers
   * YIELD:    delivers GraphQLClient to the test
   * TEARDOWN: APIRequestContext is disposed automatically by Playwright
   *
   * Environment variables:
   *   GRAPHQL_URL — GraphQL endpoint (default: https://countries.trevorblades.com/)
   *   API_TOKEN   — Bearer token injected as Authorization header when present
   *
   * In production (e.g. Instinct Science):
   *   Set GRAPHQL_URL to the application GraphQL endpoint and API_TOKEN to a
   *   valid session or service-account token. The fixture propagates both.
   *
   * C# equivalent: no direct analog — this replaces manual HttpClient setup
   * that would otherwise be duplicated in every API test method.
   */
  graphqlClient: GraphQLClient;
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

  graphqlClient: async ({ request }, use) => {
    // ── SETUP ────────────────────────────────────────────────────────────────
    const endpoint = process.env['GRAPHQL_URL'] ?? 'https://countries.trevorblades.com/';

    // Inject Authorization header when API_TOKEN is present.
    // No-op when absent so unauthenticated public APIs work without config.
    const headers: Record<string, string> = {};
    const token = process.env['API_TOKEN'];
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // ── YIELD — test body receives a ready-to-use GraphQLClient ──────────────
    await use(new GraphQLClient(request, endpoint, headers));

    // ── TEARDOWN — Playwright disposes the APIRequestContext automatically ───
  },
});

export { expect };
