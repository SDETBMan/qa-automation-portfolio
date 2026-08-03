import { Page, Locator } from '@playwright/test';
import { BasePage } from '../basePage';

/**
 * ShopifyProductPage — POM for Shopify product detail page.
 *
 * Covers product info, variant selection, and add-to-cart across common
 * Shopify themes (Dawn, Debut, custom).
 */
export class ShopifyProductPage extends BasePage {
  readonly productTitle: Locator;
  readonly productPrice: Locator;
  readonly productDescription: Locator;
  readonly addToCartButton: Locator;
  readonly addToCartForm: Locator;
  readonly quantityInput: Locator;
  readonly productImages: Locator;
  readonly variantSelectors: Locator;

  constructor(page: Page) {
    super(page);

    // Dawn uses h1 with .product__title; Monochrome uses h2 — include both heading levels
    this.productTitle = page.locator(
      '.product__title, h1.product-single__title, [data-product-title], h1, h2',
    ).first();

    // Price — Dawn uses .price classes; Monochrome renders price as plain text
    // Try CSS classes first, fall back to text pattern matching for minimal themes
    this.productPrice = page.locator(
      '.price__regular .price-item, .product__price, [data-product-price], .price',
    ).first();

    this.productDescription = page.locator(
      '.product__description, .product-single__description, [data-product-description]',
    ).first();

    // Add-to-cart — Dawn uses <button name="add">; Monochrome uses <input type="submit" value="Add to Shopping Cart">
    // getByRole('button') matches both <button> and <input type="submit">
    this.addToCartButton = page.getByRole('button', { name: /add to/i }).first();

    this.addToCartForm = page.locator(
      'form[action*="/cart/add"], [data-product-form], .product-form',
    ).first();

    this.quantityInput = page.locator(
      'input[name="quantity"], [data-quantity-input], .quantity__input',
    ).first();

    this.productImages = page.locator(
      '.product__media img, .product-single__photo img, [data-product-media] img',
    );

    this.variantSelectors = page.locator(
      'fieldset.product-form__input, .variant-input-wrap, [data-variant-option]',
    );
  }

  // ── Actions ────────────────────────────────────────────────────────────────

  async addToCart(): Promise<void> {
    await this.addToCartButton.click();
    // Wait for network to settle (AJAX cart update)
    await this.page.waitForLoadState('networkidle');
  }

  async setQuantity(qty: number): Promise<void> {
    await this.quantityInput.fill(String(qty));
  }

  async navigateToProduct(handle: string): Promise<void> {
    await this.page.goto(`/products/${handle}`);
    await this.page.waitForLoadState('domcontentloaded');
  }

  // ── Queries ────────────────────────────────────────────────────────────────

  async getTitle(): Promise<string> {
    return await this.productTitle.innerText();
  }

  async getPrice(): Promise<string> {
    // Try CSS-class-based locator first; fall back to text pattern for minimal themes
    if (await this.productPrice.isVisible({ timeout: 3_000 }).catch(() => false)) {
      return await this.productPrice.innerText();
    }
    return await this.page.getByText(/\$\d+\.\d{2}/).first().innerText();
  }

  async getDescription(): Promise<string> {
    return await this.productDescription.innerText();
  }

  async isAddToCartEnabled(): Promise<boolean> {
    return await this.addToCartButton.isEnabled();
  }

  async getImageCount(): Promise<number> {
    return await this.productImages.count();
  }

  async hasVariants(): Promise<boolean> {
    return (await this.variantSelectors.count()) > 0;
  }
}
