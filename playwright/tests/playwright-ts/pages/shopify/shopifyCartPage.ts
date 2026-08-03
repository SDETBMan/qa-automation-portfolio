import { Page, Locator } from '@playwright/test';
import { BasePage } from '../basePage';

/**
 * ShopifyCartPage — POM for Shopify cart page / cart drawer.
 *
 * Supports both full-page cart (/cart) and AJAX cart drawers used by
 * Dawn and other modern Shopify themes.
 */
export class ShopifyCartPage extends BasePage {
  readonly cartTitle: Locator;
  readonly cartItems: Locator;
  readonly cartItemNames: Locator;
  readonly cartItemPrices: Locator;
  readonly cartSubtotal: Locator;
  readonly checkoutButton: Locator;
  readonly emptyCartMessage: Locator;
  readonly quantityInputs: Locator;
  readonly removeButtons: Locator;
  readonly continueShoppingLink: Locator;

  constructor(page: Page) {
    super(page);

    this.cartTitle = page.locator(
      '.cart__title, h1:has-text("cart"), [data-cart-title]',
    ).first();

    // Dawn uses .cart-item divs; Monochrome uses a <table> with <tr> rows (skip header row via tbody or :not(:first-child))
    this.cartItems = page.locator(
      '.cart-item, .cart__item, [data-cart-item], table tr:has(td)',
    );

    // Dawn uses .cart-item__name; Monochrome puts the product name in an h3 > a inside a table cell
    this.cartItemNames = page.locator(
      '.cart-item__name, .cart-item__title a, [data-cart-item-name], table td h3 a',
    );

    this.cartItemPrices = page.locator(
      '.cart-item__price, .cart-item__total, [data-cart-item-price]',
    );

    this.cartSubtotal = page.locator(
      '.totals__subtotal-value, .cart__subtotal, [data-cart-subtotal], .cart-subtotal',
    ).first();

    // Dawn uses button[name="checkout"]; Monochrome uses a plain <button>Checkout</button>
    this.checkoutButton = page.getByRole('button', { name: /checkout/i }).first();

    this.emptyCartMessage = page.locator(
      '.cart__empty-text, .cart--empty-message, [data-empty-cart]',
    ).first();

    this.quantityInputs = page.locator(
      '.cart-item input[name="updates[]"], .quantity__input, [data-cart-quantity]',
    );

    this.removeButtons = page.locator(
      '.cart-item a[href*="/cart/change"], cart-remove-button, [data-cart-remove], a[href*="/cart/change"], a:has-text("Remove")',
    );

    this.continueShoppingLink = page.locator(
      'a[href="/"], a[href="/collections/all"], .cart__continue',
    ).first();
  }

  // ── Actions ────────────────────────────────────────────────────────────────

  async navigateToCart(): Promise<void> {
    await this.page.goto('/cart');
    await this.page.waitForLoadState('domcontentloaded');
  }

  async clickCheckout(): Promise<void> {
    await this.checkoutButton.click();
  }

  async continueShopping(): Promise<void> {
    await this.continueShoppingLink.click();
    await this.page.waitForLoadState('domcontentloaded');
  }

  // ── Queries ────────────────────────────────────────────────────────────────

  async getItemCount(): Promise<number> {
    return await this.cartItems.count();
  }

  async getItemNames(): Promise<string[]> {
    return await this.cartItemNames.allInnerTexts();
  }

  async getSubtotal(): Promise<string> {
    return await this.cartSubtotal.innerText();
  }

  async isEmpty(): Promise<boolean> {
    return await this.emptyCartMessage.isVisible({ timeout: 3_000 }).catch(() => false);
  }

  async isCheckoutEnabled(): Promise<boolean> {
    return await this.checkoutButton.isVisible({ timeout: 3_000 }).catch(() => false);
  }
}
