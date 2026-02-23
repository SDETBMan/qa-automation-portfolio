using Microsoft.Playwright;
using Framework.Core.Config;

namespace Framework.Tests.Tests;

/// <summary>
/// SanityTest: "Bare metal" infrastructure checks that validate the test environment
/// itself, not the application under test.
///
/// WHY SANITY TESTS EXIST: Before trusting test results, you must trust the test
/// environment. If Playwright can't launch a browser, if appsettings.json is missing
/// a required key, or if the Selenium Grid hub isn't running, every test will fail for
/// infrastructure reasons — not application bugs. Sanity tests diagnose these problems
/// directly, giving a clear "environment is broken" signal before any app tests run.
///
/// WHY THIS CLASS DOES NOT EXTEND BaseTest:
/// BaseTest contains shared setup and teardown logic. If BaseTest itself is broken,
/// tests extending it would all fail in setUp — masking the real cause. SanityTest
/// bypasses BaseTest entirely, using Playwright APIs directly. This isolation means:
///   - If SanityTest passes but other tests fail → the issue is in the framework code.
///   - If SanityTest fails → the environment itself is broken (browser, config, etc.).
///
/// MIRRORS THE JAVA SanityTest: This C# class follows the same design as the Java
/// framework's SanityTest — one of the ways the portfolio demonstrates cross-language
/// consistency in testing principles.
///
/// WHAT THIS CLASS COVERS:
///   1. RawPlaywrightLaunch  — creates a browser directly (no BaseTest wrappers)
///      to confirm Playwright and browsers are correctly installed.
///   2. ConfigurationLoad    — reads appsettings.json and confirms required keys
///      (url, username, password) are present and non-empty.
///   3. HubConnectivity      — pings the Selenium/Playwright Grid hub URL to confirm
///      it's reachable before grid-targeted tests run.
/// </summary>
[TestFixture]
public class SanityTest
{
    /// <summary>
    /// RawPlaywrightLaunch: Creates a Playwright browser instance manually (without
    /// BaseTest or PageTest) and navigates to SauceDemo to confirm the browser works.
    ///
    /// WHY "BARE METAL": This test intentionally avoids all framework abstractions —
    /// no BaseTest, no ConfigReader for the URL, no page objects. It uses only the raw
    /// Playwright.NET API. This is the most honest test of whether "Playwright works
    /// on this machine" because there is no framework code between the test and the
    /// browser that could hide or cause the failure.
    ///
    /// WHY HEADLESS: CI environments have no graphical display. Headless = true
    /// launches Chrome without a visible window, which works in any environment.
    ///
    /// RESOURCE MANAGEMENT: The test uses 'using' and 'await using' to ensure
    /// IPlaywright and IBrowser are disposed (closed/cleaned up) even if the
    /// test throws an exception — preventing orphan browser processes.
    /// </summary>
    [Test]
    [Category("sanity")]
    public async Task RawPlaywrightLaunch()
    {
        // Playwright.CreateAsync() is the entry point for the entire Playwright library.
        // It returns the top-level object from which you create browsers.
        using IPlaywright playwright = await Playwright.CreateAsync();

        // Launch Chromium (the open-source base of Google Chrome) in headless mode.
        // 'await using' ensures the browser is closed and resources freed after the test.
        await using IBrowser browser = await playwright.Chromium.LaunchAsync(
            new BrowserTypeLaunchOptions { Headless = true });

        // Open a new browser tab (page) to navigate to the application.
        IPage page = await browser.NewPageAsync();
        await page.GotoAsync("https://www.saucedemo.com");

        // Verify navigation succeeded — the URL should contain "saucedemo".
        // This confirms the browser launched, the network is reachable, and
        // the page responded (not a connection refused or DNS failure).
        Assert.That(page.Url, Does.Contain("saucedemo"),
            "Raw Playwright should navigate to saucedemo.com.");

        await browser.CloseAsync();
    }

    /// <summary>
    /// ConfigurationLoad: Reads appsettings.json and verifies that the three
    /// critical keys (url, app:username, app:password) are present and non-empty.
    ///
    /// WHY TEST THE CONFIG: Every test in the framework depends on these values.
    /// If appsettings.json is missing, malformed, or doesn't contain the expected keys,
    /// every other test will fail with cryptic NullReferenceExceptions or empty-string
    /// errors deep inside page objects. This test provides an early, clear failure
    /// message ("app:username must be set") rather than a confusing late failure.
    ///
    /// ASSERT.MULTIPLE: Collects all three assertions before reporting failures.
    /// If all three keys are missing, you see all three failures at once rather than
    /// fixing them one at a time — a more efficient debugging experience.
    /// </summary>
    [Test]
    [Category("sanity")]
    public void ConfigurationLoad()
    {
        // Read the three most critical configuration values.
        // ConfigReader reads from appsettings.json and supports environment variable
        // overrides — so CI pipelines can inject values without modifying the file.
        string url      = ConfigReader.GetProperty("url");
        string username = ConfigReader.GetProperty("app:username");
        string password = ConfigReader.GetProperty("app:password");

        // Collect all assertion failures before reporting — if multiple keys are
        // missing, all are reported in one test run rather than one-at-a-time.
        Assert.Multiple(() =>
        {
            Assert.That(url,      Is.Not.Empty, "url must be set in appsettings.json");
            Assert.That(username, Is.Not.Empty, "app:username must be set");
            Assert.That(password, Is.Not.Empty, "app:password must be set");
        });
    }

    /// <summary>
    /// HubConnectivity: Pings the Playwright/Selenium Grid hub URL to confirm
    /// it's reachable before grid-dependent tests run.
    ///
    /// WHY CHECK THE HUB: Tests that use a remote grid (Docker Compose or Kubernetes)
    /// will fail immediately with connection errors if the hub isn't running. This
    /// sanity test catches that condition with a clear message before any app tests
    /// start, saving debugging time.
    ///
    /// WHY IGNORE (NOT FAIL) IF HUB:URL IS NOT CONFIGURED: The hub is only needed
    /// when running tests in grid mode. Local development runs don't use a grid.
    /// Using Assert.Ignore() gracefully skips this test rather than failing it when
    /// no hub URL is configured — the skip appears in reports so you know it ran
    /// but wasn't applicable in this environment.
    ///
    /// WHY NOT ALWAYS ASSERT: If the hub is configured but unreachable, the test
    /// fails with "Could not connect to hub" — a clear actionable message.
    /// If the hub is not configured, the test is ignored — also a clear message.
    /// Both outcomes are more helpful than a generic failure.
    /// </summary>
    [Test]
    [Category("sanity")]
    public async Task HubConnectivity()
    {
        // Read the hub URL from config — only present when running in grid mode.
        string hubUrl = ConfigReader.GetProperty("hub:url");

        // If hub:url is not configured, this test isn't applicable in this environment.
        // Assert.Ignore() marks the test as "skipped" in the report — not a failure,
        // not a pass, just "not applicable here."
        if (string.IsNullOrWhiteSpace(hubUrl))
        {
            Assert.Ignore("hub:url is not configured — skipping hub connectivity check.");
            return;
        }

        // Create a short-lived HttpClient for this health check.
        // 'using var' ensures it's disposed (connection closed) after the test,
        // even if an exception is thrown.
        using var http = new System.Net.Http.HttpClient();
        http.Timeout = TimeSpan.FromSeconds(10); // Fail fast — hub should respond in ms if it's up

        try
        {
            // Send a GET request to the hub URL. The Selenium Grid /status endpoint
            // returns a JSON health payload — any non-5xx response means it's alive.
            var response = await http.GetAsync(hubUrl);

            // Any response below 500 (200 OK, 301 redirect, etc.) means the hub
            // is reachable and responding. A 5xx means the hub is up but broken.
            Assert.That((int)response.StatusCode, Is.LessThan(500),
                $"Hub at {hubUrl} should respond with a non-5xx status.");
        }
        catch (Exception ex)
        {
            // Connection refused, DNS failure, timeout — the hub is unreachable.
            Assert.Fail($"Could not connect to hub at {hubUrl}: {ex.Message}");
        }
    }
}
