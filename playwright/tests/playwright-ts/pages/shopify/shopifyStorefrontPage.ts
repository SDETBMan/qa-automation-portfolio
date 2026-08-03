import { Page, Locator } from '@playwright/test';
import { BasePage } from '../basePage';

/**
 * ShopifyStorefrontPage — POM for Shopify storefront (home, collection, search).
 *
 * Selector strategy:
 * Shopify themes vary, but Dawn (default) and most modern themes use
 * predictable patterns.  Selectors use fallback chains — the first visible
 * match wins — so the same POM works across Dawn, Debut, and custom themes.
 */
export class ShopifyStorefrontPage extends BasePage {
  // ── Locators (resilient fallback selectors) ────────────────────────────────

  /** Navigation / header */
  readonly header: Locator;
  readonly mainNav: Locator;
  readonly cartIcon: Locator;
  readonly cartCount: Locator;
  readonly searchToggle: Locator;
  readonly searchInput: Locator;

  /** Product listing */
  readonly productCards: Locator;
  readonly productLinks: Locator;

  /** Collection / hero */
  readonly heroSection: Locator;
  readonly collectionTitle: Locator;

  constructor(page: Page) {
    super(page);

    // Monochrome and minimal themes lack a <header> tag; fall back to nav or the top-level div containing the logo
    this.header = page.locator('header, nav, [role="banner"]').first();
    this.mainNav = page.locator('nav').first();

    // Cart icon — multiple selectors for theme compatibility
    this.cartIcon = page.locator(
      '[data-cart-icon], a[href="/cart"], .cart-icon-bubble, .header__icon--cart',
    ).first();
    this.cartCount = page.locator(
      '.cart-count-bubble, [data-cart-count], .cart-count, .cart__count',
    ).first();

    // Search — Dawn uses a details/summary toggle, others use a direct input
    this.searchToggle = page.locator(
      '[data-search-toggle], details-modal[data-modal="search"], button[aria-label*="Search"]',
    ).first();
    this.searchInput = page.locator(
      'input[type="search"], [data-search-input], input[name="q"]',
    ).first();

    // Product cards
    this.productCards = page.locator(
      '[data-product-card], .product-card, .card--product, .product-grid-item',
    );
    this.productLinks = page.locator('a[href*="/products/"]');

    // Hero / collection
    this.heroSection = page.locator(
      '.banner, .hero, .slideshow, [data-section-type="slideshow"]',
    ).first();
    this.collectionTitle = page.locator(
      '.collection-hero__title, h1.title, h1',
    ).first();
  }

  // ── Actions ────────────────────────────────────────────────────────────────

  async navigateToHome(): Promise<void> {
    await this.page.goto('/');
    await this.page.waitForLoadState('domcontentloaded');
  }

  async navigateToCollections(): Promise<void> {
    await this.page.goto('/collections/all');
    await this.page.waitForLoadState('domcontentloaded');
  }

  async searchFor(query: string): Promise<void> {
    // Try clicking the search toggle first (Dawn pattern)
    if (await this.searchToggle.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await this.searchToggle.click();
    }
    await this.searchInput.waitFor({ state: 'visible', timeout: 5_000 });
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
    await this.page.waitForLoadState('domcontentloaded');
  }

  async clickFirstProduct(): Promise<void> {
    await this.productLinks.first().click();
    await this.page.waitForLoadState('domcontentloaded');
  }

  // ── Queries ────────────────────────────────────────────────────────────────

  async getProductCardCount(): Promise<number> {
    return await this.productLinks.count();
  }

  async getPageTitle(): Promise<string> {
    return await this.page.title();
  }

  async isHeaderVisible(): Promise<boolean> {
    // Fall back to checking for the store logo link if no header/nav element exists
    if (await this.header.isVisible().catch(() => false)) return true;
    return await this.page.locator('a[href="/"] img').first().isVisible().catch(() => false);
  }

  async getCollectionTitle(): Promise<string> {
    return await this.collectionTitle.innerText();
  }
}
