import { InventoryPage } from '../pages/InventoryPage';
import { CartPage } from '../pages/CartPage';

const inventoryPage = new InventoryPage();
const cartPage = new CartPage();

/**
 * testIsolation: false — Cypress does NOT clear cookies/localStorage/sessionStorage
 * between tests in this suite. A single login in `before()` covers all six tests,
 * avoiding repeated cy.visit('/') calls that trigger SauceDemo rate-limiting in CI.
 *
 * beforeEach calls cy.clearCart() which navigates to the cart, removes any leftover
 * items from the previous test, then clicks "Continue Shopping" to land back on
 * /inventory.html — giving every test a clean starting state.
 */
describe('Inventory', { testIsolation: false }, () => {
  before(() => {
    cy.fixture('users').then((users) => {
      cy.login(users.standard.username, users.standard.password);
    });
  });

  beforeEach(() => {
    // Remove any items left in the cart by the previous test and return to inventory.
    cy.clearCart();
  });

  // ── Smoke ──────────────────────────────────────────────────────────────────

  it('@smoke page loads all 6 products', () => {
    inventoryPage.getProductCount().should('eq', 6);
  });

  it('@smoke add item to cart increments badge to 1', () => {
    cy.fixture('products').then((data) => {
      inventoryPage.addItemToCart(data.products[0].name);
      inventoryPage.getCartBadgeCount().should('eq', '1');
    });
  });

  // ── Regression ─────────────────────────────────────────────────────────────

  it('@regression add then remove item removes cart badge', () => {
    cy.fixture('products').then((data) => {
      inventoryPage.addItemToCart(data.products[0].name);
      inventoryPage.removeItemFromCart(data.products[0].name);
      inventoryPage.cartBadgeShouldNotExist();
    });
  });

  it('@regression sort A→Z lists products alphabetically', () => {
    inventoryPage.sortBy('az');
    inventoryPage.getProductNames().then((names) => {
      const sorted = [...names].sort();
      expect(names).to.deep.equal(sorted);
    });
  });

  it('@regression sort price low→high lists cheapest first', () => {
    inventoryPage.sortBy('lohi');
    inventoryPage.getProductPrices().then((prices) => {
      const sorted = [...prices].sort((a, b) => a - b);
      expect(prices).to.deep.equal(sorted);
    });
  });

  it('@regression navigate to cart shows added item', () => {
    cy.fixture('products').then((data) => {
      const product = data.products[0];
      inventoryPage.addItemToCart(product.name);
      inventoryPage.goToCart();
      cartPage.assertItemInCart(product.name);
    });
  });
});
