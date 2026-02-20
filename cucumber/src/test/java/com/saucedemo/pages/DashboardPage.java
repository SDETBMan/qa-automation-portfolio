package com.saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

public class DashboardPage extends BasePage {

    private final By cartIcon   = By.className("shopping_cart_link");
    private final By menuButton = By.id("react-burger-menu-btn");
    private final By logoutLink = By.id("logout_sidebar_link");
    private final By pageTitle  = By.className("title");

    public DashboardPage(WebDriver driver) {
        super(driver);
    }

    public boolean isCartIconDisplayed() {
        try {
            return driver.findElement(cartIcon).isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    public String getWelcomeMessageText() {
        return getText(pageTitle);
    }

    public void clickLogoutButton() {
        click(menuButton);
        try {
            WebElement logoutBtn = wait.until(ExpectedConditions.presenceOfElementLocated(logoutLink));
            ((JavascriptExecutor) driver).executeScript("arguments[0].click();", logoutBtn);
        } catch (Exception e) {
            click(logoutLink);
        }
    }
}
