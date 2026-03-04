import { InventoryPage } from '../pages/InventoryPage';
import { CartPage } from '../pages/CartPage';
import { CheckoutPage } from '../pages/CheckoutPage';

const inventoryPage = new InventoryPage();
const cartPage = new CartPage();
const checkoutPage = new CheckoutPage();

/**
 * testIsolation: false — browser state is NOT cleared between tests.
 * A single login in `before()` covers all four tests, avoiding repeated
 * cy.visit('/') calls that trigger SauceDemo rate-limiting in CI.
 *
 * beforeEach uses cy.clearCart() as a universal reset: it navigates to the
 * cart from wherever the previous test left off (checkout-complete, checkout
 * step one, or the cart itself), removes any remaining items, then clicks
 * "Continue Shopping" to land on /inventory.html. It then adds a product and
 * navigates to the cart so every test starts on /cart.html with one item.
 */
describe('Checkout', { testIsolation: false }, () => {
  before(() => {
    cy.fixture('users').then((users) => {
      cy.login(users.standard.username, users.standard.password);
    });
  });

  beforeEach(() => {
    // Reset to inventory with an empty cart, then set up one item in the cart.
    cy.clearCart();
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
