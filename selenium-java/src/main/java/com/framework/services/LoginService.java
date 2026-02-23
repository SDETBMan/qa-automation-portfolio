package com.framework.services;

import com.framework.pages.InventoryPage;
import com.framework.pages.LoginPage;

/**
 * LoginService: Orchestrates the login workflow by coordinating LoginPage and InventoryPage.
 *
 * WHY THIS CLASS EXISTS — The Service Layer Pattern:
 * In a framework that only uses Page Objects, tests directly call page object methods.
 * That works fine, but it makes tests harder to unit test because page objects require a
 * real browser. The Service Layer solves this by sitting between the test and the page objects:
 *
 *   Test → LoginService → [LoginPage, InventoryPage]
 *
 * Benefits:
 *   1. Tests become shorter and more readable (one service call vs. multiple page calls)
 *   2. Business logic ("login AND verify the products page loaded") lives in one place
 *   3. UNIT TESTING WITHOUT A BROWSER: LoginServiceTest uses Mockito to replace the real
 *      LoginPage and InventoryPage with fake (mock) objects. The service is tested in
 *      milliseconds without launching Chrome or touching a website.
 *
 * WHY CONSTRUCTOR INJECTION (vs. creating page objects inside the methods):
 * The page objects are passed in via the constructor rather than created inside this class.
 * This is called "constructor dependency injection." It is the key design choice that makes
 * unit testing possible — if LoginService created its own LoginPage internally, a unit test
 * would need a real browser. By accepting them as parameters, a unit test can pass in mock
 * objects instead.
 *
 * For recruiters: The service layer plus constructor injection plus Mockito tests demonstrates
 * awareness of software design principles (Dependency Injection, Separation of Concerns)
 * that go beyond basic Selenium scripting.
 */
public class LoginService {

    // Dependencies are stored as final fields — they cannot be reassigned after construction,
    // which makes this class's behavior predictable and thread-safe.
    private final LoginPage loginPage;
    private final InventoryPage inventoryPage;

    /**
     * Constructor: Receives the page objects this service will coordinate.
     *
     * WHY THIS DESIGN:
     * In real test execution, the test class creates real LoginPage and InventoryPage instances
     * backed by a live WebDriver, then passes them here. In unit tests, mock (fake) implementations
     * are passed instead. The service code itself is identical in both cases — it doesn't know or
     * care whether it is talking to a real browser or a mock object.
     *
     * @param loginPage     The page object representing the login screen
     * @param inventoryPage The page object representing the products/inventory screen
     */
    public LoginService(LoginPage loginPage, InventoryPage inventoryPage) {
        this.loginPage = loginPage;
        this.inventoryPage = inventoryPage;
    }

    /**
     * Performs a complete login and verifies the products page loaded successfully.
     *
     * WHY THIS WRAPS TWO STEPS:
     * Login is rarely tested in isolation — what matters is not just that the login form was
     * submitted, but that the application responded correctly by loading the products page.
     * Bundling both steps into one service method enforces this complete verification
     * and prevents tests from short-circuiting with a "login passed" result when the
     * products page never appeared.
     *
     * @param username The login username
     * @param password The login password
     * @return true if login succeeded and the products header appeared; false otherwise
     */
    public boolean loginAndVerify(String username, String password) {
        loginPage.login(username, password);
        return inventoryPage.isProductsHeaderDisplayed();
    }

    /**
     * Retrieves the error message text currently displayed on the login page.
     *
     * WHY THIS IS A SEPARATE METHOD:
     * Negative login tests (wrong password, locked out user) need to inspect the error
     * message to verify the correct failure is shown. Exposing this as a service method
     * allows unit tests to verify that the service correctly surfaces login errors,
     * without those unit tests needing to interact with a real browser.
     *
     * @return The error message text from the login page, or empty string if none is shown
     */
    public String getLoginError() {
        return loginPage.getErrorMessage();
    }
}
