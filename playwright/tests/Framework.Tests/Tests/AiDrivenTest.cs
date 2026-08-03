using Allure.NUnit.Attributes;
using Framework.Core.Config;
using Framework.Core.Pages;
using Framework.Core.Utils;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

/// <summary>
/// Demonstrates AI-assisted test data generation integrated with Playwright UI tests.
///
/// Why this exists: AI-driven testing is an emerging practice where large language models
/// (LLMs) generate or suggest test inputs, reducing the effort of writing exhaustive
/// test data sets by hand. This class shows how an SDET can integrate OpenAI's API
/// into the test framework to produce test credentials dynamically.
///
/// The practical value demonstrated here:
///   1. The test asks an LLM to provide valid login credentials in a structured format
///   2. It parses the AI response to extract username and password
///   3. It uses those credentials to perform a real browser login
///   4. Crucially, it falls back to config-based credentials when the AI is unavailable
///      (no API key, quota exceeded, network error) — ensuring the test always runs
///
/// This "AI with fallback" pattern is the right approach for enterprise test frameworks:
/// AI enhances the test when available but never becomes a single point of failure.
///
/// [AllureSuite("AiDriven")]: groups this test under its own suite in the Allure report.
/// Extends BaseTest — handles its own login because this test IS testing the login process.
/// </summary>
[TestFixture]
[AllureSuite("AiDriven")]
public class AiDrivenTest : BaseTest
{
    /// <summary>
    /// Tests that AI-generated credentials can be used to successfully log in to SauceDemo.
    ///
    /// Flow:
    ///   1. Construct a prompt asking the AI for SauceDemo credentials in a parseable format
    ///   2. Call AiHelper.AskAsync() to send the prompt to OpenAI (or get the "no key" fallback)
    ///   3. If the response looks like real AI output, parse username and password from it
    ///   4. Fall back to config credentials if parsing fails or AI is unavailable
    ///   5. Perform the login and assert the inventory page is reached
    ///
    /// Prompt engineering: the prompt is very specific about the exact output format
    /// ("username=&lt;value&gt; password=&lt;value&gt;"). Structured output makes parsing reliable.
    /// For production AI-driven tests, consider using OpenAI's "structured output" or
    /// "function calling" features for even more reliable parsing.
    ///
    /// [Category("ai")]: allows AI tests to be run or skipped independently via NUnit filters.
    /// In CI environments without an OpenAI key, the test still passes using config credentials.
    /// </summary>
    [Test]
    [Category("ai")]
    [AllureFeature("AI")]
    [AllureStory("Login with AI-generated credentials")]
    public async Task TestLoginWithAiGeneratedData()
    {
        // Craft a precise prompt that asks for credentials in a machine-parseable format.
        // The hint "Use: standard_user / secret_sauce" guides the AI toward valid values.
        // Without the hint the AI might invent credentials that don't exist on SauceDemo.
        string prompt = "Provide a valid SauceDemo username and password in this exact format: " +
                        "username=<value> password=<value>. " +
                        "Use: standard_user / secret_sauce";

        // Send the prompt to OpenAI (async HTTP call). If no API key is configured,
        // AiHelper returns a "[AiHelper] No API key..." string rather than throwing.
        string aiResponse = await AiHelper.AskAsync(prompt);

        // Log the AI response to the test output for debugging and reporting purposes.
        Console.WriteLine($"[AiDrivenTest] AI response: {aiResponse}");

        // Start with config-based fallback credentials.
        // These are always valid and provide a safety net when AI is unavailable.
        string username = ConfigReader.GetProperty("app:username", "standard_user");
        string password = ConfigReader.GetProperty("app:password", "secret_sauce");

        // Only attempt to parse the AI response if:
        //   1. It doesn't start with "[AiHelper]" (which signals a no-key fallback)
        //   2. It contains the expected "username=" and "password=" tokens
        if (!aiResponse.StartsWith("[AiHelper]") &&
            aiResponse.Contains("username=") && aiResponse.Contains("password="))
        {
            // Split the response into tokens by spaces and newlines, then parse each token.
            // StringSplitOptions.RemoveEmptyEntries skips empty tokens from consecutive delimiters.
            foreach (string part in aiResponse.Split(' ', '\n', StringSplitOptions.RemoveEmptyEntries))
            {
                // Extract username value from "username=<value>" token.
                if (part.StartsWith("username=", StringComparison.OrdinalIgnoreCase))
                    username = part.Split('=', 2)[1].Trim();  // Split on the first "=" only (limit=2)

                // Extract password value from "password=<value>" token.
                if (part.StartsWith("password=", StringComparison.OrdinalIgnoreCase))
                    password = part.Split('=', 2)[1].Trim();
            }
        }

        // Perform the login with whichever credentials were resolved (AI or config fallback).
        var loginPage = new LoginPage(Page);
        await loginPage.LoginAs(username, password);

        // Verify the login resulted in reaching the inventory page.
        Assert.That(Page.Url, Does.Contain("inventory"),
            "Should reach the inventory page with AI-suggested credentials.");
    }
}
