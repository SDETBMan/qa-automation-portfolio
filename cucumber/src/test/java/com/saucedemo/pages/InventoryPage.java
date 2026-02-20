package com.saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

public class InventoryPage extends BasePage {

    private final By productsHeader = By.className("title");
    private final By cartBadge      = By.className("shopping_cart_badge");
    private final By cartLink       = By.className("shopping_cart_link");

    public InventoryPage(WebDriver driver) {
        super(driver);
    }

    public boolean isProductsHeaderDisplayed() {
        try {
            wait.until(ExpectedConditions.visibilityOfElementLocated(productsHeader));
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public int getCartItemCount() {
        try {
            String text = driver.findElement(cartBadge).getText();
            return text.isEmpty() ? 0 : Integer.parseInt(text);
        } catch (Exception e) {
            return 0;
        }
    }

    public void waitForCartBadge() {
        wait.until(ExpectedConditions.visibilityOfElementLocated(cartBadge));
    }

    public void addToCart(String productName) {
        String formattedName = productName.toLowerCase().replace(" ", "-");
        By addButton    = By.id("add-to-cart-" + formattedName);
        By removeButton = By.id("remove-" + formattedName);

        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(addButton));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
        wait.until(ExpectedConditions.visibilityOfElementLocated(removeButton));
    }

    public void removeFromCart(String productName) {
        String formattedName = productName.toLowerCase().replace(" ", "-");
        By addButton = By.id("add-to-cart-" + formattedName);
        click(By.id("remove-" + formattedName));
        // Wait for "Add to Cart" to reappear — confirms DOM has updated before getCartItemCount() is called
        wait.until(ExpectedConditions.visibilityOfElementLocated(addButton));
    }

    public CartPage goToCart() {
        // JS click bypasses headless CI intercept issues on the cart icon link
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(cartLink));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
        wait.until(ExpectedConditions.urlContains("cart.html"));
        return new CartPage(driver);
    }
}
