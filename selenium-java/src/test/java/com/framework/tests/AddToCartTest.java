package com.framework.tests;

import com.framework.base.BaseTest;
import com.framework.driver.DriverManager;
import com.framework.pages.CartPage;
import com.framework.pages.InventoryPage;
import com.framework.pages.LoginPage;
import com.framework.utils.ConfigReader;
import org.testng.Assert;
import org.testng.annotations.Test;

public class AddToCartTest extends BaseTest {

    // ---------------------------------------------------------
    // HAPPY PATH (Smoke): Critical User Flow
    // ---------------------------------------------------------
    @Test(groups = {"smoke", "regression", "web"})
    public void testAddBackpackToCart() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());

        // Step 1: Login
        loginPage.login(ConfigReader.getProperty("app_username"), ConfigReader.getProperty("app_password"));

        // Step 2: Pre-Condition Check
        Assert.assertEquals(inventoryPage.getCartItemCount(), 0, "Pre-condition Failed: Cart was not empty.");

        // Step 3: Action - Add 1 Item
        inventoryPage.addToCart("Sauce Labs Backpack");

        // Step 4: UI Sync
        inventoryPage.waitForCartBadge();
        Assert.assertEquals(inventoryPage.getCartItemCount(), 1, "Inventory page badge did not update.");

        // Step 5: Navigation - Move to Cart Page
        CartPage cartPage = inventoryPage.goToCart();

        // Step 6: Final Validation - Verify item is actually in the cart list
        Assert.assertTrue(cartPage.isItemInCart("Sauce Labs Backpack"),
                "VALIDATION FAILED: Item added but not found on Cart Page!");

        System.out.println("[PASS] Backpack successfully added and verified in cart.");
    }

    // ---------------------------------------------------------
    // EDGE CASE (Regression): Boundary Testing
    // Does the system handle multiple rapid additions correctly?
    // ---------------------------------------------------------
    @Test(groups = {"regression", "web"})
    public void testAddMultipleItemsToCart() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());

        loginPage.login(ConfigReader.getProperty("app_username"), ConfigReader.getProperty("app_password"));

        // Action: Add 3 specific items
        inventoryPage.addToCart("Sauce Labs Backpack");
        inventoryPage.addToCart("Sauce Labs Bike Light");
        inventoryPage.addToCart("Sauce Labs Bolt T-Shirt");

        // UI Sync
        inventoryPage.waitForCartBadge();

        // Validation: Expect 3
        int currentCount = inventoryPage.getCartItemCount();
        Assert.assertEquals(currentCount, 3, "Cart count failed to reach 3.");
    }

    // ---------------------------------------------------------
    // NEGATIVE / STATE TEST (Regression): Undo Action
    // Can the user correct a mistake (Remove item)?
    // ---------------------------------------------------------
    @Test(groups = {"regression", "web"})
    public void testAddAndRemoveItem() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());

        // 1. LOGIN
        loginPage.login(ConfigReader.getProperty("app_username"), ConfigReader.getProperty("app_password"));

        // 2. PRE-CHECK: Verify clean state before doing anything
        // This proves your @AfterMethod cleanup worked
        Assert.assertEquals(inventoryPage.getCartItemCount(), 0,
                "TEST ABORTED: Ghost items detected in cart at start of test!");

        // 3. ACT: Add item
        inventoryPage.addToCart("Sauce Labs Backpack");

        // 4. SYNC: Wait for badge visibility then assert count — uses page object locator, not raw By
        inventoryPage.waitForCartBadge();
        Assert.assertEquals(inventoryPage.getCartItemCount(), 1, "Cart badge count was not 1 after adding item.");

        // 5. ACT: Remove the item
        inventoryPage.removeFromCart("Sauce Labs Backpack");

        // 6. ASSERT: Final verification that count is 0
        Assert.assertEquals(inventoryPage.getCartItemCount(), 0,
                "Cart count did not return to 0 after removal.");
    }

    @Test(groups = {"regression", "web"})
    public void testNavigateToCheckout() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());

        loginPage.login(ConfigReader.getProperty("app_username"), ConfigReader.getProperty("app_password"));
        inventoryPage.addToCart("Sauce Labs Backpack");

        // SYNC: Wait for badge visibility — replaces both the inline By.className and the Thread.sleep
        inventoryPage.waitForCartBadge();

        CartPage cartPage = inventoryPage.goToCart();
        cartPage.clickCheckout();

        boolean isOnCheckoutPage = cartPage.waitForUrlToContain("checkout-step-one");
        Assert.assertTrue(isOnCheckoutPage, "Failed to navigate to Checkout Step 1. Current URL: " + DriverManager.getDriver().getCurrentUrl());
    }
}
