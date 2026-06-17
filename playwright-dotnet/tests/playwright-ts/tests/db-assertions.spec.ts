import { test, expect } from '../fixtures/fixtures';
import { suite, feature, story, severity, step, tag, attach } from '../utils/allureHelper';

/**
 * Database-to-UI assertion demo tests.
 *
 * These tests demonstrate the full data-integrity verification pattern:
 *   1. Query the database for backend state
 *   2. Navigate to the corresponding UI view
 *   3. Assert that rendered values match the DB source of truth
 *
 * This pattern catches bugs that purely UI-based or purely API-based tests miss:
 *   - UI renders stale cached data while DB has the correct value
 *   - API returns 200 + success message but the DB write silently failed
 *   - Frontend formatting/rounding differs from the stored value
 *
 * NOTE: These tests require a running database. Set DB_HOST, DB_PORT, DB_NAME,
 * DB_USER, DB_PASSWORD env vars. When no database is available (e.g., SauceDemo
 * has no public DB), the tests demonstrate the pattern with skips.
 *
 * To run:   npm run test:db
 * In CI:    Set DB_* env vars in the workflow and remove the skip conditions.
 *
 * C# equivalent: No direct equivalent — this is a TypeScript-only addition.
 * The C# DatabaseUtils.cs provides the raw query layer; these tests add the
 * assertion bridge between DB and Playwright locators.
 */

test.describe('Database-to-UI Assertions @regression', () => {
  /**
   * PATTERN 1: Scalar match
   * Query a single value from the DB and assert it matches a locator's text.
   */
  test('scalar value matches rendered text', async ({ authenticatedPage, dbAssertions, page }) => {
    suite('Data Integrity');
    feature('Database-to-UI Verification');
    story('Product name from DB matches inventory page');
    severity('critical');
    tag('regression');
    tag('db');

    // Skip if no database is configured (SauceDemo has no public DB).
    // Remove this guard when pointing at a real application with a database.
    test.skip(!process.env['DB_HOST'], 'Requires DB_HOST — skipping against SauceDemo');

    await step('Query product name from database', async () => {
      await dbAssertions.scalarMatchesText(
        'SELECT name FROM products WHERE sku = ?',
        ['sauce-labs-backpack'],
        page.locator('.inventory_item_name').first(),
      );
    });
  });

  /**
   * PATTERN 2: Row count match
   * Verify the number of items rendered in a list matches the DB row count.
   */
  test('row count matches UI list length', async ({ authenticatedPage, dbAssertions, page }) => {
    suite('Data Integrity');
    feature('Database-to-UI Verification');
    story('Product count in DB matches inventory list');
    severity('critical');
    tag('regression');
    tag('db');

    test.skip(!process.env['DB_HOST'], 'Requires DB_HOST — skipping against SauceDemo');

    await step('Count active products in database', async () => {
      await dbAssertions.rowCountMatchesLocatorCount(
        'SELECT id FROM products WHERE active = ?',
        [true],
        page.locator('.inventory_item'),
      );
    });
  });

  /**
   * PATTERN 3: Named field match with transform
   * Query a specific column, apply formatting, and compare to UI text.
   * Demonstrates the transformDb option for currency/number formatting.
   */
  test('price field matches with currency formatting', async ({ authenticatedPage, dbAssertions, page }) => {
    suite('Data Integrity');
    feature('Database-to-UI Verification');
    story('Product price from DB matches displayed price after formatting');
    severity('normal');
    tag('regression');
    tag('db');

    test.skip(!process.env['DB_HOST'], 'Requires DB_HOST — skipping against SauceDemo');

    await step('Query price and compare with $XX.XX format', async () => {
      await dbAssertions.fieldMatchesText(
        'SELECT price FROM products WHERE sku = ?',
        ['sauce-labs-backpack'],
        'price',
        page.locator('.inventory_item_price').first(),
        { transformDb: (v) => `$${Number(v).toFixed(2)}` },
      );
    });
  });

  /**
   * PATTERN 4: Form input pre-fill match
   * Verify that a form field's value attribute matches the DB-stored value.
   * Common for edit/profile screens where fields are pre-populated from backend data.
   */
  test('input value matches DB record', async ({ authenticatedPage, dbAssertions, page }) => {
    suite('Data Integrity');
    feature('Database-to-UI Verification');
    story('Profile email input pre-filled from database');
    severity('normal');
    tag('regression');
    tag('db');

    test.skip(!process.env['DB_HOST'], 'Requires DB_HOST — skipping against SauceDemo');

    await step('Verify email input pre-fill from DB', async () => {
      await dbAssertions.scalarMatchesInputValue(
        'SELECT email FROM users WHERE id = ?',
        [1],
        page.locator('#email-input'),
      );
    });
  });

  /**
   * PATTERN 5: Column values in list (order-independent)
   * Verify that all DB values for a column appear somewhere in a list of UI elements.
   * Does not enforce ordering — useful for tag clouds, filter chips, category lists.
   */
  test('all DB categories appear in filter sidebar', async ({ authenticatedPage, dbAssertions, page }) => {
    suite('Data Integrity');
    feature('Database-to-UI Verification');
    story('All active categories from DB appear in UI filter list');
    severity('minor');
    tag('regression');
    tag('db');

    test.skip(!process.env['DB_HOST'], 'Requires DB_HOST — skipping against SauceDemo');

    await step('Verify all categories render in sidebar', async () => {
      await dbAssertions.columnValuesInList(
        'SELECT name FROM categories WHERE active = ?',
        [true],
        'name',
        page.locator('.filter-category'),
      );
    });
  });
});

/**
 * Standalone DB-to-UI test demonstrating the functional import style
 * (as opposed to the class-based dbAssertions fixture).
 */
test.describe('DB Assertions — standalone function style @regression', () => {
  test('direct function import pattern', async ({ authenticatedPage, dbClient, page }) => {
    suite('Data Integrity');
    feature('Database-to-UI Verification');
    story('Demonstrate standalone function imports');
    severity('normal');
    tag('regression');
    tag('db');

    test.skip(!process.env['DB_HOST'], 'Requires DB_HOST — skipping against SauceDemo');

    // Import the standalone functions directly instead of using the DbAssertions class.
    const { expectDbValueMatchesText, expectDbRowCountMatchesLocatorCount } = await import('../utils/dbAssertions');

    await step('Query and verify user name', async () => {
      await expectDbValueMatchesText(
        dbClient,
        'SELECT display_name FROM users WHERE id = ?',
        [1],
        page.locator('[data-testid="user-name"]'),
      );
    });

    await step('Query and verify order count', async () => {
      await expectDbRowCountMatchesLocatorCount(
        dbClient,
        'SELECT id FROM orders WHERE user_id = ?',
        [1],
        page.locator('[data-testid="order-row"]'),
      );
    });
  });
});

/**
 * Allure metadata demo — runs against SauceDemo without a database.
 * Demonstrates step annotations, attachments, and severity/tag/suite labels.
 */
test.describe('Allure Reporting Metadata @smoke', () => {
  test('inventory item count with Allure steps', async ({ authenticatedPage, page }) => {
    suite('Inventory');
    feature('Product Listing');
    story('All 6 SauceDemo products render on inventory page');
    severity('blocker');
    tag('smoke');

    const items = page.locator('.inventory_item');

    await step('Verify inventory page loaded with products', async () => {
      await expect(items.first()).toBeVisible();
    });

    const count = await items.count();

    await step('Attach item count to report', async () => {
      attach('inventory-item-count', JSON.stringify({ count }, null, 2), 'application/json');
    });

    await step('Assert 6 products displayed', async () => {
      expect(count).toBe(6);
    });
  });
});
