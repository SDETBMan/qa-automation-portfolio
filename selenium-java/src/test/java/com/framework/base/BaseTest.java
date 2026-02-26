package com.framework.base;

import com.framework.driver.DriverFactory;
import com.framework.driver.DriverManager;
import com.framework.services.AuthService;
import com.framework.utils.ConfigReader;
import com.framework.utils.TokenManager;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.testng.ITestContext;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.AfterSuite;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.BeforeSuite;
import org.testng.annotations.Optional;
import org.testng.annotations.Parameters;

import java.net.MalformedURLException;
import java.time.Duration;

/**
 * BaseTest: The foundation class that every test class in this framework extends.
 *
 * <p>WHY A BASE CLASS EXISTS: Without BaseTest, every single test would have to
 * individually set up a browser, navigate to the app, configure timeouts, and
 * tear everything down after. That's hundreds of lines of duplicated code.
 * Instead, BaseTest handles the "before every test" and "after every test" work
 * automatically — test classes inherit that behaviour for free just by extending
 * this class. This is the "Don't Repeat Yourself" (DRY) principle in action.
 *
 * <p>HOW TESTNG LIFECYCLE ANNOTATIONS WORK:
 * <ul>
 *   <li>{@code @BeforeMethod} — TestNG automatically runs the annotated method
 *       before every {@code @Test} method in any class that extends BaseTest.</li>
 *   <li>{@code @AfterMethod} — TestNG automatically runs this after every test,
 *       even if the test failed — hence {@code alwaysRun = true}.</li>
 * </ul>
 *
 * <p>PARALLEL SAFETY: When multiple tests run at the same time (parallel execution),
 * each test runs on its own thread. A naive approach of storing the WebDriver in a
 * shared instance variable would cause threads to interfere with each other's browsers.
 * BaseTest hands the driver to {@link DriverManager}, which stores it in a
 * {@code ThreadLocal} — meaning each thread has its own private copy. This is what
 * makes parallel test execution safe.
 */
public class BaseTest {

    // ==========================================================
    // SUITE LIFECYCLE
    // ==========================================================

    /**
     * suiteSetup: Runs once before the entire suite begins — not per test.
     *
     * <p>WHY {@code @BeforeSuite}: Some resources are expensive to create and safe
     * to share across all tests. A bearer token is the prime example — there is no
     * reason to call the auth endpoint 100 times when one token can serve the whole
     * suite. {@code @BeforeSuite} guarantees this runs exactly once, before the first
     * {@code @BeforeMethod} of any test class.
     *
     * <p>WHY {@code alwaysRun = true}: Prevents TestNG group filters from accidentally
     * skipping suite setup when only a subset of tests (e.g. {@code @smoke}) is run.
     * Without this, running {@code mvn test -Dgroups=smoke} could skip suiteSetup
     * entirely, leaving API tests with no token.
     */
    @BeforeSuite(alwaysRun = true)
    public void suiteSetup() {
        System.out.println("==================================================");
        System.out.println("[SUITE] Starting suite — generating auth token");
        System.out.println("==================================================");

        // Generate bearer token once. AuthService skips gracefully if api.auth.url
        // is not configured — safe to run against SauceDemo or any unauth'd environment.
        AuthService.generateToken();

        if (TokenManager.hasToken()) {
            System.out.println("[SUITE] Auth token ready. API tests will attach Authorization header.");
        } else {
            System.out.println("[SUITE] No auth token configured — API tests will run unauthenticated.");
        }
    }

    /**
     * suiteTeardown: Runs once after all tests in the suite have completed.
     *
     * <p>Clears the bearer token from {@link TokenManager} to prevent a stale token
     * from persisting if the JVM is reused across suite runs (common in certain IDE
     * and Maven Surefire fork configurations).
     */
    @AfterSuite(alwaysRun = true)
    public void suiteTeardown() {
        TokenManager.clearToken();
        System.out.println("[SUITE] Auth token cleared. Suite complete.");
    }

    /**
     * setUp: Creates and configures a browser instance before every test method.
     *
     * <p>WHY {@code alwaysRun = true}: TestNG has a concept of groups (smoke, regression,
     * web). If a test belongs to a group but setUp is not in that group, TestNG might skip
     * the setup entirely — leaving the test with no browser. {@code alwaysRun = true}
     * guarantees setUp runs regardless of which group the test belongs to.
     *
     * <p>WHY {@code @Parameters}: testng.xml can declare parameter values (e.g.
     * {@code <parameter name="browser" value="firefox"/>}), and {@code @Parameters}
     * injects them here. {@code @Optional} provides the fallback ("chrome" / "false")
     * if the XML doesn't declare that parameter — so tests also work when run directly
     * from an IDE without any XML config.
     *
     * <p>WHY {@code ITestContext}: Gives access to the TestNG execution context at
     * runtime — used here to print the suite name for debugging parallel runs.
     *
     * @param browser   The browser to launch (chrome / firefox / edge / android / ios).
     *                  Defaults to "chrome" if not specified.
     * @param headless  Whether to run the browser without a visible window.
     *                  Headless mode is faster and required in CI environments
     *                  that have no graphical display. Defaults to "false".
     * @param context   TestNG context — used here to print the test suite name.
     * @throws MalformedURLException If the Selenium Grid URL in config is malformed.
     */
    @BeforeMethod(alwaysRun = true)
    @Parameters({"browser", "headless"})
    public void setUp(@Optional("chrome") String browser,
                      @Optional("false") String headless,
                      ITestContext context) throws MalformedURLException {

        // Print a separator and identifiers so parallel logs don't get confusing.
        // Each thread ID is unique, so you can match setUp/tearDown pairs in logs.
        long threadId = Thread.currentThread().getId();
        String testName = context.getCurrentXmlTest().getName();
        System.out.println("--------------------------------------------------");
        System.out.println("[SETUP] Thread " + threadId + " | Test: " + testName);

        // ======================================================
        // 1. CONFIG RESOLUTION (Priority: System Prop > XML > Config)
        // ======================================================
        // Maven command-line flags (-Dbrowser=firefox) take highest priority,
        // overriding whatever the XML file says. This lets CI pipelines switch
        // browsers without editing any file — just pass a different flag.
        String targetBrowser = System.getProperty("browser", browser);
        String targetHeadless = System.getProperty("headless", headless);

        System.out.println("[SETUP] Target: " + targetBrowser + " | Headless: " + targetHeadless);

        // ======================================================
        // 2. CREATE DRIVER
        // ======================================================
        // DriverFactory decides WHERE to launch the browser (local machine,
        // Docker Selenium Grid, BrowserStack, Appium for mobile, etc.) based
        // on the "target" system property. It returns a ready-to-use WebDriver.
        WebDriver driver = DriverFactory.createInstance(targetBrowser, targetHeadless);

        // Guard against a misconfigured environment returning null instead of
        // throwing — a null driver would cause cryptic NullPointerExceptions
        // deep inside tests rather than a clear error here at the source.
        if (driver == null) {
            throw new RuntimeException("[FATAL] DriverFactory returned NULL. Check your Config/Grid status.");
        }

        // ======================================================
        // 3. STORE IN ThreadLocal VIA DriverManager
        // ======================================================
        // DriverManager.setDriver() stores the driver in a ThreadLocal variable.
        // ThreadLocal gives each thread its own isolated storage slot, so when
        // Test A (thread 1) and Test B (thread 2) both call getDriver(), they
        // each get back their own browser — they never see each other's instance.
        DriverManager.setDriver(driver);

        // ======================================================
        // 4. CONFIGURE WINDOW SIZE, TIMEOUTS, AND NAVIGATE TO APP
        // ======================================================
        // Extracted to a helper method to keep setUp clean and readable.
        configureDriver(driver, targetBrowser, targetHeadless);
    }

    /**
     * tearDown: Cleans up browser state and releases resources after every test.
     *
     * <p>WHY CLEAN UP: If tearDown didn't run, each test would leave behind a
     * browser process consuming memory and CPU. After 50 tests running in parallel,
     * you'd have 50 zombie browsers. {@code alwaysRun = true} ensures cleanup
     * happens even after a test failure — you never want a crash to leak resources.
     *
     * <p>WHY CLEAR COOKIES AND STORAGE — NOT JUST QUIT: When running tests back-to-back
     * on the same browser session (an optimisation sometimes used), leftover cookies
     * could keep a user "logged in" from a previous test, contaminating the next test's
     * starting state. Explicitly clearing cookies, localStorage, and sessionStorage
     * guarantees a clean slate. If the driver is already dead (e.g. the browser crashed),
     * the catch block silently absorbs the error rather than masking the real failure.
     *
     * <p>WHY {@code DriverManager.unload()}: Simply calling {@code driver.quit()} closes
     * the browser but leaves the ThreadLocal variable holding a stale reference. Calling
     * {@code unload()} removes the entry from the ThreadLocal entirely, preventing memory
     * leaks in long-running test suites.
     */
    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        WebDriver driver = DriverManager.getDriver();

        if (driver != null) {
            try {
                // Delete all HTTP cookies (session tokens, auth cookies, etc.)
                driver.manage().deleteAllCookies();

                // JavaScript executor lets us run JS directly in the browser.
                // localStorage persists across page navigations; sessionStorage
                // persists only for the tab lifetime. Both must be cleared to
                // ensure the next test starts with zero stored state.
                JavascriptExecutor js = (JavascriptExecutor) driver;
                js.executeScript("window.localStorage.clear();");
                js.executeScript("window.sessionStorage.clear();");

                // CRITICAL: Small delay to let the browser commit the clear commands
                // before quit() tears down the session. Without this, the clear
                // commands can be silently dropped if quit() fires too fast.
                Thread.sleep(100);

                System.out.println("[TEARDOWN] Browser state cleared for Thread " + Thread.currentThread().getId());
            } catch (Exception e) {
                // Silently absorb errors here — the browser session may already
                // be dead (e.g. tab crashed mid-test). We do NOT want a tearDown
                // exception to mask the original test failure in the report.
            } finally {
                // quit() closes the browser window AND kills the driver process.
                // Always runs even if the try block threw — hence the finally block.
                driver.quit();

                // Remove the ThreadLocal entry to avoid memory leaks in long runs.
                // Without this, the ThreadLocal holds a dead WebDriver reference forever.
                DriverManager.unload();
            }
        }
    }

    /**
     * configureDriver: Applies timeout, window size, and initial URL navigation.
     *
     * <p>WHY SEPARATE METHOD: Keeps {@link #setUp} short and readable. The logic
     * inside here is secondary to the main flow of setUp — separating it lets you
     * scan setUp at a glance and dive into details only when needed.
     *
     * <p>WHY DIFFERENT HANDLING FOR MOBILE: Android and iOS apps launched via Appium
     * don't have a "browser window" to maximise, and they don't navigate to a URL —
     * they open a native app. The mobile guard prevents calling window.maximize() on
     * an Appium session, which would throw an unsupported command exception.
     *
     * <p>WHY EXPLICIT SIZE IN HEADLESS MODE: A headless browser (no visible window)
     * has no natural window size. Without setting one, it defaults to a very small
     * viewport where buttons and menus may not render or may be positioned off-screen,
     * causing tests to fail for environment reasons rather than real defects.
     *
     * @param driver    The WebDriver instance to configure.
     * @param browser   The browser type string — used to detect mobile targets.
     * @param headless  Whether headless mode is active — determines window sizing strategy.
     */
    private void configureDriver(WebDriver driver, String browser, String headless) {
        // Read implicit wait timeout from config. Implicit wait tells Selenium to
        // wait up to N seconds when looking for an element before giving up.
        // Reading from config means QA can tune it per environment without code changes.
        int implicitTimeout = Integer.parseInt(ConfigReader.getProperty("timeout.implicit", "10"));
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(implicitTimeout));

        // Mobile browsers (Android / iOS via Appium) don't support window manipulation
        // or URL navigation — those concepts belong to web browsers, not native apps.
        boolean isMobile = browser.equalsIgnoreCase("android") || browser.equalsIgnoreCase("ios");

        if (!isMobile) {
            // WEB CONFIGURATION
            if (Boolean.parseBoolean(headless)) {
                // Headless browsers have no default window size — set it explicitly
                // so elements render at a predictable, full-desktop resolution.
                driver.manage().window().setSize(new org.openqa.selenium.Dimension(1920, 1080));
            } else {
                // GUI mode: maximize the window so the full page is visible,
                // preventing elements from being hidden below the fold.
                driver.manage().window().maximize();
            }

            // Navigate to the app URL from config (e.g. "https://www.saucedemo.com").
            // Tests don't hard-code the URL — they inherit it from here, so changing
            // environments (dev → staging → prod) is a one-line config edit.
            String url = ConfigReader.getProperty("url");
            if (url != null) {
                driver.get(url);
            }
        }
    }
}
