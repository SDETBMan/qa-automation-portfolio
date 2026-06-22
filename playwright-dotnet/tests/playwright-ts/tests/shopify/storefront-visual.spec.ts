import { test, expect, SHOPIFY_STORE_URL } from '../../fixtures/shopifyFixtures';
import { visualOptions } from '../../helpers/visual-config';

/**
 * Shopify Storefront Visual Regression Tests.
 *
 * Captures baseline screenshots of key Shopify storefront pages.
 * Uses the same visual-config thresholds as the SauceDemo visual tests.
 *
 * Tags: @shopify @visual @regression
 */

test.describe('Shopify Visual Regression @shopify @visual', () => {
  test.skip(!SHOPIFY_STORE_URL, 'SHOPIFY_STORE_URL not set — skipping Shopify visual tests');

  test.beforeEach(async () => {
    test.setTimeout(60_000);
  });

  test('@shopify @visual @regression homepage baseline', async ({ storefrontPage, page }) => {
    await storefrontPage.navigateToHome();
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('shopify-homepage.png', {
      ...visualOptions(),
      // Mask common dynamic elements in Shopify themes
      mask: [
        page.locator('.announcement-bar'),    // Rotating announcements
        page.locator('.cart-count-bubble'),    // Cart count
        page.locator('[data-cart-count]'),
      ],
    });
  });

  test('@shopify @visual @regression collection page baseline', async ({ storefrontPage, page }) => {
    await storefrontPage.navigateToCollections();
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('shopify-collection-page.png', {
      ...visualOptions({ maxDiffPixelRatio: 0.02 }),  // relaxed for dynamic product images
    });
  });

  test('@shopify @visual @regression product detail page baseline', async ({
    storefrontPage,
    page,
  }) => {
    await storefrontPage.navigateToCollections();
    await storefrontPage.clickFirstProduct();
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('shopify-product-detail.png', {
      ...visualOptions({ maxDiffPixelRatio: 0.02 }),
    });
  });

  test('@shopify @visual @regression cart page baseline', async ({ storefrontPage, productPage, cartPage, page }) => {
    await storefrontPage.navigateToCollections();
    await storefrontPage.clickFirstProduct();
    await productPage.addToCart();
    await cartPage.navigateToCart();
    await page.waitForLoadState('networkidle');

    await expect(page).toHaveScreenshot('shopify-cart-page.png', {
      ...visualOptions(),
      mask: [
        page.locator('.cart-count-bubble'),
        page.locator('[data-cart-count]'),
      ],
    });
  });
});
