using System.IO;
using Allure.Net.Commons;
using Allure.NUnit;
using Allure.NUnit.Attributes;
using Microsoft.Playwright;
using Microsoft.Playwright.NUnit;
using Framework.Core.Config;

namespace Framework.Tests.Base;

/// <summary>
/// Base class for all Playwright UI tests in the framework.
///
/// Why this exists: Every test needs the same lifecycle around it —
/// navigate to the app before the test, capture evidence on failure after the test,
/// and configure the browser window. Putting that logic here means individual test
/// classes inherit it automatically and never duplicate it.
///
/// Key design decisions:
///
/// Extends PageTest (from Microsoft.Playwright.NUnit):
///   PageTest is Playwright's NUnit integration class. It automatically creates a
///   fresh browser, browser context, and page (IPage) for each test, then tears
///   them down afterwards. Tests get complete isolation — one test's cookies,
///   local storage, and state cannot bleed into another test.
///
/// [AllureNUnit]:
///   Activates the Allure reporting integration for the entire class hierarchy.
///   Allure is a popular HTML test report generator. With this attribute, test
///   results, screenshots, and trace files are automatically attached to the report.
///
/// [Parallelizable(ParallelScope.Self)]:
///   Tells NUnit that tests within a single class run sequentially (one at a time),
///   but different test classes can run at the same time (in parallel). This is the
///   safest parallelism level for UI tests — it speeds up the overall suite without
///   multiple tests fighting over the same browser instance.
/// </summary>
[Parallelizable(ParallelScope.Self)]
[AllureNUnit]
public abstract class BaseTest : PageTest
{
    // RetryCount is read once when the class first loads (static field initialiser).
    // Storing it as a static field avoids reading config on every test.
    // "protected" makes it accessible to all subclasses (AuthenticatedTest, test classes, etc.).
    protected static readonly int RetryCount =
        ConfigReader.GetInt("retry:max", 1);

    /// <summary>
    /// Runs before each test in every class that extends BaseTest.
    /// Responsibilities:
    ///   1. Start a Playwright trace recording so we have a visual replay if the test fails.
    ///   2. Navigate to the application's base URL so every test starts from the login page.
    ///
    /// Playwright Tracing: A trace is a zip file containing a full timeline of browser
    /// actions, network requests, screenshots, and DOM snapshots. Opening it in
    /// https://trace.playwright.dev lets you step through exactly what happened —
    /// invaluable for debugging CI failures where you can't watch the browser live.
    ///
    /// NUnit [SetUp] chain: when AuthenticatedTest (a subclass) also has a [SetUp] method,
    /// NUnit runs BaseTest.NavigateToApp FIRST, then AuthenticatedTest.LoginBeforeEach.
    /// This is the NUnit [SetUp] execution order guarantee.
    /// </summary>
    [SetUp]
    public async Task NavigateToApp()
    {
        // Start recording a trace for this test. Screenshots and DOM snapshots
        // give a frame-by-frame view; Sources shows the test code being executed.
        await Context.Tracing.StartAsync(new TracingStartOptions
        {
            Screenshots = true,  // Captures a screenshot at each action
            Snapshots   = true,  // Captures a DOM snapshot at each action
            Sources     = true,  // Embeds the C# source code in the trace viewer
            Title       = TestContext.CurrentContext.Test.Name  // Labels the trace by test name
        });

        // Navigate to the application. The URL is read from config so the same
        // test binary can run against dev, staging, or production without recompilation.
        string url = ConfigReader.GetProperty("url", "https://www.saucedemo.com");
        await Page.GotoAsync(url);
    }

    /// <summary>
    /// Runs after each test, regardless of whether it passed or failed.
    /// On failure: captures a full-page screenshot and saves the trace zip, then
    /// attaches both to the Allure report so they appear alongside the failure details.
    /// On success: discards the trace to keep the disk footprint small (passing
    /// tests don't need a replay).
    ///
    /// Why attach to Allure rather than just saving files: Allure links the evidence
    /// directly to the failing test in the HTML report. Engineers can click one link
    /// to see the screenshot and trace without searching through a file system.
    ///
    /// FullPage = true: captures everything below the fold (not just the visible viewport),
    /// which is important when an error element may be scrolled out of view.
    /// </summary>
    [TearDown]
    public async Task OnTearDown()
    {
        if (TestContext.CurrentContext.Result.Outcome.Status ==
            NUnit.Framework.Interfaces.TestStatus.Failed)
        {
            // Build a unique filename using the test name + timestamp to avoid overwriting
            // previous failure screenshots if the same test is retried.
            string screenshotName =
                $"failure_{TestContext.CurrentContext.Test.Name}_{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}.png";

            // Capture the full browser page as a PNG byte array in memory.
            byte[] screenshot = await Page.ScreenshotAsync(new PageScreenshotOptions
            {
                FullPage = true  // Scroll and capture the entire page, not just the viewport
            });

            // Attach the screenshot to the Allure report for this test.
            AllureApi.AddAttachment(screenshotName, "image/png", screenshot);

            // Save the trace zip to the "traces" folder inside the test working directory.
            string tracesDir = Path.Combine(TestContext.CurrentContext.WorkDirectory, "traces");
            Directory.CreateDirectory(tracesDir);  // No-op if the folder already exists
            string tracePath = Path.Combine(tracesDir, $"{TestContext.CurrentContext.Test.Name}.zip");

            // StopAsync with a Path causes Playwright to finalise and save the trace zip.
            await Context.Tracing.StopAsync(new TracingStopOptions { Path = tracePath });

            // Attach the trace zip to the Allure report as a downloadable attachment.
            AllureApi.AddAttachment(
                $"trace_{TestContext.CurrentContext.Test.Name}.zip",
                "application/zip",
                await File.ReadAllBytesAsync(tracePath));
        }
        else
        {
            // Passing test — stop tracing without saving. Passing a null path discards
            // the in-memory trace buffer, reclaiming memory without writing to disk.
            await Context.Tracing.StopAsync(); // no path = discard trace for passing tests
        }
    }

    /// <summary>
    /// Overrides the Playwright browser context options to standardise the viewport size.
    /// A 1920x1080 viewport ensures tests run as if on a full HD monitor, regardless of
    /// the actual screen size of the CI agent running the tests.
    ///
    /// Why override: The default Playwright viewport is 1280x720, which may hide elements
    /// that only appear at wider resolutions, or cause layout issues in responsive designs.
    ///
    /// Headless vs. headed: this method does NOT control headless mode. Playwright's NUnit
    /// integration reads the PLAYWRIGHT_HEADLESS environment variable automatically.
    /// Set it to "false" in a .runsettings file to see the browser during local debugging.
    ///
    /// BrowserNewContextOptions also supports other settings like locale, timezone,
    /// recordVideo, and storageState (for pre-authenticated sessions) — extend here as needed.
    /// </summary>
    public override BrowserNewContextOptions ContextOptions()
    {
        return new BrowserNewContextOptions
        {
            ViewportSize = new ViewportSize { Width = 1920, Height = 1080 }
        };
    }
}
