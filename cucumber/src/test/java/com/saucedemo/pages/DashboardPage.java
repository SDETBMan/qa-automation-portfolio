package com.saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

/**
 * DashboardPage: Page Object representing the main SauceDemo dashboard (inventory) screen.
 *
 * <p>After a successful login the user lands on this screen, which displays a product
 * grid with a shopping cart icon in the header and a hamburger menu in the top-left.
 * This class models interactions with the persistent header elements that are present
 * on the dashboard regardless of which product is being viewed.
 *
 * <p>WHY SEPARATE FROM InventoryPage: The dashboard header (cart icon, menu, page title)
 * is shared across multiple screens. Isolating it in its own Page Object keeps each
 * class focused on a single responsibility and avoids one giant "everything" page class.
 *
 * <p>Extends {@link BasePage} to inherit the shared driver, wait, and helper methods.
 */
public class DashboardPage extends BasePage {

    // --- Element Locators ---

    /** The shopping cart icon in the top-right header. */
    private final By cartIcon   = By.className("shopping_cart_link");

    /** The hamburger menu button in the top-left header. */
    private final By menuButton = By.id("react-burger-menu-btn");

    /**
     * The logout link inside the slide-out navigation menu.
     * This element is hidden until the menu is opened.
     */
    private final By logoutLink = By.id("logout_sidebar_link");

    /** The page title displayed in the main content area (e.g., "Products"). */
    private final By pageTitle  = By.className("title");

    /**
     * Constructor: initialises this page with an active WebDriver instance.
     *
     * @param driver the active WebDriver instance for the current test thread
     */
    public DashboardPage(WebDriver driver) {
        super(driver);
    }

    /**
     * Checks whether the shopping cart icon is visible in the page header.
     *
     * <p>A visible cart icon is a reliable indicator that the user has successfully
     * logged in and arrived at the dashboard. Step definitions use this as a
     * post-login assertion.
     *
     * <p>The try-catch returns {@code false} rather than throwing an exception
     * when the element is absent, making this safe to use directly as a boolean
     * assertion without extra error handling in the calling step.
     *
     * @return true if the cart icon is displayed, false if not found
     */
    public boolean isCartIconDisplayed() {
        try {
            return driver.findElement(cartIcon).isDisplayed();
        } catch (Exception e) {
            // Element not found — user is not on the dashboard
            return false;
        }
    }

    /**
     * Returns the text of the main page title element.
     *
     * <p>On the products/inventory screen this reads "Products". Tests use this
     * to verify the correct page is displayed after an action (e.g., after login,
     * after navigating from cart back to shopping).
     *
     * @return the visible title text (e.g., "Products", "Your Cart")
     */
    public String getWelcomeMessageText() {
        return getText(pageTitle);
    }

    /**
     * Opens the slide-out navigation menu and clicks the Logout link.
     *
     * <p>WHY TWO-STEP LOGOUT: The logout link is inside a React-animated slide-out
     * menu. Clicking logout requires first opening the menu, then waiting for the
     * link to appear, and finally clicking it. The link is not present in the
     * accessible DOM until the menu animation completes.
     *
     * <p>WHY A JAVASCRIPT FALLBACK: After the menu opens, the logout link is
     * sometimes partially behind the animation layer for a brief moment. The
     * primary approach uses {@code wait.until(presenceOfElementLocated)} plus a
     * JavaScript click, which fires the event directly on the DOM node and avoids
     * "element not interactable" errors. If for any reason the JS click itself
     * fails, the catch block falls back to BasePage's standard click.
     */
    public void clickLogoutButton() {
        // Step 1: Open the hamburger menu — this starts the slide-out animation
        click(menuButton);
        try {
            // Step 2: Wait for the logout link to be present in the DOM
            // Note: presenceOfElementLocated is used (not visibilityOf) because
            // the element may be present but not yet fully visible during the animation
            WebElement logoutBtn = wait.until(ExpectedConditions.presenceOfElementLocated(logoutLink));
            // Step 3: Use JavaScript click to bypass any animation overlay interception
            ((JavascriptExecutor) driver).executeScript("arguments[0].click();", logoutBtn);
        } catch (Exception e) {
            // Fallback: attempt a standard Selenium click if the JS approach failed
            click(logoutLink);
        }
    }
}
