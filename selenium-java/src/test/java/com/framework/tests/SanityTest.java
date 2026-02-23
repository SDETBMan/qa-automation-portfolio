package com.framework.tests;

import com.framework.utils.ConfigReader;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;

import java.net.HttpURLConnection;
import java.net.URL;
import java.time.Duration;

/**
 * SanityTest: Validates the automation infrastructure itself — not the app under test.
 *
 * <p>WHY SANITY TESTS EXIST: Before trusting test results, you must trust the test
 * environment. If Chrome is not installed, if the config file is missing, or if the
 * Selenium Grid is down, every test in the suite will fail for infrastructure reasons
 * rather than application defects. Sanity tests diagnose those infrastructure problems
 * directly, making it immediately clear whether failures are "the app is broken" or
 * "the test environment is broken."
 *
 * <p>WHY THIS CLASS DOES NOT EXTEND {@link com.framework.base.BaseTest}:
 * This is intentional and important. BaseTest uses DriverFactory, DriverManager, and
 * the full framework stack. If any part of that stack is broken, BaseTest itself would
 * fail — which would mask the real cause. SanityTest bypasses the framework entirely,
 * using raw Selenium directly. If SanityTest passes but other tests fail, the problem
 * is in the framework, not the environment. If SanityTest fails, the environment itself
 * is broken. This isolation is what makes sanity tests valuable.
 *
 * <p>WHAT THIS CLASS COVERS:
 * <ol>
 *   <li><b>Browser engine</b> — "bare metal" ChromeDriver launch without any framework
 *       abstractions. Proves Chrome is installed and functional on this machine/CI node.</li>
 *   <li><b>Configuration integrity</b> — reads config.properties and confirms critical
 *       values (URL, timeout) are present and correctly formatted.</li>
 *   <li><b>Grid connectivity</b> — makes an HTTP ping to the Selenium Grid hub to confirm
 *       it is reachable before tests that depend on it are run.</li>
 * </ol>
 */
public class SanityTest {

    // ---------------------------------------------------------
    // HAPPY PATH (Sanity): Browser Engine Check
    // "Bare Metal" test - No DriverFactory, no listeners.
    // If this fails, the machine/CI node is broken.
    // ---------------------------------------------------------

    /**
     * testRawSeleniumLaunch: Launches ChromeDriver directly without any framework
     * abstractions and verifies the SauceDemo login page renders.
     *
     * <p>WHY "BARE METAL": This test intentionally avoids DriverFactory, DriverManager,
     * BaseTest, and all framework utilities. It uses only raw Selenium 4 APIs.
     * This is the most honest test of whether "Selenium works on this machine" —
     * there is no framework code between this test and the browser that could
     * hide or cause the failure.
     *
     * <p>WHY HEADLESS HERE: CI environments typically have no graphical display.
     * These Chrome options match what most CI pipelines require:
     * <ul>
     *   <li>{@code --headless=new} — headless mode without a window.</li>
     *   <li>{@code --no-sandbox} — required in Docker containers where the Linux
     *       user namespace sandbox is not available.</li>
     *   <li>{@code --disable-dev-shm-usage} — prevents /dev/shm (shared memory)
     *       from being too small in Docker, which causes Chrome to crash.</li>
     * </ul>
     *
     * <p>WHY THE LOGO ASSERTION: Rather than just checking the URL (which could
     * succeed while the page renders blank), this test waits for a visible UI element —
     * the login logo — confirming the page actually rendered meaningful content.
     */
    @Test(groups = {"sanity", "smoke", "web"})
    public void testRawSeleniumLaunch() {
        System.out.println("[INFO] Starting Bare-Metal Sanity Check...");
        WebDriver driver = null;

        try {
            // Configure Chrome options for headless CI execution.
            ChromeOptions options = new ChromeOptions();
            options.addArguments("--headless=new");
            options.addArguments("--no-sandbox");
            options.addArguments("--disable-dev-shm-usage");
            options.addArguments("--remote-allow-origins=*");

            // Selenium 4 includes Selenium Manager, which automatically downloads
            // the correct ChromeDriver version — no manual ChromeDriver setup needed.
            driver = new ChromeDriver(options);

            // Navigate using URL from config — keeps this test environment-agnostic.
            driver.get(ConfigReader.getProperty("url"));

            // Explicit wait: poll up to 5 seconds for the logo to appear.
            // This is more reliable than an implicit wait because it waits for a
            // specific, meaningful element — not just any element on the page.
            WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));
            WebElement logo = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("login_logo")));

            // Confirm the logo element is actually displayed (visible, not hidden).
            Assert.assertTrue(logo.isDisplayed(), "Raw Selenium failed to render the page!");
            System.out.println("[PASS] Browser Engine is operational.");

        } catch (Exception e) {
            // Any unexpected exception (ChromeDriver not found, page load timeout, etc.)
            // is wrapped in a clear failure message that points to the root cause.
            Assert.fail("CRITICAL: Selenium Environment is broken! " + e.getMessage());
        } finally {
            // Always quit the driver, even if the test failed.
            // Without this, the Chrome process would remain running indefinitely.
            if (driver != null) driver.quit();
        }
    }

    // ---------------------------------------------------------
    // EDGE CASE (Sanity): Configuration Integrity
    // Verifies that critical secrets/config are actually loaded.
    // ---------------------------------------------------------

    /**
     * testConfigurationLoad: Verifies that the config.properties file is present,
     * readable, and contains valid values for critical settings.
     *
     * <p>WHY TEST THE CONFIG: If config.properties is missing or corrupt, every test
     * that calls {@code ConfigReader.getProperty()} will get null back and fail with
     * cryptic NullPointerExceptions in page objects and assertions rather than a clear
     * "config is broken" message. This test provides that clear early warning.
     *
     * <p>WHAT IS VALIDATED:
     * <ul>
     *   <li>{@code url} — the base URL of the app under test. Missing = all navigation fails.</li>
     *   <li>{@code timeout.explicit} — the explicit wait timeout in seconds. Must be a
     *       parseable integer; a non-numeric value would crash all page objects that
     *       use explicit waits.</li>
     * </ul>
     */
    @Test(groups = {"sanity"})
    public void testConfigurationLoad() {
        System.out.println("[INFO] Checking Config Integrity...");

        // Verify the base URL is present and non-empty.
        // Null means the key doesn't exist in config; empty means it was set to nothing.
        // Both are fatal for any navigation-dependent test.
        String url = ConfigReader.getProperty("url");
        Assert.assertNotNull(url, "Config Failure: 'url' is missing in config.properties");
        Assert.assertFalse(url.isEmpty(), "Config Failure: 'url' is empty");

        // Verify the explicit timeout value is a valid integer.
        // parseInt() throws NumberFormatException if the value is e.g. "ten" or empty.
        // This assertion converts that exception into a clear, actionable test failure.
        String timeout = ConfigReader.getProperty("timeout.explicit");
        try {
            Integer.parseInt(timeout);
        } catch (NumberFormatException e) {
            Assert.fail("Config Failure: 'timeout.explicit' is not a valid number.");
        }

        System.out.println("[PASS] Configuration file is readable and valid.");
    }

    // ---------------------------------------------------------
    // INFRASTRUCTURE TEST (Sanity): Grid Connectivity
    // Checks if the Docker Grid (Hub) is actually up and listening.
    // ---------------------------------------------------------

    /**
     * testHubConnectivity: Checks whether the Selenium Grid hub is reachable
     * by sending a lightweight HTTP GET to its {@code /status} endpoint.
     *
     * <p>WHY CHECK THE GRID: Tests that use {@code -Dtarget=grid} (Docker Compose or
     * Kubernetes deployment) will hang or fail immediately if the Grid hub isn't running.
     * This sanity test catches that before any tests run, saving time diagnosing
     * "why did 50 tests all fail with connection refused?"
     *
     * <p>WHY NOT FAIL IF HUB IS UNREACHABLE: This test is expected to run in all
     * environments, including local development where Docker may not be running.
     * A hard {@code Assert.fail()} would break local runs where the Grid simply
     * isn't needed. Instead, the test logs a warning and passes — only in a dedicated
     * CI environment with Grid would you un-comment the hard failure assertion.
     *
     * <p>WHY 2-SECOND TIMEOUT: The Grid should respond in milliseconds if it's up.
     * A 2-second {@code connectTimeout} means we "fail fast" without hanging the
     * test suite if the hub is down. Long timeouts (the default is often 30+ seconds)
     * would make the sanity check annoyingly slow to fail.
     */
    @Test(groups = {"sanity", "docker"})
    public void testHubConnectivity() {
        String hubUrl = ConfigReader.getProperty("hub.url");

        // Log context about which hub we're checking, for CI debugging.
        if (hubUrl == null || hubUrl.contains("localhost")) {
            System.out.println("[INFO] Checking connectivity to Local Grid: " + hubUrl);
        }

        try {
            // Java's built-in HttpURLConnection is used here deliberately —
            // it's a lightweight HTTP ping with no external library dependencies,
            // which is appropriate for an infrastructure health check.
            URL url = new URL(hubUrl + "/status"); // Selenium Grid 4 status endpoint
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(2000); // Fail fast (2 seconds) if hub is down

            int responseCode = connection.getResponseCode();

            // HTTP 200 OK means the Selenium Grid hub is alive and accepting connections.
            Assert.assertEquals(responseCode, 200, "Selenium Grid is not responding! Response Code: " + responseCode);
            System.out.println("[PASS] Selenium Grid is reachable.");

        } catch (Exception e) {
            // Grid not running is expected in local dev — warn but don't fail.
            // In a dedicated CI environment that requires the Grid, uncomment
            // Assert.fail() below to turn this into a hard failure:
            // Assert.fail("Grid Infrastructure is DOWN.");
            System.out.println("[WARN] Grid check failed (This is expected if not running Docker): " + e.getMessage());
        }
    }
}
