using Allure.NUnit.Attributes;
using Framework.Core.Config;
using Framework.Core.Pages;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

[TestFixture]
[AllureSuite("Login")]
public class LoginTest : BaseTest
{
    [Test]
    [Category("smoke")]
    [Retry(1)]
    [AllureFeature("Authentication")]
    [AllureStory("Valid login navigates to inventory")]
    public async Task ValidLogin()
    {
        var loginPage = new LoginPage(Page);
        await loginPage.LoginAs(
            ConfigReader.GetProperty("app:username"),
            ConfigReader.GetProperty("app:password"));

        Assert.That(Page.Url, Does.Contain("inventory"),
            "Should redirect to inventory page after valid login.");
    }

    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Authentication")]
    [AllureStory("Locked-out user sees error message")]
    public async Task LockedOutUser()
    {
        var loginPage = new LoginPage(Page);
        await loginPage.LoginAs(
            ConfigReader.GetProperty("locked_out_username"),
            ConfigReader.GetProperty("app:password"));

        Assert.That(await loginPage.IsErrorDisplayed(), Is.True,
            "Error banner should be visible for locked-out user.");
        Assert.That(await loginPage.GetErrorMessage(),
            Does.Contain("locked out"),
            "Error message should mention 'locked out'.");
    }

    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Authentication")]
    [AllureStory("Empty credentials show validation error")]
    public async Task EmptyCredentials()
    {
        var loginPage = new LoginPage(Page);
        await loginPage.ClickLogin();

        Assert.That(await loginPage.IsErrorDisplayed(), Is.True,
            "Error banner should be visible when submitting empty credentials.");
        Assert.That(await loginPage.GetErrorMessage(),
            Does.Contain("Username is required"),
            "Error should request a username.");
    }
}
