package com.framework.pages;

import com.framework.utils.ConfigReader;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.ios.IOSDriver;
import org.openqa.selenium.*;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.time.Duration;

/**
 * BasePage: The shared foundation that every Page Object class in the framework inherits from.
 *
 * WHY THIS CLASS EXISTS:
 * Without a base page, every single Page Object (LoginPage, CartPage, etc.) would need to
 * duplicate the same boilerplate code: creating a WebDriverWait, writing a click() method,
 * handling flaky elements, etc. This violates the DRY principle (Don't Repeat Yourself).
 * BasePage centralizes all reusable browser interaction logic so that each individual
 * Page Object only needs to describe WHAT is on the page, not HOW to interact with it.
 *
 * WHAT IT PROVIDES:
 *   - A pre-configured WebDriverWait so waits are consistent across the entire framework
 *   - Reliable, production-grade click and type methods that handle common failure scenarios
 *   - Cross-platform awareness: the same code path works for Chrome, Firefox, AND mobile
 *   - Visual debugging: elements are highlighted in red during test execution for easy demo
 *
 * DESIGN PATTERN — Page Object Model (POM):
 * The Page Object Model is an industry-standard design pattern where each screen of the
 * application under test is represented by its own Java class. BasePage is the parent
 * of all those classes, providing the shared toolkit they all need.
 *
 * For recruiters: A well-designed BasePage is a hallmark of a mature automation framework.
 * It shows that the engineer thinks about reusability and long-term maintenance.
 */
public class BasePage {

    // The WebDriver is "protected" so all child Page Object classes (LoginPage, CartPage, etc.)
    // can access it directly. Making it "private" would prevent child classes from using it.
    protected WebDriver driver;

    // WebDriverWait makes Selenium wait up to a configured timeout for elements to appear
    // before interacting with them. Without waits, tests fail on slow networks or when
    // animations are still playing. "protected" so subclasses can use it for custom waits.
    protected WebDriverWait wait;

    /**
     * Constructor: Accepts a WebDriver and sets up the wait configuration.
     *
     * WHY INJECT THE DRIVER:
     * Rather than creating the driver here, we accept it as a parameter. This is called
     * "dependency injection" — the Page Object receives what it needs rather than creating
     * it. This makes Page Objects easy to test in isolation (you can pass a mock driver)
     * and ensures the same driver instance is shared consistently across the entire test.
     *
     * WHY READ TIMEOUT FROM CONFIG:
     * Hardcoding "20 seconds" here would require a code change to adjust the wait time.
     * Reading from config.properties lets the team tune timeouts per environment (e.g.,
     * staging might need longer waits than local) without touching source code.
     *
     * @param driver The WebDriver instance managing the current browser or mobile session
     */
    public BasePage(WebDriver driver) {
        this.driver = driver;
        int timeout = Integer.parseInt(ConfigReader.getProperty("timeout.explicit", "20"));
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(timeout));
    }

    // ==================================================
    // 1. WAITS & VISIBILITY
    // These methods solve the most common cause of flaky (intermittently failing)
    // tests: trying to interact with an element before it is ready on the page.
    // ==================================================

    /**
     * Waits for an element to be visible on the page before proceeding.
     *
     * WHY THIS EXISTS:
     * Modern web pages load content dynamically (via JavaScript). An element's locator
     * might exist in the HTML but the element itself might be hidden, still loading, or
     * not yet rendered. This method blocks test execution until the element is actually
     * visible to the user, then throws a TimeoutException with a helpful message if it
     * never appears — rather than a cryptic "NoSuchElementException."
     *
     * @param locator The By selector that identifies the element (e.g., By.id("submit"))
     */
    protected void waitForVisibility(By locator) {
        try {
            wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
        } catch (TimeoutException e) {
            System.err.println("[ERROR] Element not visible after timeout: " + locator);
            throw e;
        }
    }

    /**
     * Waits for specific text to appear inside an element, or for the element to vanish.
     *
     * WHY THIS EXISTS — "Perfect for Cart Count assertions":
     * After adding an item to a cart, the badge showing the item count changes from nothing
     * to "1". If we check the count immediately, we might read the old value ("0") before
     * the JavaScript has updated the DOM. This method waits for the NEW text to be present,
     * eliminating that race condition.
     *
     * THE EMPTY STRING SPECIAL CASE:
     * Passing an empty string means "wait until this element disappears entirely." This is
     * useful for assertions like "after removing the last item, the cart badge should vanish."
     *
     * @param locator      The element to watch
     * @param expectedText The text to wait for; pass "" to wait for element invisibility
     * @return true if the condition was met before timeout; false if it timed out
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
     * A "safe" visibility check that returns false instead of crashing when an element is absent.
     *
     * WHY THIS EXISTS:
     * Selenium's driver.findElement() throws an exception if the element is not found.
     * This is often the desired behavior, but sometimes we need to ask "is this element
     * present?" as a yes/no question — for example, checking whether an error banner
     * appeared, or whether a logout button is visible to confirm a session is active.
     * Wrapping the wait in a try/catch converts the exception into a clean boolean result.
     *
     * @param locator The element to check for
     * @return true if the element is visible within the wait timeout; false otherwise
     */
    protected boolean isElementDisplayed(By locator) {
        try {
            wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Waits for the browser's current URL to contain a specific substring.
     *
     * WHY THIS EXISTS:
     * After clicking a navigation element, the page transition happens asynchronously.
     * Tests that immediately check the URL after clicking will often fail because the
     * browser hasn't finished navigating yet. This method waits for the URL to confirm
     * the navigation succeeded before the test continues.
     *
     * Example usage: After clicking "Checkout", wait for the URL to contain "checkout-step-one"
     * to confirm the page actually changed before asserting anything on it.
     *
     * @param fraction A substring expected to appear in the URL (e.g., "inventory", "cart.html")
     * @return true if the URL contained the fragment before timeout; false otherwise
     */
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
    // These methods wrap Selenium's raw commands with reliability improvements.
    // Every interaction: waits for readiness, handles edge cases, and logs its action.
    // ==================================================

    /**
     * Clicks an element with built-in wait, visual highlighting, and a JavaScript fallback.
     *
     * WHY THE JAVASCRIPT FALLBACK:
     * The most common cause of "ElementClickInterceptedException" in Selenium is when
     * another element (like a cookie banner, loading overlay, or sticky header) is covering
     * the element you want to click. Selenium's standard click() refuses to click a covered
     * element to mimic real user behavior. The JavaScript fallback (arguments[0].click())
     * bypasses this protection and clicks the element directly in the DOM. This is acceptable
     * for automation but would not be how a real user interacts with the page.
     *
     * WHY THE ACTIONS.MOVETO:
     * For web browsers, we move the mouse to the element before clicking. This is important
     * for elements that only become interactive on hover (like dropdown menus), and it
     * ensures the element scrolls into view before Selenium attempts to click it.
     *
     * @param locator     The element to click
     * @param elementName A human-readable name shown in logs (e.g., "Login Button")
     */
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

    /**
     * Overloaded click method for when a descriptive name is not needed.
     *
     * WHY THIS OVERLOAD EXISTS:
     * Java allows multiple methods with the same name but different parameters (overloading).
     * This version is a convenience shortcut — it calls the full click() method above,
     * passing the locator's toString() as the log name. This is useful in utility code
     * where a human-readable name would add noise rather than clarity.
     *
     * @param locator The element to click; the locator's string representation is used for logging
     */
    protected void click(By locator) {
        click(locator, locator.toString());
    }

    /**
     * Types text into an input field, clearing any existing content first.
     *
     * WHY CLEAR() BEFORE SENDKEYS:
     * If this method is called on a field that already has content (perhaps from a previous
     * step or auto-fill), the new text would be appended to the old text, corrupting the
     * input. Calling clear() first guarantees the field is empty before typing.
     *
     * WHY HIDE THE KEYBOARD ON MOBILE:
     * On mobile devices, the virtual keyboard appears when a text field is focused, and it
     * can cover other elements on the screen. Hiding it after typing prevents it from
     * blocking the next interaction (like clicking the Login button).
     *
     * @param locator     The input field to type into
     * @param text        The text to enter
     * @param elementName A human-readable name for logging (e.g., "Username Field")
     */
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
     * The Flakiness Killer: Waits for element visibility and returns its trimmed text.
     *
     * WHY TRIM():
     * Web pages sometimes include invisible whitespace around text content (spaces, tabs,
     * newlines). If your assertion expects "1" but the element contains " 1 " (with spaces),
     * assertEquals will fail even though the text looks correct in the browser. Calling
     * trim() strips all leading and trailing whitespace, making assertions more reliable.
     *
     * WHY RETURN EMPTY STRING ON FAILURE:
     * Rather than propagating an exception when text cannot be retrieved, we return ""
     * and log the error. This allows callers to handle missing text gracefully (e.g.,
     * "if empty, the element wasn't there") rather than crashing the test with a stack trace.
     *
     * @param locator The element whose text content should be returned
     * @return The element's visible text with whitespace trimmed; "" if retrieval fails
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
    // Private utilities used internally by this class.
    // "private" means they are not visible to child Page Object classes.
    // ==================================================

    /**
     * Determines if the current driver is a mobile driver.
     *
     * WHY THIS EXISTS:
     * Several methods in this class behave differently on mobile vs. web. Rather than
     * duplicating the "instanceof AndroidDriver || instanceof IOSDriver" check everywhere,
     * we centralize it in this helper. Checking "instanceof" (is this object an instance
     * of this class?) is the standard Java way to determine an object's runtime type.
     *
     * @param driver The driver to inspect
     * @return true if the driver is an Appium mobile driver; false for web browsers
     */
    private boolean isMobile(WebDriver driver) {
        return driver instanceof AndroidDriver || driver instanceof IOSDriver;
    }

    /**
     * Returns a human-readable platform name for use in log messages.
     *
     * WHY THIS EXISTS:
     * When the same test runs on web and mobile, logs like "[WEB] Entered 'admin' into Username"
     * or "[ANDROID] Entered 'admin' into Username" make it immediately clear which platform
     * a log entry came from — critical when debugging parallel execution failures.
     *
     * @return "ANDROID", "IOS", or "WEB" depending on the driver type
     */
    private String getPlatform() {
        if (driver instanceof AndroidDriver) return "ANDROID";
        if (driver instanceof IOSDriver) return "IOS";
        return "WEB";
    }

    /**
     * Hides the on-screen keyboard on Android devices after text input.
     *
     * WHY THE TRY/CATCH WITH IGNORED EXCEPTION:
     * On some Android devices and emulators, the keyboard is not always visible when
     * hideKeyboard() is called (for example, if it auto-dismissed). Calling hideKeyboard()
     * when the keyboard is not present throws an exception. Since we don't actually need
     * the keyboard to be present — we just want to ensure it's gone — we safely ignore
     * that exception. The "ignored" variable name signals to other developers that this
     * is an intentional choice, not a missed error.
     */
    private void hideKeyboard() {
        if (driver instanceof AndroidDriver) {
            try {
                ((AndroidDriver) driver).hideKeyboard();
            } catch (Exception ignored) {}
        }
    }

    /**
     * Draws a red border around an element to make it visible in screen recordings and demos.
     *
     * WHY THIS EXISTS:
     * During test demos, screen recordings, or debugging sessions, it can be hard to see
     * which element Selenium just clicked or interacted with. JavaScript is used to
     * temporarily add a bright red CSS border to the element, making it visually obvious.
     *
     * WHY ONLY FOR WEB (not mobile):
     * Mobile apps don't use CSS, so JavaScript DOM manipulation doesn't apply to native
     * Android or iOS elements. We guard against mobile drivers to prevent errors.
     *
     * WHY THE TRY/CATCH WITH IGNORED EXCEPTION:
     * Highlighting is a cosmetic feature — if it fails (e.g., the element is in a shadow DOM
     * or the JS execution is restricted), we never want that to crash a test. It is purely
     * for human readability of test output.
     *
     * @param element The WebElement to highlight with a red border
     */
    private void highlightElement(WebElement element) {
        if (!isMobile(driver)) {
            try {
                ((JavascriptExecutor) driver).executeScript("arguments[0].style.border='3px solid red'", element);
            } catch (Exception ignored) {}
        }
    }
}
