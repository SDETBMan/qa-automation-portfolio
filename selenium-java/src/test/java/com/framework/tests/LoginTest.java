package com.framework.tests;

import com.framework.base.BaseTest;
import com.framework.driver.DriverManager;
import com.framework.pages.InventoryPage;
import com.framework.pages.LoginPage;
import com.framework.utils.ConfigReader;
import org.testng.Assert;
import org.testng.annotations.Test;

/**
 * LoginTest: Validates authentication flows on the SauceDemo login page.
 *
 * <p>WHY LOGIN TESTS EXIST: Login is the gateway to every other feature in the app.
 * If login breaks, the entire test suite fails. Catching login regressions early —
 * before they reach users — is the highest-value test you can have.
 *
 * <p>WHAT THIS CLASS COVERS: Three fundamentally different authentication scenarios:
 * <ol>
 *   <li><b>Valid login (happy path)</b> — the normal flow that real users take daily.</li>
 *   <li><b>Locked-out user (negative path)</b> — a business rule test: the app must
 *       actively block certain accounts, not just let everyone in.</li>
 *   <li><b>Empty credentials (edge case)</b> — what happens at the input boundary:
 *       the form should validate and show a helpful message, not crash.</li>
 * </ol>
 *
 * <p>TESTNG GROUPS: Each test is tagged with groups like {@code smoke} and
 * {@code regression}. Groups allow selective execution:
 * <ul>
 *   <li>{@code smoke} — the most critical tests, run first on every deployment.</li>
 *   <li>{@code regression} — the full suite, run nightly or before releases.</li>
 *   <li>{@code web} — marks this as a browser-based test (as opposed to API or unit).</li>
 * </ul>
 *
 * <p>Extends {@link BaseTest}: inherits automatic browser setup before each test
 * and cleanup after each test. LoginTest itself only needs to focus on login logic.
 */
public class LoginTest extends BaseTest {

    // ---------------------------------------------------------
    // HAPPY PATH (Smoke): Critical Path
    // Does the system allow a valid user to enter?
    // ---------------------------------------------------------

    /**
     * testValidLogin: Verifies that a valid username and password land the user
     * on the inventory/products page.
     *
     * <p>WHY THIS IS A SMOKE TEST: If this test fails, nothing else in the suite
     * can run meaningfully — every other test requires a logged-in user. Tagging
     * it as {@code smoke} ensures CI runs it first and stops early if login is broken.
     *
     * <p>CREDENTIALS FROM CONFIG: Username and password come from
     * {@code config.properties} rather than being hard-coded. This allows the same
     * test to run against different environments (dev, staging, prod) by simply
     * changing the config file — no code changes needed.
     *
     * <p>ASSERTION: Checks that the "Products" header is visible on the inventory page.
     * This is a behavioural assertion — it doesn't just verify the URL changed,
     * it verifies the page actually rendered correctly.
     */
    @Test(groups = {"smoke", "regression", "web"})
    public void testValidLogin() {
        // Page objects encapsulate how to interact with each page.
        // Tests work at the "what" level (login with these credentials),
        // not the "how" level (find element by CSS selector, click, etc.).
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());
        InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());

        System.out.println("[INFO] Executing Valid Login Test...");

        // Perform the login action — the page object handles the mechanics.
        loginPage.login(
                ConfigReader.getProperty("app_username"),
                ConfigReader.getProperty("app_password")
        );

        // Verify we reached the correct destination page.
        // "Products" header visibility is the definitive signal that login succeeded
        // and the inventory page rendered properly — not just that the URL changed.
        Assert.assertTrue(inventoryPage.isProductsHeaderDisplayed(),
                "CRITICAL FAILURE: Products header not displayed after valid login.");
    }

    // ---------------------------------------------------------
    // NEGATIVE TEST (Regression): Business Logic
    // Does the system correctly block a banned user?
    // ---------------------------------------------------------

    /**
     * testLockedOutUser: Verifies that an account flagged as locked out is blocked
     * from logging in and receives the correct error message.
     *
     * <p>WHY THIS TEST EXISTS: SauceDemo ships with a built-in "locked_out_user"
     * persona to demonstrate that the application enforces account bans. In real
     * systems, this represents fraud detection, compliance requirements, or admin
     * suspension. Testing it ensures the business rule is enforced and the
     * error message remains accurate — not confusingly generic.
     *
     * <p>WHY CHECK THE ERROR MESSAGE TEXT: An error banner appearing is necessary
     * but not sufficient. The error must say the right thing. "Sorry, this user has
     * been locked out" correctly tells the user WHY they can't log in, rather than
     * a misleading "wrong password" message that would send them in circles.
     */
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

        // Assert: the error banner must appear and carry the correct message.
        // We're not just checking that login failed — we're checking the app
        // communicated the failure reason clearly and correctly.
        String error = loginPage.getErrorMessage();
        System.out.println("[INFO] Error displayed: " + error);

        Assert.assertTrue(error.contains("Sorry, this user has been locked out"),
                "FAIL: Incorrect error message for locked out user. Found: " + error);
    }

    // ---------------------------------------------------------
    // EDGE CASE (Regression): Validation Logic
    // Does the system handle empty inputs gracefully?
    // ---------------------------------------------------------

    /**
     * testEmptyCredentials: Verifies that submitting the login form with no username
     * and no password shows a validation error rather than crashing the application.
     *
     * <p>WHY EDGE CASES MATTER: Real users accidentally click "Login" without filling
     * in the form. The app must handle this gracefully — showing a helpful message —
     * rather than throwing a server error or silently doing nothing. This also tests
     * that client-side or server-side input validation is present and working.
     *
     * <p>WHY "Username is required": This exact message is what the SauceDemo app
     * is designed to show for empty input. Asserting the specific text ensures that
     * error messaging wasn't accidentally changed to something less helpful, and
     * that the validation fires on the right field (username, not password).
     */
    @Test(groups = {"regression", "web"})
    public void testEmptyCredentials() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        System.out.println("[INFO] Executing Empty Credentials Test...");

        // Action: click login with empty strings — no username, no password.
        // The login() method in LoginPage will type these empty strings into
        // the fields and click the button, simulating a user who forgot to type.
        loginPage.login("", "");

        // Assert: The app must display a validation message.
        // Checking for "Username is required" confirms that:
        //   1. The form didn't silently pass empty inputs to the backend.
        //   2. The validation fires on username first (correct priority).
        //   3. The user gets actionable feedback about what to fix.
        String error = loginPage.getErrorMessage();

        Assert.assertTrue(error.contains("Username is required"),
                "FAIL: App crashed or allowed empty login! Found: " + error);
    }
}
