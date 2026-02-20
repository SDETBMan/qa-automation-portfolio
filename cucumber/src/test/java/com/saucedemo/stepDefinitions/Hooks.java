package com.saucedemo.stepDefinitions;

import com.saucedemo.utils.DriverManager;
import io.cucumber.java.After;
import io.cucumber.java.Scenario;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;

public class Hooks {

    @After
    public void tearDown(Scenario scenario) {
        // Get the driver instance safely
        WebDriver driver = DriverManager.getDriver();

        // Only try to take a screenshot if the driver is actually alive
        if (scenario.isFailed() && driver != null) {
            try {
                final byte[] screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);
                scenario.attach(screenshot, "image/png", "Failure Screenshot");
            } catch (Exception e) {
                System.out.println("Failed to capture screenshot: " + e.getMessage());
            }
        }

        // Close the browser
        DriverManager.quitDriver();
    }
}
