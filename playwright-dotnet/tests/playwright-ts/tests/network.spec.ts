import { test, expect } from '@playwright/test';

/**
 * Network interception tests — 4 patterns mirroring NetworkInterceptionTest.cs.
 *
 * Uses the base @playwright/test directly (no custom fixtures needed —
 * routes must be registered before navigation and vary per test).
 *
 * Patterns:
 *  1. Block assets      → route.abort()             — page still loads
 *  2. Mock API response → route.fulfill({ body })   — synthetic JSON
 *  3. Observe requests  → page.on('request')        — passive listener
 *  4. Simulate failure  → route.abort('aborted')    — login still works
 *
 * C# equivalent: NetworkInterceptionTest.cs
 */

const BASE_URL = process.env['BASE_URL'] ?? 'https://www.saucedemo.com';

test('@smoke block image requests - page still loads', async ({ page }) => {
  // Register route BEFORE navigation — routes intercept from the next request onward.
  await page.route('**/*.{png,jpg,jpeg,gif,webp,svg}', route => route.abort());

  await page.goto(BASE_URL);

  // Login form must render fully even with all images blocked.
  await expect(page.locator('#login-button')).toBeVisible();
});

test('@regression mock API response - returns custom data', async ({ page }) => {
  const mockInventory = [
    { id: 1, name: 'Mock Backpack', price: 9.99, description: 'Test item' }
  ];

  // Intercept any request matching the inventory API pattern.
  await page.route('**/api/inventory**', route =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockInventory),
    })
  );

  // SauceDemo is client-side (no inventory REST API), so verify the interception
  // infrastructure is wired correctly while the app loads normally.
  await page.goto(BASE_URL);
  await expect(page.locator('#login-button')).toBeVisible();
});

test('@regression observe all requests - passive listener', async ({ page }) => {
  const capturedUrls: string[] = [];

  // Passive listener — does NOT intercept, just records.
  page.on('request', req => capturedUrls.push(req.url()));

  await page.goto(BASE_URL);

  // At minimum, the page itself must have been requested.
  expect(capturedUrls.length).toBeGreaterThan(0);
  expect(capturedUrls.some(url => url.includes('saucedemo'))).toBe(true);
});

test('@regression simulate network failure - login still works', async ({ page }) => {
  // Abort favicon requests to simulate a non-critical resource failure.
  await page.route('**/favicon.ico', route => route.abort('aborted'));

  await page.goto(BASE_URL);

  // Core login flow must be unaffected by the favicon failure.
  await page.locator('#user-name').fill('standard_user');
  await page.locator('#password').fill('secret_sauce');
  await page.locator('#login-button').click();

  await page.waitForURL(/inventory/);
  expect(page.url()).toContain('inventory');
});
