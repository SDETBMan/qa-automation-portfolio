package com.cucumber.framework.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

/**
 * InventoryPage — SauceDemo product catalog and cart operations.
 */
public class InventoryPage extends BasePage {

    private final By cartBadge = By.className("shopping_cart_badge");
    private final By cartLink  = By.className("shopping_cart_link");

    public InventoryPage(WebDriver driver) {
        super(driver);
    }

    public void addItemToCart(String itemSlug) {
        click(By.id("add-to-cart-" + itemSlug));
    }

    public void removeItemFromCart(String itemSlug) {
        click(By.id("remove-" + itemSlug));
    }

    public void goToCart() {
        click(cartLink);
        waitForUrl("cart");
    }

    public String getCartBadgeCount() {
        return getText(cartBadge);
    }

    public boolean isCartBadgeVisible() {
        return isVisible(cartBadge);
    }
}
