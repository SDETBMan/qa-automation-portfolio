import { Page, Locator } from '@playwright/test';
import { BasePage } from './basePage';

/**
 * CartPage — wraps SauceDemo shopping cart interactions.
 *
 * Locator strategy:
 *   - Checkout button: getByTestId — data-test='checkout'
 *   - Cart items: scoped CSS — no data-test on the container
 *   - Item name: scoped CSS within cart item — structural but stable
 *
 * C# equivalent: CartPage.cs
 */
export class CartPage extends BasePage {
  readonly cartItems: Locator;
  readonly checkoutButton: Locator;
  readonly itemName: Locator;

  constructor(page: Page) {
    super(page);
    this.cartItems = page.locator('.cart_item');
    this.checkoutButton = page.getByTestId('checkout');
    this.itemName = page.locator('.cart_item .inventory_item_name');
  }

  async clickCheckout(): Promise<void> {
    await this.checkoutButton.click();
  }

  async getCartItemCount(): Promise<number> {
    return await this.cartItems.count();
  }

  async getFirstItemName(): Promise<string> {
    return await this.itemName.first().innerText();
  }

  async isOnCartPage(): Promise<boolean> {
    return this.page.url().includes('cart');
  }
}
