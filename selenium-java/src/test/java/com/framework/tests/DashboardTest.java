package com.framework.tests;

import com.framework.base.BaseTest;
import com.framework.driver.DriverManager;
import com.framework.pages.DashboardPage;
import com.framework.pages.LoginPage;
import com.framework.utils.ConfigReader;
import org.testng.Assert;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

/**
 * DashboardTest: Validates user access, navigation, and session management
 * on the SauceDemo dashboard (inventory/products page).
 *
 * <p>WHY DASHBOARD TESTS: The dashboard is the first page a user sees after
 * logging in. If the cart icon is missing, if the page header is wrong, or
 * if logout doesn't work, the user experience is broken even though login
 * technically succeeded. These tests prove the post-login state is correct.
 *
 * <p>WHAT THIS CLASS COVERS:
 * <ol>
 *   <li><b>Multi-user access (data-driven)</b> — different SauceDemo personas
 *       (standard user, problem user, performance glitch user) should all reach
 *       the same functional dashboard despite their different quirks.</li>
 *   <li><b>Logout flow (smoke)</b> — verifies the user can end their session
 *       and is returned to the login page.</li>
 *   <li><b>Direct URL access (security)</b> — verifies unauthenticated users
 *       are redirected to login when they try to skip it by navigating directly
 *       to the dashboard URL.</li>
 * </ol>
 *
 * <p>Extends {@link BaseTest}: inherits automatic browser setup and teardown.
 */
public class DashboardTest extends BaseTest {

    // ---------------------------------------------------------
    // DATA-DRIVEN TEST (Regression)
    // Runs 3 times: Standard, Visual Bug User, Performance Glitch User
    // ---------------------------------------------------------

    /**
     * testUserCanAccessDashboard: Data-driven test that verifies all three
     * SauceDemo user personas can log in and see a functional dashboard.
     *
     * <p>WHY DATA-DRIVEN: Rather than writing three nearly identical tests,
     * {@code @DataProvider} feeds this single test method with different
     * username/password pairs. TestNG runs the method once per row in the
     * returned table — three inputs produce three test cases. This is the
     * "Parameterised Test" pattern: more coverage with less code.
     *
     * <p>WHAT THE PERSONAS TEST:
     * <ul>
     *   <li>{@code standard_user} — the baseline happy path.</li>
     *   <li>{@code problem_user} — has broken images; tests that the UI structure
     *       (headers, cart icon) still loads even when assets are corrupted.</li>
     *   <li>{@code performance_glitch_user} — deliberately slow (5 s login delay);
     *       tests that the framework's timeouts handle real-world latency without
     *       flaking.</li>
     * </ul>
     *
     * @param username The login username for this test iteration.
     * @param password The login password for this test iteration.
     */
    @Test(groups = {"regression", "web"}, dataProvider = "loginData")
    public void testUserCanAccessDashboard(String username, String password) {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        DashboardPage dashboardPage = new DashboardPage(DriverManager.getDriver());

        System.out.println("[INFO] Testing Persona: " + username);

        // Step 1: Log in with the current test iteration's persona credentials.
        loginPage.login(username, password);

        // Step 2: Verify the cart icon is visible — this is a key functional
        // element present on every dashboard. Its absence indicates a broken page.
        Assert.assertTrue(dashboardPage.isCartIconDisplayed(),
                "CRITICAL: Shopping cart icon missing for user: " + username);

        // Step 3: Verify the page header says "Products" — confirming the user
        // landed on the correct page, not a blank or error page.
        // equalsIgnoreCase handles any potential casing inconsistency in the app.
        String headerText = dashboardPage.getWelcomeMessageText();
        Assert.assertTrue(headerText.equalsIgnoreCase("Products"),
                "VALIDATION FAILED: Header mismatch. Found: " + headerText);
    }

    // ---------------------------------------------------------
    // HAPPY PATH (Smoke): Logout Flow
    // ---------------------------------------------------------

    /**
     * testLogoutFlow: Verifies that clicking "Logout" from the dashboard ends
     * the session and returns the user to the login page.
     *
     * <p>WHY TEST LOGOUT: Logout is a security feature, not just a UX convenience.
     * If logout doesn't work, another person using the same computer could access
     * the previous user's account. This test confirms that the session is truly
     * terminated — the login button reappearing is proof that the app considers
     * the user unauthenticated.
     *
     * <p>WHY THIS IS ALSO A SMOKE TEST: Along with valid login, logout is part of
     * the most critical user journey. A broken logout means no user can safely
     * exit their session.
     */
    @Test(groups = {"smoke", "regression", "web"})
    public void testLogoutFlow() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        DashboardPage dashboardPage = new DashboardPage(DriverManager.getDriver());

        // Step 1: Establish a session by logging in with valid credentials.
        loginPage.login(ConfigReader.getProperty("app_username"), ConfigReader.getProperty("app_password"));

        // Step 2: Click the logout button (found in the hamburger menu).
        dashboardPage.clickLogoutButton();

        // Step 3: Assert that the login button is now visible.
        // The login button is only present on the login page —
        // its visibility confirms the session was terminated and the user
        // was redirected back to the unauthenticated entry point.
        Assert.assertTrue(loginPage.isLoginButtonDisplayed(),
                "SESSION ERROR: Login button not visible after logout.");
    }

    // ---------------------------------------------------------
    // NEGATIVE / SECURITY TEST (Regression)
    // Can a user bypass login by typing the URL directly?
    // ---------------------------------------------------------

    /**
     * testDirectAccessWithoutLogin: Verifies that an unauthenticated user who
     * navigates directly to the inventory URL is redirected to the login page.
     *
     * <p>WHY THIS IS A SECURITY TEST: URL-based access control is a common
     * vulnerability. Without this protection, anyone who knows the URL
     * "https://www.saucedemo.com/inventory.html" could bypass the login screen
     * entirely. This test confirms the application enforces authentication
     * at the server/application level, not just by hiding the URL.
     *
     * <p>This pattern is important in real applications too — simply not showing
     * a link to a protected page is not security. The server must also reject
     * unauthenticated requests to that page.
     *
     * <p>URL CONSTRUCTION FROM CONFIG: Building the URL as {@code base_url + "inventory.html"}
     * means this test works correctly across all environments without code changes —
     * the base URL is the only thing that differs between dev, staging, and prod.
     */
    @Test(groups = {"regression", "web", "security"})
    public void testDirectAccessWithoutLogin() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        // Attempt to force-navigate to the dashboard without logging in first.
        // This simulates a user — or an attacker — trying to skip the auth step.
        // URL is constructed from config so it works across all environments.
        String dashboardUrl = ConfigReader.getProperty("url") + "inventory.html";
        DriverManager.getDriver().get(dashboardUrl);

        // Assert: the app must redirect unauthenticated users back to the login page.
        // The login button appearing proves we were sent to the login page —
        // not that we were served the inventory page without credentials.
        Assert.assertTrue(loginPage.isLoginButtonDisplayed(),
                "SECURITY FAILURE: Unauthenticated user was able to access Dashboard!");

        // Optional additional check: if the app shows an error banner, verify its message.
        // This is conditional because some apps redirect silently without a message.
        String error = loginPage.getErrorMessage();
        if (!error.isEmpty()) {
            Assert.assertTrue(error.contains("only access"), "Unexpected error message: " + error);
        }
    }

    /**
     * getLoginData: TestNG DataProvider that supplies username/password pairs
     * for the data-driven {@link #testUserCanAccessDashboard} test.
     *
     * <p>WHY USE CONFIG FOR PERSONAS: Usernames and passwords are externalised
     * to {@code config.properties} so they can be updated without changing test code.
     * This is especially important for CI environments where credentials might differ
     * or be injected as environment variables.
     *
     * <p>RETURN FORMAT: A 2D Object array where each inner array is one test case.
     * Column 0 = username, Column 1 = password. TestNG maps these to the method
     * parameters by position.
     *
     * @return A 2D array of {username, password} pairs, one row per persona.
     */
    @DataProvider(name = "loginData")
    public Object[][] getLoginData() {
        String password = ConfigReader.getProperty("app_password");
        return new Object[][]{
                // Standard user: the baseline happy path persona
                {ConfigReader.getProperty("persona.standard"),     password},
                // "problem_user" has broken images — good for testing resilience
                // when the UI has rendering issues but the structure still exists
                {ConfigReader.getProperty("persona.problem"),      password},
                // "performance_glitch_user" has a 5-second login delay — tests
                // that the framework's implicit/explicit waits handle real latency
                {ConfigReader.getProperty("persona.performance"),  password}
        };
    }
}
