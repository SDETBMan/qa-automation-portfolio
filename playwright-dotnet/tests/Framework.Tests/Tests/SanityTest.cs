using Microsoft.Playwright;
using Framework.Core.Config;

namespace Framework.Tests.Tests;

/// <summary>
/// "Bare metal" sanity checks that bypass BaseTest/PageTest entirely —
/// mirrors the Java SanityTest that bypasses BaseTest/DriverFactory.
/// </summary>
[TestFixture]
public class SanityTest
{
    [Test]
    [Category("sanity")]
    public async Task RawPlaywrightLaunch()
    {
        using IPlaywright playwright = await Playwright.CreateAsync();
        await using IBrowser browser = await playwright.Chromium.LaunchAsync(
            new BrowserTypeLaunchOptions { Headless = true });

        IPage page = await browser.NewPageAsync();
        await page.GotoAsync("https://www.saucedemo.com");

        Assert.That(page.Url, Does.Contain("saucedemo"),
            "Raw Playwright should navigate to saucedemo.com.");

        await browser.CloseAsync();
    }

    [Test]
    [Category("sanity")]
    public void ConfigurationLoad()
    {
        string url      = ConfigReader.GetProperty("url");
        string username = ConfigReader.GetProperty("app:username");
        string password = ConfigReader.GetProperty("app:password");

        Assert.Multiple(() =>
        {
            Assert.That(url,      Is.Not.Empty, "url must be set in appsettings.json");
            Assert.That(username, Is.Not.Empty, "app:username must be set");
            Assert.That(password, Is.Not.Empty, "app:password must be set");
        });
    }

    [Test]
    [Category("sanity")]
    public async Task HubConnectivity()
    {
        string hubUrl = ConfigReader.GetProperty("hub:url");

        if (string.IsNullOrWhiteSpace(hubUrl))
        {
            Assert.Ignore("hub:url is not configured — skipping hub connectivity check.");
            return;
        }

        using var http = new System.Net.Http.HttpClient();
        http.Timeout = TimeSpan.FromSeconds(10);

        try
        {
            var response = await http.GetAsync(hubUrl);
            Assert.That((int)response.StatusCode, Is.LessThan(500),
                $"Hub at {hubUrl} should respond with a non-5xx status.");
        }
        catch (Exception ex)
        {
            Assert.Fail($"Could not connect to hub at {hubUrl}: {ex.Message}");
        }
    }
}
