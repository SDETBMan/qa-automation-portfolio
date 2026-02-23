package com.saucedemo.utils;

import com.epam.healenium.SelfHealingDriver;
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
import java.util.HashMap;

/**
 * DriverManager: The central factory responsible for creating, storing, and
 * destroying WebDriver instances across the entire test framework.
 *
 * <p>WHY THIS CLASS EXISTS: Every test needs a browser (or mobile device) to
 * interact with. Rather than letting each test create its own driver — which
 * would be chaotic and hard to maintain — this single class handles driver
 * lifecycle for the whole suite. Tests simply call {@code DriverManager.getDriver()}
 * to get whichever browser they need, without caring how it was set up.
 *
 * <p>THREAD SAFETY (ThreadLocal): When tests run in parallel, each thread must
 * have its own private browser instance. If threads shared a single driver,
 * they would interfere with each other (e.g., Thread A navigates away while
 * Thread B is trying to click something). ThreadLocal solves this by giving
 * every thread its own isolated copy of the driver variable, invisible to
 * other threads.
 *
 * <p>MULTI-TARGET SUPPORT: The framework can run tests against:
 * <ul>
 *   <li>local  — a browser installed on the developer's machine (default)</li>
 *   <li>grid   — a Selenium Grid server for distributed parallel execution</li>
 *   <li>browserstack — BrowserStack cloud for cross-browser/OS testing</li>
 *   <li>android — a real or emulated Android device via Appium</li>
 *   <li>ios    — a real or simulated iOS device via Appium</li>
 * </ul>
 * The active target is selected by passing {@code -Dtarget=<value>} on the
 * Maven command line, or by setting {@code target} in config.properties.
 *
 * <p>HEALENIUM: When the Healenium backend server is running, web drivers are
 * wrapped with SelfHealingDriver, which automatically retries failed element
 * lookups using alternative locator strategies. This reduces test flakiness
 * caused by minor UI changes without requiring manual test updates.
 */
public class DriverManager {

    /**
     * ThreadLocal storage for the WebDriver instance.
     *
     * ThreadLocal is a Java class that maintains a separate value of a variable
     * for each thread. Think of it as a map keyed by thread ID — each thread
     * reads and writes only its own slot. This is what makes parallel test
     * execution safe: Thread 1's Chrome driver never bleeds into Thread 2's
     * Firefox driver.
     */
    private static final ThreadLocal<WebDriver> driver = new ThreadLocal<>();

    /**
     * Returns the WebDriver for the current thread, creating it on first call.
     *
     * <p>WHY LAZY INITIALIZATION: The driver is not created until a test actually
     * needs it. This avoids launching unnecessary browsers for tests that might
     * be skipped, and it keeps the construction logic in one predictable place.
     *
     * @return the active WebDriver instance for this thread
     */
    public static WebDriver getDriver() {
        // If no driver exists yet for this thread, create one now
        if (driver.get() == null) {
            initializeDriver();
        }
        return driver.get();
    }

    /**
     * Reads the target environment from config/system properties and delegates
     * to the appropriate initialization method.
     *
     * <p>The switch statement maps the string value of the "target" property to
     * a specific initialization strategy. Adding a new target (e.g., "sauce")
     * only requires adding a new case here and a new private method — all other
     * code remains unchanged (Open/Closed Principle).
     */
    private static void initializeDriver() {
        // Read the target from config.properties first, then fall back to the
        // -Dtarget JVM system property, then default to "local"
        String target = ConfigReader.getProperty("target",
                System.getProperty("target", "local")).toLowerCase();

        System.out.println("=========================================");
        System.out.println("[INFO] DriverManager Initialized");
        System.out.println("[INFO] Target: " + target);
        System.out.println("=========================================");

        // Route to the correct browser/device setup based on the target value
        switch (target) {
            case "browserstack": initBrowserStack(); break;
            case "grid":         initGrid();         break;
            case "android":      initAndroid();      break;
            case "ios":          initIOS();          break;
            default:             initLocalDriver();  break; // "local" is the safe fallback
        }
    }

    // ----------------------------------------------------------------
    // LOCAL (Chrome / Firefox / Edge) with optional Healenium wrapping
    // ----------------------------------------------------------------

    /**
     * Starts a browser on the local machine where the tests are running.
     *
     * <p>This is the most common mode for developer workstations. The browser
     * binary must be installed; WebDriverManager (or Selenium Manager, built
     * into Selenium 4) automatically downloads a matching driver executable.
     *
     * <p>The raw driver is passed through {@link #wrapWithHealenium(WebDriver)}
     * so that self-healing is active whenever the Healenium backend is available.
     */
    private static void initLocalDriver() {
        String browser = ConfigReader.getProperty("browser", "chrome").toLowerCase();
        boolean headless = isHeadless();

        WebDriver rawDriver;
        // Select browser implementation; Chrome is the industry default fallback
        switch (browser) {
            case "firefox": rawDriver = new FirefoxDriver(buildFirefoxOptions(headless)); break;
            case "edge":    rawDriver = new EdgeDriver(buildEdgeOptions(headless));       break;
            default:        rawDriver = new ChromeDriver(buildChromeOptions(headless));   break;
        }

        System.out.println("[INFO] Started local " + browser + " (headless=" + headless + ")");
        // Store the (possibly healenium-wrapped) driver in this thread's slot
        driver.set(wrapWithHealenium(rawDriver));
    }

    // ----------------------------------------------------------------
    // SELENIUM GRID
    // ----------------------------------------------------------------

    /**
     * Connects to a Selenium Grid hub and runs tests on a remote node.
     *
     * <p>WHY SELENIUM GRID: A Grid allows many machines (nodes) to run browsers
     * simultaneously, dramatically speeding up large test suites. The hub
     * receives test commands and routes them to an appropriate node. This is
     * essential for CI pipelines that need to finish quickly or for cross-browser
     * testing across multiple OS/browser combinations.
     *
     * <p>The URL format is {@code http://<host>:4444/wd/hub} for Selenium 3/4.
     */
    private static void initGrid() {
        String gridUrl = ConfigReader.getProperty("grid_url", "http://localhost:4444/wd/hub");
        String browser = ConfigReader.getProperty("browser", "chrome").toLowerCase();
        boolean headless = isHeadless();

        try {
            WebDriver rawDriver;
            // RemoteWebDriver sends commands over HTTP to the Grid instead of
            // controlling a local browser process directly
            switch (browser) {
                case "firefox": rawDriver = new RemoteWebDriver(new URL(gridUrl), buildFirefoxOptions(headless)); break;
                case "edge":    rawDriver = new RemoteWebDriver(new URL(gridUrl), buildEdgeOptions(headless));    break;
                default:        rawDriver = new RemoteWebDriver(new URL(gridUrl), buildChromeOptions(headless));  break;
            }
            System.out.println("[INFO] Started Grid driver -> " + gridUrl + " (" + browser + ")");
            driver.set(wrapWithHealenium(rawDriver));
        } catch (MalformedURLException e) {
            // A bad URL string is a configuration error, not a recoverable runtime issue
            throw new RuntimeException("Invalid Grid URL: " + gridUrl, e);
        }
    }

    // ----------------------------------------------------------------
    // BROWSERSTACK
    // ----------------------------------------------------------------

    /**
     * Connects to BrowserStack's cloud platform to run tests on real devices
     * and browsers hosted in BrowserStack's data centres.
     *
     * <p>WHY BROWSERSTACK: Maintaining a local farm of physical devices and every
     * browser version is expensive. BrowserStack provides on-demand access to
     * thousands of real device/OS/browser combinations, making cross-platform
     * coverage practical without infrastructure overhead.
     *
     * <p>Authentication uses a username + access key pair that is stored as CI
     * secrets (never hard-coded). The {@code bstack:options} capability map
     * passes BrowserStack-specific settings such as OS version and session name.
     */
    private static void initBrowserStack() {
        // Credentials are read from config or CI environment secrets, NOT source code
        String username  = ConfigReader.getProperty("bs_user");
        String accessKey = ConfigReader.getProperty("bs_key");

        // Fail fast with a clear message rather than a cryptic NullPointerException later
        if (username == null || username.isEmpty() || accessKey == null || accessKey.isEmpty()) {
            throw new RuntimeException(
                    "BrowserStack credentials not found. Set BS_USER / BS_KEY secrets or -Dbs_user=... -Dbs_key=...");
        }

        ChromeOptions options = new ChromeOptions();
        // BrowserStack reads its configuration from this special capability map
        HashMap<String, Object> bstackOptions = new HashMap<>();
        bstackOptions.put("os", "Windows");
        bstackOptions.put("osVersion", "11");
        bstackOptions.put("sessionName", "CucumberFramework Build");
        options.setCapability("bstack:options", bstackOptions);

        try {
            // Credentials are embedded in the URL — this is BrowserStack's required format
            String url = "https://" + username + ":" + accessKey + "@hub-cloud.browserstack.com/wd/hub";
            driver.set(new RemoteWebDriver(new URL(url), options));
            System.out.println("[INFO] Started BrowserStack remote driver");
        } catch (MalformedURLException e) {
            throw new RuntimeException("Invalid BrowserStack URL", e);
        }
    }

    // ----------------------------------------------------------------
    // ANDROID (Appium)
    // ----------------------------------------------------------------

    /**
     * Starts an Appium session targeting a real Android device or emulator.
     *
     * <p>WHY APPIUM: Appium is the industry-standard tool for automating mobile
     * apps. It exposes the same WebDriver API used for browsers, so much of the
     * framework code (waits, assertions, etc.) can be reused for mobile testing.
     * UiAutomator2 is Google's recommended automation engine for Android.
     *
     * <p>The Appium server must already be running at {@code appium_url} before
     * this method is called. The APK file must exist at {@code android_app_path}.
     */
    private static void initAndroid() {
        String appiumUrl    = ConfigReader.getProperty("appium_url", "http://127.0.0.1:4723");
        String deviceName   = ConfigReader.getProperty("android_device_name", "Google Pixel 8");
        // Path to the compiled Android application package (.apk) to install and test
        String appPath      = ConfigReader.getProperty("android_app_path",
                "src/test/resources/apps/Android.SauceLabs.Mobile.Sample.app.2.7.1.apk");

        // UiAutomator2Options is the strongly-typed capability builder for Android/Appium
        UiAutomator2Options options = new UiAutomator2Options();
        options.setDeviceName(deviceName);
        options.setApp(appPath);

        try {
            driver.set(new AndroidDriver(new URL(appiumUrl), options));
            System.out.println("[INFO] Started Android driver -> " + deviceName);
        } catch (MalformedURLException e) {
            throw new RuntimeException("Invalid Appium URL: " + appiumUrl, e);
        }
    }

    // ----------------------------------------------------------------
    // iOS (Appium)
    // ----------------------------------------------------------------

    /**
     * Starts an Appium session targeting a real iOS device or Simulator.
     *
     * <p>XCUITest is Apple's native UI testing framework; Appium uses it as its
     * automation engine on iOS. Unlike Android, iOS requires specifying the
     * platform version to match the correct Simulator image or device OS.
     *
     * <p>NOTE: Building and running iOS tests requires a Mac with Xcode installed.
     * The Appium server must be started separately before invoking this method.
     */
    private static void initIOS() {
        String appiumUrl  = ConfigReader.getProperty("appium_url", "http://127.0.0.1:4723");
        String deviceName = ConfigReader.getProperty("ios_device_name", "iPhone 15");
        String iosVersion = ConfigReader.getProperty("ios_version", "17.0");
        // Path to the compiled iOS application bundle (.app) to install on the Simulator
        String appPath    = ConfigReader.getProperty("ios_app_path",
                "src/test/resources/apps/iOS.Simulator.SauceLabs.Mobile.Sample.app.2.7.1.app");

        // XCUITestOptions is the strongly-typed capability builder for iOS/Appium
        XCUITestOptions options = new XCUITestOptions();
        options.setDeviceName(deviceName);
        options.setPlatformVersion(iosVersion);
        options.setApp(appPath);

        try {
            driver.set(new IOSDriver(new URL(appiumUrl), options));
            System.out.println("[INFO] Started iOS driver -> " + deviceName);
        } catch (MalformedURLException e) {
            throw new RuntimeException("Invalid Appium URL: " + appiumUrl, e);
        }
    }

    // ----------------------------------------------------------------
    // HEALENIUM WRAPPER  (gracefully degrades if backend is offline)
    // ----------------------------------------------------------------

    /**
     * Attempts to wrap the given driver with Healenium's self-healing capability.
     *
     * <p>WHAT HEALENIUM DOES: When a test fails to find an element because its
     * locator has become stale (e.g., a CSS class was renamed after a UI update),
     * Healenium uses a machine-learning model to find the same element using
     * alternative attributes. It then updates the stored locator so future runs
     * do not fail again. This reduces test maintenance burden significantly.
     *
     * <p>GRACEFUL DEGRADATION: Healenium requires a separate backend service
     * (a Docker container). If that service is not running — which is fine on
     * a developer laptop — this method silently falls back to the plain driver
     * rather than crashing the entire test suite.
     *
     * @param rawDriver the plain WebDriver instance to potentially wrap
     * @return a SelfHealingDriver if Healenium is available, otherwise the original driver
     */
    private static WebDriver wrapWithHealenium(WebDriver rawDriver) {
        try {
            WebDriver healed = SelfHealingDriver.create(rawDriver);
            System.out.println("[INFO] Healenium self-healing active");
            return healed;
        } catch (Exception e) {
            // Healenium backend not reachable is expected in local dev — just warn and continue
            System.out.println("[WARN] Healenium backend not reachable — using standard driver. " + e.getMessage());
            return rawDriver;
        }
    }

    // ----------------------------------------------------------------
    // BROWSER OPTIONS BUILDERS
    // ----------------------------------------------------------------

    /**
     * Builds Chrome-specific startup options.
     *
     * <p>{@code --remote-allow-origins=*} is required in newer Chrome versions
     * to allow WebDriver to connect without CORS errors. The headless arguments
     * make Chrome run without a visible UI, which is required in CI environments
     * that have no display server (e.g., Linux GitHub Actions runners).
     *
     * @param headless true to run without a visible browser window
     * @return configured ChromeOptions ready to pass to ChromeDriver or RemoteWebDriver
     */
    private static ChromeOptions buildChromeOptions(boolean headless) {
        ChromeOptions opts = new ChromeOptions();
        opts.addArguments("--remote-allow-origins=*");
        if (headless) {
            // "--headless=new" uses Chrome's modern headless mode (more stable than the old flag)
            // "--no-sandbox" is needed in Docker/CI environments where Chrome cannot create a sandbox
            // "--disable-dev-shm-usage" prevents crashes in Docker due to limited shared memory
            // "--window-size" sets a consistent viewport so responsive layouts behave predictably
            opts.addArguments("--headless=new", "--no-sandbox",
                    "--disable-dev-shm-usage", "--window-size=1920,1080");
        }
        return opts;
    }

    /**
     * Builds Firefox-specific startup options.
     *
     * @param headless true to run without a visible browser window
     * @return configured FirefoxOptions ready to pass to FirefoxDriver or RemoteWebDriver
     */
    private static FirefoxOptions buildFirefoxOptions(boolean headless) {
        FirefoxOptions opts = new FirefoxOptions();
        // Firefox uses "-headless" (single dash) rather than Chrome's "--headless" style
        if (headless) opts.addArguments("-headless", "--width=1920", "--height=1080");
        return opts;
    }

    /**
     * Builds Edge-specific startup options.
     *
     * <p>Edge is Chromium-based, so its options are nearly identical to Chrome's,
     * but using a dedicated EdgeOptions class keeps the driver configuration
     * unambiguous and properly typed.
     *
     * @param headless true to run without a visible browser window
     * @return configured EdgeOptions ready to pass to EdgeDriver or RemoteWebDriver
     */
    private static EdgeOptions buildEdgeOptions(boolean headless) {
        EdgeOptions opts = new EdgeOptions();
        if (headless) opts.addArguments("--headless");
        return opts;
    }

    /**
     * Determines whether the browser should run in headless (no visible window) mode.
     *
     * <p>Headless mode is enabled if ANY of the following are true:
     * <ol>
     *   <li>The {@code headless} key in config.properties is set to {@code true}</li>
     *   <li>The JVM system property {@code -Dheadless=true} was passed at runtime</li>
     *   <li>The {@code CI} environment variable is set (standard on GitHub Actions,
     *       Jenkins, GitLab CI, and most other CI platforms)</li>
     * </ol>
     * This design means CI environments automatically get headless mode without
     * any special configuration change.
     *
     * @return true if headless mode should be used
     */
    private static boolean isHeadless() {
        return Boolean.parseBoolean(ConfigReader.getProperty("headless", "false"))
                || Boolean.parseBoolean(System.getProperty("headless", "false"))
                || System.getenv("CI") != null; // CI env var is set automatically by most CI platforms
    }

    // ----------------------------------------------------------------
    // TEARDOWN
    // ----------------------------------------------------------------

    /**
     * Closes the browser and removes the driver from ThreadLocal storage.
     *
     * <p>WHY BOTH quit() AND remove(): {@code driver.quit()} closes the browser
     * window and kills the browser process. {@code driver.remove()} clears the
     * ThreadLocal variable so the slot is freed — without this, the ThreadLocal
     * would hold a reference to the dead driver object, which can cause memory
     * leaks in long-running thread pools (like those used by parallel test runners).
     *
     * <p>This method is called from {@code Hooks.java} after every Cucumber scenario,
     * ensuring every test gets a clean browser and no state bleeds between tests.
     */
    public static void quitDriver() {
        if (driver.get() != null) {
            driver.get().quit();    // Close the browser process
            driver.remove();        // Free the ThreadLocal memory slot
        }
    }
}
