package com.saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

/**
 * LoginPage: Page Object representing the SauceDemo login screen.
 *
 * <p>WHY A DEDICATED PAGE OBJECT: The Page Object Model (POM) is a design pattern
 * that creates one class per screen of the application under test. Each class owns
 * the locators for that screen's elements and exposes human-readable action methods.
 * This means that if the login form's HTML ever changes (e.g., the username field
 * changes from {@code id="user-name"} to {@code id="username"}), the fix is made
 * in exactly one place — this file — rather than hunting through dozens of test files.
 *
 * <p>GRANULAR vs. COMPOSITE METHODS: This page exposes both fine-grained methods
 * ({@code enterUsername}, {@code enterPassword}, {@code clickLogin}) and a
 * convenience composite ({@code login}). The fine-grained methods are used by
 * Cucumber step definitions so each Gherkin step maps to one clear action.
 * The composite exists for situations where the entire login flow is just setup
 * noise before the real test begins.
 *
 * <p>This class extends {@link BasePage}, inheriting the shared driver, wait,
 * and wrapper methods (click, sendKeys, getText, etc.).
 */
public class LoginPage extends BasePage {

    // --- Element Locators ---
    // Locators are stored as private fields at the top of the class.
    // This keeps them in one place: if a locator changes, you update it here
    // and every method in this class automatically uses the new value.

    /** The username text input field. */
    private By usernameField = By.id("user-name");

    /** The password text input field. */
    private By passwordField = By.id("password");

    /** The "Login" submit button. */
    private By loginButton = By.id("login-button");

    /** The error banner displayed when login fails (e.g., wrong credentials). */
    private By errorMessage = By.cssSelector("[data-test='error']"); // Locator for the error

    /**
     * Constructor: initialises this page with an active WebDriver instance.
     *
     * <p>Calling {@code super(driver)} runs BasePage's constructor, which stores
     * the driver reference and creates the shared WebDriverWait. After this call,
     * {@code this.driver} and {@code this.wait} are ready to use.
     *
     * @param driver the active WebDriver instance for the current test thread
     */
    public LoginPage(WebDriver driver) {
        super(driver);
    }

    // --- Granular Methods for Cucumber Steps ---
    // Each method below corresponds to one Gherkin "When" step, keeping the
    // mapping between plain-English test steps and browser actions transparent.

    /**
     * Types the given username into the username input field.
     *
     * <p>Delegates to BasePage's {@code sendKeys}, which automatically waits for
     * the field to be visible, clears any existing value, then types the text.
     *
     * @param username the username string to enter
     */
    public void enterUsername(String username) {
        // Uses BasePage's 'sendKeys' (clears + waits + types)
        sendKeys(usernameField, username);
    }

    /**
     * Types the given password into the password input field.
     *
     * @param password the password string to enter
     */
    public void enterPassword(String password) {
        sendKeys(passwordField, password);
    }

    /**
     * Clicks the Login button to submit the credentials.
     *
     * <p>After this call, the browser will either navigate to the Products page
     * (on success) or remain on the login page and display an error message
     * (on failure). The test step calling this method is responsible for
     * asserting which outcome occurred.
     */
    public void clickLogin() {
        // Uses BasePage's 'click' (waits for clickable + clicks)
        click(loginButton);
    }

    /**
     * Checks whether the error message banner is currently visible on the page.
     *
     * <p>Returns {@code true} if the element is present and displayed. This is
     * used by assertion steps to confirm that an invalid login attempt produced
     * the expected error feedback to the user.
     *
     * <p>Uses {@code driver.findElement} directly (rather than BasePage's
     * {@code getText}) because we only need a boolean presence check, not the
     * element's text content.
     *
     * @return true if the error message is displayed, false otherwise
     */
    public boolean isErrorDisplayed() {
        // We can still access 'driver' directly because it's protected in BasePage
        return driver.findElement(errorMessage).isDisplayed();
    }

    /**
     * Convenience method: enters credentials and clicks the login button in one call.
     *
     * <p>Useful in test setup (Before hooks, background steps) where login is just
     * a prerequisite and breaking it into three separate steps would add noise.
     * Feature files that specifically test the login form itself should use the
     * individual methods instead so each step maps to one clear action.
     *
     * @param username the username to enter
     * @param password the password to enter
     */
    // Optional: Keep this helper if you ever want to do it all in one line
    public void login(String username, String password) {
        enterUsername(username);
        enterPassword(password);
        clickLogin();
    }

    /**
     * Checks whether the Login button is currently visible on the page.
     *
     * <p>This is used as a lightweight indicator that the browser is on the login
     * screen. For example, after a logout action, a test can call this to verify
     * the user was actually redirected back to the login page.
     *
     * <p>The try-catch pattern returns {@code false} instead of throwing an exception
     * when the element is not found, making it safe to call as a boolean assertion
     * without extra boilerplate in the calling step.
     *
     * @return true if the login button is visible, false if not found or not displayed
     */
    public boolean isLoginButtonDisplayed() {
        try {
            return driver.findElement(loginButton).isDisplayed();
        } catch (Exception e) {
            // NoSuchElementException means the login page is not shown — return false
            return false;
        }
    }
}
