package com.framework.driver;

import com.epam.healenium.SelfHealingDriver;
import com.framework.utils.ConfigReader;
import io.appium.java_client.android.AndroidDriver;
import io.appium.java_client.android.options.UiAutomator2Options;
import io.appium.java_client.ios.IOSDriver;
import io.appium.java_client.ios.options.XCUITestOptions;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.edge.EdgeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;
import org.openqa.selenium.remote.RemoteWebDriver;

import java.net.MalformedURLException;
import java.net.URL;

/**
 * DriverFactory: Universal logic for Web, Android, and iOS.
 * Includes Self-Healing (Healenium) and Cloud (Sauce Labs) support.
 */
public class DriverFactory {

    public static WebDriver createInstance(String browser, String headless) throws MalformedURLException {
        WebDriver delegate = null;
        // Check system property first (from Maven -P), then fall back to config file
        String mode = System.getProperty("execution.env", ConfigReader.getProperty("execution_mode"));
        if (mode == null) mode = "local";

        System.out.println("=========================================");
        System.out.println("[INFO] DriverFactory Initialized");
        System.out.println("[INFO] Mode: " + mode);
        System.out.println("[INFO] Browser: " + browser);
        System.out.println("=========================================");

        boolean isHeadless = Boolean.parseBoolean(headless);

        // --- 1. WEB OPTIONS ---
        ChromeOptions chromeOptions = new ChromeOptions();
        chromeOptions.addArguments("--remote-allow-origins=*");
        if (isHeadless) {
            chromeOptions.addArguments("--headless=new", "--window-size=1920,1080");
        }

        FirefoxOptions firefoxOptions = new FirefoxOptions();
        if (isHeadless) {
            firefoxOptions.addArguments("-headless", "--width=1920", "--height=1080");
        }

        EdgeOptions edgeOptions = new EdgeOptions();
        if (isHeadless) edgeOptions.addArguments("--headless");

        // --- 2. MOBILE OPTIONS ---
        UiAutomator2Options androidOptions = new UiAutomator2Options();
        XCUITestOptions iosOptions = new XCUITestOptions();
        // ... (Your existing Android/iOS options logic here)

        // --- 3. EXECUTION LOGIC ---
        if ("cloud".equalsIgnoreCase(mode)) {
            // ... (Your existing Cloud/Sauce Labs switch case here)

        } else if ("grid".equalsIgnoreCase(mode)) {
            // --- SELENIUM GRID CONFIGURATION ---
            String gridUrl = System.getProperty("grid.url", "http://localhost:4444/wd/hub");
            URL remoteUrl = new URL(gridUrl);

            switch (browser.toLowerCase()) {
                case "chrome": delegate = new RemoteWebDriver(remoteUrl, chromeOptions); break;
                case "firefox": delegate = new RemoteWebDriver(remoteUrl, firefoxOptions); break;
                case "edge": delegate = new RemoteWebDriver(remoteUrl, edgeOptions); break;
            }

        } else {
            // --- LOCAL EXECUTION (Default) ---
            // Appium URL is read from config so it works across local, CI, and remote Appium servers.
            String appiumUrl = ConfigReader.getProperty("appium_url");

            if ("android".equalsIgnoreCase(browser)) {
                delegate = new AndroidDriver(new URL(appiumUrl), androidOptions);
            } else if ("ios".equalsIgnoreCase(browser)) {
                delegate = new IOSDriver(new URL(appiumUrl), iosOptions);
            } else {
                switch (browser.toLowerCase()) {
                    case "chrome": delegate = new ChromeDriver(chromeOptions); break;
                    case "firefox": delegate = new FirefoxDriver(firefoxOptions); break;
                    case "edge": delegate = new EdgeDriver(edgeOptions); break;
                }
            }
        }

        // --- 4. HEALENIUM WRAPPING ---
        // Only wrap Web Drivers. Mobile drivers (AndroidDriver/IOSDriver) should remain raw.
        boolean isMobile = "android".equalsIgnoreCase(browser) || "ios".equalsIgnoreCase(browser);

        if (delegate != null && !isMobile) {
            try {
                System.out.println("[INFO] Wrapping driver with Healenium Self-Healing");
                return SelfHealingDriver.create(delegate);
            } catch (Exception e) {
                System.out.println("[WARN] Healenium backend not found. Using standard driver. Error: " + e.getMessage());
                return delegate;
            }
        }

        // Return the raw driver if it's mobile or if it's null
        return delegate;
    } // End of createInstance
} // End of Class
