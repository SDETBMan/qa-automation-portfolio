using Allure.NUnit.Attributes;
using Framework.Core.Config;
using Framework.Core.Pages;
using Framework.Core.Utils;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

[TestFixture]
[AllureSuite("AiDriven")]
public class AiDrivenTest : BaseTest
{
    [Test]
    [Category("ai")]
    [AllureFeature("AI")]
    [AllureStory("Login with AI-generated credentials")]
    public async Task TestLoginWithAiGeneratedData()
    {
        string prompt = "Provide a valid SauceDemo username and password in this exact format: " +
                        "username=<value> password=<value>. " +
                        "Use: standard_user / secret_sauce";

        string aiResponse = await AiHelper.AskAsync(prompt);
        Console.WriteLine($"[AiDrivenTest] AI response: {aiResponse}");

        // Fall back to config credentials when AI is unavailable.
        // Only parse a real AI response (one that does NOT start with the "[AiHelper]" prefix).
        string username = ConfigReader.GetProperty("app:username", "standard_user");
        string password = ConfigReader.GetProperty("app:password", "secret_sauce");

        if (!aiResponse.StartsWith("[AiHelper]") &&
            aiResponse.Contains("username=") && aiResponse.Contains("password="))
        {
            foreach (string part in aiResponse.Split(' ', '\n', StringSplitOptions.RemoveEmptyEntries))
            {
                if (part.StartsWith("username=", StringComparison.OrdinalIgnoreCase))
                    username = part.Split('=', 2)[1].Trim();
                if (part.StartsWith("password=", StringComparison.OrdinalIgnoreCase))
                    password = part.Split('=', 2)[1].Trim();
            }
        }

        var loginPage = new LoginPage(Page);
        await loginPage.LoginAs(username, password);

        Assert.That(Page.Url, Does.Contain("inventory"),
            "Should reach the inventory page with AI-suggested credentials.");
    }
}
