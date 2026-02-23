package com.saucedemo.stepDefinitions;

import com.saucedemo.utils.DriverManager;
import io.cucumber.java.en.Then;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.openqa.selenium.By;
import org.testng.Assert;

/**
 * SecuritySteps: Cucumber step definitions for OWASP-aware security test scenarios.
 *
 * <p>WHY SECURITY STEPS IN A QA PORTFOLIO: Application security is a shared
 * responsibility between developers and QA engineers. SDETs are increasingly expected
 * to cover OWASP Top 10 vulnerabilities at the functional test level. Including
 * security scenarios demonstrates awareness of threats beyond typical happy-path
 * and negative-path UI testing.
 *
 * <p>WHAT THIS CLASS COVERS:
 * <ul>
 *   <li><b>SQL Injection</b>: verifies that injecting SQL keywords into the login form
 *       does not cause the app to leak internal database error details.</li>
 *   <li><b>XSS (Cross-Site Scripting)</b>: verifies that injecting a JavaScript payload
 *       into the login form does not execute in the browser (i.e., the payload is
 *       treated as literal text, not code).</li>
 *   <li><b>Security Response Headers</b>: checks for the presence of HTTP headers that
 *       protect users from clickjacking, MIME sniffing, and content injection attacks.</li>
 * </ul>
 *
 * <p>STEP REUSE: The SQL injection and XSS scenarios reuse the existing login steps from
 * {@link LoginSteps} to navigate and enter payloads. Only the three assertion steps
 * that are unique to security testing are defined in this class.
 *
 * <p>DEMO SITE LIMITATION: SauceDemo is a controlled demo site, not a live production
 * system. The security header check logs findings rather than hard-asserting on every
 * header because the site's headers are outside the tester's control. The goal is to
 * demonstrate the testing technique, not to gate CI on a third-party demo site's
 * security posture.
 */
public class SecuritySteps {

    /**
     * Locator for the error message element on the login screen.
     * Used to read the error text and verify it does not expose sensitive internals.
     * Declared {@code static final} because it is a constant — the same locator is
     * needed for every security assertion that reads the login error.
     */
    private static final By ERROR_LOCATOR = By.cssSelector("[data-test='error']");

    // ------------------------------------------------------------------
    // Step: error message should not expose system internals
    // Used by: SQL injection scenario
    // ------------------------------------------------------------------

    /**
     * THEN step: Asserts the login error message does not leak internal system details.
     *
     * <p>WHY THIS MATTERS (SQL Injection — OWASP A03:2021): When an application
     * passes user input directly to a database query without sanitisation, an attacker
     * can inject SQL keywords to manipulate the query. A secure application should
     * reject the input and display only a generic error message. A vulnerable application
     * might return an error like "SQL syntax error near 'OR'" or expose a full stack trace,
     * revealing the database technology and query structure to the attacker.
     *
     * <p>This step converts the error text to lowercase before checking, so the
     * assertions catch both "SQL" and "sql" regardless of the application's casing.
     */
    @Then("the error message should not expose system internals")
    public void errorMessageShouldNotExposeSystemInternals() {
        // Read the error text and normalise to lowercase for case-insensitive keyword checks
        String errorText = DriverManager.getDriver()
                .findElement(ERROR_LOCATOR)
                .getText()
                .toLowerCase();

        // Check for SQL keyword leak — a message containing "sql" suggests the database error
        // was passed through directly instead of being wrapped in a safe generic message
        Assert.assertFalse(errorText.contains("sql"),
                "SECURITY: Error message leaks SQL keyword — " + errorText);
        // Check for Java/server exception text — indicates unhandled exceptions are surfaced to users
        Assert.assertFalse(errorText.contains("exception"),
                "SECURITY: Error message leaks exception details — " + errorText);
        // Check for stack trace text — a full stack trace reveals application internals to attackers
        Assert.assertFalse(errorText.contains("stacktrace"),
                "SECURITY: Error message leaks stack trace — " + errorText);
    }

    // ------------------------------------------------------------------
    // Step: the page title should not be {string}
    // Used by: XSS scenario
    // ------------------------------------------------------------------

    /**
     * THEN step: Asserts the browser's page title is NOT the given string.
     *
     * <p>WHY THIS MATTERS (XSS — OWASP A03:2021 / A07:2021): A Cross-Site Scripting
     * attack injects JavaScript into a page. A classic XSS payload is:
     * {@code <script>document.title='XSS'</script>}. If this payload executes in
     * the browser, the document title changes to "XSS". If the application correctly
     * sanitises input (escaping {@code <} and {@code >} as HTML entities), the script
     * tag is rendered as literal text and the title remains unchanged.
     *
     * <p>This step verifies the title was NOT changed to the payload string, confirming
     * the injection was neutralised.
     *
     * @param unexpectedTitle the title value that would indicate successful XSS execution
     */
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
    // saucedemo.com is a demo site we do not control — headers are logged
    // rather than asserted so this step documents posture without blocking CI.

    /**
     * THEN step: Checks for the presence of key security-related HTTP response headers.
     *
     * <p>WHY THESE HEADERS MATTER:
     * <ul>
     *   <li><b>X-Frame-Options</b>: Prevents the site from being embedded in an
     *       {@code <iframe>} on a malicious page, protecting against Clickjacking
     *       attacks (OWASP A05:2021).</li>
     *   <li><b>X-Content-Type-Options</b>: Tells the browser not to try to guess (sniff)
     *       the MIME type of a response — prevents content-sniffing attacks where a
     *       browser might execute a file uploaded as an image but containing JavaScript.</li>
     *   <li><b>Content-Security-Policy</b>: Specifies which sources the browser is
     *       allowed to load scripts, styles, and images from. A strong CSP is one of
     *       the most effective defences against XSS (OWASP A03:2021).</li>
     * </ul>
     *
     * <p>INTENTIONAL SOFT ASSERTION: The step asserts only that the server is reachable
     * (status < 500), then LOGS — rather than hard-asserts — header presence. This is
     * because SauceDemo is a demo site managed by Sauce Labs; whether it sends these
     * headers is outside the tester's control and should not block CI. In a real project
     * where the team controls the server, these would be hard assertions.
     *
     * <p>WHY RESTASSURED HERE: The browser's response headers are not directly accessible
     * via Selenium WebDriver. RestAssured issues a fresh HTTP request to the same URL
     * independently, which allows inspection of the full response headers.
     */
    @Then("the security response headers should be present")
    public void securityResponseHeadersShouldBePresent() {
        // Issue a plain HTTP GET to saucedemo.com to retrieve its response headers
        Response response = RestAssured.get("https://www.saucedemo.com");

        // Hard assert: the site must at least be up (no 5xx server errors)
        Assert.assertTrue(response.getStatusCode() < 500,
                "SECURITY: saucedemo.com returned a server error: " + response.getStatusCode());

        // For each recommended security header, log whether it is present or missing.
        // Logging rather than asserting is appropriate here because we do not control
        // the server; this documents the security posture without blocking CI on a demo site.
        String[] headersToCheck = {"X-Frame-Options", "X-Content-Type-Options", "Content-Security-Policy"};
        for (String header : headersToCheck) {
            String value = response.getHeader(header);
            System.out.println("[SECURITY HEADER] " + header + ": " + (value != null ? "present" : "MISSING"));
        }
    }
}
