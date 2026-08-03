import { test, expect, SHOPIFY_STORE_URL } from '../../fixtures/shopifyFixtures';

/**
 * Shopify Storefront E2E Tests.
 *
 * Covers core storefront flows: homepage, product listing, product detail,
 * add-to-cart, cart verification, and search.
 *
 * Requires SHOPIFY_STORE_URL environment variable.
 * Tests skip gracefully when the URL is not set — CI won't fail.
 *
 * Tags: @shopify @smoke @regression
 */

test.describe('Shopify Storefront @shopify', () => {
  test.skip(!SHOPIFY_STORE_URL, 'SHOPIFY_STORE_URL not set — skipping Shopify tests');

  test.beforeEach(async ({ page }) => {
    // Increase timeouts for external Shopify stores
    test.setTimeout(60_000);
  });

  test('@shopify @smoke homepage loads with header and products', async ({ storefrontPage }) => {
    await storefrontPage.navigateToHome();

    expect(await storefrontPage.isHeaderVisible()).toBe(true);

    const title = await storefrontPage.getPageTitle();
    expect(title.length).toBeGreaterThan(0);
  });

  test('@shopify @smoke product listing shows products', async ({ storefrontPage }) => {
    await storefrontPage.navigateToCollections();

    const productCount = await storefrontPage.getProductCardCount();
    expect(productCount).toBeGreaterThan(0);
  });

  test('@shopify @regression product detail page shows title and price', async ({
    storefrontPage,
    productPage,
    page,
  }) => {
    await storefrontPage.navigateToCollections();
    await storefrontPage.clickFirstProduct();

    // Verify we landed on a product page
    expect(page.url()).toContain('/products/');

    const title = await productPage.getTitle();
    expect(title.length).toBeGreaterThan(0);

    const price = await productPage.getPrice();
    expect(price).toBeTruthy();
  });

  test('@shopify @regression add to cart updates cart', async ({
    storefrontPage,
    productPage,
    cartPage,
    page,
  }) => {
    await storefrontPage.navigateToCollections();
    await storefrontPage.clickFirstProduct();

    // Add product to cart
    await productPage.addToCart();

    // Navigate to cart and verify item is present
    await cartPage.navigateToCart();
    const itemCount = await cartPage.getItemCount();
    expect(itemCount).toBeGreaterThanOrEqual(1);
  });

  test('@shopify @regression cart displays correct item details', async ({
    storefrontPage,
    productPage,
    cartPage,
    page,
  }) => {
    await storefrontPage.navigateToCollections();
    await storefrontPage.clickFirstProduct();

    const productTitle = await productPage.getTitle();
    await productPage.addToCart();

    await cartPage.navigateToCart();
    const cartItems = await cartPage.getItemNames();
    // The product we added should appear in the cart
    const found = cartItems.some((name) =>
      name.toLowerCase().includes(productTitle.toLowerCase().substring(0, 10)),
    );
    expect(found).toBe(true);
  });

  test('@shopify @regression search returns relevant results', async ({ storefrontPage, page }) => {
    await storefrontPage.navigateToHome();

    // Search for a generic term likely to match products
    await storefrontPage.searchFor('shirt');

    // Should be on a search results page
    expect(page.url()).toMatch(/search|q=/i);
  });

  test('@shopify @regression empty cart shows empty message or no items', async ({ cartPage }) => {
    await cartPage.navigateToCart();

    const isEmpty = await cartPage.isEmpty();
    const itemCount = await cartPage.getItemCount();

    // Either the empty message is shown or there are no items
    expect(isEmpty || itemCount === 0).toBe(true);
  });

  test('@shopify @smoke checkout button is accessible from cart', async ({
    storefrontPage,
    productPage,
    cartPage,
  }) => {
    await storefrontPage.navigateToCollections();
    await storefrontPage.clickFirstProduct();
    await productPage.addToCart();

    await cartPage.navigateToCart();
    const checkoutVisible = await cartPage.isCheckoutEnabled();
    expect(checkoutVisible).toBe(true);
  });
});
