using Allure.NUnit.Attributes;
using Framework.Core.Config;
using Framework.Core.Pages;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

[TestFixture]
[AllureSuite("Dashboard")]
public class DashboardTest : BaseTest
{
    // ─── Data Provider ────────────────────────────────────────────────────────
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

    [Test]
    [TestCaseSource(nameof(PersonaTestCases))]
    [Category("regression")]
    [AllureFeature("Dashboard")]
    [AllureStory("Data-driven login for multiple personas")]
    public async Task DataDrivenPersonaLogin(string username, string expectedPersona)
    {
        var loginPage     = new LoginPage(Page);
        var dashboardPage = new DashboardPage(Page);

        await loginPage.LoginAs(username, ConfigReader.GetProperty("app:password"));

        Assert.That(await dashboardPage.IsOnDashboard(), Is.True,
            $"Persona '{expectedPersona}' should reach the dashboard.");
        Assert.That(await dashboardPage.GetPageTitle(), Is.EqualTo("Products"),
            "Page title should be 'Products'.");
    }

    [Test]
    [Category("smoke")]
    [Retry(1)]
    [AllureFeature("Dashboard")]
    [AllureStory("Logout returns user to login page")]
    public async Task LogoutFlow()
    {
        var loginPage     = new LoginPage(Page);
        var dashboardPage = new DashboardPage(Page);

        await loginPage.LoginAs(
            ConfigReader.GetProperty("app:username"),
            ConfigReader.GetProperty("app:password"));

        await dashboardPage.Logout();

        Assert.That(await loginPage.IsLoginButtonVisible(), Is.True,
            "Login button should be visible after logout.");
    }

    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Dashboard")]
    [AllureStory("Direct access without login redirects to login")]
    public async Task DirectAccessWithoutLogin()
    {
        await Page.GotoAsync($"{ConfigReader.GetProperty("url")}/inventory.html");

        // Playwright auto-waits; check URL or error element
        bool onLogin = Page.Url.Contains("saucedemo.com") && !Page.Url.Contains("inventory");
        bool hasError = await Page.Locator("h3[data-test='error']").IsVisibleAsync();

        Assert.That(onLogin || hasError, Is.True,
            "Accessing inventory without login should redirect or show an error.");
    }
}
