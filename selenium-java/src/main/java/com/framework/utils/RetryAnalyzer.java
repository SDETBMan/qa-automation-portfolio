package com.framework.utils;

import org.testng.IRetryAnalyzer;
import org.testng.ITestResult;

/**
 * RetryAnalyzer: Implements logic to automatically re-run failed tests.
 * This is essential for handling "flaky" tests caused by network instability.
 */
public class RetryAnalyzer implements IRetryAnalyzer {
    private int count = 0;

    private static final int MAX_RETRY_COUNT;

    static {
        MAX_RETRY_COUNT = Integer.parseInt(ConfigReader.getProperty("retry.max", "1"));
    }

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
        return false;
    }
}
