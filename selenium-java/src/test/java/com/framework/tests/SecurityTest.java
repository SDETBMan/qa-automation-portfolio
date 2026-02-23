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
 * <p>WHY SECURITY TESTS IN A QA AUTOMATION PORTFOLIO: Application security is a shared
 * responsibility between developers and QA engineers. SDETs are increasingly expected
 * to cover OWASP Top 10 vulnerabilities at the functional test level. Including
 * security scenarios demonstrates awareness of threats beyond typical happy-path
 * and negative-path UI testing, and catches regressions before they reach production.
 *
 * <p>WHAT THE OWASP TOP 10 IS: The Open Web Application Security Project publishes a
 * list of the 10 most critical security risks to web applications. This class covers
 * three of them:
 * <ul>
 *   <li><b>A03 Injection</b> (SQL injection, XSS): attackers embed malicious code in
 *       user inputs hoping the app will execute it.</li>
 *   <li><b>A05 Security Misconfiguration</b> (response headers): missing HTTP security
 *       headers leave browsers unprotected against clickjacking and content injection.</li>
 *   <li><b>A07 Identification and Authentication Failures</b> (brute force): weak
 *       authentication handling allows attackers to guess passwords at scale.</li>
 * </ul>
 *
 * <p>WHAT THIS CLASS COVERS:
 * <ol>
 *   <li>SQL injection — verifies the app rejects SQL payloads and does NOT leak
 *       internal database error details in the error message.</li>
 *   <li>XSS injection — verifies that a JavaScript payload in the username field
 *       is not executed by the browser (page title must not change to "xss").</li>
 *   <li>Repeated failed logins — verifies the app handles 5 consecutive bad attempts
 *       gracefully and still allows a valid login after failures.</li>
 *   <li>Security response headers — checks for X-Frame-Options, X-Content-Type-Options,
 *       and Content-Security-Policy headers via a raw HTTP GET (not the browser).</li>
 * </ol>
 *
 * <p>NOTE ON HEADER TEST: SauceDemo is a public demo site not under our control.
 * The header check logs results rather than asserting, because the site's header
 * configuration may change and failing CI over a demo site's missing header is not
 * appropriate. In real projects, these would be hard assertions against your own server.
 *
 * <p>Reuses {@link BaseTest} setUp/tearDown and {@link LoginPage} page object.
 * RestAssured is already a pom.xml dependency (used in UserApiTest).
 */
public class SecurityTest extends BaseTest {

    // ------------------------------------------------------------------
    // 1. SQL INJECTION
    // ------------------------------------------------------------------

    /**
     * testSqlInjectionIsRejected: Verifies that a classic SQL injection payload
     * in the username field is rejected and does not leak internal error details.
     *
     * <p>WHAT SQL INJECTION IS (OWASP A03): When a backend builds database queries
     * by concatenating user input directly into SQL strings (bad practice), an
     * attacker can embed SQL syntax to manipulate the query. The payload
     * {@code ' OR '1'='1' --} closes the username string, adds an always-true condition,
     * and comments out the password check — potentially granting access without credentials.
     *
     * <p>TWO LAYERS OF ASSERTION:
     * <ol>
     *   <li>An error banner must appear — the payload was NOT accepted as valid login.</li>
     *   <li>The error message must NOT contain "sql" or "exception" — the app must not
     *       leak implementation details. A message like "MySqlException: syntax error near
     *       '1'='1'" tells an attacker which database is running and confirms the injection
     *       is close to working — a critical information disclosure vulnerability.</li>
     * </ol>
     *
     * <p>.toLowerCase() normalises the error text before checking, so the assertions
     * catch "SQL" and "sql" and "Exception" and "exception" equally.
     */
    @Test(groups = {"security", "regression", "web"})
    public void testSqlInjectionIsRejected() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        // Enter a classic SQL injection payload as the username.
        // A correctly parameterised backend treats this as a literal string and rejects it.
        // A vulnerable backend might execute it and bypass authentication.
        loginPage.login("' OR '1'='1' --", "anything");

        // Read the error message that should have appeared after the failed login.
        String error = loginPage.getErrorMessage();

        // ASSERTION 1: an error message must be displayed — the injection must not grant access.
        Assert.assertFalse(error.isEmpty(),
                "SECURITY: SQL injection payload did not produce an error message.");

        // ASSERTION 2: the error message must not contain SQL keywords.
        // Lowercase normalisation ensures "SQL", "Sql", and "sql" are all caught.
        Assert.assertFalse(error.toLowerCase().contains("sql"),
                "SECURITY: Error message leaks SQL keyword — " + error);

        // ASSERTION 3: the error message must not contain "exception".
        // A Java/server exception being surfaced reveals application internals to attackers.
        Assert.assertFalse(error.toLowerCase().contains("exception"),
                "SECURITY: Error message leaks exception details — " + error);
    }

    // ------------------------------------------------------------------
    // 2. XSS INJECTION
    // ------------------------------------------------------------------

    /**
     * testXssInjectionIsHandledSafely: Verifies that a Cross-Site Scripting payload
     * entered in the username field is not executed by the browser.
     *
     * <p>WHAT XSS IS (OWASP A03/A07): Cross-Site Scripting attacks inject JavaScript
     * into a page. If the app reflects user input back into the rendered HTML without
     * encoding it, the browser executes the embedded script. Real-world XSS attacks
     * steal session cookies, redirect users to phishing pages, or perform actions on
     * behalf of the user — one of the most common and damaging web vulnerabilities.
     *
     * <p>HOW THE TEST DETECTS XSS: The payload {@code <script>document.title='xss'</script>}
     * attempts to change the browser's page title to "xss" via JavaScript. If the app
     * sanitises the input (encodes {@code <} and {@code >} as HTML entities), the script
     * tag is rendered as harmless text and the title stays unchanged. If the title IS
     * "xss" after the login attempt, the script executed — XSS confirmed.
     *
     * <p>WHY THE TITLE CHECK IS THE KEY ASSERTION: The title change is an observable,
     * side-effect-free indicator of script execution that doesn't require checking
     * network traffic or inspecting the DOM source.
     */
    @Test(groups = {"security", "regression", "web"})
    public void testXssInjectionIsHandledSafely() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        // Enter an XSS payload as the username.
        // If rendered unencoded in the page HTML, the script tag would execute.
        loginPage.login("<script>document.title='xss'</script>", "anything");

        // The login must be rejected — an error banner confirms the payload was not accepted.
        String error = loginPage.getErrorMessage();
        Assert.assertFalse(error.isEmpty(),
                "SECURITY: XSS payload did not produce an error message.");

        // Critical check: if the title changed to "xss", the script was executed.
        // The title not changing confirms the input was properly sanitised/encoded
        // before being rendered in the page HTML.
        Assert.assertNotEquals(DriverManager.getDriver().getTitle(), "xss",
                "SECURITY: XSS payload executed — page title was changed to 'xss'.");
    }

    // ------------------------------------------------------------------
    // 3. REPEATED FAILED LOGIN ATTEMPTS
    // ------------------------------------------------------------------

    /**
     * testRepeatedFailedLoginAttempts: Verifies that the application handles
     * 5 consecutive failed login attempts gracefully and still allows a valid
     * login to succeed after those failures.
     *
     * <p>WHAT BRUTE FORCE PROTECTION IS (OWASP A07): Attackers try thousands of
     * username/password combinations to guess credentials. Proper defences include
     * rate limiting (slow down responses after N failures) and account lockout
     * (block the account after N failures for the same username). This test validates
     * two complementary properties:
     * <ol>
     *   <li><b>Resilience</b> — the app does not crash or expose internals after
     *       5 consecutive failures (would indicate insufficient error handling).</li>
     *   <li><b>No over-aggressive lockout</b> — the valid account can still log in
     *       after 5 failures using DIFFERENT bad usernames. The failures used
     *       bad_user_1 through bad_user_5, so the valid "standard_user" account
     *       should not be locked out.</li>
     * </ol>
     *
     * <p>WHY DIFFERENT BAD USERNAMES: Using the same bad username repeatedly would
     * test per-username lockout (a feature, not a bug, when applied correctly).
     * Using different usernames tests application resilience without triggering
     * intentional lockout behaviour.
     */
    @Test(groups = {"security", "regression", "web"})
    public void testRepeatedFailedLoginAttempts() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        // Attempt login 5 times with different invalid username/password combinations.
        // Using unique usernames (bad_user_1 through bad_user_5) avoids triggering
        // SauceDemo's intentional per-username lockout for the "locked_out_user" persona.
        for (int i = 1; i <= 5; i++) {
            loginPage.login("bad_user_" + i, "wrong_password");

            // Each failed attempt must produce an error — the app must not silently
            // accept bad credentials or navigate away from the login page.
            Assert.assertFalse(loginPage.getErrorMessage().isEmpty(),
                    "SECURITY: No error shown on failed attempt " + i);
        }

        // After 5 failures with different bad usernames, the valid account must still work.
        // A locked-out valid user here would indicate the lockout logic is too aggressive —
        // locking accounts based on IP or overall failure count rather than per-username.
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

    /**
     * testSecurityResponseHeaders: Checks which HTTP security response headers
     * are present on the target site and logs the findings to test output.
     *
     * <p>WHAT HTTP SECURITY HEADERS ARE (OWASP A05): HTTP security headers are
     * browser-side controls configured on the server. Key headers:
     * <ul>
     *   <li><b>X-Frame-Options: DENY</b> — prevents clickjacking attacks where an
     *       attacker embeds the site in an invisible iframe to trick users into
     *       clicking things they didn't intend to click.</li>
     *   <li><b>X-Content-Type-Options: nosniff</b> — prevents MIME type sniffing,
     *       where a browser might interpret an uploaded image file as JavaScript
     *       and execute it.</li>
     *   <li><b>Content-Security-Policy</b> — an allowlist of permitted content
     *       sources. A strong CSP is one of the most effective defences against XSS.</li>
     * </ul>
     *
     * <p>WHY LOG INSTEAD OF ASSERT: SauceDemo is a third-party demo site managed by
     * Sauce Labs. Its header configuration is outside our control and could change
     * at any time. Using {@code System.out.println()} records findings in the build
     * log without causing a CI failure. In a real project testing your own server,
     * these would be hard {@code Assert.assertTrue()} checks.
     *
     * <p>WHY RESTASSURED (NOT THE BROWSER): Security response headers are part of
     * the HTTP layer, not the rendered page. Selenium/WebDriver doesn't expose raw
     * HTTP response headers. RestAssured sends a standalone HTTP GET request, which
     * returns the full response including all headers, independent of the browser.
     */
    @Test(groups = {"security", "regression", "web"})
    public void testSecurityResponseHeaders() {
        // Send a raw HTTP GET to the target site — bypasses the browser so we can
        // inspect the actual HTTP response headers returned by the server.
        Response response = RestAssured.get("https://www.saucedemo.com");

        // Hard assertion: the site must at least be reachable and not returning
        // a 5xx server error. If this fails, the site is broken, not just missing headers.
        Assert.assertTrue(response.getStatusCode() < 500,
                "SECURITY: saucedemo.com returned a server error: " + response.getStatusCode());

        // For each recommended security header, log whether it is present or missing.
        // This documents the site's security posture in the CI build log without
        // failing the build for headers on a demo site we don't control.
        String[] headersToCheck = {"X-Frame-Options", "X-Content-Type-Options", "Content-Security-Policy"};
        for (String header : headersToCheck) {
            String value = response.getHeader(header);
            System.out.println("[SECURITY HEADER] " + header + ": " + (value != null ? "present" : "MISSING"));
        }
    }
}
