package com.saucedemo.stepDefinitions;

import com.saucedemo.utils.DriverManager;
import io.cucumber.java.After;
import io.cucumber.java.Scenario;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;

/**
 * Hooks: Cucumber lifecycle hooks that run automatically before or after every scenario.
 *
 * <p>WHAT ARE CUCUMBER HOOKS: In Cucumber, hooks are special methods annotated with
 * {@code @Before} or {@code @After} that run automatically at the start or end of
 * every test scenario — similar to TestNG's {@code @BeforeMethod} / {@code @AfterMethod},
 * but without needing to be declared in every test class. They live in a class in the
 * "glue" package and Cucumber discovers them automatically.
 *
 * <p>WHY THIS CLASS EXISTS: Two critical tasks must happen after every scenario:
 * <ol>
 *   <li>If the scenario failed, capture a screenshot and attach it to the report so
 *       developers can see exactly what the browser looked like at the point of failure.
 *       This is one of the most valuable debugging aids in UI automation.</li>
 *   <li>Quit the browser to release resources. Without this, each parallel thread
 *       would accumulate open browser windows until the machine runs out of memory.</li>
 * </ol>
 *
 * <p>Centralising both responsibilities here means no individual step definition class
 * needs to remember to clean up — cleanup is guaranteed for every scenario automatically.
 */
public class Hooks {

    /**
     * Runs automatically after every Cucumber scenario completes.
     *
     * <p>The {@code @After} annotation tells Cucumber to call this method once the
     * last step of each scenario has finished (whether it passed, failed, or was
     * skipped). Cucumber injects the {@link Scenario} object, which provides
     * metadata about the just-finished scenario including its pass/fail status.
     *
     * <p>SCREENSHOT ON FAILURE: Capturing a screenshot only on failure avoids
     * cluttering the report with passing-scenario screenshots that add no value.
     * The screenshot bytes are attached directly to the Cucumber scenario object;
     * the HTML report and Allure/Extent integrations automatically embed it inline.
     *
     * <p>TEARDOWN ORDER: The screenshot must be taken BEFORE the browser is closed.
     * This method captures the screenshot first, then quits the driver.
     *
     * @param scenario the Cucumber Scenario object for the test that just finished;
     *                 provides pass/fail status and an attachment API for reports
     */
    @After
    public void tearDown(Scenario scenario) {
        // Get the driver instance safely — returns null if it was never initialised
        WebDriver driver = DriverManager.getDriver();

        // Only try to take a screenshot if the driver is actually alive
        if (scenario.isFailed() && driver != null) {
            try {
                // Cast driver to TakesScreenshot — all standard WebDriver implementations
                // support this interface; it provides getScreenshotAs() to capture the viewport
                final byte[] screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);
                // Attach the PNG bytes to the scenario — the HTML/Allure/Extent report
                // will embed this image inline next to the failing step
                scenario.attach(screenshot, "image/png", "Failure Screenshot");
            } catch (Exception e) {
                // The driver may have crashed or the session may have expired;
                // log the warning but do not fail the teardown because of it
                System.out.println("Failed to capture screenshot: " + e.getMessage());
            }
        }

        // Close the browser and free the ThreadLocal driver slot for this thread
        DriverManager.quitDriver();
    }
}
