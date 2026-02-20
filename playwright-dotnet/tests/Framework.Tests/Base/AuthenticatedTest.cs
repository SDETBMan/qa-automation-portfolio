using Framework.Core.Config;
using Framework.Core.Pages;

namespace Framework.Tests.Base;

/// <summary>
/// Fixture base class: provides pre-authenticated IPage + page objects.
/// NUnit [SetUp] chain: BaseTest.NavigateToApp() → AuthenticatedTest.LoginBeforeEach()
/// Tests inheriting this class begin already on inventory.html with no login code.
///
/// C# equivalent of TypeScript's authenticatedPage fixture (test.extend).
/// The setup/teardown lifecycle maps directly:
///   TypeScript: async ({ page }, use) => { /* setup */ await use(po); /* teardown */ }
///   C# NUnit:   [SetUp] LoginBeforeEach() runs after BaseTest.NavigateToApp() in the [SetUp] chain.
/// </summary>
public abstract class AuthenticatedTest : BaseTest
{
    protected LoginPage LoginPage { get; private set; } = null!;
    protected InventoryPage InventoryPage { get; private set; } = null!;

    [SetUp]
    public async Task LoginBeforeEach()
    {
        LoginPage     = new LoginPage(Page);
        InventoryPage = new InventoryPage(Page);

        await LoginPage.LoginAs(
            ConfigReader.GetProperty("app:username", "standard_user"),
            ConfigReader.GetProperty("app:password", "secret_sauce"));

        // Fixture guard: surface credential failures immediately rather than
        // letting each test fail with a confusing "element not found" error.
        Assert.That(Page.Url, Does.Contain("inventory"),
            "AuthenticatedTest: Login did not reach inventory. Check credentials.");
    }
}
