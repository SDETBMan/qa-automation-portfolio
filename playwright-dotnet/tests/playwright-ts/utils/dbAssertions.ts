import { Locator, expect } from '@playwright/test';
import { DbClient, DbRow } from './dbClient';

/**
 * Database-to-UI assertion helpers.
 *
 * These functions bridge the gap between backend database state and frontend
 * rendered content — the core pattern for end-to-end data integrity validation.
 *
 * Why this matters:
 *   A UI test that only checks "success toast appeared" can silently pass even
 *   when the database write failed. Conversely, an API test that only checks
 *   the response body can miss rendering bugs. DB-to-UI assertions close both
 *   gaps by verifying the full round-trip: database → API → UI.
 *
 * Usage: Import individual helpers or use the `DbAssertions` class which bundles
 * a DbClient reference for a more fluent API inside test bodies.
 */

// ─── Standalone helper functions ────────────────────────────────────────────

/**
 * Assert that a database scalar value matches a locator's visible text.
 *
 * Queries the database for a single value (first column, first row) and asserts
 * that the target locator's trimmed innerText matches the stringified DB value.
 *
 * @param db      — Active DbClient instance
 * @param sql     — SELECT query expected to return one scalar value
 * @param params  — Parameterized query values
 * @param locator — Playwright Locator pointing to the UI element
 * @param options — Optional: transform functions, custom message, timeout
 *
 * Example:
 *   await expectDbValueMatchesText(
 *     db,
 *     'SELECT display_name FROM users WHERE id = ?', [userId],
 *     page.locator('[data-testid="user-name"]'),
 *   );
 */
export async function expectDbValueMatchesText(
  db: DbClient,
  sql: string,
  params: unknown[],
  locator: Locator,
  options?: {
    /** Transform the DB value before comparison (e.g., formatting currency). */
    transformDb?: (value: unknown) => string;
    /** Transform the UI text before comparison (e.g., stripping whitespace). */
    transformUi?: (text: string) => string;
    /** Custom assertion message on failure. */
    message?: string;
  },
): Promise<void> {
  const dbValue = await db.executeScalar(sql, params);

  const dbText = options?.transformDb
    ? options.transformDb(dbValue)
    : String(dbValue ?? '');

  // Use Playwright's auto-retrying assertions to handle UI render lag gracefully.
  if (options?.transformUi) {
    // transformUi requires reading raw text then comparing — use expect.poll
    // so the read+transform retries until match or timeout, just like toHaveText.
    const transform = options.transformUi;
    await expect.poll(
      async () => transform(await locator.innerText()),
      { message: options?.message ?? `DB value "${dbText}" should match transformed UI text` },
    ).toBe(dbText);
  } else {
    await expect(
      locator,
      options?.message ?? `Expected locator text to match DB value "${dbText}"`,
    ).toHaveText(dbText);
  }
}

/**
 * Assert that a specific field in a DB row matches a locator's text.
 *
 * Runs a SELECT query, picks a named column from the first row, and compares
 * its stringified value against the locator's visible text.
 *
 * @param db       — Active DbClient instance
 * @param sql      — SELECT query returning at least one row
 * @param params   — Parameterized query values
 * @param column   — Column name to extract from the result row
 * @param locator  — Playwright Locator for the UI element
 *
 * Example:
 *   await expectDbFieldMatchesText(
 *     db,
 *     'SELECT price, name FROM products WHERE sku = ?', ['SKU-001'],
 *     'price',
 *     page.locator('.product-price'),
 *     { transformDb: (v) => `$${Number(v).toFixed(2)}` },
 *   );
 */
export async function expectDbFieldMatchesText(
  db: DbClient,
  sql: string,
  params: unknown[],
  column: string,
  locator: Locator,
  options?: {
    transformDb?: (value: unknown) => string;
    transformUi?: (text: string) => string;
    message?: string;
  },
): Promise<void> {
  const rows = await db.executeQuery(sql, params);
  expect(rows.length, `Expected at least 1 row from query`).toBeGreaterThan(0);

  const rawValue = rows[0][column];
  const dbText = options?.transformDb
    ? options.transformDb(rawValue)
    : String(rawValue ?? '');

  if (options?.transformUi) {
    const transform = options.transformUi;
    await expect.poll(
      async () => transform(await locator.innerText()),
      { message: options?.message ?? `DB column "${column}" should match transformed UI text` },
    ).toBe(dbText);
  } else {
    await expect(
      locator,
      options?.message ?? `Expected locator to show DB column "${column}" value "${dbText}"`,
    ).toHaveText(dbText);
  }
}

/**
 * Assert that the number of rows returned by a DB query matches
 * the count of elements matched by a Playwright locator.
 *
 * Useful for verifying list/table views render the correct number of records.
 *
 * Example:
 *   await expectDbRowCountMatchesLocatorCount(
 *     db,
 *     'SELECT id FROM orders WHERE user_id = ? AND status = ?', [userId, 'active'],
 *     page.locator('[data-testid="order-row"]'),
 *   );
 */
export async function expectDbRowCountMatchesLocatorCount(
  db: DbClient,
  sql: string,
  params: unknown[],
  locator: Locator,
  options?: { message?: string },
): Promise<void> {
  const rows = await db.executeQuery(sql, params);
  await expect(
    locator,
    options?.message ?? `Expected ${rows.length} UI elements to match DB row count`,
  ).toHaveCount(rows.length);
}

/**
 * Assert that a DB scalar matches the `value` attribute of an input/select element.
 *
 * Targets form fields where content lives in `.value`, not `.innerText`.
 *
 * Example:
 *   await expectDbValueMatchesInputValue(
 *     db,
 *     'SELECT email FROM users WHERE id = ?', [userId],
 *     page.locator('#email-input'),
 *   );
 */
export async function expectDbValueMatchesInputValue(
  db: DbClient,
  sql: string,
  params: unknown[],
  locator: Locator,
  options?: {
    transformDb?: (value: unknown) => string;
    message?: string;
  },
): Promise<void> {
  const dbValue = await db.executeScalar(sql, params);
  const dbText = options?.transformDb
    ? options.transformDb(dbValue)
    : String(dbValue ?? '');

  await expect(
    locator,
    options?.message ?? `Expected input value to match DB value "${dbText}"`,
  ).toHaveValue(dbText);
}

/**
 * Assert that every row's column value appears somewhere in a list of UI elements.
 *
 * Queries the database for a list of values, then checks each one appears in the
 * locator's allInnerTexts(). Order-independent comparison.
 *
 * Example:
 *   await expectDbColumnValuesInList(
 *     db,
 *     'SELECT name FROM categories WHERE active = ?', [true],
 *     'name',
 *     page.locator('.category-name'),
 *   );
 */
export async function expectDbColumnValuesInList(
  db: DbClient,
  sql: string,
  params: unknown[],
  column: string,
  locator: Locator,
  options?: {
    transformDb?: (value: unknown) => string;
    message?: string;
  },
): Promise<void> {
  const rows = await db.executeQuery(sql, params);
  const dbValues = rows.map((row) =>
    options?.transformDb
      ? options.transformDb(row[column])
      : String(row[column] ?? ''),
  );

  const uiTexts = await locator.allInnerTexts();
  const trimmedUiTexts = uiTexts.map((t) => t.trim());

  for (const dbVal of dbValues) {
    expect(
      trimmedUiTexts,
      options?.message ?? `Expected UI list to contain DB value "${dbVal}"`,
    ).toContain(dbVal);
  }
}

// ─── Class-based API for fluent usage ───────────────────────────────────────

/**
 * Bundles a DbClient reference for a cleaner API when running multiple
 * DB-to-UI assertions in a single test.
 *
 * Example:
 *   const assert = new DbAssertions(dbClient);
 *   await assert.scalarMatchesText(
 *     'SELECT name FROM users WHERE id = ?', [1],
 *     page.locator('#user-name'),
 *   );
 *   await assert.rowCountMatchesLocatorCount(
 *     'SELECT * FROM orders WHERE user_id = ?', [1],
 *     page.locator('.order-row'),
 *   );
 */
export class DbAssertions {
  constructor(private readonly db: DbClient) {}

  async scalarMatchesText(
    sql: string,
    params: unknown[],
    locator: Locator,
    options?: Parameters<typeof expectDbValueMatchesText>[4],
  ) {
    return expectDbValueMatchesText(this.db, sql, params, locator, options);
  }

  async fieldMatchesText(
    sql: string,
    params: unknown[],
    column: string,
    locator: Locator,
    options?: Parameters<typeof expectDbFieldMatchesText>[5],
  ) {
    return expectDbFieldMatchesText(this.db, sql, params, column, locator, options);
  }

  async rowCountMatchesLocatorCount(
    sql: string,
    params: unknown[],
    locator: Locator,
    options?: Parameters<typeof expectDbRowCountMatchesLocatorCount>[4],
  ) {
    return expectDbRowCountMatchesLocatorCount(this.db, sql, params, locator, options);
  }

  async scalarMatchesInputValue(
    sql: string,
    params: unknown[],
    locator: Locator,
    options?: Parameters<typeof expectDbValueMatchesInputValue>[4],
  ) {
    return expectDbValueMatchesInputValue(this.db, sql, params, locator, options);
  }

  async columnValuesInList(
    sql: string,
    params: unknown[],
    column: string,
    locator: Locator,
    options?: Parameters<typeof expectDbColumnValuesInList>[5],
  ) {
    return expectDbColumnValuesInList(this.db, sql, params, column, locator, options);
  }
}
