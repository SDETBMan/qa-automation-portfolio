import { Page } from '@playwright/test';
import { BasePage } from './basePage';

/**
 * CartPage — wraps SauceDemo shopping cart interactions.
 * Selectors mirror C# CartPage.cs.
 */
export class CartPage extends BasePage {
  private readonly cartItems      = '.cart_item';
  private readonly checkoutButton = '#checkout';
  private readonly itemName       = '.cart_item .inventory_item_name';

  constructor(page: Page) {
    super(page);
  }

  async clickCheckout(): Promise<void> {
    await this.click(this.checkoutButton);
  }

  async getCartItemCount(): Promise<number> {
    return await this.page.locator(this.cartItems).count();
  }

  async getFirstItemName(): Promise<string> {
    return await this.getText(this.itemName);
  }

  async isOnCartPage(): Promise<boolean> {
    return this.page.url().includes('cart');
  }
}
