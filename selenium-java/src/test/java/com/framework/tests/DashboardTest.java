package com.framework.tests;

import com.framework.base.BaseTest;
import com.framework.driver.DriverManager;
import com.framework.pages.DashboardPage;
import com.framework.pages.LoginPage;
import com.framework.utils.ConfigReader;
import org.testng.Assert;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

public class DashboardTest extends BaseTest {

    // ---------------------------------------------------------
    // DATA-DRIVEN TEST (Regression)
    // Runs 3 times: Standard, Visual Bug User, Performance Glitch User
    // ---------------------------------------------------------
    @Test(groups = {"regression", "web"}, dataProvider = "loginData")
    public void testUserCanAccessDashboard(String username, String password) {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        DashboardPage dashboardPage = new DashboardPage(DriverManager.getDriver());

        System.out.println("[INFO] Testing Persona: " + username);

        // 1. Unified Login
        loginPage.login(username, password);

        // 2. Functional UI Assertions
        Assert.assertTrue(dashboardPage.isCartIconDisplayed(),
                "CRITICAL: Shopping cart icon missing for user: " + username);

        String headerText = dashboardPage.getWelcomeMessageText();

        // Products is the standard header for Swag Labs
        Assert.assertTrue(headerText.equalsIgnoreCase("Products"),
                "VALIDATION FAILED: Header mismatch. Found: " + headerText);
    }

    // ---------------------------------------------------------
    // HAPPY PATH (Smoke): Logout Flow
    // ---------------------------------------------------------
    @Test(groups = {"smoke", "regression", "web"})
    public void testLogoutFlow() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        DashboardPage dashboardPage = new DashboardPage(DriverManager.getDriver());

        // 1. Establish session
        loginPage.login(ConfigReader.getProperty("app_username"), ConfigReader.getProperty("app_password"));

        // 2. Execute Logout
        dashboardPage.clickLogoutButton();

        // 3. Verify Session Termination
        Assert.assertTrue(loginPage.isLoginButtonDisplayed(),
                "SESSION ERROR: Login button not visible after logout.");
    }

    // ---------------------------------------------------------
    // NEGATIVE / SECURITY TEST (Regression)
    // Can a user bypass login by typing the URL directly?
    // ---------------------------------------------------------
    @Test(groups = {"regression", "web", "security"})
    public void testDirectAccessWithoutLogin() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        // 1. Try to force navigate to Dashboard URL without logging in.
        //    URL is built from config so it works across all environments.
        String dashboardUrl = ConfigReader.getProperty("url") + "inventory.html";
        DriverManager.getDriver().get(dashboardUrl);

        // 2. Assert: Application should kick us back to Login
        Assert.assertTrue(loginPage.isLoginButtonDisplayed(),
                "SECURITY FAILURE: Unauthenticated user was able to access Dashboard!");

        // Optional: specific error message check
        String error = loginPage.getErrorMessage();
        if (!error.isEmpty()) {
            Assert.assertTrue(error.contains("only access"), "Unexpected error message: " + error);
        }
    }

    /**
     * Test Data Provider: Covers standard, UI-bug, and latency-heavy user accounts.
     * Persona usernames and the shared password are sourced from config.properties
     * so they can be overridden per environment without touching test code.
     */
    @DataProvider(name = "loginData")
    public Object[][] getLoginData() {
        String password = ConfigReader.getProperty("app_password");
        return new Object[][]{
                {ConfigReader.getProperty("persona.standard"),     password},
                // "problem_user" has broken images (good for checking resilience)
                {ConfigReader.getProperty("persona.problem"),      password},
                // "performance_glitch_user" takes 5 seconds to load (good for checking timeouts)
                {ConfigReader.getProperty("persona.performance"),  password}
        };
    }
}
