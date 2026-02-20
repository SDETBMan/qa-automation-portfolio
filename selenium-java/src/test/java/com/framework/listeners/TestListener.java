package com.framework.listeners;

import com.framework.driver.DriverManager;
import com.framework.utils.SlackUtils;
import io.qameta.allure.Attachment;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.testng.ITestContext;
import org.testng.ITestListener;
import org.testng.ITestResult;

/**
 * TestListener: Global observer for test execution events.
 * Handles logging, screenshot capture on failure, and CI/CD notifications.
 */
public class TestListener implements ITestListener {

    @Override
    public void onTestStart(ITestResult result) {
        System.out.println("--------------------------------------------------");
        System.out.println("[INFO] STARTED TEST: " + result.getMethod().getMethodName());
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
        String reason = (t != null) ? t.getMessage() : "No exception captured";
        System.err.println("[ERROR] Reason: " + reason);

        WebDriver driver = DriverManager.getDriver();
        if (driver != null) {
            System.out.println("[INFO] Capturing failure screenshot for Allure report...");
            saveScreenshot(driver);
        }
    }

    @Override
    public void onTestSkipped(ITestResult result) {
        System.out.println("[WARN] SKIPPED: " + result.getMethod().getMethodName());
    }

    @Override
    public void onFinish(ITestContext context) {
        // Constructing a Director-Level Summary for Slack
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
        SlackUtils.sendResult(summary);
    }

    /**
     * Captures a screenshot and attaches it directly to the Allure Report.
     */
    @Attachment(value = "Failure Screenshot", type = "image/png")
    public byte[] saveScreenshot(WebDriver driver) {
        return ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);
    }
}
