package com.saucedemo.stepDefinitions;

import com.saucedemo.utils.DriverManager;
import io.cucumber.java.en.Then;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.openqa.selenium.By;
import org.testng.Assert;
import org.testng.asserts.SoftAssert;

/**
 * SecuritySteps: Cucumber step definitions for OWASP-aware security scenarios.
 *
 * SQL injection and XSS scenarios reuse existing steps from LoginSteps.java.
 * This class provides only the 3 new assertion steps that security.feature needs.
 */
public class SecuritySteps {

    private static final By ERROR_LOCATOR = By.cssSelector("[data-test='error']");

    // ------------------------------------------------------------------
    // Step: error message should not expose system internals
    // Used by: SQL injection scenario
    // ------------------------------------------------------------------
    @Then("the error message should not expose system internals")
    public void errorMessageShouldNotExposeSystemInternals() {
        String errorText = DriverManager.getDriver()
                .findElement(ERROR_LOCATOR)
                .getText()
                .toLowerCase();

        Assert.assertFalse(errorText.contains("sql"),
                "SECURITY: Error message leaks SQL keyword — " + errorText);
        Assert.assertFalse(errorText.contains("exception"),
                "SECURITY: Error message leaks exception details — " + errorText);
        Assert.assertFalse(errorText.contains("stacktrace"),
                "SECURITY: Error message leaks stack trace — " + errorText);
    }

    // ------------------------------------------------------------------
    // Step: the page title should not be {string}
    // Used by: XSS scenario
    // ------------------------------------------------------------------
    @Then("the page title should not be {string}")
    public void pageTitleShouldNotBe(String unexpectedTitle) {
        String actualTitle = DriverManager.getDriver().getTitle();
        Assert.assertNotEquals(actualTitle, unexpectedTitle,
                "SECURITY: Page title equals '" + unexpectedTitle + "' — possible XSS execution.");
    }

    // ------------------------------------------------------------------
    // Step: the security response headers should be present
    // Uses RestAssured (already a pom.xml dependency via ApiSteps).
    // SoftAssert: documents posture without failing on missing headers on
    // a demo site we do not control.
    // ------------------------------------------------------------------
    @Then("the security response headers should be present")
    public void securityResponseHeadersShouldBePresent() {
        SoftAssert softAssert = new SoftAssert();

        Response response = RestAssured.get("https://www.saucedemo.com");

        softAssert.assertNotNull(response.getHeader("X-Frame-Options"),
                "SECURITY HEADER MISSING: X-Frame-Options (clickjacking risk)");
        softAssert.assertNotNull(response.getHeader("X-Content-Type-Options"),
                "SECURITY HEADER MISSING: X-Content-Type-Options (MIME sniffing risk)");
        softAssert.assertNotNull(response.getHeader("Content-Security-Policy"),
                "SECURITY HEADER MISSING: Content-Security-Policy (XSS risk)");

        softAssert.assertAll();
    }
}
