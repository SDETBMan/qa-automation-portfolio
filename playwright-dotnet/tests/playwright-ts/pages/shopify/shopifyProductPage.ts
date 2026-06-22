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

    this.productTitle = page.locator(
      '.product__title, h1.product-single__title, [data-product-title], h1',
    ).first();

    this.productPrice = page.locator(
      '.price__regular .price-item, .product__price, [data-product-price], .price',
    ).first();

    this.productDescription = page.locator(
      '.product__description, .product-single__description, [data-product-description]',
    ).first();

    // Add-to-cart button — most themes use button[name="add"] inside an add-to-cart form
    this.addToCartButton = page.locator(
      'button[name="add"], button[type="submit"][data-add-to-cart], .product-form__submit, [data-add-to-cart-btn]',
    ).first();

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
    return await this.productPrice.innerText();
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
