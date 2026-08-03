using Allure.NUnit.Attributes;
using Framework.Core.Config;
using Framework.Core.Pages;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

/// <summary>
/// Test class covering the SauceDemo dashboard (inventory page) scenarios.
///
/// Demonstrates two advanced testing techniques used in professional QA frameworks:
///
/// 1. Data-Driven Testing (DataDrivenPersonaLogin):
///    The same test logic runs multiple times, once for each "persona" (user type).
///    SauceDemo ships with pre-built test personas (standard_user, problem_user,
///    performance_glitch_user) that exhibit different behaviours. Running the same
///    login-and-check test against all three verifies the app works for every user
///    type without writing three separate test methods.
///    This pattern scales well — to add a new persona, add one line to PersonaTestCases().
///
/// 2. Negative/Security test (DirectAccessWithoutLogin):
///    Directly navigating to a protected URL without a session should be blocked.
///    This is an important security verification that ensures the app enforces
///    authentication on all protected routes, not just the happy path.
///
/// [AllureSuite("Dashboard")]: groups these tests under "Dashboard" in Allure reports.
/// Extends BaseTest — tests in this class handle their own login setup because different
/// tests use different personas. AuthenticatedTest would lock them into a single user.
/// </summary>
[TestFixture]
[AllureSuite("Dashboard")]
public class DashboardTest : BaseTest
{
    // ─── Data Provider ────────────────────────────────────────────────────────

    /// <summary>
    /// Provides the test data rows for the data-driven persona login test.
    /// Returns one TestCaseData per persona; each row becomes a separate named test run.
    ///
    /// IEnumerable + yield return: this is a C# "iterator method" — it produces items
    /// one at a time as NUnit requests them, rather than building the whole list upfront.
    /// For small datasets (like 3 personas) this makes no performance difference, but
    /// it is the idiomatic NUnit pattern for [TestCaseSource].
    ///
    /// TestCaseData.SetName() gives each run a readable name in the test output:
    /// "DataDriven_Standard", "DataDriven_Problem", "DataDriven_Performance".
    /// Without SetName, NUnit auto-generates names from the parameter values.
    ///
    /// ConfigReader.GetProperty with a default: if the config key is not set, the
    /// default persona name is used directly, so the data provider always returns
    /// valid test cases regardless of environment configuration.
    /// </summary>
    public static IEnumerable<TestCaseData> PersonaTestCases()
    {
        yield return new TestCaseData(
            ConfigReader.GetProperty("persona:standard", "standard_user"),
            "standard_user").SetName("DataDriven_Standard");

        yield return new TestCaseData(
            ConfigReader.GetProperty("persona:problem", "problem_user"),
            "problem_user").SetName("DataDriven_Problem");

        yield return new TestCaseData(
            ConfigReader.GetProperty("persona:performance", "performance_glitch_user"),
            "performance_glitch_user").SetName("DataDriven_Performance");
    }

    // ─── Tests ────────────────────────────────────────────────────────────────

    /// <summary>
    /// Data-driven test: verifies that multiple SauceDemo user personas can all
    /// successfully log in and land on the dashboard with the expected page title.
    ///
    /// [TestCaseSource(nameof(PersonaTestCases))]: tells NUnit to call PersonaTestCases()
    /// to get the data rows. NUnit generates one test run per row returned.
    /// The nameof() operator avoids a magic string — if PersonaTestCases is renamed,
    /// the compiler catches the mismatch instead of failing silently at runtime.
    ///
    /// Parameters:
    ///   username        — the actual username value to type into the login form
    ///   expectedPersona — a human-readable label used in the assertion failure message
    /// </summary>
    [Test]
    [TestCaseSource(nameof(PersonaTestCases))]
    [Category("regression")]
    [AllureFeature("Dashboard")]
    [AllureStory("Data-driven login for multiple personas")]
    public async Task DataDrivenPersonaLogin(string username, string expectedPersona)
    {
        var loginPage     = new LoginPage(Page);
        var dashboardPage = new DashboardPage(Page);

        // All personas share the same password on SauceDemo.
        await loginPage.LoginAs(username, ConfigReader.GetProperty("app:password"));

        // Verify the user reached the dashboard — the URL should contain "inventory".
        Assert.That(await dashboardPage.IsOnDashboard(), Is.True,
            $"Persona '{expectedPersona}' should reach the dashboard.");

        // Verify the page title text — guards against the app loading a blank or error page.
        Assert.That(await dashboardPage.GetPageTitle(), Is.EqualTo("Products"),
            "Page title should be 'Products'.");
    }

    /// <summary>
    /// Smoke test: verifies that a logged-in user can successfully log out and
    /// is returned to the login page.
    ///
    /// Why test logout: logout is a critical security function. If it is broken,
    /// users cannot end their sessions (e.g., on a shared computer), which is a
    /// security vulnerability. It also verifies the sidebar navigation works end-to-end.
    ///
    /// Assertion: checks that the Login button is visible after logout — which confirms
    /// the user is back on the login page and the session was terminated.
    /// </summary>
    [Test]
    [Category("smoke")]
    [Retry(1)]
    [AllureFeature("Dashboard")]
    [AllureStory("Logout returns user to login page")]
    public async Task LogoutFlow()
    {
        var loginPage     = new LoginPage(Page);
        var dashboardPage = new DashboardPage(Page);

        // First, log in so there is a valid session to log out of.
        await loginPage.LoginAs(
            ConfigReader.GetProperty("app:username"),
            ConfigReader.GetProperty("app:password"));

        // Perform logout — this opens the sidebar menu and clicks the logout link.
        await dashboardPage.Logout();

        // After logout the login button must be visible again.
        Assert.That(await loginPage.IsLoginButtonVisible(), Is.True,
            "Login button should be visible after logout.");
    }

    /// <summary>
    /// Regression/security test: verifies that directly navigating to a protected
    /// URL without an active session is blocked by the application.
    ///
    /// Why this matters: Without this protection, anyone who knows the URL could
    /// bypass the login screen entirely and access the app's features. This test
    /// catches accidental removal of the authentication guard.
    ///
    /// Two acceptable outcomes (checked with an OR assertion):
    ///   1. The browser is redirected back to the login page (URL does not contain "inventory")
    ///   2. An error element appears on the page (the app displays an "access denied" message)
    /// Either outcome satisfies the security requirement that unauthenticated access is blocked.
    ///
    /// Note: BaseTest.NavigateToApp() has already navigated to the base URL. This test
    /// then issues a second navigation directly to the protected path.
    /// </summary>
    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Dashboard")]
    [AllureStory("Direct access without login redirects to login")]
    public async Task DirectAccessWithoutLogin()
    {
        // Navigate directly to the protected inventory URL without logging in.
        await Page.GotoAsync($"{ConfigReader.GetProperty("url")}/inventory.html");

        // Playwright auto-waits; check URL or error element
        // Check 1: the URL does not contain "inventory" (redirect occurred).
        bool onLogin = Page.Url.Contains("saucedemo.com") && !Page.Url.Contains("inventory");

        // Check 2: an error element is visible on the page (access denied message).
        bool hasError = await Page.Locator("h3[data-test='error']").IsVisibleAsync();

        // Either a redirect or an error message satisfies the access-control requirement.
        Assert.That(onLogin || hasError, Is.True,
            "Accessing inventory without login should redirect or show an error.");
    }
}
