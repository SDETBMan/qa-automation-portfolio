package com.cucumber.framework.hooks;

import com.cucumber.framework.driver.DriverManager;
import io.cucumber.java.After;
import io.cucumber.java.Before;
import io.cucumber.java.Scenario;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;

/**
 * Cucumber scenario hooks — driver lifecycle + screenshot on failure.
 *
 * @Before  → runs before each scenario   (equivalent to NUnit [SetUp] / Playwright beforeEach)
 * @After   → runs after  each scenario   (equivalent to NUnit [TearDown] / Playwright afterEach)
 *
 * Screenshots are attached to the Allure report via scenario.attach(),
 * mirroring the AllureApi.AddAttachment() call in playwright-dotnet's BaseTest.cs.
 */
public class Hooks {

    @Before(order = 0)
    public void setUp(Scenario scenario) {
        System.out.println("[HOOKS] Starting: " + scenario.getName());
        DriverManager.init();
    }

    @After(order = 0)
    public void tearDown(Scenario scenario) {
        if (scenario.isFailed()) {
            try {
                byte[] screenshot = ((TakesScreenshot) DriverManager.getDriver())
                        .getScreenshotAs(OutputType.BYTES);
                scenario.attach(screenshot, "image/png",
                        "failure_" + scenario.getName().replace(" ", "_"));
            } catch (Exception e) {
                System.err.println("[HOOKS] Screenshot failed: " + e.getMessage());
            }
        }
        DriverManager.quit();
        System.out.println("[HOOKS] Finished: " + scenario.getName()
                + " — " + scenario.getStatus());
    }
}
