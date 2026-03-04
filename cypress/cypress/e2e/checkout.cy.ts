import { InventoryPage } from '../pages/InventoryPage';
import { CartPage } from '../pages/CartPage';
import { CheckoutPage } from '../pages/CheckoutPage';

const inventoryPage = new InventoryPage();
const cartPage = new CartPage();
const checkoutPage = new CheckoutPage();

describe('Checkout', () => {
  beforeEach(() => {
    cy.fixture('users').then((users) => {
      cy.login(users.standard.username, users.standard.password);
    });
    cy.fixture('products').then((data) => {
      inventoryPage.addItemToCart(data.products[0].name);
      inventoryPage.goToCart();
    });
  });

  // ── Regression ─────────────────────────────────────────────────────────────

  it('@regression complete full checkout shows success confirmation', () => {
    cartPage.proceedToCheckout();
    checkoutPage.fillInfo('Jane', 'Doe', '94105');
    checkoutPage.continueToStepTwo();
    checkoutPage.finish();
    checkoutPage.assertOrderComplete();
  });

  it('@regression missing first name shows validation error', () => {
    cartPage.proceedToCheckout();
    checkoutPage.fillInfo('', 'Doe', '94105');
    checkoutPage.continueToStepTwo();
    checkoutPage.assertErrorContains('First Name is required');
  });

  it('@regression missing last name shows validation error', () => {
    cartPage.proceedToCheckout();
    checkoutPage.fillInfo('Jane', '', '94105');
    checkoutPage.continueToStepTwo();
    checkoutPage.assertErrorContains('Last Name is required');
  });

  it('@regression cancel checkout returns to cart', () => {
    cartPage.proceedToCheckout();
    checkoutPage.cancel();
    cy.url().should('include', '/cart.html');
  });
});
