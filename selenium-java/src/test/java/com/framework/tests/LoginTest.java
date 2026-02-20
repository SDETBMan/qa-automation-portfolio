package com.framework.tests;

import com.framework.base.BaseTest;
import com.framework.driver.DriverManager;
import com.framework.pages.InventoryPage;
import com.framework.pages.LoginPage;
import com.framework.utils.ConfigReader;
import org.testng.Assert;
import org.testng.annotations.Test;

/**
 * LoginTest: Validates authentication flows.
 * Covers: Valid Login (Smoke), Locked Out User (Negative), Empty Input (Edge).
 */
public class LoginTest extends BaseTest {

    // ---------------------------------------------------------
    // HAPPY PATH (Smoke): Critical Path
    // Does the system allow a valid user to enter?
    // ---------------------------------------------------------
    @Test(groups = {"smoke", "regression", "web"})
    public void testValidLogin() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());

        System.out.println("[INFO] Executing Valid Login Test...");

        loginPage.login(
                ConfigReader.getProperty("app_username"),
                ConfigReader.getProperty("app_password")
        );

        Assert.assertTrue(inventoryPage.isProductsHeaderDisplayed(),
                "CRITICAL FAILURE: Products header not displayed after valid login.");
    }

    // ---------------------------------------------------------
    // NEGATIVE TEST (Regression): Business Logic
    // Does the system correctly block a banned user?
    // ---------------------------------------------------------
    @Test(groups = {"regression", "web"})
    public void testLockedOutUser() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        System.out.println("[INFO] Executing Locked Out User Test...");

        // Credentials sourced from config so the locked-out persona can be
        // swapped per environment without touching test code.
        loginPage.login(
                ConfigReader.getProperty("locked_out_username"),
                ConfigReader.getProperty("app_password")
        );

        // Assert: Expect an error, not the inventory page
        String error = loginPage.getErrorMessage();
        System.out.println("[INFO] Error displayed: " + error);

        Assert.assertTrue(error.contains("Sorry, this user has been locked out"),
                "FAIL: Incorrect error message for locked out user. Found: " + error);
    }

    // ---------------------------------------------------------
    // EDGE CASE (Regression): Validation Logic
    // Does the system handle empty inputs gracefully?
    // ---------------------------------------------------------
    @Test(groups = {"regression", "web"})
    public void testEmptyCredentials() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        System.out.println("[INFO] Executing Empty Credentials Test...");

        // Action: Click login without typing anything
        loginPage.login("", "");

        // Assert: HTML5 validation or JS error should appear
        String error = loginPage.getErrorMessage();

        Assert.assertTrue(error.contains("Username is required"),
                "FAIL: App crashed or allowed empty login! Found: " + error);
    }
}
