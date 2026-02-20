package com.framework.pages;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

public class LoginPage extends BasePage {

    private By usernameField;
    private By passwordField;
    private By loginButton;
    private By errorMessage;

    public LoginPage(WebDriver driver) {
        super(driver);
        initLocators();
    }

    /**
     * Initializes locators based on the active Driver (Web vs. Mobile).
     */
    private void initLocators() {
        boolean isNativeMobile = (driver instanceof AndroidDriver) || (driver instanceof IOSDriver);

        if (isNativeMobile) {
            // SWAG LABS NATIVE APP LOCATORS (Accessibility IDs)
            usernameField = AppiumBy.accessibilityId("test-Username");
            passwordField = AppiumBy.accessibilityId("test-Password");
            loginButton = AppiumBy.accessibilityId("test-LOGIN");
            errorMessage = AppiumBy.accessibilityId("test-Error message");
        } else {
            // SWAG LABS WEB LOCATORS (Standard IDs/CSS)
            usernameField = By.id("user-name");
            passwordField = By.id("password");
            loginButton = By.id("login-button");
            errorMessage = By.cssSelector("h3[data-test='error']");
        }
    }

    // ==================================================
    // ACTIONS
    // ==================================================

    /**
     * Performs a unified login action.
     */
    public void login(String username, String password) {
        // We use the 3-parameter version to maintain descriptive logs.
        enterText(usernameField, username, "Username Field");
        enterText(passwordField, password, "Password Field");
        click(loginButton, "Login Button");
    }

    /**
     * Robust Error Message Retrieval for Web and Mobile platforms.
     */
    public String getErrorMessage() {
        // 1. Try standard getText (Works for Web)
        String text = getText(errorMessage);

        // 2. Mobile Fallback Logic for nested or attributed text.
        if (text == null || text.isEmpty()) {
            if (driver instanceof AndroidDriver) {
                try {
                    text = driver.findElement(errorMessage)
                            .findElement(By.className("android.widget.TextView"))
                            .getText();
                } catch (Exception e) {
                    System.out.println("[WARN] Failed to find child TextView on Android");
                }
            } else if (driver instanceof IOSDriver) {
                try {
                    text = driver.findElement(errorMessage).getAttribute("label");
                    if (text == null || text.isEmpty()) {
                        text = driver.findElement(errorMessage).getAttribute("name");
                    }
                } catch (Exception e) {
                    System.out.println("[WARN] Failed to retrieve iOS attribute");
                }
            }
        }
        return text;
    }

    /**
     * Verifies if the login button is visible, used for session state validation.
     */
    public boolean isLoginButtonDisplayed() {
        try {
            return driver.findElement(loginButton).isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }
}
