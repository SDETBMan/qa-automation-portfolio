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
 * DriverFactory: The single entry point for creating any WebDriver instance in the framework.
 *
 * WHY THIS CLASS EXISTS:
 * Without a factory, every test would have to know exactly how to build its own driver —
 * what options to set for Chrome, how to connect to a Grid, how to talk to Appium for
 * mobile, etc. That creates massive duplication and makes changes painful. This factory
 * centralizes all of that complexity so tests can simply say "give me a driver" and this
 * class figures out all the details.
 *
 * WHAT IT SUPPORTS (in one method):
 *   - Web browsers: Chrome, Firefox, Edge (local and headless)
 *   - Mobile: Android (via Appium + UiAutomator2) and iOS (via Appium + XCUITest)
 *   - Execution modes:
 *       "local"  — runs directly on the developer's machine
 *       "grid"   — runs on a Selenium Grid (e.g., Docker containers in CI/CD)
 *       "cloud"  — runs on a cloud service like Sauce Labs
 *   - Self-Healing (Healenium): Automatically repairs broken locators without manual fixes
 *
 * DESIGN PATTERN — Factory Method:
 * The factory pattern is used when you need to create objects but the exact type depends
 * on runtime conditions (like which browser was requested). The caller asks for a WebDriver;
 * the factory decides whether to build a ChromeDriver, FirefoxDriver, AndroidDriver, etc.
 *
 * For recruiters: Supporting web AND mobile from a single factory, plus cloud and Grid
 * execution modes, demonstrates enterprise-level framework design.
 */
public class DriverFactory {

    /**
     * Creates and returns the appropriate WebDriver based on the requested browser and execution mode.
     *
     * WHY THE PARAMETERS:
     * - "browser" is passed in (rather than hardcoded) so tests can be run against different
     *   browsers from the command line: mvn test -Dbrowser=firefox
     * - "headless" controls whether a visible browser window opens. Headless mode (no window)
     *   is required in CI/CD pipelines where there is no display screen available.
     *
     * @param browser  The browser or platform to launch: "chrome", "firefox", "edge", "android", "ios"
     * @param headless "true" to run without a visible browser window; "false" for a normal window
     * @return A WebDriver instance ready to control the browser or mobile device
     * @throws MalformedURLException if the Grid or Appium URL in config is not a valid URL format
     */
    public static WebDriver createInstance(String browser, String headless) throws MalformedURLException {
        WebDriver delegate = null;
        // Check system property first (from Maven -P), then fall back to config file.
        // This priority order lets CI override the config file without editing files.
        String mode = System.getProperty("execution.env", ConfigReader.getProperty("execution_mode"));
        if (mode == null) mode = "local";

        // Diagnostic banner so test logs clearly show what environment was chosen.
        System.out.println("=========================================");
        System.out.println("[INFO] DriverFactory Initialized");
        System.out.println("[INFO] Mode: " + mode);
        System.out.println("[INFO] Browser: " + browser);
        System.out.println("=========================================");

        // Parse headless string to boolean once so we don't repeat the conversion below.
        boolean isHeadless = Boolean.parseBoolean(headless);

        // ==================================================================
        // 1. WEB BROWSER OPTIONS
        // Options are pre-built for all browsers up front, even if only one
        // will be used. This keeps the conditional logic below clean and avoids
        // duplicating option-building code inside each execution-mode block.
        // ==================================================================

        // Chrome options — "--remote-allow-origins=*" is required in Chrome 111+
        // to prevent WebSocket connection errors when Selenium communicates with the browser.
        ChromeOptions chromeOptions = new ChromeOptions();
        chromeOptions.addArguments("--remote-allow-origins=*");
        if (isHeadless) {
            // "--headless=new" uses Chrome's modern headless mode (faster and more stable
            // than the legacy "--headless" flag). The other args prevent crashes in Docker
            // containers where shared memory (/dev/shm) is limited.
            chromeOptions.addArguments("--headless=new", "--no-sandbox",
                    "--disable-dev-shm-usage", "--window-size=1920,1080");
        }

        FirefoxOptions firefoxOptions = new FirefoxOptions();
        if (isHeadless) {
            firefoxOptions.addArguments("-headless", "--width=1920", "--height=1080");
        }

        EdgeOptions edgeOptions = new EdgeOptions();
        if (isHeadless) edgeOptions.addArguments("--headless");

        // ==================================================================
        // 2. MOBILE OPTIONS (Appium)
        // UiAutomator2 is the standard Android automation engine.
        // XCUITest is Apple's standard iOS automation engine.
        // Device-specific capabilities (device name, OS version, app path) are
        // typically configured here from ConfigReader properties.
        // ==================================================================
        UiAutomator2Options androidOptions = new UiAutomator2Options();
        XCUITestOptions iosOptions = new XCUITestOptions();
        // ... (Your existing Android/iOS options logic here)

        // ==================================================================
        // 3. EXECUTION LOGIC — decide WHERE to run based on "mode"
        // ==================================================================
        if ("cloud".equalsIgnoreCase(mode)) {
            // ... (Your existing Cloud/Sauce Labs switch case here)

        } else if ("grid".equalsIgnoreCase(mode)) {
            // --- SELENIUM GRID CONFIGURATION ---
            // Selenium Grid allows tests to run on a farm of machines. The Hub (central
            // coordinator) receives test requests and routes them to available Nodes
            // (machines with browsers installed). This enables large-scale parallel execution.
            // The grid URL can be overridden via -Dgrid.url=http://my-grid:4444/wd/hub
            String gridUrl = System.getProperty("grid.url", "http://localhost:4444/wd/hub");
            URL remoteUrl = new URL(gridUrl);

            // RemoteWebDriver sends commands over HTTP to the Grid rather than controlling
            // a local browser directly. The capabilities (chromeOptions, etc.) tell the
            // Grid which browser/version is needed on the remote node.
            switch (browser.toLowerCase()) {
                case "chrome": delegate = new RemoteWebDriver(remoteUrl, chromeOptions); break;
                case "firefox": delegate = new RemoteWebDriver(remoteUrl, firefoxOptions); break;
                case "edge": delegate = new RemoteWebDriver(remoteUrl, edgeOptions); break;
            }

        } else {
            // --- LOCAL EXECUTION (Default) ---
            // Selenium Manager (built into Selenium 4.6+) automatically downloads and
            // manages browser driver binaries, so no manual driver setup is needed.

            // Appium URL is read from config so it works across local, CI, and remote Appium servers.
            String appiumUrl = ConfigReader.getProperty("appium_url");

            if ("android".equalsIgnoreCase(browser)) {
                // AndroidDriver extends RemoteWebDriver but speaks the Appium mobile protocol.
                // It connects to a running Appium server, which in turn controls the device.
                delegate = new AndroidDriver(new URL(appiumUrl), androidOptions);
            } else if ("ios".equalsIgnoreCase(browser)) {
                // IOSDriver works the same way as AndroidDriver but for iOS simulators/devices.
                delegate = new IOSDriver(new URL(appiumUrl), iosOptions);
            } else {
                // Standard local browser launch — Selenium Manager handles driver binaries automatically.
                switch (browser.toLowerCase()) {
                    case "chrome": delegate = new ChromeDriver(chromeOptions); break;
                    case "firefox": delegate = new FirefoxDriver(firefoxOptions); break;
                    case "edge": delegate = new EdgeDriver(edgeOptions); break;
                }
            }
        }

        // ==================================================================
        // 4. HEALENIUM SELF-HEALING WRAPPER
        //
        // What is Healenium?
        // Healenium is an open-source library that wraps a WebDriver and adds
        // AI-powered self-healing to locator resolution. When a test fails because
        // a locator (like a CSS selector) no longer matches an element — perhaps
        // because a developer renamed a CSS class — Healenium compares the saved
        // page structure against the current one and tries to find the element
        // using a "closest match" algorithm. If successful, it reports the fix
        // so you can update your locator later, but the test passes NOW.
        //
        // WHY WE ONLY WRAP WEB DRIVERS:
        // Mobile drivers (AndroidDriver, IOSDriver) already have their own
        // healing mechanisms within Appium, and wrapping them with Healenium
        // can cause conflicts. So we only apply the wrapper to web drivers.
        //
        // WHY WE USE A TRY/CATCH:
        // Healenium requires a separate backend service to be running (a PostgreSQL
        // database + Healenium service container). In local development environments
        // where this service is not running, we gracefully fall back to the standard
        // driver rather than crashing the entire test run.
        // ==================================================================
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
