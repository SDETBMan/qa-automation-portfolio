import { test, expect } from '../fixtures/fixtures';

/**
 * Login tests — use the loginPage fixture (browser on baseURL / login screen).
 *
 * Tags use @tag convention in the title string.
 * --grep "@smoke"      runs the happy-path test.
 * --grep "@regression" runs the negative-path tests.
 *
 * C# equivalent: LoginTest.cs
 */

test('@smoke valid login navigates to inventory', async ({ loginPage, page }) => {
  await page.goto('/');
  await loginPage.loginAs('standard_user', 'secret_sauce');

  await expect(page).toHaveURL(/inventory/);
});

test('@regression locked-out user sees error message', async ({ loginPage, page }) => {
  await page.goto('/');
  await loginPage.loginAs('locked_out_user', 'secret_sauce');

  expect(await loginPage.isErrorDisplayed()).toBe(true);
  const errorText = await loginPage.getErrorMessage();
  expect(errorText).toContain('locked out');
});

test('@regression empty credentials show validation error', async ({ loginPage, page }) => {
  await page.goto('/');
  await loginPage.loginAs('', '');

  expect(await loginPage.isErrorDisplayed()).toBe(true);
  const errorText = await loginPage.getErrorMessage();
  expect(errorText).toContain('Username is required');
});
