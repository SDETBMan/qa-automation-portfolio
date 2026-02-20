package com.saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;

public class ProductsPage extends BasePage {

    private By title = By.className("title");
    private By cartBadge = By.className("shopping_cart_badge");
    private By cartLink = By.className("shopping_cart_link");

    public ProductsPage(WebDriver driver) {
        super(driver);
    }

    public boolean isProductsPageDisplayed() {
        // For boolean checks, we often still use driver directly or a try-catch,
        // but 'isDisplayed()' is fast, so this is fine.
        return driver.findElement(title).isDisplayed();
    }

    public String getPageTitle() {
        return getText(title);
    }

    public void addToCart(String productName) {
        String addId = "add-to-cart-" + productName.toLowerCase().replace(" ", "-");
        String removeId = "remove-" + productName.toLowerCase().replace(" ", "-");

        // CHANGE: Using javascriptClick method
        // This bypasses the UI lag and forces the event to fire
        javascriptClick(By.id(addId));

        // We can still access 'wait' directly for complex logic
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id(removeId)));
    }

    public String getCartBadgeText() {
        return getText(cartBadge);
    }

    public void clickCartIcon() {
        click(cartLink);
    }
}
