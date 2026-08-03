import { test, expect } from '../fixtures/fixtures';
import { visualOptions, dynamicMasks } from '../helpers/visual-config';

/**
 * Visual Regression Tests — SauceDemo pages.
 *
 * Uses Playwright's built-in `toHaveScreenshot()` with configured diff
 * thresholds to catch unintended UI changes.
 *
 * First run:  creates baseline snapshots (committed to git).
 * Later runs: compares against baselines, fails on regressions.
 *
 * Update baselines:  npm run test:visual:update
 *
 * Baselines are stored per-project and per-platform in the
 * visual-regression.spec.ts-snapshots/ directory (Playwright default).
 *
 * Tags: @visual @regression
 */

test.describe('Visual Regression — SauceDemo @visual', () => {
  test('@visual @regression login page baseline', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('login-page.png', {
      ...visualOptions(),
      mask: dynamicMasks(page),
    });
  });

  test('@visual @regression inventory page baseline', async ({ authenticatedPage, page }) => {
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('inventory-page.png', {
      ...visualOptions(),
      mask: dynamicMasks(page),
    });
  });

  test('@visual @regression cart page baseline', async ({ authenticatedPage, page }) => {
    // Add an item so the cart is non-empty
    await authenticatedPage.addItemToCart('sauce-labs-backpack');
    await authenticatedPage.goToCart();
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('cart-page.png', {
      ...visualOptions(),
      mask: dynamicMasks(page),
    });
  });

  test('@visual @regression individual product page baseline', async ({ authenticatedPage, page }) => {
    // Click into the first product detail page
    await page.locator('.inventory_item_name').first().click();
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('product-detail-page.png', {
      ...visualOptions(),
      mask: dynamicMasks(page),
    });
  });

  test('@visual @regression login error state baseline', async ({ loginPage, page }) => {
    await page.goto('/');
    // Trigger an error state for visual capture
    await loginPage.loginAs('locked_out_user', 'secret_sauce');
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('login-error-state.png', {
      ...visualOptions({ threshold: 0.25 }),  // slightly relaxed for error animation
    });
  });
});
