using Framework.Core.Config;
using Framework.Core.Pages;

namespace Framework.Tests.Base;

/// <summary>
/// Fixture base class that provides a pre-authenticated browser session to every
/// test that extends it.
///
/// Why this exists: Many tests verify features that are only accessible after login
/// (product inventory, cart, checkout). Without this class, every such test would
/// need to repeat the same login steps, which creates noise and slows the suite down.
/// By inheriting AuthenticatedTest, a test class gets login "for free" — each test
/// starts already on inventory.html with a valid session.
///
/// How the NUnit [SetUp] chain works:
///   NUnit calls all [SetUp] methods in the inheritance hierarchy, from the topmost
///   base class down to the most derived class. The execution order is:
///     1. BaseTest.NavigateToApp()  — navigates to the login URL and starts tracing
///     2. AuthenticatedTest.LoginBeforeEach() — fills credentials and submits the form
///   By the time any test method runs, the browser is on inventory.html.
///
/// Equivalent pattern in TypeScript/Playwright:
///   This mirrors the "authenticatedPage" fixture defined with test.extend() in
///   fixtures.ts. Instead of a fixture function, C# NUnit uses class inheritance
///   and [SetUp] methods to achieve the same "setup → test → teardown" lifecycle.
///
/// Protected properties: LoginPage and InventoryPage are exposed as protected properties
/// so subclass test methods can use them directly (e.g., "await InventoryPage.AddItemToCart(...)").
/// They are null! at field-declaration time but are guaranteed to be set before any test
/// runs because LoginBeforeEach is always called first.
/// </summary>
public abstract class AuthenticatedTest : BaseTest
{
    // Page object instances available to all tests that inherit this class.
    // "null!" (null-forgiving operator) tells the compiler "I know this is null now
    // but I guarantee it will be set before first use" — avoiding a false warning.
    protected LoginPage LoginPage { get; private set; } = null!;
    protected InventoryPage InventoryPage { get; private set; } = null!;

    /// <summary>
    /// Runs after BaseTest.NavigateToApp() for each test in subclasses.
    /// Creates the page object instances for the current test's IPage and performs
    /// a complete login using credentials from configuration.
    ///
    /// The assertion at the end is a "fixture guard" — it verifies the login actually
    /// succeeded before the real test logic begins. Without this guard, a credential
    /// misconfiguration would cause every test to fail with a confusing
    /// "element not found on inventory page" error instead of a clear "login failed" message.
    ///
    /// Credentials are read from config (appsettings.json or environment variables),
    /// allowing different environments to use different accounts without code changes.
    /// </summary>
    [SetUp]
    public async Task LoginBeforeEach()
    {
        // Instantiate page objects bound to the current test's Page instance.
        // A new IPage is provided by PageTest for every test, so these must be
        // created fresh each time rather than sharing instances across tests.
        LoginPage     = new LoginPage(Page);
        InventoryPage = new InventoryPage(Page);

        // Perform the login using credentials from appsettings.json or environment variables.
        // The default values ("standard_user" / "secret_sauce") match the SauceDemo demo site
        // and act as a safe fallback when config keys are not explicitly set.
        await LoginPage.LoginAs(
            ConfigReader.GetProperty("app:username", "standard_user"),
            ConfigReader.GetProperty("app:password", "secret_sauce"));

        // Fixture guard: surface credential failures immediately rather than
        // letting each test fail with a confusing "element not found" error.
        // If this assertion fails, the test reports "Login did not reach inventory"
        // which immediately tells the engineer to check credentials and config.
        Assert.That(Page.Url, Does.Contain("inventory"),
            "AuthenticatedTest: Login did not reach inventory. Check credentials.");
    }
}
