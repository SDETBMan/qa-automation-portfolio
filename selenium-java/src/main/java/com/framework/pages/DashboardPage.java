package com.framework.pages;

import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

/**
 * DashboardPage: Handles post-login interactions for both Web and Mobile platforms.
 */
public class DashboardPage extends BasePage {

    private By cartIcon;
    private By menuButton;
    private By logoutLink;
    private By pageTitle;

    public DashboardPage(WebDriver driver) {
        super(driver);
        initLocators();
    }

    /**
     * Initializes locators dynamically based on the active platform.
     */
    private void initLocators() {
        boolean isNativeMobile = (driver instanceof AndroidDriver) || (driver instanceof IOSDriver);

        if (isNativeMobile) {
            // MOBILE (Accessibility IDs)
            cartIcon = AppiumBy.accessibilityId("test-Cart");
            menuButton = AppiumBy.accessibilityId("test-Menu");
            logoutLink = AppiumBy.accessibilityId("test-LOGOUT");
            pageTitle = By.xpath("//android.widget.TextView[@text='PRODUCTS']");
        } else {
            // WEB (Standard CSS/ID)
            cartIcon = By.className("shopping_cart_link");
            menuButton = By.id("react-burger-menu-btn");
            logoutLink = By.id("logout_sidebar_link");
            pageTitle = By.className("title");
        }
    }

    // ==================================================
    // ACTION METHODS
    // ==================================================

    /**
     * Verifies visibility of the Shopping Cart icon.
     */
    public boolean isCartIconDisplayed() {
        try {
            return driver.findElement(cartIcon).isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Executes the logout sequence, handling platform-specific menu animations.
     */
    public void clickLogoutButton() {
        // 1. Open Menu
        click(menuButton, "Hamburger Menu");

        // 2. Platform-Specific Click Logic
        if (driver instanceof AndroidDriver || driver instanceof IOSDriver) {
            // Mobile: Wait for menu transition before clicking
            waitForVisibility(logoutLink);
            click(logoutLink, "Logout Link");
        } else {
            // Web: Use JavascriptExecutor to bypass potential animation overlays
            try {
                WebElement logoutBtn = wait.until(ExpectedConditions.presenceOfElementLocated(logoutLink));
                ((JavascriptExecutor) driver).executeScript("arguments[0].click();", logoutBtn);
                System.out.println("[WEB-ACTION] Force Clicked Logout via JS");
            } catch (Exception e) {
                click(logoutLink, "Logout Link (Fallback)");
            }
        }
    }

    /**
     * Retrieves the primary header/welcome text from the dashboard.
     */
    public String getWelcomeMessageText() {
        waitForVisibility(pageTitle);
        return getText(pageTitle);
    }
}