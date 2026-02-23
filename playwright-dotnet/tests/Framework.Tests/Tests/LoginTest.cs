using Allure.NUnit.Attributes;
using Framework.Core.Config;
using Framework.Core.Pages;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

/// <summary>
/// Test class covering the SauceDemo login page scenarios.
///
/// Why these tests matter: Authentication is the gateway to the entire application.
/// If login is broken, no other feature can be tested or used. These tests are
/// therefore high-priority and include both smoke and regression coverage:
///
///   - Smoke: "Does valid login work?" — must pass before any other test can run
///   - Regression: negative paths (locked out user, empty fields) that protect
///     against regressions introduced when developers change the login logic
///
/// [AllureSuite("Login")]: Groups all tests in this class under a "Login" suite
/// in the Allure HTML report, making results easy to filter and read.
///
/// Extends BaseTest (not AuthenticatedTest) because the login page tests are the
/// ones that actually test the login process — they cannot start already logged in.
/// </summary>
[TestFixture]
[AllureSuite("Login")]
public class LoginTest : BaseTest
{
    /// <summary>
    /// Smoke test: verifies that a valid username and password successfully
    /// authenticate and redirect the user to the inventory page.
    ///
    /// This is the most critical test in the suite — if it fails, the application
    /// is fundamentally broken and all other tests will fail too.
    ///
    /// [Category("smoke")]: marks this as part of the fast smoke suite that runs
    /// after every deployment to verify the app is alive.
    /// [Retry(1)]: if the test fails once (e.g., due to a transient network issue
    /// in CI), NUnit will automatically re-run it one time before reporting failure.
    ///
    /// Allure attributes ([AllureFeature], [AllureStory]) create a hierarchical
    /// structure in the Allure report: Suite → Feature → Story, mirroring
    /// the way product managers write user stories.
    /// </summary>
    [Test]
    [Category("smoke")]
    [Retry(1)]
    [AllureFeature("Authentication")]
    [AllureStory("Valid login navigates to inventory")]
    public async Task ValidLogin()
    {
        // Instantiate the LoginPage object, binding it to the IPage for this test.
        var loginPage = new LoginPage(Page);

        // Perform login using credentials from appsettings.json (or environment variables).
        // Reading credentials from config means this test works against any environment
        // without hardcoded values.
        await loginPage.LoginAs(
            ConfigReader.GetProperty("app:username"),
            ConfigReader.GetProperty("app:password"));

        // Assert: the URL should now contain "inventory" — confirming the login
        // was accepted and the app redirected to the products page.
        Assert.That(Page.Url, Does.Contain("inventory"),
            "Should redirect to inventory page after valid login.");
    }

    /// <summary>
    /// Regression test: verifies that a locked-out user account cannot log in and
    /// sees the correct error message.
    ///
    /// SauceDemo provides "locked_out_user" as a built-in test persona specifically
    /// to test this scenario. In a real application, accounts may be locked after
    /// repeated failed login attempts (brute-force protection).
    ///
    /// Two assertions are made:
    ///   1. The error banner is visible (something went wrong is communicated to the user)
    ///   2. The error text contains "locked out" (the message is specific, not generic)
    /// Both assertions are needed — the banner could appear with the wrong message.
    /// </summary>
    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Authentication")]
    [AllureStory("Locked-out user sees error message")]
    public async Task LockedOutUser()
    {
        var loginPage = new LoginPage(Page);

        // Use the "locked_out_username" config key — defaults to "locked_out_user"
        // (the SauceDemo built-in persona) if not explicitly set.
        await loginPage.LoginAs(
            ConfigReader.GetProperty("locked_out_username"),
            ConfigReader.GetProperty("app:password"));

        // Assert 1: the error banner must be visible after a failed login attempt.
        Assert.That(await loginPage.IsErrorDisplayed(), Is.True,
            "Error banner should be visible for locked-out user.");

        // Assert 2: the error text must specifically mention "locked out".
        // Does.Contain is case-insensitive in NUnit, matching both "locked out" and "Locked Out".
        Assert.That(await loginPage.GetErrorMessage(),
            Does.Contain("locked out"),
            "Error message should mention 'locked out'.");
    }

    /// <summary>
    /// Regression test: verifies that submitting the login form with no credentials
    /// displays a field-level validation error.
    ///
    /// Why test empty credentials: security best practice requires that authentication
    /// forms reject empty input with a clear, actionable message rather than crashing
    /// or silently failing. This test catches regressions where client-side validation
    /// is accidentally removed during a UI refactor.
    ///
    /// Only ClickLogin() is called (no username/password entry) to simulate a user
    /// who clicks "Login" immediately without filling in the form.
    /// </summary>
    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Authentication")]
    [AllureStory("Empty credentials show validation error")]
    public async Task EmptyCredentials()
    {
        var loginPage = new LoginPage(Page);

        // Submit the form without entering any credentials.
        await loginPage.ClickLogin();

        // Assert 1: an error banner must appear (the form was not accepted).
        Assert.That(await loginPage.IsErrorDisplayed(), Is.True,
            "Error banner should be visible when submitting empty credentials.");

        // Assert 2: the error must specifically ask for a username — confirming
        // field-level validation is active and the message is meaningful.
        Assert.That(await loginPage.GetErrorMessage(),
            Does.Contain("Username is required"),
            "Error should request a username.");
    }
}
