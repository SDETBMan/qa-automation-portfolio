package com.saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

/**
 * CartPage: Page Object representing the SauceDemo shopping cart screen.
 *
 * <p>This screen lists all items currently in the user's cart and provides a
 * "Checkout" button to begin the purchase flow. It also offers a "Continue Shopping"
 * link to return to the inventory, though that is not modelled here as the current
 * test scenarios do not require it.
 *
 * <p>CART ITEM VERIFICATION: This page provides both a simple "get first item name"
 * method (useful for quick single-item scenarios) and a more robust XPath-based
 * search method ({@link #isItemInCart(String)}) that checks whether a named item
 * appears anywhere in the cart list — useful for multi-item scenarios.
 *
 * <p>Extends {@link BasePage} to inherit the shared driver, wait, and helper methods.
 */
public class CartPage extends BasePage {

    // --- Element Locators ---

    /**
     * The product name label for items in the cart list.
     * Note: when multiple items are in the cart, {@code driver.findElement} returns
     * the first one; use {@code driver.findElements} to get all.
     */
    private final By cartItemName   = By.className("inventory_item_name");

    /** The "Checkout" button that begins the purchase flow. */
    private final By checkoutButton = By.id("checkout");

    /**
     * Constructor: initialises this page with an active WebDriver instance.
     *
     * @param driver the active WebDriver instance for the current test thread
     */
    public CartPage(WebDriver driver) {
        super(driver);
    }

    /**
     * Returns the display name of the first item in the cart list.
     *
     * <p>Intended for simple single-item test scenarios where only one product
     * is expected to be in the cart. For multi-item carts, use
     * {@link #isItemInCart(String)} instead.
     *
     * @return the text of the first cart item's name label
     */
    public String getFirstItemName() {
        return driver.findElement(cartItemName).getText();
    }

    /**
     * Checks whether a specific product name appears anywhere in the cart list.
     *
     * <p>WHY XPATH WITH normalize-space(): Product names sometimes have leading or
     * trailing whitespace in the DOM due to how the React component renders. The
     * {@code normalize-space()} XPath function trims that whitespace before
     * comparing, preventing false negatives from invisible characters.
     *
     * <p>The {@code contains()} function makes the match partial — e.g., searching
     * for "Backpack" will find "Sauce Labs Backpack" — which keeps feature file
     * step text concise without requiring the full product name every time.
     *
     * @param productName the product name (or partial name) to search for in the cart
     * @return true if a matching item is found and displayed, false otherwise
     */
    public boolean isItemInCart(String productName) {
        // Build a dynamic XPath that finds a cart item div whose text contains the product name
        String xpath = String.format(
                "//div[@class='inventory_item_name' and contains(normalize-space(text()),'%s')]", productName);
        try {
            return driver.findElement(By.xpath(xpath)).isDisplayed();
        } catch (Exception e) {
            // NoSuchElementException — the item is not in the cart
            return false;
        }
    }

    /**
     * Clicks the Checkout button to proceed to the checkout information screen.
     *
     * <p>A JavaScript click is used here (rather than a standard Selenium click)
     * because in headless CI environments the checkout button is occasionally
     * reported as "not interactable" even after the wait confirms it is clickable.
     * The JavaScript approach fires the DOM click event directly, bypassing any
     * rendering or overlay issue that might block the standard click.
     */
    public void clickCheckout() {
        // JS click — standard click can be silently intercepted in headless CI
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(checkoutButton));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
    }
}
