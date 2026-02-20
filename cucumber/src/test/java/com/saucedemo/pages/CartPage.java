package com.saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

public class CartPage extends BasePage {

    private final By cartItemName   = By.className("inventory_item_name");
    private final By checkoutButton = By.id("checkout");

    public CartPage(WebDriver driver) {
        super(driver);
    }

    public String getFirstItemName() {
        return driver.findElement(cartItemName).getText();
    }

    public boolean isItemInCart(String productName) {
        String xpath = String.format(
                "//div[@class='inventory_item_name' and contains(normalize-space(text()),'%s')]", productName);
        try {
            return driver.findElement(By.xpath(xpath)).isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    public void clickCheckout() {
        // JS click — standard click can be silently intercepted in headless CI
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(checkoutButton));
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
    }
}
