package com.framework.tests;

import com.framework.base.BaseTest;
import com.framework.driver.DriverManager;
import com.framework.pages.LoginPage;
import com.framework.utils.ConfigReader;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.testng.Assert;
import org.testng.annotations.Test;

/**
 * SecurityTest: OWASP-aware security test cases for the SauceDemo login surface.
 *
 * Covers:
 *   1. SQL injection — input sanitisation / error message leakage
 *   2. XSS injection — reflected script execution prevention
 *   3. Repeated failed logins — account lockout / resilience
 *   4. Security response headers — HTTP security posture (soft assertions)
 *
 * Reuses BaseTest setUp/tearDown and LoginPage page object.
 * RestAssured is already a pom.xml dependency (used in UserApiTest).
 */
public class SecurityTest extends BaseTest {

    // ------------------------------------------------------------------
    // 1. SQL INJECTION
    // ------------------------------------------------------------------
    @Test(groups = {"security", "regression", "web"})
    public void testSqlInjectionIsRejected() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        loginPage.login("' OR '1'='1' --", "anything");

        String error = loginPage.getErrorMessage();

        Assert.assertFalse(error.isEmpty(),
                "SECURITY: SQL injection payload did not produce an error message.");
        Assert.assertFalse(error.toLowerCase().contains("sql"),
                "SECURITY: Error message leaks SQL keyword — " + error);
        Assert.assertFalse(error.toLowerCase().contains("exception"),
                "SECURITY: Error message leaks exception details — " + error);
    }

    // ------------------------------------------------------------------
    // 2. XSS INJECTION
    // ------------------------------------------------------------------
    @Test(groups = {"security", "regression", "web"})
    public void testXssInjectionIsHandledSafely() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        loginPage.login("<script>document.title='xss'</script>", "anything");

        String error = loginPage.getErrorMessage();

        Assert.assertFalse(error.isEmpty(),
                "SECURITY: XSS payload did not produce an error message.");
        Assert.assertNotEquals(DriverManager.getDriver().getTitle(), "xss",
                "SECURITY: XSS payload executed — page title was changed to 'xss'.");
    }

    // ------------------------------------------------------------------
    // 3. REPEATED FAILED LOGIN ATTEMPTS
    // ------------------------------------------------------------------
    @Test(groups = {"security", "regression", "web"})
    public void testRepeatedFailedLoginAttempts() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        for (int i = 1; i <= 5; i++) {
            loginPage.login("bad_user_" + i, "wrong_password");
            Assert.assertFalse(loginPage.getErrorMessage().isEmpty(),
                    "SECURITY: No error shown on failed attempt " + i);
        }

        // Valid login must still succeed after repeated failures
        loginPage.login(
                ConfigReader.getProperty("app_username"),
                ConfigReader.getProperty("app_password"));

        Assert.assertTrue(DriverManager.getDriver().getCurrentUrl().contains("inventory"),
                "SECURITY: Valid login failed after repeated bad attempts — possible account lockout.");
    }

    // ------------------------------------------------------------------
    // 4. SECURITY RESPONSE HEADERS
    // saucedemo.com is a demo site we do not control — headers are logged
    // rather than asserted so this test documents posture without blocking CI.
    // ------------------------------------------------------------------
    @Test(groups = {"security", "regression", "web"})
    public void testSecurityResponseHeaders() {
        Response response = RestAssured.get("https://www.saucedemo.com");

        Assert.assertTrue(response.getStatusCode() < 500,
                "SECURITY: saucedemo.com returned a server error: " + response.getStatusCode());

        String[] headersToCheck = {"X-Frame-Options", "X-Content-Type-Options", "Content-Security-Policy"};
        for (String header : headersToCheck) {
            String value = response.getHeader(header);
            System.out.println("[SECURITY HEADER] " + header + ": " + (value != null ? "present" : "MISSING"));
        }
    }
}
