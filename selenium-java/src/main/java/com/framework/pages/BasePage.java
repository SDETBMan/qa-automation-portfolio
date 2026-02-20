package com.framework.pages;

import com.framework.utils.ConfigReader;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

public class BasePage {
    protected WebDriver driver;
    protected WebDriverWait wait;

    public BasePage(WebDriver driver) {
        this.driver = driver;
        int timeout = Integer.parseInt(ConfigReader.getProperty("timeout.explicit", "20"));
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(timeout));
    }

    // ==================================================
    // 1. WAITS & VISIBILITY
    // ==================================================

    protected void waitForVisibility(By locator) {
        try {
            wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
        } catch (TimeoutException e) {
            System.err.println("[ERROR] Element not visible after timeout: " + locator);
            throw e;
        }
    }

    /**
     * Perfect for "Cart Count" assertions.
     * Waits for the actual text value to change before proceeding.
     */
    public boolean waitForTextToBePresent(By locator, String expectedText) {
        try {
            if(expectedText.isEmpty()) {
                return wait.until(ExpectedConditions.invisibilityOfElementLocated(locator));
            }
            return wait.until(ExpectedConditions.textToBePresentInElementLocated(locator, expectedText));
        } catch (TimeoutException e) {
            return false;
        }
    }

    /**
     * A "Safe" display check. Returns false instead of crashing if element is missing.
     */
    protected boolean isElementDisplayed(By locator) {
        try {
            wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public boolean waitForUrlToContain(String fraction) {
        try {
            return wait.until(ExpectedConditions.urlContains(fraction));
        } catch (TimeoutException e) {
            System.err.println("[ERROR] URL did not contain '" + fraction + "' | Current URL: " + driver.getCurrentUrl());
            return false;
        }
    }

    // ==================================================
    // 2. INTERACTION METHODS
    // ==================================================

    protected void click(By locator, String elementName) {
        try {
            WebElement element = wait.until(ExpectedConditions.elementToBeClickable(locator));
            if (!isMobile(driver)) {
                highlightElement(element);
                // Lead Move: Move to element before clicking to ensure it's in the viewport
                new org.openqa.selenium.interactions.Actions(driver).moveToElement(element).perform();
            }
            element.click();
            System.out.println("[WEB-ACTION] Clicking on: " + elementName);
        } catch (Exception e) {
            // Fallback: If standard click fails due to intercept, use JS
            ((JavascriptExecutor) driver).executeScript("arguments[0].click();", driver.findElement(locator));
            System.out.println("[WEB-ACTION] JS Force Clicked: " + elementName);
        }
    }

    protected void click(By locator) {
        click(locator, locator.toString());
    }

    protected void enterText(By locator, String text, String elementName) {
        try {
            WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
            element.clear();
            element.sendKeys(text);

            if (isMobile(driver)) {
                hideKeyboard();
            }
            System.out.println("[" + getPlatform() + "] Entered '" + text + "' into: " + elementName);
        } catch (TimeoutException e) {
            System.err.println("[ERROR] Could not type into " + elementName);
            throw e;
        }
    }

    /**
     * The Flakiness Killer: Automatically waits for visibility before grabbing text.
     * trim() prevents "Expected '1' but found ' 1 '" failures.
     */
    protected String getText(By locator) {
        try {
            return wait.until(ExpectedConditions.visibilityOfElementLocated(locator)).getText().trim();
        } catch (Exception e) {
            System.err.println("[ERROR] Failed to get text from locator: " + locator);
            return "";
        }
    }

    // ==================================================
    // 3. HELPER METHODS
    // ==================================================

    private boolean isMobile(WebDriver driver) {
        return driver instanceof AndroidDriver || driver instanceof IOSDriver;
    }

    private String getPlatform() {
        if (driver instanceof AndroidDriver) return "ANDROID";
        if (driver instanceof IOSDriver) return "IOS";
        return "WEB";
    }

    private void hideKeyboard() {
        if (driver instanceof AndroidDriver) {
            try {
                ((AndroidDriver) driver).hideKeyboard();
            } catch (Exception ignored) {}
        }
    }

    private void highlightElement(WebElement element) {
        if (!isMobile(driver)) {
            try {
                ((JavascriptExecutor) driver).executeScript("arguments[0].style.border='3px solid red'", element);
            } catch (Exception ignored) {}
        }
    }
}
