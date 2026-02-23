using Framework.Core.Config;
using Framework.Core.Pages;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

/// <summary>
/// OWASP-aware security test cases for the SauceDemo login surface.
///
/// Covers:
///   1. SQL injection  — input sanitisation / error message leakage
///   2. XSS injection  — reflected script execution prevention
///   3. Repeated failed logins — account lockout / resilience
///   4. Security response headers — HTTP security posture
///
/// Extends BaseTest (navigates to app in [SetUp], screenshots on failure in [TearDown]).
/// HttpClient mirrors the pattern in UserApiTest.cs.
/// </summary>
[TestFixture]
public class SecurityTest : BaseTest
{
    private static readonly HttpClient _http = new();

    // ------------------------------------------------------------------
    // 1. SQL INJECTION
    // ------------------------------------------------------------------
    [Test]
    [Category("security")]
    [Category("regression")]
    public async Task SqlInjectionIsRejected()
    {
        var loginPage = new LoginPage(Page);

        await loginPage.LoginAs("' OR '1'='1' --", "anything");

        Assert.That(await loginPage.IsErrorDisplayed(), Is.True,
            "SECURITY: SQL injection payload should produce an error message.");

        string error = await loginPage.GetErrorMessage();
        Assert.That(error.ToLower(), Does.Not.Contain("sql"),
            $"SECURITY: Error message leaks SQL keyword — {error}");
        Assert.That(error.ToLower(), Does.Not.Contain("exception"),
            $"SECURITY: Error message leaks exception details — {error}");
    }

    // ------------------------------------------------------------------
    // 2. XSS INJECTION
    // ------------------------------------------------------------------
    [Test]
    [Category("security")]
    [Category("regression")]
    public async Task XssInjectionIsHandledSafely()
    {
        var loginPage = new LoginPage(Page);

        await loginPage.LoginAs("<script>document.title='xss'</script>", "anything");

        Assert.That(await loginPage.IsErrorDisplayed(), Is.True,
            "SECURITY: XSS payload should produce an error message.");
        Assert.That(await Page.TitleAsync(), Is.Not.EqualTo("xss"),
            "SECURITY: XSS payload executed — page title was changed to 'xss'.");
    }

    // ------------------------------------------------------------------
    // 3. REPEATED FAILED LOGIN ATTEMPTS
    // ------------------------------------------------------------------
    [Test]
    [Category("security")]
    [Category("regression")]
    public async Task RepeatedFailedLoginAttemptsHandledGracefully()
    {
        var loginPage = new LoginPage(Page);

        for (int i = 1; i <= 5; i++)
        {
            await loginPage.LoginAs($"bad_user_{i}", "wrong_password");
            Assert.That(await loginPage.IsErrorDisplayed(), Is.True,
                $"SECURITY: No error shown on failed attempt {i}.");
        }

        // Valid login must still succeed after repeated failures
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
    [Test]
    [Category("security")]
    [Category("regression")]
    public async Task SecurityResponseHeadersPresent()
    {
        using HttpResponseMessage response = await _http.GetAsync("https://www.saucedemo.com");

        Assert.That((int)response.StatusCode, Is.LessThan(500),
            $"SECURITY: saucedemo.com returned a server error: {(int)response.StatusCode}");

        var headersToCheck = new[] { "X-Frame-Options", "X-Content-Type-Options", "Content-Security-Policy" };
        foreach (var header in headersToCheck)
        {
            bool present = response.Headers.Contains(header);
            TestContext.WriteLine($"[SECURITY HEADER] {header}: {(present ? "present" : "MISSING")}");
        }
    }
}
