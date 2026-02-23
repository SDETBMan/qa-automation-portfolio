package com.framework.pages;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

/**
 * DashboardPage: Represents the main product listing screen shown after successful login.
 *
 * WHY THIS CLASS EXISTS:
 * After a user logs in to Swag Labs, they land on the "Products" / dashboard screen.
 * This Page Object models the interactive elements on that screen: the shopping cart icon,
 * the hamburger menu, and the logout link nested inside it. Test classes use this Page
 * Object to verify post-login state and to perform navigation actions like logout.
 *
 * CROSS-PLATFORM DESIGN:
 * Like LoginPage, this class detects whether it is running against a web browser or a
 * native mobile app and loads the appropriate set of locators. The test methods themselves
 * (isCartIconDisplayed, clickLogoutButton, getWelcomeMessageText) work identically
 * regardless of which platform is active — the platform differences are hidden inside
 * the private initLocators() method.
 *
 * LOGOUT COMPLEXITY:
 * The logout action is more complex than a simple click because it involves:
 *   1. Opening a slide-in hamburger menu (which has an animation)
 *   2. Waiting for the menu to stabilize
 *   3. Clicking the logout link inside it
 * Each platform handles this menu animation differently, so platform-specific code is
 * needed inside clickLogoutButton() rather than the simpler initLocators() approach.
 */
public class DashboardPage extends BasePage {

    private By cartIcon;
    private By menuButton;
    private By logoutLink;
    private By pageTitle;

    /**
     * Constructor: Passes the driver to BasePage and initializes platform-specific locators.
     *
     * @param driver The WebDriver or AppiumDriver managing the current test session
     */
    public DashboardPage(WebDriver driver) {
        super(driver);
        initLocators();
    }

    /**
     * Initializes locators dynamically based on whether the active driver is web or mobile.
     *
     * WHY THE XPATH FOR MOBILE PAGE TITLE:
     * On Android, the "PRODUCTS" heading is a native TextView widget. Appium locates it via
     * XPath by matching the widget class and its text content. On iOS, the simpler
     * AppiumBy.accessibilityId() is not shown here but would be used similarly.
     * Note: The Android locator uses the full class path "android.widget.TextView" because
     * Android's accessibility tree exposes native widget class names, not HTML tag names.
     */
    private void initLocators() {
        boolean isNativeMobile = (driver instanceof AndroidDriver) || (driver instanceof IOSDriver);

        if (isNativeMobile) {
            // MOBILE (Accessibility IDs)
            cartIcon = AppiumBy.accessibilityId("test-Cart");
            menuButton = AppiumBy.accessibilityId("test-Menu");
            logoutLink = AppiumBy.accessibilityId("test-LOGOUT");
            // XPath for Android because the "PRODUCTS" title is a native TextView, not a web element.
            pageTitle = By.xpath("//android.widget.TextView[@text='PRODUCTS']");
        } else {
            // WEB (Standard CSS/ID)
            cartIcon = By.className("shopping_cart_link");
            menuButton = By.id("react-burger-menu-btn");
            logoutLink = By.id("logout_sidebar_link");
            pageTitle = By.className("title");
        }
    }

    // ==================================================
    // ACTION METHODS
    // Each method represents a user-facing action or verification on this page.
    // ==================================================

    /**
     * Checks whether the shopping cart icon is visible on the dashboard.
     *
     * WHY THIS IS A MEANINGFUL ASSERTION:
     * The cart icon being present is one of the key indicators that login succeeded
     * and the user is on the correct post-login screen. If login failed silently (e.g.,
     * the app redirected to an error page rather than showing an error message), the
     * cart icon would not appear, and this check would catch that failure.
     *
     * @return true if the cart icon is displayed; false if it is absent or hidden
     */
    public boolean isCartIconDisplayed() {
        try {
            return driver.findElement(cartIcon).isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Executes the complete logout sequence, handling platform-specific menu animations.
     *
     * WHY THE PLATFORM-SPECIFIC CLICK STRATEGY:
     * On mobile, the hamburger menu slides in from the side, and we simply wait for the
     * logout link to become visible before clicking it — Appium handles the animation naturally.
     *
     * On web, the React-based menu animation can cause a timing issue where Selenium thinks
     * the logout link is interactable before it has finished animating into position, causing
     * an "ElementClickInterceptedException." Using JavascriptExecutor to click the logout link
     * directly in the DOM bypasses this animation-related intercept entirely.
     *
     * WHY THERE IS A WEB FALLBACK:
     * The JS click is the first attempt. If JS click fails for any reason (e.g., the element
     * is detached from the DOM during animation), we fall back to the standard BasePage click().
     * Layered fallbacks like this are a key strategy for building stable, non-flaky tests.
     */
    public void clickLogoutButton() {
        // 1. Open Menu — same action on both platforms
        click(menuButton, "Hamburger Menu");

        // 2. Platform-Specific Click Logic
        if (driver instanceof AndroidDriver || driver instanceof IOSDriver) {
            // Mobile: Wait for the menu transition animation to complete before clicking.
            // Without this wait, Appium might try to click the logout link before it is
            // fully on screen, causing the tap to miss or hit the wrong element.
            waitForVisibility(logoutLink);
            click(logoutLink, "Logout Link");
        } else {
            // Web: Use JavascriptExecutor to bypass potential animation overlays.
            // "presence" (not "visibility") is used here because the element exists in the DOM
            // during the animation even before it is fully visible to the user.
            try {
                WebElement logoutBtn = wait.until(ExpectedConditions.presenceOfElementLocated(logoutLink));
                ((JavascriptExecutor) driver).executeScript("arguments[0].click();", logoutBtn);
                System.out.println("[WEB-ACTION] Force Clicked Logout via JS");
            } catch (Exception e) {
                click(logoutLink, "Logout Link (Fallback)");
            }
        }
    }

    /**
     * Retrieves the primary page title text from the dashboard header.
     *
     * WHY THIS EXISTS:
     * The page title ("Products" on Swag Labs) is a key verification point. After login,
     * tests assert this text to confirm the correct page loaded. The getText() method
     * inherited from BasePage handles the wait and trim automatically, so this method
     * is a clean, one-line delegation with a meaningful name.
     *
     * @return The visible text of the dashboard's page title element
     */
    public String getWelcomeMessageText() {
        waitForVisibility(pageTitle);
        return getText(pageTitle);
    }
}
