package com.saucedemo.utils;

import org.testng.IRetryAnalyzer;
import org.testng.ITestResult;

/**
 * RetryAnalyzer: Automatically re-runs failed scenarios up to retry.max times.
 * Registered globally via AnnotationTransformer — no per-test annotation needed.
 */
public class RetryAnalyzer implements IRetryAnalyzer {

    private int count = 0;

    private static final int MAX_RETRY_COUNT;

    static {
        MAX_RETRY_COUNT = Integer.parseInt(ConfigReader.getProperty("retry.max", "1"));
    }

    @Override
    public boolean retry(ITestResult result) {
        if (!result.isSuccess()) {
            if (count < MAX_RETRY_COUNT) {
                count++;
                System.out.println("[WARN] Scenario Failed: " + result.getName()
                        + " | Attempt: " + count + "/" + MAX_RETRY_COUNT + ". Retrying...");
                return true;
            }
        }
        return false;
    }
}
