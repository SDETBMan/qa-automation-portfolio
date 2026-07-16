import { Page, Locator } from '@playwright/test';
import { BasePage } from './basePage';

/**
 * InventoryPage — wraps SauceDemo product listing interactions.
 *
 * Locator strategy:
 *   - Cart link: getByTestId — data-test='shopping-cart-link'
 *   - Cart badge: scoped CSS on the cart link — no data-test attribute available
 *   - Add/Remove buttons: getByTestId with dynamic slug — data-test='add-to-cart-{slug}'
 *
 * C# equivalent: InventoryPage.cs
 */
export class InventoryPage extends BasePage {
  readonly cartLink: Locator;
  readonly cartBadge: Locator;

  constructor(page: Page) {
    super(page);
    this.cartLink = page.getByTestId('shopping-cart-link');
    this.cartBadge = page.locator('.shopping_cart_badge');
  }

  async addItemToCart(itemSlug: string): Promise<void> {
    await this.page.getByTestId(`add-to-cart-${itemSlug}`).click();
  }

  async removeItemFromCart(itemSlug: string): Promise<void> {
    await this.page.getByTestId(`remove-${itemSlug}`).click();
  }

  async goToCart(): Promise<void> {
    await this.cartLink.click();
  }

  async getCartBadgeCount(): Promise<string> {
    return await this.cartBadge.innerText();
  }

  async isCartBadgeVisible(): Promise<boolean> {
    return await this.cartBadge.isVisible();
  }
}
