import { BasePage } from './BasePage';

const SELECTORS = {
  inventoryList:  '.inventory_list',
  inventoryItem:  '.inventory_item',
  cartBadge:      '.shopping_cart_badge',
  cartLink:       '.shopping_cart_link',
  sortDropdown:   '[data-test="product-sort-container"]',
  productName:    '.inventory_item_name',
  productPrice:   '.inventory_item_price',
} as const;

export class InventoryPage extends BasePage {
  open(): void {
    this.visit('/inventory.html');
  }

  getProductCount(): Cypress.Chainable<number> {
    return cy.get(SELECTORS.inventoryItem).its('length');
  }

  addItemToCart(productName: string): void {
    cy.contains(SELECTORS.inventoryItem, productName)
      .find('button[id^="add-to-cart"]')
      .click();
  }

  removeItemFromCart(productName: string): void {
    cy.contains(SELECTORS.inventoryItem, productName)
      .find('button[id^="remove"]')
      .click();
  }

  getCartBadgeCount(): Cypress.Chainable<string> {
    return cy.get(SELECTORS.cartBadge).invoke('text');
  }

  cartBadgeShouldNotExist(): void {
    cy.get(SELECTORS.cartBadge).should('not.exist');
  }

  goToCart(): void {
    this.click(SELECTORS.cartLink);
  }

  sortBy(option: 'az' | 'za' | 'lohi' | 'hilo'): void {
    cy.get(SELECTORS.sortDropdown).select(option);
  }

  getProductNames(): Cypress.Chainable<string[]> {
    return cy.get(SELECTORS.productName).then(($els) =>
      Array.from($els, (el) => el.textContent?.trim() ?? ''),
    );
  }

  getProductPrices(): Cypress.Chainable<number[]> {
    return cy.get(SELECTORS.productPrice).then(($els) =>
      Array.from($els, (el) =>
        parseFloat((el.textContent ?? '0').replace('$', '')),
      ),
    );
  }
}
