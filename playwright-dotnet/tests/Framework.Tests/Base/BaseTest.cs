using System.IO;
using Allure.Net.Commons;
using Allure.NUnit;
using Allure.NUnit.Attributes;
using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using Framework.Core.Config;

namespace Framework.Tests.Base;

/// <summary>
/// Base class for all Playwright UI tests.
/// Extends PageTest which provides a fresh IPage per test with full isolation.
/// [Parallelizable(ParallelScope.Self)] enables parallel execution across test classes.
/// </summary>
[Parallelizable(ParallelScope.Self)]
[AllureNUnit]
public abstract class BaseTest : PageTest
{
    // Retry count read once from config at class-load time.
    protected static readonly int RetryCount =
        ConfigReader.GetInt("retry:max", 1);

    [SetUp]
    public async Task NavigateToApp()
    {
        await Context.Tracing.StartAsync(new TracingStartOptions
        {
            Screenshots = true,
            Snapshots   = true,
            Sources     = true,
            Title       = TestContext.CurrentContext.Test.Name
        });

        string url = ConfigReader.GetProperty("url", "https://www.saucedemo.com");
        await Page.GotoAsync(url);
    }

    [TearDown]
    public async Task OnTearDown()
    {
        if (TestContext.CurrentContext.Result.Outcome.Status ==
            NUnit.Framework.Interfaces.TestStatus.Failed)
        {
            string screenshotName =
                $"failure_{TestContext.CurrentContext.Test.Name}_{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}.png";

            byte[] screenshot = await Page.ScreenshotAsync(new PageScreenshotOptions
            {
                FullPage = true
            });

            AllureApi.AddAttachment(screenshotName, "image/png", screenshot);

            string tracesDir = Path.Combine(TestContext.CurrentContext.WorkDirectory, "traces");
            Directory.CreateDirectory(tracesDir);
            string tracePath = Path.Combine(tracesDir, $"{TestContext.CurrentContext.Test.Name}.zip");
            await Context.Tracing.StopAsync(new TracingStopOptions { Path = tracePath });
            AllureApi.AddAttachment(
                $"trace_{TestContext.CurrentContext.Test.Name}.zip",
                "application/zip",
                await File.ReadAllBytesAsync(tracePath));
        }
        else
        {
            await Context.Tracing.StopAsync(); // no path = discard trace for passing tests
        }
    }

    /// <summary>
    /// Override context options to set a 1920x1080 viewport.
    /// Headless behaviour is driven by the PLAYWRIGHT_HEADLESS environment variable
    /// (set via .runsettings) which Microsoft.Playwright.NUnit reads automatically.
    /// </summary>
    public override BrowserNewContextOptions ContextOptions()
    {
        return new BrowserNewContextOptions
        {
            ViewportSize = new ViewportSize { Width = 1920, Height = 1080 }
        };
    }
}
