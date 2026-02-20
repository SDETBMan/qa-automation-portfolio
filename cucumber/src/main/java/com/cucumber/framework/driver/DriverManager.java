package com.cucumber.framework.driver;

import com.cucumber.framework.utils.ConfigReader;
import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;

import java.time.Duration;

/**
 * Thread-safe WebDriver lifecycle manager using ThreadLocal.
 *
 * Each test scenario gets its own driver instance, ensuring full isolation
 * during parallel execution — the same pattern used in selenium-java's
 * DriverManager but without the mobile/Healenium complexity.
 *
 * Lifecycle:
 *   Hooks.setUp()     → DriverManager.init()
 *   [test runs]
 *   Hooks.tearDown()  → DriverManager.quit()
 */
public class DriverManager {

    private static final ThreadLocal<WebDriver> driver = new ThreadLocal<>();

    private DriverManager() {}

    public static WebDriver getDriver() {
        return driver.get();
    }

    public static void init() {
        String browser  = ConfigReader.get("browser", "chrome");
        boolean headless = Boolean.parseBoolean(ConfigReader.get("headless", "false"));

        WebDriver webDriver;

        if ("firefox".equalsIgnoreCase(browser)) {
            WebDriverManager.firefoxdriver().setup();
            FirefoxOptions options = new FirefoxOptions();
            if (headless) options.addArguments("--headless");
            webDriver = new FirefoxDriver(options);
        } else {
            WebDriverManager.chromedriver().setup();
            ChromeOptions options = new ChromeOptions();
            if (headless) options.addArguments("--headless=new");
            webDriver = new ChromeDriver(options);
        }

        webDriver.manage().window().maximize();
        webDriver.manage().timeouts().implicitlyWait(
                Duration.ofSeconds(Long.parseLong(ConfigReader.get("timeout.implicit", "10"))));

        driver.set(webDriver);
    }

    public static void quit() {
        if (driver.get() != null) {
            driver.get().quit();
            driver.remove();
        }
    }
}
