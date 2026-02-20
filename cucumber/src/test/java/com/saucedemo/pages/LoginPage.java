package com.saucedemo.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

public class LoginPage extends BasePage {

    private By usernameField = By.id("user-name");
    private By passwordField = By.id("password");
    private By loginButton = By.id("login-button");
    private By errorMessage = By.cssSelector("[data-test='error']"); // Locator for the error

    public LoginPage(WebDriver driver) {
        super(driver);
    }

    // --- Granular Methods for Cucumber Steps ---

    public void enterUsername(String username) {
        // Uses BasePage's 'sendKeys' (clears + waits + types)
        sendKeys(usernameField, username);
    }

    public void enterPassword(String password) {
        sendKeys(passwordField, password);
    }

    public void clickLogin() {
        // Uses BasePage's 'click' (waits for clickable + clicks)
        click(loginButton);
    }

    public boolean isErrorDisplayed() {
        // We can still access 'driver' directly because it's protected in BasePage
        return driver.findElement(errorMessage).isDisplayed();
    }

    // Optional: Keep this helper if you ever want to do it all in one line
    public void login(String username, String password) {
        enterUsername(username);
        enterPassword(password);
        clickLogin();
    }

    public boolean isLoginButtonDisplayed() {
        try {
            return driver.findElement(loginButton).isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }
}
