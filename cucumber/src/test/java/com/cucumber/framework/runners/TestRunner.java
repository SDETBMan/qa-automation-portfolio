package com.cucumber.framework.runners;

import io.cucumber.junit.Cucumber;
import io.cucumber.junit.CucumberOptions;
import org.junit.runner.RunWith;

/**
 * JUnit 4 Cucumber runner.
 *
 * CucumberOptions:
 *   features  → where .feature files live
 *   glue      → packages containing step definitions and hooks
 *   tags      → filter by @smoke or @regression (override via -Dcucumber.filter.tags)
 *   plugin    → pretty console output + HTML report + Allure integration
 *   monochrome → cleaner console output (no ANSI escape codes)
 *
 * Run specific tags from CLI:
 *   mvn test -Dcucumber.filter.tags="@smoke"
 *   mvn test -Dcucumber.filter.tags="@regression"
 *   mvn test -Dcucumber.filter.tags="@login"
 */
@RunWith(Cucumber.class)
@CucumberOptions(
        features  = "src/test/resources/features",
        glue      = "com.cucumber.framework",
        tags      = "@smoke or @regression",
        plugin    = {
                "pretty",
                "html:target/cucumber-reports/cucumber.html",
                "json:target/cucumber-reports/cucumber.json",
                "io.qameta.allure.cucumber7jvm.AllureCucumber7Jvm"
        },
        monochrome = true
)
public class TestRunner {}
