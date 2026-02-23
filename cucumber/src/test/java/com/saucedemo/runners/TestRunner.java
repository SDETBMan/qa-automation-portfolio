package com.saucedemo.runners;

import io.cucumber.testng.AbstractTestNGCucumberTests;
import io.cucumber.testng.CucumberOptions;
import org.testng.annotations.DataProvider;

/**
 * TestRunner: The entry point that wires together Cucumber and TestNG to execute
 * the entire test suite.
 *
 * <p>WHAT IS A CUCUMBER RUNNER: In a Cucumber/TestNG project, a runner class tells
 * Cucumber where to find feature files, where to find step definitions, and which
 * plugins to use for reporting. Without a runner, nothing executes — it is the bridge
 * between the build tool (Maven/Gradle) and the test framework.
 *
 * <p>HOW IT WORKS:
 * <ol>
 *   <li>Maven Surefire runs this class because it extends
 *       {@link AbstractTestNGCucumberTests}, which makes it a valid TestNG test class.</li>
 *   <li>Cucumber reads the {@code @CucumberOptions} annotation to discover feature
 *       files and step definitions.</li>
 *   <li>Each scenario is passed to the {@link #scenarios()} DataProvider, which TestNG
 *       uses to invoke the scenario as an individual test method.</li>
 *   <li>With {@code parallel = true}, TestNG runs multiple scenarios concurrently
 *       using a thread pool, each getting its own browser via DriverManager's ThreadLocal.</li>
 * </ol>
 *
 * <p>REPORTING: Three reporting plugins are configured:
 * <ul>
 *   <li><b>pretty</b> — prints a colour-formatted, human-readable execution log to the console.</li>
 *   <li><b>html</b> — generates a self-contained HTML report at {@code target/cucumber-reports/}.</li>
 *   <li><b>ExtentCucumberAdapter</b> — generates rich Extent Reports with screenshots and charts.</li>
 *   <li><b>AllureCucumber7Jvm</b> — generates Allure report data consumed by the Allure CLI
 *       to produce interactive HTML dashboards with history trending.</li>
 * </ul>
 */
@CucumberOptions(
        // WHERE TO FIND FEATURE FILES: Cucumber scans this directory recursively for all .feature files
        features = "src/test/resources/features",

        // WHERE TO FIND STEP DEFINITIONS: Cucumber scans this Java package for classes
        // annotated with @Given, @When, @Then, @Before, @After, etc.
        glue = "com.saucedemo.stepDefinitions",

        // REPORTING PLUGINS: multiple plugins can be configured simultaneously
        plugin = {
                "pretty",                                                              // Console output
                "html:target/cucumber-reports/cucumber.html",                          // Built-in HTML report
                "com.aventstack.extentreports.cucumber.adapter.ExtentCucumberAdapter:", // Extent Reports
                "io.qameta.allure.cucumber7jvm.AllureCucumber7Jvm"                     // Allure Reports
        },

        // MONOCHROME: removes ANSI colour escape codes from console output, making logs
        // readable in CI environments and log files that do not support terminal colours
        monochrome = true
)
public class TestRunner extends AbstractTestNGCucumberTests {

    /**
     * DataProvider that supplies each Cucumber scenario to TestNG as a separate
     * data set, enabling parallel scenario execution.
     *
     * <p>WHAT THIS DOES: {@link AbstractTestNGCucumberTests#scenarios()} returns a
     * 2D array where each row represents one Cucumber scenario (or one Scenario Outline
     * example row). By overriding this method and adding {@code @DataProvider(parallel = true)},
     * TestNG runs multiple rows — i.e., multiple scenarios — concurrently on separate threads.
     *
     * <p>WHY OVERRIDE IT: The default implementation in the parent class uses
     * {@code parallel = false}. Overriding it here with {@code parallel = true} activates
     * parallel execution without requiring any other changes to the framework. TestNG
     * manages the thread pool size (configured in testng.xml or via the
     * {@code dataproviderthreadcount} property in Maven Surefire).
     *
     * <p>THREAD SAFETY: Parallel scenarios are safe here because DriverManager uses
     * ThreadLocal storage — each thread gets its own isolated browser instance. Without
     * ThreadLocal, parallel tests would share a single driver and corrupt each other.
     *
     * @return a 2D Object array where each inner array holds one Cucumber scenario
     */
    @Override
    @DataProvider(parallel = true)
    public Object[][] scenarios() {
        return super.scenarios();
    }
}
