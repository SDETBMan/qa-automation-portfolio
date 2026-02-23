package com.saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;

/**
 * ProductsPage: Page Object representing the SauceDemo products/inventory listing screen.
 *
 * <p>NOTE ON OVERLAP WITH InventoryPage: Both {@link InventoryPage} and this class
 * model the same SauceDemo screen. They exist because different feature files and
 * step definition classes evolved independently in the portfolio. In a production
 * framework these would be merged; here they demonstrate that there are multiple
 * valid ways to structure Page Objects and that both approaches work correctly.
 *
 * <p>This version of the products screen page object uses BasePage's
 * {@link BasePage#javascriptClick(By)} helper for add-to-cart actions, while
 * InventoryPage inlines its own JavaScript executor call. Both achieve the same
 * result — this version is slightly more concise because the JS logic is centralised
 * in BasePage.
 *
 * <p>Extends {@link BasePage} to inherit the shared driver, wait, and helper methods.
 */
public class ProductsPage extends BasePage {

    // --- Element Locators ---

    /** The page title element (displays "Products" when on the inventory screen). */
    private By title = By.className("title");

    /**
     * The numeric badge on the cart icon showing how many items are in the cart.
     * This element is absent from the DOM when the cart is empty.
     */
    private By cartBadge = By.className("shopping_cart_badge");

    /** The shopping cart icon link in the top-right header. */
    private By cartLink = By.className("shopping_cart_link");

    /**
     * Constructor: initialises this page with an active WebDriver instance.
     *
     * @param driver the active WebDriver instance for the current test thread
     */
    public ProductsPage(WebDriver driver) {
        super(driver);
    }

    /**
     * Checks whether the products page title element is visible.
     *
     * <p>A visible title confirms the browser is on the products screen, not
     * the login page or cart. Used as a post-login assertion in step definitions.
     *
     * <p>Uses {@code driver.findElement} directly (not BasePage's {@code getText})
     * because we only need the presence/visibility check, not the text value.
     *
     * @return true if the title element is displayed on screen
     */
    public boolean isProductsPageDisplayed() {
        // For boolean checks, we often still use driver directly or a try-catch,
        // but 'isDisplayed()' is fast, so this is fine.
        return driver.findElement(title).isDisplayed();
    }

    /**
     * Returns the text of the page title element (e.g., "Products").
     *
     * <p>Delegates to BasePage's {@code getText} which waits for the element to be
     * visible before reading its text — this prevents empty-string results when
     * the page is still loading.
     *
     * @return the visible title text
     */
    public String getPageTitle() {
        return getText(title);
    }

    /**
     * Adds the named product to the shopping cart using a JavaScript click.
     *
     * <p>HOW THE BUTTON ID IS BUILT: SauceDemo names each "Add to Cart" button by
     * lower-casing the product name and replacing spaces with hyphens:
     * {@code "Sauce Labs Backpack"} → {@code "add-to-cart-sauce-labs-backpack"}.
     * The corresponding "Remove" button uses {@code "remove-sauce-labs-backpack"}.
     *
     * <p>After the JavaScript click, the method waits for the "Remove" button to
     * appear. This is a DOM-confirmation technique: Selenium waits until the UI
     * has updated (the button flips from "Add" to "Remove"), ensuring the cart
     * state is stable before the next step reads the badge count.
     *
     * @param productName the display name of the product to add (case-insensitive)
     */
    public void addToCart(String productName) {
        String addId    = "add-to-cart-" + productName.toLowerCase().replace(" ", "-");
        String removeId = "remove-"      + productName.toLowerCase().replace(" ", "-");

        // CHANGE: Using javascriptClick method
        // This bypasses the UI lag and forces the event to fire
        javascriptClick(By.id(addId));

        // We can still access 'wait' directly for complex logic
        // Wait until the "Remove" button appears — this confirms the cart add was processed
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id(removeId)));
    }

    /**
     * Returns the text currently displayed on the cart badge (e.g., "1", "3").
     *
     * <p>Delegates to BasePage's {@code getText}, which waits for the element to
     * be visible. If the badge is not present (empty cart), this will throw a
     * TimeoutException — callers should only use this after confirming at least
     * one item is in the cart.
     *
     * @return the badge text as a String (e.g., "1")
     */
    public String getCartBadgeText() {
        return getText(cartBadge);
    }

    /**
     * Clicks the cart icon to navigate to the shopping cart screen.
     *
     * <p>Uses BasePage's standard {@code click} method (wait for clickable, then click).
     * After this call, the browser should navigate to the cart page. The calling
     * step definition is responsible for asserting the navigation succeeded.
     */
    public void clickCartIcon() {
        click(cartLink);
    }
}
