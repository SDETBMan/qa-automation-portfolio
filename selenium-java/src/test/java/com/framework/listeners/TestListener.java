package com.framework.listeners;

import com.framework.driver.DriverManager;
import com.framework.utils.DataDogUtils;
import com.framework.utils.SlackUtils;
import io.qameta.allure.Attachment;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.testng.ITestContext;
import org.testng.ITestListener;
import org.testng.ITestResult;

/**
 * TestListener: Global observer for test execution events in this framework.
 *
 * <p>WHY A LISTENER EXISTS: In large test suites, you need cross-cutting behaviour
 * that applies to every single test — screenshot on failure, structured logging,
 * CI/CD notifications — without copy-pasting that code into every test class.
 * TestNG's listener mechanism solves this: register the listener once (in testng.xml)
 * and it automatically fires its callback methods for every test in the suite.
 *
 * <p>WHAT {@code ITestListener} IS: An interface provided by TestNG. By implementing
 * it, this class "subscribes" to the TestNG execution lifecycle. TestNG calls the
 * appropriate method at each lifecycle event — start, success, failure, skip, finish.
 * All methods have default no-op implementations in the interface; this class only
 * overrides the ones it cares about.
 *
 * <p>HOW IT IS REGISTERED: In {@code testng.xml}, under {@code <listeners>}:
 * {@code <listener class-name="com.framework.listeners.TestListener"/>}
 * That single line activates this listener for the entire suite — no per-test
 * annotation needed.
 *
 * <p>WHAT THIS CLASS DOES:
 * <ul>
 *   <li>Prints structured start/pass/skip banners to CI build logs.</li>
 *   <li>On failure: logs the error message AND captures a screenshot that is
 *       embedded directly in the Allure HTML report.</li>
 *   <li>After the whole suite finishes: sends a pass/fail summary to Slack
 *       so the team knows the result without opening CI.</li>
 * </ul>
 */
public class TestListener implements ITestListener {

    // Records the wall-clock time when the suite context begins so onFinish can
    // report accurate duration to DataDog.
    private long suiteStartTime;

    /**
     * onStart: Called by TestNG when the test context initialises, before any tests run.
     * Captures the suite start time for DataDog duration reporting.
     *
     * @param context TestNG context — represents the test block in testng.xml.
     */
    @Override
    public void onStart(ITestContext context) {
        suiteStartTime = System.currentTimeMillis();
    }

    /**
     * onTestStart: Called by TestNG immediately before each {@code @Test} method runs.
     *
     * <p>WHY LOG THE TEST NAME: When tests run in parallel, console output from
     * multiple threads interleaves. Printing the method name here creates a clear
     * "start marker" that lets you trace which output belongs to which test.
     *
     * @param result TestNG result object — contains the test method name, class, etc.
     */
    @Override
    public void onTestStart(ITestResult result) {
        System.out.println("--------------------------------------------------");
        System.out.println("[INFO] STARTED TEST: " + result.getMethod().getMethodName());
        System.out.println("--------------------------------------------------");
    }

    /**
     * onTestSuccess: Called by TestNG after a test method passes.
     *
     * <p>Prints a [PASS] line so the CI build log provides a quick human-readable
     * summary of what passed without having to open the full Allure report.
     *
     * @param result TestNG result — contains the method name and duration.
     */
    @Override
    public void onTestSuccess(ITestResult result) {
        System.out.println("[PASS] " + result.getMethod().getMethodName());
    }

    /**
     * onTestFailure: Called by TestNG after a test method fails (assertion error or exception).
     *
     * <p>WHY CAPTURE A SCREENSHOT ON FAILURE: When a test fails in CI, the browser
     * window is invisible — there's nothing to look at. A screenshot captured at the
     * exact moment of failure is the single most valuable debugging artefact available.
     * Without it, engineers waste time trying to reproduce the failure locally.
     *
     * <p>WHY USE {@code @Attachment}: The Allure report framework intercepts methods
     * annotated with {@code @Attachment} and embeds their return value directly in the
     * test report. Calling {@code saveScreenshot()} here means the PNG is embedded in
     * the Allure report's failure detail view — one click to see exactly what the
     * browser looked like when the test broke.
     *
     * <p>WHY {@code DriverManager.getDriver()}: The WebDriver for the failing test lives
     * in a ThreadLocal inside DriverManager. The listener runs on the same thread as the
     * test, so {@code getDriver()} returns that test's specific browser — not another
     * parallel test's browser.
     *
     * @param result TestNG result — contains the exception/assertion error that caused failure.
     */
    @Override
    public void onTestFailure(ITestResult result) {
        System.err.println("[FAIL] " + result.getMethod().getMethodName());

        // Extract the failure reason (exception message) and print it.
        // This appears in CI build logs so engineers can see the failure reason
        // without opening any report — useful when reports aren't published yet.
        Throwable t = result.getThrowable();
        String reason = (t != null) ? t.getMessage() : "No exception captured";
        System.err.println("[ERROR] Reason: " + reason);

        // Capture a screenshot from the browser that was active for this test.
        // Only attempt this if a driver is available — the test might have failed
        // before the browser was even launched (e.g. a config error in setUp).
        WebDriver driver = DriverManager.getDriver();
        if (driver != null) {
            System.out.println("[INFO] Capturing failure screenshot for Allure report...");
            saveScreenshot(driver);
        }
    }

    /**
     * onTestSkipped: Called by TestNG when a test is skipped.
     *
     * <p>A test is skipped when its dependencies fail or when setUp threw an exception.
     * Logging skips separately makes it easy to distinguish "didn't run" from "failed"
     * — a distinction that matters when triaging CI results.
     *
     * @param result TestNG result — contains the skip reason if one was provided.
     */
    @Override
    public void onTestSkipped(ITestResult result) {
        System.out.println("[WARN] SKIPPED: " + result.getMethod().getMethodName());
    }

    /**
     * onFinish: Called by TestNG after all tests in the current suite have completed.
     *
     * <p>WHY SEND A SLACK NOTIFICATION: CI/CD pipelines are designed to be automated
     * and unattended. Without notifications, the team must proactively check GitHub
     * Actions to find out if tests passed. A Slack message with pass/fail counts
     * ensures the whole team sees results immediately after each pipeline run,
     * enabling faster response to regressions.
     *
     * <p>THE SUMMARY FORMAT: Structured with labelled counts (Passed / Failed / Skipped)
     * so a non-technical stakeholder can read it at a glance in Slack without
     * understanding what a test framework is.
     *
     * @param context TestNG context — provides access to the suite name and result sets.
     */
    @Override
    public void onFinish(ITestContext context) {
        // Build a human-readable multi-line summary of the suite execution.
        // String.format() with %d (integer) and %s (string) placeholders keeps this
        // clean — no string concatenation chains to maintain.
        String summary = String.format(
                "Test Suite Execution Complete\n" +
                        "----------------------------\n" +
                        "Suite: %s\n" +
                        "Total Passed: %d\n" +
                        "Total Failed: %d\n" +
                        "Total Skipped: %d\n" +
                        "----------------------------",
                context.getSuite().getName(),
                context.getPassedTests().size(),
                context.getFailedTests().size(),
                context.getSkippedTests().size()
        );

        System.out.println("[INFO] Dispatching execution summary to Slack...");

        // SlackUtils.sendResult() posts the message to a webhook URL configured
        // in config.properties. If no webhook is set, it logs a warning and skips.
        SlackUtils.sendResult(summary);

        // Send suite-level metrics to DataDog (passed/failed/skipped counts + duration).
        // DataDogUtils.sendTestMetrics() is a no-op if DD_API_KEY is not set.
        long durationMs = System.currentTimeMillis() - suiteStartTime;
        DataDogUtils.sendTestMetrics(
                context.getPassedTests().size(),
                context.getFailedTests().size(),
                context.getSkippedTests().size(),
                durationMs,
                "selenium-java"
        );
    }

    /**
     * saveScreenshot: Captures the current browser screen as a PNG byte array.
     *
     * <p>WHY RETURN {@code byte[]}: The Allure {@code @Attachment} annotation works by
     * intercepting the return value of the annotated method and storing it as an
     * attachment in the test report. Returning raw bytes (rather than a file path)
     * means the screenshot is embedded directly in the report — no external file
     * storage needed, and the report remains self-contained.
     *
     * <p>WHY {@code TakesScreenshot}: This is a Selenium interface that WebDriver
     * implementations (ChromeDriver, FirefoxDriver, etc.) all implement. Casting
     * to it unlocks the {@code getScreenshotAs()} method. {@code OutputType.BYTES}
     * requests the screenshot as an in-memory byte array (as opposed to a File or
     * a Base64 string).
     *
     * @param driver The WebDriver instance whose current page should be captured.
     * @return The screenshot as a PNG byte array, embedded in the Allure report.
     */
    @Attachment(value = "Failure Screenshot", type = "image/png")
    public byte[] saveScreenshot(WebDriver driver) {
        return ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);
    }
}
