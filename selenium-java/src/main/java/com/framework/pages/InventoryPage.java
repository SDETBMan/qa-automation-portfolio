package com.framework.pages;

import com.framework.utils.ConfigReader;
import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.ExpectedConditions;

/**
 * InventoryPage: Models the product listing screen where users browse and add items to the cart.
 *
 * WHY THIS CLASS EXISTS:
 * The inventory/products page is the most heavily interacted-with page in the Swag Labs
 * application. It contains the product list, "Add to Cart" buttons (one per product),
 * the cart badge showing the item count, and a link to navigate to the cart. This Page
 * Object encapsulates all of those interactions so test classes can call clean, readable
 * methods instead of working with raw Selenium locators.
 *
 * KEY TECHNIQUES DEMONSTRATED:
 *   1. Dynamic locator construction: Product names are converted into button IDs at runtime,
 *      allowing tests to add any product to the cart with a single line.
 *   2. Implicit wait suppression: The getCartItemCount() method temporarily disables the
 *      global implicit wait to avoid unnecessary 10-second pauses when the cart is empty.
 *   3. JavaScript click: All cart interactions use JS-based clicks for CI/headless reliability.
 *   4. State verification: After every cart action, the method waits for the DOM to reflect
 *      the new state (button changes from "Add to Cart" to "Remove", or vice versa).
 *
 * CROSS-PLATFORM SUPPORT:
 * Platform detection in initLocators() sets up the correct locator strategy for web vs. mobile.
 * All public action methods work the same regardless of which platform is active.
 */
public class InventoryPage extends BasePage {

    private By productsHeader;
    private By cartBadge;
    private By cartLink;

    /**
     * Constructor: Passes the driver to BasePage and initializes platform-specific locators.
     *
     * @param driver The WebDriver or AppiumDriver managing the current test session
     */
    public InventoryPage(WebDriver driver) {
        super(driver);
        initLocators();
    }

    /**
     * Initializes locators based on the current platform (web, Android, or iOS).
     *
     * WHY ANDROID AND IOS HAVE SEPARATE LOCATORS FOR THE HEADER:
     * Android native apps surface the "PRODUCTS" title as an android.widget.TextView,
     * located by XPath with the exact text value. iOS surfaces the same element differently —
     * it can be found via AppiumBy.accessibilityId(). Both achieve the same goal but require
     * different locator strategies because Android and iOS have different accessibility trees.
     */
    private void initLocators() {
        boolean isNativeMobile = (driver instanceof AndroidDriver) || (driver instanceof IOSDriver);

        if (isNativeMobile) {
            if (driver instanceof AndroidDriver) {
                // Android: The heading is a native TextView widget; XPath text matching is reliable here.
                productsHeader = By.xpath("//android.widget.TextView[@text='PRODUCTS']");
            } else {
                // iOS: The heading has an accessibility ID, which is the preferred iOS locator strategy.
                productsHeader = AppiumBy.accessibilityId("PRODUCTS");
            }
            cartBadge = AppiumBy.accessibilityId("test-Cart badge");
            cartLink = AppiumBy.accessibilityId("test-Cart");
        } else {
            // Web: Standard CSS class-based locators. By.className() maps to CSS class selector.
            productsHeader = By.className("title");
            cartBadge = By.className("shopping_cart_badge");
            cartLink = By.className("shopping_cart_link");
        }
    }

    // ==================================================
    // 1. VALIDATION METHODS
    // Methods that return state information about the page for test assertions.
    // ==================================================

    /**
     * Verifies the "Products" header is visible, confirming the inventory page has fully loaded.
     *
     * WHY THIS EXISTS:
     * After login, tests call this method to confirm they landed on the correct page.
     * The waitForVisibility() call handles the page load delay — the header might not appear
     * instantly if the JavaScript framework is still rendering. Returning a boolean (rather
     * than throwing an exception) allows tests to use assertFalse or assertTrue cleanly.
     *
     * @return true if the products header appears within the configured wait timeout; false otherwise
     */
    public boolean isProductsHeaderDisplayed() {
        try {
            waitForVisibility(productsHeader);
            return true;
        } catch (TimeoutException e) {
            return false;
        }
    }

    /**
     * Returns the current number of items shown in the shopping cart badge.
     *
     * THE IMPLICIT WAIT SUPPRESSION TECHNIQUE:
     * Selenium has two types of waits:
     *   - Explicit wait (WebDriverWait): waits for a SPECIFIC condition before continuing
     *   - Implicit wait: makes EVERY findElement() call wait up to N seconds before giving up
     *
     * The cart badge element only exists in the DOM when the cart has items. When the cart is
     * empty, there is no badge. With a 10-second implicit wait active, calling findElement()
     * on the (absent) badge would cause the test to pause for 10 full seconds before concluding
     * the badge isn't there — making the "empty cart" check painfully slow.
     *
     * Solution: Temporarily set implicit wait to 0 (instant check), attempt to read the badge,
     * then restore the original implicit wait in the "finally" block (which ALWAYS runs, even if
     * an exception is thrown). This pattern guarantees the implicit wait is always restored.
     *
     * @return The integer value shown in the cart badge; 0 if the badge is absent (cart is empty)
     */
    public int getCartItemCount() {
        // Disable implicit wait for this instant check — the badge either exists or it doesn't.
        // With a 10s implicit wait, findElement hangs the full timeout on an empty cart.
        driver.manage().timeouts().implicitlyWait(java.time.Duration.ofSeconds(0));
        try {
            return Integer.parseInt(driver.findElement(cartBadge).getText());
        } catch (Exception e) {
            return 0;
        } finally {
            // "finally" runs whether or not an exception occurred — this guarantees the
            // original implicit wait is restored so subsequent interactions are not affected.
            int implicit = Integer.parseInt(ConfigReader.getProperty("timeout.implicit", "10"));
            driver.manage().timeouts().implicitlyWait(java.time.Duration.ofSeconds(implicit));
        }
    }

    /**
     * Explicitly waits for the cart badge to appear after adding an item.
     *
     * WHY THIS EXISTS SEPARATELY:
     * After calling addToCart(), there is a brief moment before the badge appears. Tests
     * should call waitForCartBadge() before calling getCartItemCount() to ensure the badge
     * has actually appeared. Without this wait, getCartItemCount() might return 0 because
     * it ran before the badge element existed in the DOM.
     */
    public void waitForCartBadge() {
        waitForVisibility(cartBadge);
    }

    // ==================================================
    // 2. INTERACTION METHODS
    // Methods that perform actions on the inventory page.
    // ==================================================

    /**
     * Adds a product to the cart by its display name.
     *
     * DYNAMIC LOCATOR CONSTRUCTION:
     * Swag Labs uses predictable button IDs based on product names:
     *   "Sauce Labs Backpack" → button id = "add-to-cart-sauce-labs-backpack"
     *   "Sauce Labs Bike Light" → button id = "add-to-cart-sauce-labs-bike-light"
     * By converting the product name to lowercase and replacing spaces with dashes, we can
     * construct the correct button ID at runtime without hardcoding a locator for every product.
     *
     * WHY JS CLICK (NOT STANDARD CLICK):
     * In headless Chrome and under CI conditions with slower rendering, the standard Selenium
     * click() can miss the button or be intercepted by invisible overlay elements. Using
     * JavascriptExecutor to click directly in the DOM is more reliable in these environments.
     *
     * STATE CHANGE VERIFICATION:
     * After clicking "Add to Cart", the button text changes to "Remove". Waiting for the
     * Remove button to appear confirms the DOM has processed the add action. This prevents
     * the test from racing ahead to check the cart count before the UI has updated.
     *
     * @param productName The product's display name as shown on the page (e.g., "Sauce Labs Backpack")
     */
    public void addToCart(String productName) {
        String formattedName = productName.toLowerCase().replace(" ", "-");
        By addButton = By.id("add-to-cart-" + formattedName);
        By removeButton = By.id("remove-" + formattedName);

        // 1. Wait and capture the element in one go
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(addButton));

        // 2. Log the action (Optional, but great for Allure reports)
        System.out.println("[WEB-ACTION] Force Clicking Add to Cart: " + productName);

        // 3. Force the click via JS to handle Headless/CI latency
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);

        // 4. Confirm the state change (The 'Remove' button appearing means the add was registered)
        waitForVisibility(removeButton);
    }

    /**
     * Removes a product from the cart by its display name.
     *
     * WHY THE SAME JS CLICK PATTERN AS addToCart():
     * For the same CI/headless reliability reasons described in addToCart(). The standard
     * BasePage.click() uses Actions.moveToElement() before clicking, which can scroll
     * the page or trigger hover states that interfere with the remove button in headless
     * Chrome — making the click miss silently (no exception, but nothing happens either).
     *
     * STATE CHANGE VERIFICATION:
     * After clicking "Remove", the button changes back to "Add to Cart". Waiting for the
     * "Add to Cart" button to reappear confirms the DOM has processed the removal before
     * the test reads the cart count. This mirrors the same pattern used in addToCart().
     *
     * @param productName The product's display name to remove (e.g., "Sauce Labs Backpack")
     */
    public void removeFromCart(String productName) {
        String formattedName = productName.toLowerCase().replace(" ", "-");
        By removeButton = By.id("remove-" + formattedName);
        By addButton    = By.id("add-to-cart-" + formattedName);

        // JS click — same approach as addToCart for CI/headless reliability.
        // BasePage.click() uses Actions.moveToElement() which can scroll or intercept
        // in headless Chrome, causing the standard click to miss silently.
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(removeButton));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
        System.out.println("[WEB-ACTION] Force Clicking Remove from Cart: " + productName);

        // Confirm DOM state change before caller reads cart count.
        // Mirrors addToCart's waitForVisibility(removeButton).
        waitForVisibility(addButton);
    }

    /**
     * Clicks the cart icon and returns a CartPage object representing the cart screen.
     *
     * WHY RETURN A CartPage:
     * This is the "Page Object chaining" pattern. When navigating from one page to another,
     * the method returns an instance of the destination page. The test code reads naturally:
     *   CartPage cartPage = inventoryPage.goToCart();
     *   cartPage.isItemInCart("Sauce Labs Backpack");
     *
     * WHY WAIT FOR URL CHANGE:
     * The cart page navigation is asynchronous — clicking the cart icon triggers JavaScript
     * that changes the URL. Without waiting for the URL to change, the CartPage returned
     * by this method might still be pointing to the inventory page, and interactions on it
     * would fail because the cart page elements haven't loaded yet.
     *
     * @return A CartPage instance representing the shopping cart page after navigation
     */
    public CartPage goToCart() {
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(cartLink));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
        System.out.println("[WEB-ACTION] Force Clicking Shopping Cart Icon");
        waitForUrlToContain("cart.html");
        return new CartPage(driver);
    }
}
