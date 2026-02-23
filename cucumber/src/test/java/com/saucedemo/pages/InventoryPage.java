package com.saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

/**
 * InventoryPage: Page Object representing the SauceDemo product inventory (shopping) screen.
 *
 * <p>This screen is the main shopping area where users browse products, add them to
 * the cart, and remove them. It also hosts the cart badge (the small number on the
 * cart icon showing how many items are in the basket) and the cart icon itself.
 *
 * <p>KEY DESIGN DECISIONS:
 * <ul>
 *   <li>Add-to-cart and remove-from-cart button IDs are dynamically built from the
 *       product name (e.g., "Sauce Labs Backpack" → "add-to-cart-sauce-labs-backpack").
 *       This means a single method handles any product, keeping the class lean.</li>
 *   <li>JavaScript clicks are used throughout because headless CI environments
 *       occasionally intercept standard Selenium clicks on these elements.</li>
 *   <li>{@link #goToCart()} returns a new {@link CartPage} instance, modelling the
 *       natural page transition — a pattern known as "chained Page Objects".</li>
 * </ul>
 *
 * <p>Extends {@link BasePage} to inherit the shared driver, wait, and helper methods.
 */
public class InventoryPage extends BasePage {

    // --- Element Locators ---

    /** The "Products" heading at the top of the inventory list. */
    private final By productsHeader = By.className("title");

    /**
     * The numeric badge on the cart icon showing item count.
     * This element only exists in the DOM when at least one item is in the cart;
     * querying it when the cart is empty will throw NoSuchElementException.
     */
    private final By cartBadge      = By.className("shopping_cart_badge");

    /** The cart icon link in the top-right header. */
    private final By cartLink       = By.className("shopping_cart_link");

    /**
     * Constructor: initialises this page with an active WebDriver instance.
     *
     * @param driver the active WebDriver instance for the current test thread
     */
    public InventoryPage(WebDriver driver) {
        super(driver);
    }

    /**
     * Checks whether the "Products" header is visible, confirming the inventory
     * page has fully loaded.
     *
     * <p>Uses an explicit wait so the check still passes even if the page is
     * rendering slowly. Returns {@code false} on timeout rather than throwing,
     * so callers can use this directly as a boolean assertion.
     *
     * @return true if the products header is visible within the wait timeout
     */
    public boolean isProductsHeaderDisplayed() {
        try {
            wait.until(ExpectedConditions.visibilityOfElementLocated(productsHeader));
            return true;
        } catch (Exception e) {
            // Timeout — the header never appeared; the page did not load correctly
            return false;
        }
    }

    /**
     * Returns the current number of items shown in the cart badge.
     *
     * <p>If the badge element does not exist (empty cart) or its text is blank,
     * this method returns 0 rather than throwing an exception. This makes it
     * safe to call in assertions like {@code Assert.assertEquals(getCartItemCount(), 0)}.
     *
     * @return the integer item count from the badge, or 0 if the badge is absent
     */
    public int getCartItemCount() {
        try {
            String text = driver.findElement(cartBadge).getText();
            // If the badge exists but somehow has empty text, treat it as 0
            return text.isEmpty() ? 0 : Integer.parseInt(text);
        } catch (Exception e) {
            // NoSuchElementException — badge not present means cart is empty
            return 0;
        }
    }

    /**
     * Waits (up to the standard timeout) for the cart badge to become visible.
     *
     * <p>WHY THIS IS USEFUL: The badge appears asynchronously after an "Add to Cart"
     * click. Without this wait, the very next call to {@link #getCartItemCount()}
     * might read the badge before it has rendered, returning 0 even when an item
     * was added. Calling this method in between ensures the DOM has settled.
     */
    public void waitForCartBadge() {
        wait.until(ExpectedConditions.visibilityOfElementLocated(cartBadge));
    }

    /**
     * Adds the named product to the shopping cart and waits for the action to complete.
     *
     * <p>HOW SAUCEDEMO BUTTON IDs WORK: Each product's "Add to Cart" button has an
     * ID formed by lower-casing the product name and replacing spaces with hyphens:
     * {@code "Sauce Labs Backpack"} → {@code "add-to-cart-sauce-labs-backpack"}.
     * The corresponding "Remove" button uses the same slug: {@code "remove-sauce-labs-backpack"}.
     * This convention allows one method to handle any product dynamically.
     *
     * <p>After clicking Add, the method waits for the "Remove" button to appear,
     * which confirms the cart update was registered in the DOM before the test
     * proceeds to check the badge count.
     *
     * @param productName the display name of the product (case-insensitive, spaces allowed)
     */
    public void addToCart(String productName) {
        // Transform the display name into the format used in SauceDemo button IDs
        String formattedName = productName.toLowerCase().replace(" ", "-");
        By addButton    = By.id("add-to-cart-" + formattedName);
        By removeButton = By.id("remove-" + formattedName);

        // JavaScript click bypasses any overlay that might intercept in headless CI
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(addButton));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
        // Waiting for the Remove button is a DOM-based confirmation that the add succeeded
        wait.until(ExpectedConditions.visibilityOfElementLocated(removeButton));
    }

    /**
     * Removes the named product from the shopping cart and waits for the action to complete.
     *
     * <p>Mirror of {@link #addToCart}: clicks the "Remove" button for the given product
     * and then waits for the "Add to Cart" button to reappear, confirming the removal
     * was processed before any subsequent cart count assertions run.
     *
     * @param productName the display name of the product to remove
     */
    public void removeFromCart(String productName) {
        String formattedName = productName.toLowerCase().replace(" ", "-");
        By addButton    = By.id("add-to-cart-" + formattedName);
        By removeButton = By.id("remove-" + formattedName);
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(removeButton));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
        // Wait for "Add to Cart" to reappear — confirms DOM has updated before getCartItemCount() is called
        wait.until(ExpectedConditions.visibilityOfElementLocated(addButton));
    }

    /**
     * Clicks the cart icon and returns a CartPage object representing the resulting screen.
     *
     * <p>CHAINED PAGE OBJECTS: When an action causes a page navigation, the method
     * responsible for that action returns an instance of the destination page. This
     * technique makes test code fluent and self-documenting:
     * {@code CartPage cart = inventoryPage.goToCart();}
     *
     * <p>The URL wait after the click ensures the CartPage object is returned only
     * after the browser has genuinely navigated, preventing stale-element errors on
     * the cart page's elements.
     *
     * @return a new CartPage instance representing the cart screen
     */
    public CartPage goToCart() {
        // JS click bypasses headless CI intercept issues on the cart icon link
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(cartLink));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
        // Wait until the URL confirms we have arrived at the cart page
        wait.until(ExpectedConditions.urlContains("cart.html"));
        return new CartPage(driver);
    }
}
