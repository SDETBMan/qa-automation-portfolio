package com.cucumber.framework.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

/**
 * CartPage — SauceDemo shopping cart.
 */
public class CartPage extends BasePage {

    private final By cartItems      = By.className("cart_item");
    private final By checkoutButton = By.id("checkout");
    private final By itemNames      = By.className("inventory_item_name");

    public CartPage(WebDriver driver) {
        super(driver);
    }

    public int getCartItemCount() {
        return driver.findElements(cartItems).size();
    }

    public boolean isItemInCart(String itemName) {
        return driver.findElements(itemNames).stream()
                .anyMatch(el -> el.getText().trim().equalsIgnoreCase(itemName));
    }

    public void clickCheckout() {
        click(checkoutButton);
        waitForUrl("checkout-step-one");
    }

    public boolean isOnCartPage() {
        return driver.getCurrentUrl().contains("cart");
    }
}
