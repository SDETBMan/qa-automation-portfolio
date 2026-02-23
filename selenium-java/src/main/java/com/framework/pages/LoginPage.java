package com.framework.pages;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

/**
 * LoginPage: Represents the login screen of the Swag Labs application.
 *
 * WHY THIS CLASS EXISTS:
 * The Page Object Model (POM) principle says every screen of the application should
 * have its own dedicated Java class. This class owns everything about the login screen:
 * where the username field is, where the password field is, and how to perform a login.
 * Tests never interact with locators directly — they call methods on this class instead.
 *
 * WHY THIS IS BENEFICIAL FOR MAINTENANCE:
 * If the developer renames the login button's HTML id from "login-button" to "btn-login",
 * you only update the locator in ONE place (here in loginButton), and every test that
 * calls loginPage.login() automatically gets the fix. Without POM, you'd need to find and
 * update every test file that hard-coded that selector.
 *
 * CROSS-PLATFORM SUPPORT (Web + Mobile):
 * This is an advanced technique that makes the same Page Object work for both the Swag Labs
 * website (web browser) AND the Swag Labs native mobile app (Android/iOS via Appium).
 * The locators are different on each platform, so the constructor detects which driver type
 * is active and initializes the correct locators. Tests are written once and run everywhere.
 *
 * For recruiters: A cross-platform Page Object demonstrates that this framework supports
 * both web and mobile from shared test code — a significant engineering achievement.
 */
public class LoginPage extends BasePage {

    // Locators are stored as instance variables so they're set once (in initLocators)
    // and reused in every method. This avoids re-evaluating the platform check on every action.
    private By usernameField;
    private By passwordField;
    private By loginButton;
    private By errorMessage;

    /**
     * Constructor: Passes the driver to BasePage and immediately initializes locators.
     *
     * WHY CALL initLocators() IN THE CONSTRUCTOR:
     * The moment a test creates a LoginPage, the locators need to be ready. Calling
     * initLocators() here ensures that by the time any test method (like login()) runs,
     * the correct platform-specific locators are already set up.
     *
     * @param driver The WebDriver or AppiumDriver managing the current test session
     */
    public LoginPage(WebDriver driver) {
        super(driver);
        initLocators();
    }

    /**
     * Initializes locators based on the active Driver type (Web vs. Mobile).
     *
     * WHY SEPARATE LOCATOR INITIALIZATION:
     * Web and mobile apps are fundamentally different technologies. A web browser renders
     * HTML, so we find elements by HTML attributes (id, CSS class). A native mobile app
     * renders native UI components, so we find elements by their accessibility labels —
     * the "test-Username" strings shown below are accessibility identifiers assigned by
     * the mobile app developers specifically for testing.
     *
     * AppiumBy.accessibilityId() is Appium's way of locating native mobile elements by
     * their accessibility label — the equivalent of By.id() for web browsers.
     */
    private void initLocators() {
        boolean isNativeMobile = (driver instanceof AndroidDriver) || (driver instanceof IOSDriver);

        if (isNativeMobile) {
            // SWAG LABS NATIVE APP LOCATORS (Accessibility IDs)
            // Accessibility IDs are preferred for mobile because they are stable across
            // app versions and work on both Android and iOS without platform-specific code.
            usernameField = AppiumBy.accessibilityId("test-Username");
            passwordField = AppiumBy.accessibilityId("test-Password");
            loginButton = AppiumBy.accessibilityId("test-LOGIN");
            errorMessage = AppiumBy.accessibilityId("test-Error message");
        } else {
            // SWAG LABS WEB LOCATORS (Standard IDs/CSS)
            // By.id() is the most reliable web locator because IDs are meant to be unique per page.
            // By.cssSelector() is used for the error message because it has no id, but does have
            // a unique "data-test" attribute that's more stable than a class name.
            usernameField = By.id("user-name");
            passwordField = By.id("password");
            loginButton = By.id("login-button");
            errorMessage = By.cssSelector("h3[data-test='error']");
        }
    }

    // ==================================================
    // ACTIONS
    // Public methods that represent what a user can DO on this page.
    // Tests call these methods — they never manipulate elements directly.
    // ==================================================

    /**
     * Performs a complete login by entering credentials and clicking the login button.
     *
     * WHY THIS METHOD EXISTS:
     * Every test that needs to be logged in calls this single method. If the login flow
     * ever changes (e.g., a CAPTCHA is added, or a "Remember Me" checkbox appears), you
     * update only this method, and all tests benefit automatically.
     *
     * WHY USE THE 3-PARAMETER enterText() VERSION:
     * The 3-parameter version (locator, text, elementName) passes a descriptive name
     * to the logging system. This produces log entries like:
     *   "[WEB] Entered 'standard_user' into: Username Field"
     * rather than the less readable auto-generated locator string.
     *
     * @param username The username credential to enter
     * @param password The password credential to enter
     */
    public void login(String username, String password) {
        // We use the 3-parameter version to maintain descriptive logs.
        enterText(usernameField, username, "Username Field");
        enterText(passwordField, password, "Password Field");
        click(loginButton, "Login Button");
    }

    /**
     * Reads and returns the error message text shown when login fails.
     *
     * WHY THE PLATFORM-SPECIFIC FALLBACK LOGIC:
     * On web, getText() reliably returns the visible text of the error element.
     * On mobile, getText() sometimes returns empty for elements whose text is stored
     * in a different attribute depending on the platform:
     *   - Android: The text lives in a nested "android.widget.TextView" child element
     *   - iOS: The text is stored in either the "label" or "name" attribute, not in text()
     *
     * This method tries the simple path first, then falls back to platform-specific
     * attribute reading if the simple approach returns nothing. This is called
     * "defensive programming" — anticipating how things can differ and handling each case.
     *
     * @return The error message text displayed on screen, or an empty string if not found
     */
    public String getErrorMessage() {
        // 1. Try standard getText (Works for Web and sometimes mobile)
        String text = getText(errorMessage);

        // 2. Mobile Fallback Logic for nested or attribute-stored text.
        if (text == null || text.isEmpty()) {
            if (driver instanceof AndroidDriver) {
                try {
                    // On Android, the visible error text may live inside a child TextView
                    // rather than in the parent container's text property.
                    text = driver.findElement(errorMessage)
                            .findElement(By.className("android.widget.TextView"))
                            .getText();
                } catch (Exception e) {
                    System.out.println("[WARN] Failed to find child TextView on Android");
                }
            } else if (driver instanceof IOSDriver) {
                try {
                    // On iOS, text may be stored as an accessibility attribute rather than
                    // as the element's text content. We try "label" first, then "name".
                    text = driver.findElement(errorMessage).getAttribute("label");
                    if (text == null || text.isEmpty()) {
                        text = driver.findElement(errorMessage).getAttribute("name");
                    }
                } catch (Exception e) {
                    System.out.println("[WARN] Failed to retrieve iOS attribute");
                }
            }
        }
        return text;
    }

    /**
     * Checks whether the login button is currently visible on screen.
     *
     * WHY THIS EXISTS — Session State Validation:
     * After a logout action, tests need to confirm the user was actually returned to the
     * login screen. The simplest way to verify this is to check whether the login button
     * is visible again — if it is, the session has been properly terminated. This method
     * also avoids propagating a NoSuchElementException by catching it and returning false,
     * which lets tests make clean boolean assertions.
     *
     * @return true if the login button is displayed on the current screen; false otherwise
     */
    public boolean isLoginButtonDisplayed() {
        try {
            return driver.findElement(loginButton).isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }
}
