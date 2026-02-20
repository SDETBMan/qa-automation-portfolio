import { test, expect } from '../fixtures/fixtures';
import { CartPage } from '../pages/cartPage';

/**
 * Inventory / cart tests — use the authenticatedPage fixture.
 * Every test starts already logged in on inventory.html.
 * Zero login boilerplate in any test method.
 *
 * C# equivalent: CartFixtureTest.cs (extends AuthenticatedTest)
 */

test('@smoke add backpack to cart - badge shows 1', async ({ authenticatedPage }) => {
  await authenticatedPage.addItemToCart('sauce-labs-backpack');

  expect(await authenticatedPage.getCartBadgeCount()).toBe('1');
});

test('@regression add multiple items to cart - badge shows count', async ({ authenticatedPage }) => {
  await authenticatedPage.addItemToCart('sauce-labs-backpack');
  await authenticatedPage.addItemToCart('sauce-labs-bike-light');

  expect(await authenticatedPage.getCartBadgeCount()).toBe('2');
});

test('@regression add then remove item - cart badge disappears', async ({ authenticatedPage }) => {
  await authenticatedPage.addItemToCart('sauce-labs-backpack');
  expect(await authenticatedPage.isCartBadgeVisible()).toBe(true);

  await authenticatedPage.removeItemFromCart('sauce-labs-backpack');
  expect(await authenticatedPage.isCartBadgeVisible()).toBe(false);
});

test('@regression navigate to checkout from cart', async ({ authenticatedPage, page }) => {
  await authenticatedPage.addItemToCart('sauce-labs-backpack');
  await authenticatedPage.goToCart();

  const cartPage = new CartPage(page);
  expect(await cartPage.getCartItemCount()).toBe(1);
  expect(await cartPage.isOnCartPage()).toBe(true);
});
