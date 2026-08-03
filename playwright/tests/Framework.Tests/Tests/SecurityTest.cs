using Framework.Core.Config;
using Framework.Core.Pages;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

/// <summary>
/// OWASP-aware security test cases for the SauceDemo login surface.
///
/// Why security tests in a QA automation portfolio: Security testing is a core
/// SDET responsibility, not just a penetration tester's job. Automated security
/// checks integrated into the CI pipeline catch regressions before they reach
/// production. This class demonstrates awareness of the OWASP Top 10 — the
/// industry-standard list of critical web application security risks.
///
/// Scenarios covered:
///
///   1. SQL Injection (OWASP A03: Injection):
///      Attackers try to manipulate database queries by embedding SQL syntax in
///      form fields. The test verifies the app rejects the payload AND does not
///      leak internal error details (stack traces, SQL keywords) in the response.
///
///   2. Cross-Site Scripting / XSS (OWASP A03: Injection):
///      Attackers embed JavaScript in form inputs hoping the browser will execute it.
///      The test verifies the script was NOT executed (page title unchanged).
///
///   3. Brute-Force Resilience (OWASP A07: Identification and Authentication Failures):
///      Attackers try thousands of passwords to guess credentials. The test verifies
///      the app handles repeated failures gracefully and still allows valid logins
///      after failed attempts (ensuring legitimate users are not locked out unfairly).
///
///   4. Security Response Headers (OWASP A05: Security Misconfiguration):
///      HTTP headers like X-Frame-Options and Content-Security-Policy tell browsers
///      how to protect the page from clickjacking, MIME sniffing, and other attacks.
///      The test documents which headers are present/missing on the target site.
///
/// Note on test assertions:
///   SauceDemo is a public demo site not under our control. The header check (test 4)
///   logs results rather than asserting, because the site's header configuration may
///   change and failing CI over a demo site's missing header is not appropriate.
///   In real projects, these would be hard assertions against your own application.
///
/// Extends BaseTest (navigates to app in [SetUp], screenshots on failure in [TearDown]).
/// HttpClient is created once at the class level for the HTTP-based header check test.
/// </summary>
[TestFixture]
public class SecurityTest : BaseTest
{
    // A single HttpClient instance shared across all tests in this class.
    // Used for the HTTP header check which requires a raw HTTP response, not a browser page.
    private static readonly HttpClient _http = new();

    // ------------------------------------------------------------------
    // 1. SQL INJECTION
    // ------------------------------------------------------------------

    /// <summary>
    /// Security test: verifies that SQL injection payloads in the username field
    /// are rejected, and that the error response does not leak internal implementation
    /// details like SQL keywords or exception stack traces.
    ///
    /// The classic payload "' OR '1'='1' --" attempts to comment out the password
    /// check in a SQL query. If the backend constructs queries via string concatenation
    /// (bad practice), this could bypass authentication entirely.
    ///
    /// Two assertions guard against two different failure modes:
    ///   1. The error banner must appear — the payload was not accepted
    ///   2. The error text must not contain "sql" or "exception" — no internal
    ///      implementation details are exposed to the attacker
    ///
    /// Why test for error leakage: an error message like "MySqlException: syntax error
    /// near '1'='1'" tells an attacker exactly which database is in use and confirms
    /// the injection is almost working — a critical information disclosure vulnerability.
    /// </summary>
    [Test]
    [Category("security")]
    [Category("regression")]
    public async Task SqlInjectionIsRejected()
    {
        var loginPage = new LoginPage(Page);

        // Enter a classic SQL injection payload as the username.
        await loginPage.LoginAs("' OR '1'='1' --", "anything");

        // The injection payload must not grant access — an error must appear.
        Assert.That(await loginPage.IsErrorDisplayed(), Is.True,
            "SECURITY: SQL injection payload should produce an error message.");

        // Read the error message and verify it contains no SQL or exception keywords.
        string error = await loginPage.GetErrorMessage();

        // .ToLower() normalises the case before checking for the keyword.
        Assert.That(error.ToLower(), Does.Not.Contain("sql"),
            $"SECURITY: Error message leaks SQL keyword — {error}");
        Assert.That(error.ToLower(), Does.Not.Contain("exception"),
            $"SECURITY: Error message leaks exception details — {error}");
    }

    // ------------------------------------------------------------------
    // 2. XSS INJECTION
    // ------------------------------------------------------------------

    /// <summary>
    /// Security test: verifies that a cross-site scripting (XSS) payload entered
    /// in the username field is not executed by the browser.
    ///
    /// The test payload attempts to change the page title to "xss" via JavaScript.
    /// If the app reflects the input unsanitised back into the page HTML, the browser
    /// executes the script and the title changes — confirming the XSS vulnerability.
    ///
    /// The assertion checks the page title AFTER the login attempt. If the title is
    /// still the original value (not "xss"), the script was not executed, meaning
    /// the input was properly sanitised or encoded before being rendered.
    ///
    /// Real-world impact of XSS: attackers can steal session cookies, redirect users
    /// to phishing pages, or perform actions on behalf of the user — one of the most
    /// common and damaging web vulnerabilities.
    /// </summary>
    [Test]
    [Category("security")]
    [Category("regression")]
    public async Task XssInjectionIsHandledSafely()
    {
        var loginPage = new LoginPage(Page);

        // Enter a script tag as the username — if rendered unencoded this executes in the browser.
        await loginPage.LoginAs("<script>document.title='xss'</script>", "anything");

        // The payload must produce an error (login rejected).
        Assert.That(await loginPage.IsErrorDisplayed(), Is.True,
            "SECURITY: XSS payload should produce an error message.");

        // Critical check: if the title changed to "xss" the script was executed — XSS confirmed.
        Assert.That(await Page.TitleAsync(), Is.Not.EqualTo("xss"),
            "SECURITY: XSS payload executed — page title was changed to 'xss'.");
    }

    // ------------------------------------------------------------------
    // 3. REPEATED FAILED LOGIN ATTEMPTS
    // ------------------------------------------------------------------

    /// <summary>
    /// Security test: verifies that the application handles repeated failed login
    /// attempts gracefully without crashing, and that a valid login still succeeds
    /// after multiple failures.
    ///
    /// This test checks two security properties simultaneously:
    ///   1. Resilience: the app does not crash, hang, or expose error details after
    ///      5 consecutive failed attempts (would indicate insufficient error handling)
    ///   2. No over-aggressive lockout: the valid user account can still log in after
    ///      5 failures with different usernames (the failures used different bad_user_N
    ///      usernames, so the valid account should not be locked)
    ///
    /// In real applications this test would be adapted to also verify rate limiting
    /// (the app slows down responses after repeated failures) and account lockout
    /// (after N failures with the SAME username, the account is locked — a feature,
    /// not a bug, when applied correctly).
    /// </summary>
    [Test]
    [Category("security")]
    [Category("regression")]
    public async Task RepeatedFailedLoginAttemptsHandledGracefully()
    {
        var loginPage = new LoginPage(Page);

        // Attempt login with 5 different invalid username/password combinations.
        // Each iteration uses a unique username to avoid triggering SauceDemo's
        // per-username lockout (locked_out_user is a special built-in persona).
        for (int i = 1; i <= 5; i++)
        {
            await loginPage.LoginAs($"bad_user_{i}", "wrong_password");

            // Each failed attempt must produce an error banner — the app must not silently
            // accept bad credentials or return a different page.
            Assert.That(await loginPage.IsErrorDisplayed(), Is.True,
                $"SECURITY: No error shown on failed attempt {i}.");
        }

        // After 5 failures, a valid login must still succeed.
        // This confirms the repeated bad attempts did not lock out the valid account.
        await loginPage.LoginAs(
            ConfigReader.GetProperty("app:username", "standard_user"),
            ConfigReader.GetProperty("app:password", "secret_sauce"));

        Assert.That(Page.Url, Does.Contain("inventory"),
            "SECURITY: Valid login failed after repeated bad attempts — possible account lockout.");
    }

    // ------------------------------------------------------------------
    // 4. SECURITY RESPONSE HEADERS
    // saucedemo.com is a demo site we do not control — headers are logged
    // rather than asserted so this test documents posture without blocking CI.
    // ------------------------------------------------------------------

    /// <summary>
    /// Security audit test: checks which HTTP security response headers are present
    /// on the target site and logs the findings to the test output.
    ///
    /// HTTP security headers are browser-side security controls. Key headers:
    ///   X-Frame-Options: DENY           — prevents clickjacking (embedding the page in an iframe)
    ///   X-Content-Type-Options: nosniff — prevents MIME type sniffing attacks
    ///   Content-Security-Policy         — allowlist of permitted content sources (XSS mitigation)
    ///
    /// Why log rather than assert: SauceDemo is a third-party demo site. Its header
    /// configuration may change at any time and is outside our control. Using
    /// TestContext.WriteLine() records the header status in the test report without
    /// causing a CI failure when SauceDemo is missing a header.
    ///
    /// In a real project testing your own application, these should be hard assertions:
    ///   Assert.That(response.Headers.Contains("X-Frame-Options"), Is.True, "...");
    ///
    /// This test uses HttpClient directly (not a browser page) because security headers
    /// are part of the HTTP response layer, not the rendered page content.
    /// </summary>
    [Test]
    [Category("security")]
    [Category("regression")]
    public async Task SecurityResponseHeadersPresent()
    {
        // Make a direct HTTP GET request to the site — bypasses the browser
        // so we can inspect the raw HTTP response headers.
        using HttpResponseMessage response = await _http.GetAsync("https://www.saucedemo.com");

        // The site must be reachable — a 5xx server error means the site is broken.
        Assert.That((int)response.StatusCode, Is.LessThan(500),
            $"SECURITY: saucedemo.com returned a server error: {(int)response.StatusCode}");

        // Check for each security header and log whether it is present or missing.
        // TestContext.WriteLine writes to the NUnit output visible in CI build logs
        // and the Allure report's "Attachments" section.
        var headersToCheck = new[] { "X-Frame-Options", "X-Content-Type-Options", "Content-Security-Policy" };
        foreach (var header in headersToCheck)
        {
            bool present = response.Headers.Contains(header);
            TestContext.WriteLine($"[SECURITY HEADER] {header}: {(present ? "present" : "MISSING")}");
        }
    }
}
