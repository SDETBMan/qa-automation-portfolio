package com.framework.utils;

import org.testng.IRetryAnalyzer;
import org.testng.ITestResult;

/**
 * RetryAnalyzer: Automatically re-runs failed test methods up to a configurable maximum.
 *
 * WHY THIS CLASS EXISTS — Dealing With Flaky Tests:
 * In real-world test automation, some tests fail intermittently not because the application
 * has a bug, but due to transient infrastructure issues:
 *   - Network packet loss causing Selenium commands to time out
 *   - A slow CI server causing an element to appear later than the wait timeout allows
 *   - Selenium Grid nodes becoming temporarily overloaded
 *   - Browser startup race conditions in parallel execution
 *
 * These failures are called "flaky" tests — they pass most of the time but fail occasionally
 * for reasons unrelated to the application under test. A retry mechanism provides a safety
 * net: if a test fails once, it is automatically re-run. If it passes on the retry, the test
 * suite continues normally. Only if it fails every attempt does it count as a real failure.
 *
 * HOW TESTNG USES THIS CLASS:
 * TestNG calls the retry() method after every test failure. If retry() returns true, TestNG
 * re-runs the test. If it returns false, TestNG marks the test as failed permanently.
 * The AnnotationTransformer class (in this same framework) automatically applies this
 * RetryAnalyzer to all non-unit tests so no individual @Test annotation needs it.
 *
 * CONFIGURABLE RETRY COUNT:
 * The max retry count is read from config.properties (key: "retry.max") with a default of 1.
 * Setting it to 1 means one retry is allowed — a test gets 2 total attempts before failing.
 * Setting it to 0 effectively disables retry. This can be tuned per environment without
 * changing code.
 *
 * For recruiters: Retry logic is a standard requirement in enterprise automation frameworks.
 * Making it configurable and applying it globally via the transformer (rather than manually
 * per test) demonstrates framework maturity and maintainability.
 */
public class RetryAnalyzer implements IRetryAnalyzer {

    // Tracks how many retries have been used for the current test instance.
    // Each test method gets its own RetryAnalyzer instance (TestNG creates a new one per test),
    // so this counter is per-test, not shared across the suite.
    private int count = 0;

    // Static final: computed once when the class is first loaded, shared by all instances.
    // Reading from config allows the retry count to be tuned per environment.
    private static final int MAX_RETRY_COUNT;

    static {
        // "retry.max" defaults to 1 if not specified — allowing one re-run per failed test.
        MAX_RETRY_COUNT = Integer.parseInt(ConfigReader.getProperty("retry.max", "1"));
    }

    /**
     * Called by TestNG after every test failure. Decides whether to retry the test.
     *
     * THE DECISION LOGIC:
     * We first check that the test actually failed (not just "passed but with warnings").
     * Then we compare the used retry count against the maximum. If we have attempts left,
     * we increment the counter and return true (retry). Once the count is exhausted,
     * we return false (mark as permanently failed).
     *
     * WHY THE isSuccess() CHECK:
     * TestNG can call this method for test results that are not failures in some edge cases.
     * Guarding with !result.isSuccess() ensures we only retry actual failures, not skipped
     * or passed tests that somehow triggered this callback.
     *
     * @param result The test result object containing the failure details and test name
     * @return true to tell TestNG to re-execute this test; false to accept the failure
     */
    @Override
    public boolean retry(ITestResult result) {
        if (!result.isSuccess()) { // Only retry if the test failed
            if (count < MAX_RETRY_COUNT) {
                count++;
                System.out.println("[WARN] Test Failed: " + result.getName() +
                        " | Attempt: " + count + "/" + MAX_RETRY_COUNT + ". Retrying...");
                return true; // Tells TestNG to re-execute
            }
        }
        return false; // No more retries — accept the failure
    }
}
