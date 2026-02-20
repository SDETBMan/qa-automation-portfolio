import { Page } from '@playwright/test';
import { BasePage } from './basePage';

/**
 * InventoryPage — wraps SauceDemo product listing interactions.
 * Selectors mirror C# InventoryPage.cs.
 */
export class InventoryPage extends BasePage {
  private readonly cartBadge  = '.shopping_cart_badge';
  private readonly cartLink   = '.shopping_cart_link';

  constructor(page: Page) {
    super(page);
  }

  async addItemToCart(itemSlug: string): Promise<void> {
    await this.click(`#add-to-cart-${itemSlug}`);
  }

  async removeItemFromCart(itemSlug: string): Promise<void> {
    await this.click(`#remove-${itemSlug}`);
  }

  async goToCart(): Promise<void> {
    await this.click(this.cartLink);
  }

  async getCartBadgeCount(): Promise<string> {
    return await this.getText(this.cartBadge);
  }

  async isCartBadgeVisible(): Promise<boolean> {
    return await this.isVisible(this.cartBadge);
  }
}
