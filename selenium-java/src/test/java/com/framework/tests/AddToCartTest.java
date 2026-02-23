package com.framework.tests;

import com.framework.base.BaseTest;
import com.framework.driver.DriverManager;
import com.framework.pages.CartPage;
import com.framework.pages.InventoryPage;
import com.framework.pages.LoginPage;
import com.framework.utils.ConfigReader;
import org.testng.Assert;
import org.testng.annotations.Test;

/**
 * AddToCartTest: Validates the core e-commerce cart workflow on SauceDemo.
 *
 * <p>WHY CART TESTS ARE CRITICAL: In any e-commerce application, the ability to
 * add items to a cart and proceed to checkout is the primary revenue-generating
 * user journey. If any step in this flow is broken — add fails, badge doesn't
 * update, item isn't in the cart, checkout button doesn't navigate — users cannot
 * make purchases and the business loses revenue.
 *
 * <p>WHAT THIS CLASS COVERS: Four distinct scenarios that progressively test
 * the cart lifecycle:
 * <ol>
 *   <li><b>Add one item (smoke)</b> — the critical path: add → verify badge → open
 *       cart → verify item is listed there.</li>
 *   <li><b>Add multiple items (regression)</b> — boundary/volume: does the counter
 *       correctly track multiple additions?</li>
 *   <li><b>Add then remove (regression)</b> — state reversal: can the user undo
 *       their action and return to a clean cart?</li>
 *   <li><b>Navigate to checkout (regression)</b> — end-to-end: does the checkout
 *       button actually navigate to the checkout page?</li>
 * </ol>
 *
 * <p>PRE-CONDITION CHECKS: Several tests assert that the cart is empty (count = 0)
 * before acting. This is a best practice — it proves that the test's own starting
 * state is clean, rather than assuming the previous test's cleanup worked correctly.
 *
 * <p>Extends {@link BaseTest}: inherits automatic browser launch before each test
 * and state-clearing teardown after each test.
 */
public class AddToCartTest extends BaseTest {

    // ---------------------------------------------------------
    // HAPPY PATH (Smoke): Critical User Flow
    // ---------------------------------------------------------

    /**
     * testAddBackpackToCart: Validates the complete add-to-cart flow for a
     * single product — the most fundamental e-commerce action.
     *
     * <p>WHY THIS IS A SMOKE TEST: If you can't add an item to the cart, the
     * entire purchase flow is broken. This test must pass before any deployment
     * reaches users. It's the single most important test in this class.
     *
     * <p>PRE-CONDITION ASSERTION: Before adding anything, the test verifies the
     * cart badge shows 0. This proves the test environment is clean and that any
     * badge count change we observe is caused by THIS test's actions, not leftover
     * state from a previous test.
     *
     * <p>MULTI-STEP VERIFICATION: The test doesn't just verify the badge count —
     * it also navigates to the cart page and checks that the item actually appears
     * in the cart list. Badge count = 1 is a UI signal; item in cart list = the
     * data persisted correctly. Both checks together provide full confidence.
     */
    @Test(groups = {"smoke", "regression", "web"})
    public void testAddBackpackToCart() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());

        // Step 1: Log in to access the inventory page.
        loginPage.login(ConfigReader.getProperty("app_username"), ConfigReader.getProperty("app_password"));

        // Step 2: Pre-condition check — cart must start empty.
        // If this assertion fails, it means teardown from a previous test didn't
        // clear the cart, which would make the subsequent count assertions unreliable.
        Assert.assertEquals(inventoryPage.getCartItemCount(), 0, "Pre-condition Failed: Cart was not empty.");

        // Step 3: Add the backpack to the cart by its displayed product name.
        inventoryPage.addToCart("Sauce Labs Backpack");

        // Step 4: Wait for the cart badge to appear, then verify the count is 1.
        // waitForCartBadge() uses an explicit wait — it polls until the badge
        // becomes visible, handling the brief animation delay without a hard sleep.
        inventoryPage.waitForCartBadge();
        Assert.assertEquals(inventoryPage.getCartItemCount(), 1, "Inventory page badge did not update.");

        // Step 5: Navigate to the cart page.
        CartPage cartPage = inventoryPage.goToCart();

        // Step 6: Confirm the item actually appears in the cart's item list.
        // This is the definitive data-layer check — the cart API/state persisted
        // the add, not just the UI badge updating as a visual trick.
        Assert.assertTrue(cartPage.isItemInCart("Sauce Labs Backpack"),
                "VALIDATION FAILED: Item added but not found on Cart Page!");

        System.out.println("[PASS] Backpack successfully added and verified in cart.");
    }

    // ---------------------------------------------------------
    // EDGE CASE (Regression): Boundary Testing
    // Does the system handle multiple rapid additions correctly?
    // ---------------------------------------------------------

    /**
     * testAddMultipleItemsToCart: Verifies that adding three distinct products
     * results in a cart badge showing exactly 3.
     *
     * <p>WHY TEST MULTIPLE ADDITIONS: Adding items in rapid succession is a common
     * real-world usage pattern. The test checks that the application's state
     * management handles concurrent additions correctly — the badge must accurately
     * reflect the true cart size, not get stuck at 1 or skip values.
     *
     * <p>WHY THREE ITEMS: Three is enough to validate counting beyond 1 (ruling out
     * a "stuck at 1" bug) while keeping the test fast. Each item has a distinct name,
     * confirming that different SKUs are all tracked independently.
     */
    @Test(groups = {"regression", "web"})
    public void testAddMultipleItemsToCart() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());

        loginPage.login(ConfigReader.getProperty("app_username"), ConfigReader.getProperty("app_password"));

        // Add three different products — each click should increment the badge count.
        inventoryPage.addToCart("Sauce Labs Backpack");
        inventoryPage.addToCart("Sauce Labs Bike Light");
        inventoryPage.addToCart("Sauce Labs Bolt T-Shirt");

        // Wait for the badge to reflect all three additions before asserting.
        inventoryPage.waitForCartBadge();

        // The badge must show exactly 3 — no items dropped, no double-counts.
        int currentCount = inventoryPage.getCartItemCount();
        Assert.assertEquals(currentCount, 3, "Cart count failed to reach 3.");
    }

    // ---------------------------------------------------------
    // NEGATIVE / STATE TEST (Regression): Undo Action
    // Can the user correct a mistake (Remove item)?
    // ---------------------------------------------------------

    /**
     * testAddAndRemoveItem: Verifies that adding an item and then removing it
     * returns the cart to its original empty state (badge count = 0).
     *
     * <p>WHY TEST REMOVAL: Accidental additions are common — users browsing and
     * clicking "Add to Cart" by mistake need to be able to undo that action.
     * If "Remove" doesn't work, users are forced to abandon carts or complete
     * purchases they didn't intend, causing frustration and chargebacks.
     *
     * <p>PRE-CONDITION AND POST-CONDITION ASSERTIONS: This test asserts the count
     * is 0 both BEFORE adding (proving a clean start) and AFTER removing (proving
     * the removal worked). The two-sided assertion pattern ensures the test detects
     * both "remove did nothing" and "remove reduced count but not to 0" failure modes.
     */
    @Test(groups = {"regression", "web"})
    public void testAddAndRemoveItem() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());

        // Step 1: Log in.
        loginPage.login(ConfigReader.getProperty("app_username"), ConfigReader.getProperty("app_password"));

        // Step 2: Pre-condition check — confirm the cart is clean before the test acts.
        // This validates that @AfterMethod teardown from any previous test worked.
        // "Ghost items in cart" would make the subsequent count assertions meaningless.
        Assert.assertEquals(inventoryPage.getCartItemCount(), 0,
                "TEST ABORTED: Ghost items detected in cart at start of test!");

        // Step 3: Add the item to the cart.
        inventoryPage.addToCart("Sauce Labs Backpack");

        // Step 4: Wait for the badge to update, then confirm count is 1.
        // waitForCartBadge() uses an explicit wait — safer than Thread.sleep().
        inventoryPage.waitForCartBadge();
        Assert.assertEquals(inventoryPage.getCartItemCount(), 1, "Cart badge count was not 1 after adding item.");

        // Step 5: Remove the item that was just added.
        inventoryPage.removeFromCart("Sauce Labs Backpack");

        // Step 6: Confirm the badge count returned to 0.
        // A value of 0 proves the item was fully removed from the cart state,
        // not just hidden from the badge visually.
        Assert.assertEquals(inventoryPage.getCartItemCount(), 0,
                "Cart count did not return to 0 after removal.");
    }

    /**
     * testNavigateToCheckout: Verifies that clicking "Checkout" from the cart
     * page navigates to the checkout step-one page.
     *
     * <p>WHY TEST NAVIGATION TO CHECKOUT: The checkout button is the final step
     * before order confirmation. If the button doesn't navigate correctly — due to
     * a broken link, JavaScript error, or missing route — users cannot complete
     * purchases. Catching this in automation prevents silent revenue loss.
     *
     * <p>URL-BASED ASSERTION: Checking that the URL contains "checkout-step-one"
     * is a reliable navigation assertion. It doesn't depend on specific page text
     * that might be internationalised or changed — the URL path is a stable
     * contract between the frontend routing and this test.
     */
    @Test(groups = {"regression", "web"})
    public void testNavigateToCheckout() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());

        // Log in and add an item — a non-empty cart is required to proceed to checkout.
        loginPage.login(ConfigReader.getProperty("app_username"), ConfigReader.getProperty("app_password"));
        inventoryPage.addToCart("Sauce Labs Backpack");

        // Wait for the badge — confirms the item was registered before navigating.
        // Proceeding to cart without waiting could result in an empty cart page.
        inventoryPage.waitForCartBadge();

        // Navigate to the cart page, then click the "Checkout" button.
        CartPage cartPage = inventoryPage.goToCart();
        cartPage.clickCheckout();

        // Wait for URL to contain "checkout-step-one" — this is the SauceDemo
        // URL path for the first step of checkout (enter customer information).
        // waitForUrlToContain() uses an explicit wait rather than asserting immediately,
        // giving the page transition time to complete.
        boolean isOnCheckoutPage = cartPage.waitForUrlToContain("checkout-step-one");
        Assert.assertTrue(isOnCheckoutPage, "Failed to navigate to Checkout Step 1. Current URL: " + DriverManager.getDriver().getCurrentUrl());
    }
}
