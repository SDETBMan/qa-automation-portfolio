package com.saucedemo.pages;

import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import java.time.Duration;

/**
 * BasePage: The parent class that every Page Object in this framework extends.
 *
 * <p>WHY A BASE PAGE EXISTS (Page Object Model pattern): In Selenium tests, the
 * same low-level actions — wait for an element, then click it; wait for an element,
 * then read its text — appear hundreds of times across a test suite. Without a
 * shared base class, each page would duplicate this boilerplate, and a single change
 * (e.g., increasing the wait timeout from 10 to 15 seconds) would require editing
 * every single page file.
 *
 * <p>BasePage centralises these shared behaviours in one place:
 * <ul>
 *   <li>Every page gets a {@link WebDriverWait} instance tuned to the same timeout.</li>
 *   <li>Click, type, and read operations are wrapped with automatic waiting so individual
 *       pages never need to write wait logic themselves.</li>
 *   <li>Changing the default timeout or adding a new shared utility (e.g., scroll-to-element)
 *       only requires editing this one file.</li>
 * </ul>
 *
 * <p>INHERITANCE: Child pages call {@code super(driver)} in their constructors to
 * trigger BasePage's constructor, which sets up the shared {@code driver} and
 * {@code wait} fields that child pages then inherit and use freely.
 */
public class BasePage {

    /**
     * The Selenium WebDriver instance used to control the browser.
     * Declared {@code protected} so all child page classes can access it directly
     * without needing a getter method.
     */
    protected WebDriver driver;

    /**
     * A pre-configured explicit wait (i.e., a wait that polls until a specific
     * condition is true, rather than sleeping blindly for a fixed duration).
     * Declared {@code protected} so child pages can use it for conditions not
     * covered by the helper methods defined here.
     */
    protected WebDriverWait wait;

    /**
     * Clicks an element using JavaScript rather than Selenium's native click.
     *
     * <p>WHY JAVASCRIPT CLICK: Selenium's standard {@code element.click()} can fail
     * in some browsers or CI environments with an "Element is not clickable at
     * point" error — typically because another element (like a sticky header or
     * a cookie banner) is overlapping the target. JavaScript bypasses the browser's
     * normal click-interception mechanism and fires the click event directly on the
     * DOM node, making it more reliable for these edge cases.
     *
     * <p>This method first waits for the element to be clickable (visible and not
     * disabled) before executing the JavaScript, so it still benefits from explicit
     * waiting.
     *
     * @param locator the By strategy used to find the element (e.g., By.id("submit"))
     */
    protected void javascriptClick(By locator) {
        // Wait until the element is clickable before attempting the JS click
        WebElement element = wait.until(ExpectedConditions.elementToBeClickable(locator));
        // Cast driver to JavascriptExecutor — WebDriver implements this interface,
        // which exposes the executeScript() method to run arbitrary JavaScript
        ((JavascriptExecutor) driver).executeScript("arguments[0].click();", element);
    }

    /**
     * Constructor that every child page calls via super(driver).
     *
     * <p>Storing the driver and creating the wait here means child pages get both
     * for free. The 10-second timeout is a common industry default: long enough for
     * most page transitions and AJAX calls, short enough that a genuine failure
     * does not make the suite feel frozen.
     *
     * <p>The maximize call is wrapped in a try-catch because mobile drivers
     * (Appium) and headless drivers throw exceptions when asked to maximise a
     * window — it is not a supported concept on those platforms.
     *
     * @param driver the active WebDriver instance for the current test thread
     */
    // Constructor that every Child Page will call
    public BasePage(WebDriver driver) {
        this.driver = driver;
        // WebDriverWait polls every 500ms by default until the condition is met or
        // the timeout (10 seconds here) expires, at which point it throws TimeoutException
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        try {
            driver.manage().window().maximize();
        } catch (Exception ignored) {
            // Mobile and headless drivers may not support maximize
        }
    }

    // --- WRAPPER METHODS (The "Secret Sauce") ---
    // These methods hide the wait-then-act pattern so child pages stay clean and readable.

    /**
     * Waits for an element to be clickable, then clicks it.
     *
     * <p>"Clickable" means the element is both visible on screen AND enabled
     * (not greyed out). This is stricter than just waiting for visibility,
     * which is important for buttons that may render but are temporarily disabled.
     *
     * @param locator the By strategy used to locate the element
     */
    // Click with automatic wait
    protected void click(By locator) {
        wait.until(ExpectedConditions.elementToBeClickable(locator)).click();
    }

    /**
     * Waits for an element to be visible, then returns its text content.
     *
     * <p>Waiting for visibility before reading text prevents empty-string results
     * that occur when the element exists in the DOM but has not yet rendered its
     * content (common with dynamically loaded data).
     *
     * @param locator the By strategy used to locate the element
     * @return the visible text of the element
     */
    // Get Text with automatic wait
    protected String getText(By locator) {
        return wait.until(ExpectedConditions.visibilityOfElementLocated(locator)).getText();
    }

    /**
     * Waits for an element to be visible, clears any existing text, then types
     * the given text into it.
     *
     * <p>The {@code element.clear()} call before typing is important for input
     * fields that may already contain a value (e.g., a pre-filled form field or
     * a field left over from a previous interaction). Without clearing, the new
     * text would be appended to the old text rather than replacing it.
     *
     * @param locator the By strategy used to locate the input element
     * @param text    the text to type into the field
     */
    // Type text with automatic wait
    protected void sendKeys(By locator, String text) {
        WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(locator));
        element.clear();         // Erase any pre-existing value in the field
        element.sendKeys(text);  // Type the new value character by character
    }
}
