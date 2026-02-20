package com.framework.pages;

import com.framework.utils.ConfigReader;
import io.appium.java_client.AppiumBy;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.ExpectedConditions;

/**
 * InventoryPage: Manages product selection and cart interactions for Web and Mobile.
 */
public class InventoryPage extends BasePage {

    private By productsHeader;
    private By cartBadge;
    private By cartLink;

    public InventoryPage(WebDriver driver) {
        super(driver);
        initLocators();
    }

    private void initLocators() {
        boolean isNativeMobile = (driver instanceof AndroidDriver) || (driver instanceof IOSDriver);

        if (isNativeMobile) {
            if (driver instanceof AndroidDriver) {
                productsHeader = By.xpath("//android.widget.TextView[@text='PRODUCTS']");
            } else {
                productsHeader = AppiumBy.accessibilityId("PRODUCTS");
            }
            cartBadge = AppiumBy.accessibilityId("test-Cart badge");
            cartLink = AppiumBy.accessibilityId("test-Cart");
        } else {
            productsHeader = By.className("title");
            cartBadge = By.className("shopping_cart_badge");
            cartLink = By.className("shopping_cart_link");
        }
    }

    // ==================================================
    // 1. VALIDATION METHODS
    // ==================================================

    public boolean isProductsHeaderDisplayed() {
        try {
            waitForVisibility(productsHeader);
            return true;
        } catch (TimeoutException e) {
            return false;
        }
    }

    public int getCartItemCount() {
        // Disable implicit wait for this instant check — the badge either exists or it doesn't.
        // With a 10s implicit wait, findElement hangs the full timeout on an empty cart.
        driver.manage().timeouts().implicitlyWait(java.time.Duration.ofSeconds(0));
        try {
            return Integer.parseInt(driver.findElement(cartBadge).getText());
        } catch (Exception e) {
            return 0;
        } finally {
            int implicit = Integer.parseInt(ConfigReader.getProperty("timeout.implicit", "10"));
            driver.manage().timeouts().implicitlyWait(java.time.Duration.ofSeconds(implicit));
        }
    }

    public void waitForCartBadge() {
        waitForVisibility(cartBadge);
    }

    // ==================================================
    // 2. INTERACTION METHODS
    // ==================================================

    public void addToCart(String productName) {
        String formattedName = productName.toLowerCase().replace(" ", "-");
        By addButton = By.id("add-to-cart-" + formattedName);
        By removeButton = By.id("remove-" + formattedName);

        // 1. Wait and capture the element in one go
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(addButton));

        // 2. Log the action (Optional, but great for Allure reports)
        System.out.println("[WEB-ACTION] Force Clicking Add to Cart: " + productName);

        // 3. Force the click via JS to handle Headless/CI latency
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);

        // 4. Confirm the state change (The 'Remove' button appearing)
        waitForVisibility(removeButton);
    }

    public void removeFromCart(String productName) {
        // Use the same ID pattern as addToCart — reliable, no XPath traversal
        String formattedName = productName.toLowerCase().replace(" ", "-");
        By removeButton = By.id("remove-" + formattedName);

        click(removeButton, "Remove Button: " + productName);
        // No DOM-invisibility wait here — getCartItemCount() is now a direct find (no timeout),
        // so the test assertion catches the zero state immediately without a 20s hang.
    }

    public CartPage goToCart() {
        // 1. Try a standard click first
        click(cartLink, "Shopping Cart Icon");

        // 2. Short wait to see if URL changes
        boolean moved = waitForUrlToContain("cart.html");

        // 3. Fallback: If still on inventory, force the click via JS
        if (!moved) {
            System.out.println("[WARN] Standard click failed to navigate. Forcing JS click on Cart Icon.");
            try {
                WebElement element = driver.findElement(cartLink);
                ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
                waitForUrlToContain("cart.html");
            } catch (Exception e) {
                // Last resort: Direct navigation if the UI is completely stuck.
                // URL is composed from config so it reflects any environment changes.
                driver.get(ConfigReader.getProperty("url") + "cart.html");
            }
        }

        return new CartPage(driver);
    }
}
