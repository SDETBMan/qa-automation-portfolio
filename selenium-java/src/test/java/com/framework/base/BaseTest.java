package com.framework.base;

import com.framework.driver.DriverFactory;
import com.framework.driver.DriverManager;
import com.framework.utils.ConfigReader;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.testng.ITestContext;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Optional;
import org.testng.annotations.Parameters;

import java.net.MalformedURLException;
import java.time.Duration;

public class BaseTest {

    @BeforeMethod(alwaysRun = true)
    @Parameters({"browser", "headless"})
    public void setUp(@Optional("chrome") String browser,
                      @Optional("false") String headless,
                      ITestContext context) throws MalformedURLException {

        long threadId = Thread.currentThread().getId();
        String testName = context.getCurrentXmlTest().getName();
        System.out.println("--------------------------------------------------");
        System.out.println("[SETUP] Thread " + threadId + " | Test: " + testName);

        // ======================================================
        // 1. CONFIG RESOLUTION (Priority: System Prop > XML > Config)
        // ======================================================
        // If Maven passed -Dbrowser=firefox, use that otherwise use XML value.
        String targetBrowser = System.getProperty("browser", browser);
        String targetHeadless = System.getProperty("headless", headless);

        System.out.println("[SETUP] Target: " + targetBrowser + " | Headless: " + targetHeadless);

        // ======================================================
        // 2. CREATE DRIVER
        // ======================================================
        WebDriver driver = DriverFactory.createInstance(targetBrowser, targetHeadless);

        if (driver == null) {
            throw new RuntimeException("[FATAL] DriverFactory returned NULL. Check your Config/Grid status.");
        }

        // 3. SET TO MANAGER (ThreadLocal)
        DriverManager.setDriver(driver);

        // 4. CONFIGURE WINDOW & WAITS
        configureDriver(driver, targetBrowser, targetHeadless);
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        WebDriver driver = DriverManager.getDriver();

        if (driver != null) {
            try {
                driver.manage().deleteAllCookies();
                JavascriptExecutor js = (JavascriptExecutor) driver;
                js.executeScript("window.localStorage.clear();");
                js.executeScript("window.sessionStorage.clear();");

                // CRITICAL: Small delay to let the browser commit the clear commands
                Thread.sleep(100);

                System.out.println("[TEARDOWN] Browser state cleared for Thread " + Thread.currentThread().getId());
            } catch (Exception e) {
                // Silently fail if session is already closed
            } finally {
                driver.quit();
                DriverManager.unload();
            }
        }
    }

    /**
     * Helper method to configure timeouts, window size, and navigation.
     */
    private void configureDriver(WebDriver driver, String browser, String headless) {
        int implicitTimeout = Integer.parseInt(ConfigReader.getProperty("timeout.implicit", "10"));
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(implicitTimeout));

        boolean isMobile = browser.equalsIgnoreCase("android") || browser.equalsIgnoreCase("ios");

        if (!isMobile) {
            // WEB CONFIGURATION
            if (Boolean.parseBoolean(headless)) {
                // Headless needs explicit size to "see" elements
                driver.manage().window().setSize(new org.openqa.selenium.Dimension(1920, 1080));
            } else {
                driver.manage().window().maximize();
            }

            // Navigate to URL from Config
            String url = ConfigReader.getProperty("url");
            if (url != null) {
                // System.out.println("[NAV] Navigating to: " + url);
                driver.get(url);
            }
        }
    }
}

