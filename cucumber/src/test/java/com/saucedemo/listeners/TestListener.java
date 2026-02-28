package com.saucedemo.listeners;

import com.saucedemo.utils.DataDogUtils;
import com.saucedemo.utils.SlackUtils;
import org.testng.ITestContext;
import org.testng.ITestListener;
import org.testng.ITestResult;

/**
 * TestListener: A TestNG listener that observes test execution events and reacts
 * to them — logging results to the console and sending a summary to Slack when
 * the entire suite finishes.
 *
 * <p>WHAT IS A TESTNG LISTENER: TestNG provides an event system through listener
 * interfaces. By implementing {@link ITestListener} and registering this class
 * in {@code testng.xml} (or via a Maven Surefire listener configuration), TestNG
 * automatically calls the appropriate method here whenever a test starts, passes,
 * fails, or is skipped — without any test class needing to explicitly call these methods.
 * This is the Observer design pattern applied to test execution.
 *
 * <p>RELATIONSHIP TO HOOKS.java: There is an intentional division of responsibility:
 * <ul>
 *   <li>{@code Hooks.java} (Cucumber) handles per-scenario concerns: screenshots on
 *       failure and browser teardown. It has access to the Cucumber Scenario object.</li>
 *   <li>This class (TestNG) handles suite-level concerns: structured logging of
 *       pass/fail/skip events and a final Slack notification with aggregate counts.
 *       It has access to TestNG's ITestResult and ITestContext objects.</li>
 * </ul>
 *
 * <p>SLACK INTEGRATION: At the end of the suite, this listener composes a summary
 * message and passes it to {@link SlackUtils#sendResult(String)}. This notifies the
 * team immediately when a CI run completes, without requiring anyone to check the
 * CI dashboard manually. Integrating test results into team communication tools is
 * a common requirement in professional QA setups.
 */
public class TestListener implements ITestListener {

    // Records the wall-clock time when the suite context begins so onFinish can
    // report accurate duration to DataDog.
    private long suiteStartTime;

    /**
     * Called by TestNG when the test context initialises, before any tests run.
     * Captures the suite start time for DataDog duration reporting.
     *
     * @param context TestNG context — represents the test block in testng.xml.
     */
    @Override
    public void onStart(ITestContext context) {
        suiteStartTime = System.currentTimeMillis();
    }

    /**
     * Called by TestNG at the moment a test method starts executing.
     *
     * <p>The separator lines make the test name easy to spot in long console logs,
     * especially when multiple tests run concurrently and their output is interleaved.
     *
     * @param result TestNG result object containing the test method name and metadata
     */
    @Override
    public void onTestStart(ITestResult result) {
        System.out.println("--------------------------------------------------");
        System.out.println("[INFO] STARTED: " + result.getMethod().getMethodName());
        System.out.println("--------------------------------------------------");
    }

    /**
     * Called by TestNG when a test method completes without any assertion failures
     * or exceptions — i.e., it passed.
     *
     * @param result TestNG result object for the test that just passed
     */
    @Override
    public void onTestSuccess(ITestResult result) {
        System.out.println("[PASS] " + result.getMethod().getMethodName());
    }

    /**
     * Called by TestNG when a test method throws an assertion error or any unhandled
     * exception — i.e., it failed.
     *
     * <p>Using {@code System.err} (rather than {@code System.out}) causes the failure
     * output to appear in red in most terminals and CI log viewers, making failures
     * visually distinct from passing test output.
     *
     * <p>The throwable check prevents a NullPointerException in edge cases where the
     * test failed without a root cause (which is rare but possible with certain
     * TestNG configurations).
     *
     * @param result TestNG result object containing the failure reason and stack trace
     */
    @Override
    public void onTestFailure(ITestResult result) {
        System.err.println("[FAIL] " + result.getMethod().getMethodName());
        Throwable t = result.getThrowable();
        // Log the failure cause if available — helps with quick diagnosis in CI logs
        if (t != null) System.err.println("[ERROR] " + t.getMessage());
    }

    /**
     * Called by TestNG when a test is skipped — typically because a configuration
     * method ({@code @BeforeMethod}) threw an exception, or a dependency test failed.
     *
     * <p>Logging skipped tests is important for identifying hidden failures: a suite
     * that reports "0 failures, 10 skipped" is not necessarily healthy — the skips
     * may be masking underlying problems.
     *
     * @param result TestNG result object for the skipped test
     */
    @Override
    public void onTestSkipped(ITestResult result) {
        System.out.println("[SKIP] " + result.getMethod().getMethodName());
    }

    /**
     * Called by TestNG once after all tests in the suite (or test context) have finished.
     *
     * <p>WHAT IS ITestContext: {@link ITestContext} represents the TestNG "test" block
     * in testng.xml. It provides aggregate counts of passed, failed, and skipped tests
     * for the entire run, and also exposes the suite name and other metadata.
     *
     * <p>SLACK NOTIFICATION: The summary string is formatted and passed to
     * {@link SlackUtils#sendResult(String)}, which posts it to the configured Slack
     * channel via webhook. This gives the QA team (or stakeholders) an immediate
     * pass/fail summary in their communication tool without having to open a CI dashboard.
     *
     * @param context the TestNG context object with aggregate test result counts
     */
    @Override
    public void onFinish(ITestContext context) {
        // Build a structured summary with pass/fail/skip counts for the completed suite run
        String summary = String.format(
                "CucumberFramework Execution Complete\n" +
                "-------------------------------------\n" +
                "Suite  : %s\n" +
                "Passed : %d\n" +
                "Failed : %d\n" +
                "Skipped: %d\n" +
                "-------------------------------------",
                context.getSuite().getName(),       // Suite name from testng.xml
                context.getPassedTests().size(),    // Total passed scenarios
                context.getFailedTests().size(),    // Total failed scenarios
                context.getSkippedTests().size()    // Total skipped scenarios
        );
        // Print the summary to the console for local runs and CI log archives
        System.out.println("[INFO] " + summary);
        // Post the summary to the configured Slack channel for team visibility
        SlackUtils.sendResult(summary);

        // Send suite-level metrics to DataDog (passed/failed/skipped counts + duration).
        // DataDogUtils.sendTestMetrics() is a no-op if DD_API_KEY is not set.
        long durationMs = System.currentTimeMillis() - suiteStartTime;
        DataDogUtils.sendTestMetrics(
                context.getPassedTests().size(),
                context.getFailedTests().size(),
                context.getSkippedTests().size(),
                durationMs,
                "cucumber"
        );
    }
}
