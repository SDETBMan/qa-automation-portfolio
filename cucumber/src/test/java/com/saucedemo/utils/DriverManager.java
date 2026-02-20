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
 * DriverManager: Thread-safe WebDriver factory.
 * Supports local (Chrome/Firefox/Edge), Selenium Grid, BrowserStack, Android, and iOS.
 * Wraps Web drivers with Healenium for self-healing locators when available.
 *
 * Target is controlled via -Dtarget=local|grid|browserstack|android|ios
 */
public class DriverManager {

    private static final ThreadLocal<WebDriver> driver = new ThreadLocal<>();

    public static WebDriver getDriver() {
        if (driver.get() == null) {
            initializeDriver();
        }
        return driver.get();
    }

    private static void initializeDriver() {
        String target = ConfigReader.getProperty("target",
                System.getProperty("target", "local")).toLowerCase();

        System.out.println("=========================================");
        System.out.println("[INFO] DriverManager Initialized");
        System.out.println("[INFO] Target: " + target);
        System.out.println("=========================================");

        switch (target) {
            case "browserstack": initBrowserStack(); break;
            case "grid":         initGrid();         break;
            case "android":      initAndroid();      break;
            case "ios":          initIOS();          break;
            default:             initLocalDriver();  break;
        }
    }

    // ----------------------------------------------------------------
    // LOCAL (Chrome / Firefox / Edge) with optional Healenium wrapping
    // ----------------------------------------------------------------
    private static void initLocalDriver() {
        String browser = ConfigReader.getProperty("browser", "chrome").toLowerCase();
        boolean headless = isHeadless();

        WebDriver rawDriver;
        switch (browser) {
            case "firefox": rawDriver = new FirefoxDriver(buildFirefoxOptions(headless)); break;
            case "edge":    rawDriver = new EdgeDriver(buildEdgeOptions(headless));       break;
            default:        rawDriver = new ChromeDriver(buildChromeOptions(headless));   break;
        }

        System.out.println("[INFO] Started local " + browser + " (headless=" + headless + ")");
        driver.set(wrapWithHealenium(rawDriver));
    }

    // ----------------------------------------------------------------
    // SELENIUM GRID
    // ----------------------------------------------------------------
    private static void initGrid() {
        String gridUrl = ConfigReader.getProperty("grid_url", "http://localhost:4444/wd/hub");
        String browser = ConfigReader.getProperty("browser", "chrome").toLowerCase();
        boolean headless = isHeadless();

        try {
            WebDriver rawDriver;
            switch (browser) {
                case "firefox": rawDriver = new RemoteWebDriver(new URL(gridUrl), buildFirefoxOptions(headless)); break;
                case "edge":    rawDriver = new RemoteWebDriver(new URL(gridUrl), buildEdgeOptions(headless));    break;
                default:        rawDriver = new RemoteWebDriver(new URL(gridUrl), buildChromeOptions(headless));  break;
            }
            System.out.println("[INFO] Started Grid driver -> " + gridUrl + " (" + browser + ")");
            driver.set(wrapWithHealenium(rawDriver));
        } catch (MalformedURLException e) {
            throw new RuntimeException("Invalid Grid URL: " + gridUrl, e);
        }
    }

    // ----------------------------------------------------------------
    // BROWSERSTACK
    // ----------------------------------------------------------------
    private static void initBrowserStack() {
        String username  = ConfigReader.getProperty("bs_user");
        String accessKey = ConfigReader.getProperty("bs_key");

        if (username == null || username.isEmpty() || accessKey == null || accessKey.isEmpty()) {
            throw new RuntimeException(
                    "BrowserStack credentials not found. Set BS_USER / BS_KEY secrets or -Dbs_user=... -Dbs_key=...");
        }

        ChromeOptions options = new ChromeOptions();
        HashMap<String, Object> bstackOptions = new HashMap<>();
        bstackOptions.put("os", "Windows");
        bstackOptions.put("osVersion", "11");
        bstackOptions.put("sessionName", "CucumberFramework Build");
        options.setCapability("bstack:options", bstackOptions);

        try {
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
    private static void initAndroid() {
        String appiumUrl    = ConfigReader.getProperty("appium_url", "http://127.0.0.1:4723");
        String deviceName   = ConfigReader.getProperty("android_device_name", "Google Pixel 8");
        String appPath      = ConfigReader.getProperty("android_app_path",
                "src/test/resources/apps/Android.SauceLabs.Mobile.Sample.app.2.7.1.apk");

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
    private static void initIOS() {
        String appiumUrl  = ConfigReader.getProperty("appium_url", "http://127.0.0.1:4723");
        String deviceName = ConfigReader.getProperty("ios_device_name", "iPhone 15");
        String iosVersion = ConfigReader.getProperty("ios_version", "17.0");
        String appPath    = ConfigReader.getProperty("ios_app_path",
                "src/test/resources/apps/iOS.Simulator.SauceLabs.Mobile.Sample.app.2.7.1.app");

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
    private static WebDriver wrapWithHealenium(WebDriver rawDriver) {
        try {
            WebDriver healed = SelfHealingDriver.create(rawDriver);
            System.out.println("[INFO] Healenium self-healing active");
            return healed;
        } catch (Exception e) {
            System.out.println("[WARN] Healenium backend not reachable — using standard driver. " + e.getMessage());
            return rawDriver;
        }
    }

    // ----------------------------------------------------------------
    // BROWSER OPTIONS BUILDERS
    // ----------------------------------------------------------------
    private static ChromeOptions buildChromeOptions(boolean headless) {
        ChromeOptions opts = new ChromeOptions();
        opts.addArguments("--remote-allow-origins=*");
        if (headless) {
            opts.addArguments("--headless=new", "--no-sandbox",
                    "--disable-dev-shm-usage", "--window-size=1920,1080");
        }
        return opts;
    }

    private static FirefoxOptions buildFirefoxOptions(boolean headless) {
        FirefoxOptions opts = new FirefoxOptions();
        if (headless) opts.addArguments("-headless", "--width=1920", "--height=1080");
        return opts;
    }

    private static EdgeOptions buildEdgeOptions(boolean headless) {
        EdgeOptions opts = new EdgeOptions();
        if (headless) opts.addArguments("--headless");
        return opts;
    }

    private static boolean isHeadless() {
        return Boolean.parseBoolean(ConfigReader.getProperty("headless", "false"))
                || Boolean.parseBoolean(System.getProperty("headless", "false"))
                || System.getenv("CI") != null;
    }

    // ----------------------------------------------------------------
    // TEARDOWN
    // ----------------------------------------------------------------
    public static void quitDriver() {
        if (driver.get() != null) {
            driver.get().quit();
            driver.remove();
        }
    }
}
