package com.framework.pages;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;

public class CartPage extends BasePage {

    private By cartItems;
    private By checkoutButton;

    public CartPage(WebDriver driver) {
        super(driver);
        initLocators();
    }

    private void initLocators() {
        boolean isNativeMobile = (driver instanceof AndroidDriver) || (driver instanceof IOSDriver);

        if (isNativeMobile) {
            cartItems = AppiumBy.accessibilityId("test-Item");
            checkoutButton = AppiumBy.accessibilityId("test-CHECKOUT");
        } else {
            cartItems = By.className("cart_item");
            checkoutButton = By.id("checkout");
        }
    }

    /**
     * Verifies a specific product is in the cart.
     * Uses the inherited getText() which includes the 20s safety wait.
     */
    public boolean isItemInCart(String productName) {
        // Use a locator that finds the text anywhere in the name div
        String xpath = String.format("//div[@class='inventory_item_name' and contains(normalize-space(text()), '%s')]", productName);
        return isElementDisplayed(By.xpath(xpath));
    }

    /**
     * Triggers the checkout flow.
     */
    public void clickCheckout() {
        waitForVisibility(checkoutButton);
        // Standard click
        click(checkoutButton, "Checkout Button");

        // Sync check: Did we actually move?
        boolean moved = waitForUrlToContain("checkout-step-one");

        // Fallback if the UI is stuck
        if (!moved) {
            System.out.println("[WARN] Standard Checkout click failed. Forcing JS click.");
            ((JavascriptExecutor) driver).executeScript("arguments[0].click();", driver.findElement(checkoutButton));
        }
    }
}
