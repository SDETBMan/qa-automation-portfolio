package com.framework.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

/**
 * ProductsPage: A web-only Page Object for the Swag Labs product listing screen.
 *
 * WHY THIS CLASS EXISTS ALONGSIDE InventoryPage:
 * This framework supports multiple test suites — some are feature tests that need the full
 * cross-platform support and state verification that InventoryPage provides, while others
 * (such as the Cucumber-based BDD suite mirrored in this portfolio) use a simpler,
 * web-only page model. ProductsPage provides that simpler interface without the mobile
 * complexity.
 *
 * This class demonstrates intentional architecture: when two suites in the same portfolio
 * cover the same application screen, keeping their page models separate avoids coupling one
 * suite's design decisions to the other's requirements.
 *
 * NOTE FOR FRAMEWORK LEARNERS:
 * Compare ProductsPage and InventoryPage side by side to understand the tradeoffs:
 *   - InventoryPage: cross-platform (web + mobile), state verification after cart actions,
 *     configurable implicit-wait suppression for cart badge checks
 *   - ProductsPage: web-only, lighter weight, used when mobile and advanced wait logic
 *     are not needed
 *
 * For recruiters: Maintaining separate page models for different test suite contexts shows
 * deliberate framework design and awareness of separation of concerns.
 */
public class ProductsPage extends BasePage {

    // Locators are "final" because they never change once set — this is a good practice
    // for web-only pages where there is no platform detection needed.
    private final By title     = By.className("title");
    private final By cartBadge = By.className("shopping_cart_badge");
    private final By cartLink  = By.className("shopping_cart_link");

    /**
     * Constructor: Passes the driver to BasePage.
     *
     * NOTE: No initLocators() call needed here because all locators are web-only constants
     * defined as final fields above — unlike InventoryPage and LoginPage which must choose
     * locators dynamically based on the active platform.
     *
     * @param driver The WebDriver managing the current browser session
     */
    public ProductsPage(WebDriver driver) {
        super(driver);
    }

    /**
     * Confirms the products page is fully loaded and displayed.
     *
     * WHY THIS EXISTS:
     * Tests use this as a lightweight post-login verification — if this returns true,
     * the application navigated successfully to the products screen. Uses isElementDisplayed()
     * from BasePage, which includes the safety wait and returns a boolean rather than throwing.
     *
     * @return true if the page title element is visible; false otherwise
     */
    public boolean isProductsPageDisplayed() {
        return isElementDisplayed(title);
    }

    /**
     * Returns the text content of the page title element.
     *
     * WHY THIS EXISTS:
     * Tests that need to assert the exact page title text (e.g., "Products") use this method.
     * It delegates to BasePage.getText(), which includes the visibility wait and whitespace
     * trimming, preventing flaky assertions caused by late-rendering text or extra spaces.
     *
     * @return The trimmed text of the page title (expected: "Products")
     */
    public String getPageTitle() {
        return getText(title);
    }

    /**
     * Adds a product to the cart by its display name using JavaScript click for CI reliability.
     *
     * HOW DYNAMIC LOCATORS WORK HERE:
     * The same naming convention used in InventoryPage applies: product name → lowercase
     * with spaces replaced by dashes → used as the button ID suffix. This lets one method
     * handle any product rather than requiring a separate locator per product.
     *
     * WHY WE WAIT FOR THE REMOVE BUTTON:
     * Waiting for the "Remove" button to appear after clicking "Add to Cart" confirms the DOM
     * state has changed. This prevents the test from reading the cart badge before it updates,
     * which would cause getCartBadgeText() to return stale data.
     *
     * @param productName The display name of the product to add (e.g., "Sauce Labs Backpack")
     */
    public void addToCart(String productName) {
        String formattedName = productName.toLowerCase().replace(" ", "-");
        By addButton    = By.id("add-to-cart-" + formattedName);
        By removeButton = By.id("remove-" + formattedName);

        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(addButton));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
        // Wait for state change confirmation before returning to the caller
        waitForVisibility(removeButton);
    }

    /**
     * Returns the text shown in the shopping cart badge (typically a number like "1", "2", etc.).
     *
     * WHY THIS IS USED FOR ASSERTIONS:
     * The cart badge is the primary UI indicator of how many items are in the cart.
     * Tests assert this value after calling addToCart() to verify the cart count incremented
     * correctly. getText() from BasePage handles the visibility wait and trim automatically.
     *
     * NOTE: If the cart is empty, the badge element does not exist in the DOM, and getText()
     * will return "" (empty string). Use InventoryPage.getCartItemCount() if you need a numeric
     * 0 when the cart is empty, as that method handles the missing-element case explicitly.
     *
     * @return The cart badge text (e.g., "1"); "" if the badge is not present
     */
    public String getCartBadgeText() {
        return getText(cartBadge);
    }

    /**
     * Clicks the shopping cart icon to navigate to the cart page.
     *
     * WHY SIMPLE click() HERE (vs. JS click in InventoryPage):
     * This lighter-weight page model uses BasePage's standard click() which includes the
     * visibility wait, hover, and JS fallback already built in. For suites that use
     * ProductsPage, this level of reliability is sufficient without the extra explicit
     * JS override that InventoryPage uses.
     */
    public void clickCartIcon() {
        click(cartLink, "Cart Icon");
    }
}
