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
 * CartPage: Represents the shopping cart screen in the Swag Labs application.
 *
 * WHY THIS CLASS EXISTS:
 * Once a user navigates to the cart, they land on a completely different page with its
 * own set of elements: a list of cart items and a checkout button. This Page Object
 * encapsulates the locators and interactions specific to that screen.
 *
 * ROLE IN THE TEST FLOW:
 * CartPage is typically the final step of an "Add to Cart" test scenario. After adding
 * items on the InventoryPage and navigating here, tests use isItemInCart() to verify the
 * correct item actually appears in the cart, and clickCheckout() to continue the flow.
 *
 * CROSS-PLATFORM SUPPORT:
 * Like other page objects in this framework, CartPage uses platform detection to load
 * the correct locators for web vs. mobile. The public test-facing methods work identically
 * regardless of which platform is active.
 */
public class CartPage extends BasePage {

    private By cartItems;
    private By checkoutButton;

    /**
     * Constructor: Passes the driver to BasePage and initializes platform-specific locators.
     *
     * @param driver The WebDriver or AppiumDriver managing the current test session
     */
    public CartPage(WebDriver driver) {
        super(driver);
        initLocators();
    }

    /**
     * Initializes cart page locators based on whether the active driver is web or mobile.
     *
     * NOTE ON cartItems:
     * The cartItems locator is defined here for completeness and future use (e.g., counting
     * total cart items or iterating through them). The isItemInCart() method below uses a
     * more specific XPath query rather than this general locator to find a named item.
     */
    private void initLocators() {
        boolean isNativeMobile = (driver instanceof AndroidDriver) || (driver instanceof IOSDriver);

        if (isNativeMobile) {
            // Mobile: Accessibility IDs are the stable cross-version locator strategy for Appium.
            cartItems = AppiumBy.accessibilityId("test-Item");
            checkoutButton = AppiumBy.accessibilityId("test-CHECKOUT");
        } else {
            // Web: Standard CSS class and ID locators from the Swag Labs HTML structure.
            cartItems = By.className("cart_item");
            checkoutButton = By.id("checkout");
        }
    }

    /**
     * Verifies that a specific product by name is present in the cart item list.
     *
     * WHY XPath WITH normalize-space() INSTEAD OF THE cartItems LOCATOR:
     * We need to find a SPECIFIC named product in the cart, not just any cart item.
     * An XPath query lets us search by the element's text content. The normalize-space()
     * function strips extra whitespace from the element's text before comparing — this
     * handles edge cases where the product name has leading/trailing whitespace in the HTML,
     * which would cause an exact text match to fail silently.
     *
     * String.format() builds the XPath dynamically with the requested product name inserted
     * at the %s placeholder. This makes the method reusable for any product name.
     *
     * Uses the inherited isElementDisplayed() which includes the safety wait and returns
     * a boolean rather than throwing an exception if the item is not found.
     *
     * @param productName The product name to search for in the cart (e.g., "Sauce Labs Backpack")
     * @return true if the product is visible in the cart; false if it is not present
     */
    public boolean isItemInCart(String productName) {
        // Use a locator that finds the text anywhere in the name div
        String xpath = String.format("//div[@class='inventory_item_name' and contains(normalize-space(text()), '%s')]", productName);
        return isElementDisplayed(By.xpath(xpath));
    }

    /**
     * Clicks the Checkout button to begin the checkout process.
     *
     * WHY JS CLICK:
     * For consistency with the rest of this framework's cart interaction methods, we use
     * JavascriptExecutor to click the button. This prevents "ElementClickInterceptedException"
     * in CI/headless environments where overlapping elements or animations can block standard
     * Selenium clicks.
     *
     * WHY WAIT FOR URL AFTER CLICKING:
     * Clicking checkout triggers JavaScript navigation. The waitForUrlToContain() call from
     * BasePage ensures this method doesn't return until the browser has actually navigated
     * to the checkout step one page. This protects subsequent test steps from running against
     * a page that hasn't finished loading.
     */
    public void clickCheckout() {
        WebElement element = wait.until(org.openqa.selenium.support.ui.ExpectedConditions.elementToBeClickable(checkoutButton));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
        System.out.println("[WEB-ACTION] Force Clicking Checkout Button");
        waitForUrlToContain("checkout-step-one");
    }
}
