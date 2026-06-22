import { test as base, expect } from '@playwright/test';
import { ShopifyStorefrontPage } from '../pages/shopify/shopifyStorefrontPage';
import { ShopifyProductPage } from '../pages/shopify/shopifyProductPage';
import { ShopifyCartPage } from '../pages/shopify/shopifyCartPage';

/**
 * Shopify-specific test fixtures.
 *
 * Provides pre-configured page objects for Shopify storefront testing.
 * All fixtures require the `SHOPIFY_STORE_URL` environment variable.
 * Tests using these fixtures skip gracefully when the URL is not set.
 *
 * Usage:
 *   import { test, expect, SHOPIFY_STORE_URL } from '../fixtures/shopifyFixtures';
 *
 *   test('homepage loads', async ({ storefrontPage }) => {
 *     await storefrontPage.navigateToHome();
 *     // ...
 *   });
 */

export const SHOPIFY_STORE_URL = process.env['SHOPIFY_STORE_URL'] ?? '';

type ShopifyFixtures = {
  /** Shopify storefront page — home, collections, search. */
  storefrontPage: ShopifyStorefrontPage;

  /** Shopify product detail page. */
  productPage: ShopifyProductPage;

  /** Shopify cart page / cart drawer. */
  cartPage: ShopifyCartPage;
};

export const test = base.extend<ShopifyFixtures>({
  storefrontPage: async ({ page }, use) => {
    await use(new ShopifyStorefrontPage(page));
  },

  productPage: async ({ page }, use) => {
    await use(new ShopifyProductPage(page));
  },

  cartPage: async ({ page }, use) => {
    await use(new ShopifyCartPage(page));
  },
});

export { expect };
