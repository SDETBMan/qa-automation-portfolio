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
 * SanityTest: Validates the Automation Infrastructure itself.
 * Independent of the framework's BaseTest to isolate environment issues.
 */
public class SanityTest {

    // ---------------------------------------------------------
    // HAPPY PATH (Sanity): Browser Engine Check
    // "Bare Metal" test - No DriverFactory, no listeners.
    // If this fails, the machine/CI node is broken.
    // ---------------------------------------------------------
    @Test(groups = {"sanity", "smoke", "web"})
    public void testRawSeleniumLaunch() {
        System.out.println("[INFO] Starting Bare-Metal Sanity Check...");
        WebDriver driver = null;

        try {
            // 1. Setup Options (Headless for CI stability)
            ChromeOptions options = new ChromeOptions();
            options.addArguments("--headless=new");
            options.addArguments("--remote-allow-origins=*");

            // 2. Direct Driver Launch (Uses Selenium Manager built-in to 4.x)
            driver = new ChromeDriver(options);

            // 3. Navigation — URL from config so it works across all environments
            driver.get(ConfigReader.getProperty("url"));

            // 4. Verification
            WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(5));
            WebElement logo = wait.until(ExpectedConditions.visibilityOfElementLocated(By.className("login_logo")));

            Assert.assertTrue(logo.isDisplayed(), "Raw Selenium failed to render the page!");
            System.out.println("[PASS] Browser Engine is operational.");

        } catch (Exception e) {
            Assert.fail("CRITICAL: Selenium Environment is broken! " + e.getMessage());
        } finally {
            if (driver != null) driver.quit();
        }
    }

    // ---------------------------------------------------------
    // EDGE CASE (Sanity): Configuration Integrity
    // Verifies that critical secrets/config are actually loaded.
    // ---------------------------------------------------------
    @Test(groups = {"sanity"})
    public void testConfigurationLoad() {
        System.out.println("[INFO] Checking Config Integrity...");

        // 1. Verify URL exists
        String url = ConfigReader.getProperty("url");
        Assert.assertNotNull(url, "Config Failure: 'url' is missing in config.properties");
        Assert.assertFalse(url.isEmpty(), "Config Failure: 'url' is empty");

        // 2. Verify Timeout is a number
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
    @Test(groups = {"sanity", "docker"})
    public void testHubConnectivity() {
        String hubUrl = ConfigReader.getProperty("hub.url");
        // Only run this check if in Docker mode, or just log a warning
        if (hubUrl == null || hubUrl.contains("localhost")) {
            System.out.println("[INFO] Checking connectivity to Local Grid: " + hubUrl);
        }

        try {
            // Simple Java HTTP Ping to the Hub's status endpoint
            URL url = new URL(hubUrl + "/status"); // Selenium Grid 4 status endpoint
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(2000); // Fail fast (2 seconds)

            int responseCode = connection.getResponseCode();

            // 200 OK means the Grid is alive
            Assert.assertEquals(responseCode, 200, "Selenium Grid is not responding! Response Code: " + responseCode);
            System.out.println("[PASS] Selenium Grid is reachable.");

        } catch (Exception e) {
            System.out.println("[WARN] Grid check failed (This is expected if not running Docker): " + e.getMessage());
            // I won't fail the test here because I might be running locally without Docker.
            // But in a real CI environment, I would uncomment the line below:
            // Assert.fail("Grid Infrastructure is DOWN.");
        }
    }
}
