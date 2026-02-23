package com.saucedemo.services;

import com.saucedemo.pages.InventoryPage;
import com.saucedemo.pages.LoginPage;

/**
 * LoginService: A service-layer class that orchestrates the login user flow by
 * coordinating two page objects — LoginPage and InventoryPage.
 *
 * <p>WHY A SERVICE LAYER EXISTS (Separation of Concerns): In a basic Page Object Model,
 * step definitions talk to page objects directly. As flows become more complex — spanning
 * multiple pages or requiring conditional logic — step definitions can become cluttered
 * with orchestration code that really belongs elsewhere. A service layer sits between
 * step definitions and page objects, owning multi-page workflows so each layer stays
 * focused on a single responsibility:
 * <ul>
 *   <li>Step definitions: map Gherkin sentences to method calls.</li>
 *   <li>Service classes: orchestrate multi-page flows and business rules.</li>
 *   <li>Page objects: interact with a single screen's elements.</li>
 * </ul>
 *
 * <p>WHY THIS IS IDEAL FOR MOCKITO UNIT TESTS: This class's dependencies
 * ({@link LoginPage} and {@link InventoryPage}) are injected via the constructor
 * rather than instantiated inside the class. This is called Dependency Injection (DI).
 * It means that in unit tests, real page objects (which require a running browser)
 * can be replaced with Mockito mock objects — fake implementations that return
 * controlled values without launching a browser. The result is a unit test that
 * runs in milliseconds and tests only this class's logic, not Selenium's.
 *
 * <p>This class is the target of {@link com.saucedemo.unit.LoginServiceTest}.
 */
public class LoginService {

    /**
     * The page object representing the login screen.
     * Injected via constructor to allow mocking in unit tests.
     */
    private final LoginPage loginPage;

    /**
     * The page object representing the inventory/products screen.
     * Injected via constructor to allow mocking in unit tests.
     */
    private final InventoryPage inventoryPage;

    /**
     * Constructor: injects the page object dependencies.
     *
     * <p>CONSTRUCTOR INJECTION: By receiving dependencies as constructor parameters
     * rather than creating them with {@code new} inside the class, this service
     * remains decoupled from any specific page object implementation. In production
     * tests, real page objects backed by Selenium are passed in. In unit tests,
     * Mockito mocks are passed in instead — the service code is identical in both cases.
     *
     * @param loginPage     the LoginPage page object (or mock) to use for login actions
     * @param inventoryPage the InventoryPage page object (or mock) to use for post-login checks
     */
    public LoginService(LoginPage loginPage, InventoryPage inventoryPage) {
        this.loginPage = loginPage;
        this.inventoryPage = inventoryPage;
    }

    /**
     * Performs login with the given credentials and returns whether the products
     * page loaded successfully afterwards.
     *
     * <p>This method models the complete login verification flow:
     * <ol>
     *   <li>Enter credentials and submit the login form.</li>
     *   <li>Check whether the inventory/products header is now visible.</li>
     * </ol>
     * Returning a boolean from this method keeps the caller (step definition or unit
     * test) in control of how to handle success vs. failure — the service does not
     * make assertions itself, which makes it easier to unit test.
     *
     * @param username the username to log in with
     * @param password the password to log in with
     * @return true if the products page header is displayed after login; false if login failed
     */
    /**
     * Performs login and returns true if the products page loaded successfully.
     */
    public boolean loginAndVerify(String username, String password) {
        loginPage.login(username, password);
        return inventoryPage.isProductsHeaderDisplayed();
    }

    /**
     * Checks whether the login page is currently showing an error message.
     *
     * <p>Called after a failed {@link #loginAndVerify} to confirm that the application
     * correctly surfaced an error to the user. Separating this into its own method
     * allows unit tests to verify both the return value of {@code loginAndVerify} AND
     * the error state independently.
     *
     * @return true if an error message is displayed on the login page, false otherwise
     */
    /**
     * Returns true if an error message is currently displayed on the login page.
     */
    public boolean hasLoginError() {
        return loginPage.isErrorDisplayed();
    }
}
