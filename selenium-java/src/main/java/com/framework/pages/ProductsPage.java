package com.framework.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

/**
 * ProductsPage: Web-focused page for the main products listing.
 * Mirrors CucumberFramework's ProductsPage — same capabilities, POM implementation.
 */
public class ProductsPage extends BasePage {

    private final By title     = By.className("title");
    private final By cartBadge = By.className("shopping_cart_badge");
    private final By cartLink  = By.className("shopping_cart_link");

    public ProductsPage(WebDriver driver) {
        super(driver);
    }

    public boolean isProductsPageDisplayed() {
        return isElementDisplayed(title);
    }

    public String getPageTitle() {
        return getText(title);
    }

    public void addToCart(String productName) {
        String formattedName = productName.toLowerCase().replace(" ", "-");
        By addButton    = By.id("add-to-cart-" + formattedName);
        By removeButton = By.id("remove-" + formattedName);

        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(addButton));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
        waitForVisibility(removeButton);
    }

    public String getCartBadgeText() {
        return getText(cartBadge);
    }

    public void clickCartIcon() {
        click(cartLink, "Cart Icon");
    }
}
