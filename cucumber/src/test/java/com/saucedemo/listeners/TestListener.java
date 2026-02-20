package com.saucedemo.listeners;

import com.saucedemo.utils.SlackUtils;
import org.testng.ITestContext;
import org.testng.ITestListener;
import org.testng.ITestResult;

/**
 * TestListener: Suite-level observer for logging and Slack notifications.
 * Screenshots are handled per-scenario in Hooks.java via Cucumber's scenario context.
 */
public class TestListener implements ITestListener {

    @Override
    public void onTestStart(ITestResult result) {
        System.out.println("--------------------------------------------------");
        System.out.println("[INFO] STARTED: " + result.getMethod().getMethodName());
        System.out.println("--------------------------------------------------");
    }

    @Override
    public void onTestSuccess(ITestResult result) {
        System.out.println("[PASS] " + result.getMethod().getMethodName());
    }

    @Override
    public void onTestFailure(ITestResult result) {
        System.err.println("[FAIL] " + result.getMethod().getMethodName());
        Throwable t = result.getThrowable();
        if (t != null) System.err.println("[ERROR] " + t.getMessage());
    }

    @Override
    public void onTestSkipped(ITestResult result) {
        System.out.println("[SKIP] " + result.getMethod().getMethodName());
    }

    @Override
    public void onFinish(ITestContext context) {
        String summary = String.format(
                "CucumberFramework Execution Complete\n" +
                "-------------------------------------\n" +
                "Suite  : %s\n" +
                "Passed : %d\n" +
                "Failed : %d\n" +
                "Skipped: %d\n" +
                "-------------------------------------",
                context.getSuite().getName(),
                context.getPassedTests().size(),
                context.getFailedTests().size(),
                context.getSkippedTests().size()
        );
        System.out.println("[INFO] " + summary);
        SlackUtils.sendResult(summary);
    }
}
