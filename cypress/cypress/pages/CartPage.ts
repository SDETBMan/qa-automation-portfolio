import { BasePage } from './BasePage';

const SELECTORS = {
  cartItem:           '.cart_item',
  cartItemName:       '.inventory_item_name',
  checkoutButton:     '[data-test="checkout"]',
  continueShoppingButton: '[data-test="continue-shopping"]',
  removeButton:       'button[id^="remove"]',
} as const;

export class CartPage extends BasePage {
  open(): void {
    this.visit('/cart.html');
  }

  getCartItems(): Cypress.Chainable<JQuery<HTMLElement>> {
    return cy.get(SELECTORS.cartItem);
  }

  getCartItemNames(): Cypress.Chainable<string[]> {
    return cy.get(SELECTORS.cartItemName).then(($els) =>
      Array.from($els, (el) => el.textContent?.trim() ?? ''),
    );
  }

  proceedToCheckout(): void {
    this.click(SELECTORS.checkoutButton);
  }

  continueShopping(): void {
    this.click(SELECTORS.continueShoppingButton);
  }

  assertItemInCart(productName: string): void {
    cy.get(SELECTORS.cartItemName).should('contain.text', productName);
  }

  assertCartEmpty(): void {
    cy.get(SELECTORS.cartItem).should('not.exist');
  }
}
