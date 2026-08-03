using Framework.Core.Utils;

namespace Framework.Tests.Listeners;

/// <summary>
/// Assembly-level test lifecycle hooks for the entire test suite.
///
/// Why this exists: Some actions need to happen exactly once for the whole test run,
/// not once per test class or once per test. Examples:
///   - Logging that the suite has started
///   - Sending a Slack notification with a pass/fail summary after all tests finish
///   - Starting and stopping a shared resource like a test database server
///
/// [SetUpFixture] is the NUnit attribute that marks this class as an assembly-level
/// fixture. NUnit will call [OneTimeSetUp] once before any test in the assembly runs
/// and [OneTimeTearDown] once after all tests have finished — similar to
/// ITestListener.onStart / onFinish in Java's TestNG or JUnit.
///
/// This class lives in the "Listeners" namespace to mirror the Java framework's
/// Listeners package, which contains TestNG listeners that perform the same role.
/// </summary>
[SetUpFixture]
public class TestHooks
{
    // NUnit does not expose global pass/fail counts in SetUpFixture.
    // Counts are read from environment variables set by the CI runner (or default to "?").

    // Captures the moment BeforeAll runs so AfterAll can compute total suite duration.
    private DateTime _suiteStart;

    /// <summary>
    /// Runs once before the first test in the entire assembly starts.
    /// Used for suite-level setup tasks: starting external services, printing a header,
    /// or initialising shared infrastructure that all tests depend on.
    ///
    /// [OneTimeSetUp] (as opposed to [SetUp]) means this runs at most once per
    /// test run, not once per test class.
    /// </summary>
    [OneTimeSetUp]
    public void BeforeAll()
    {
        _suiteStart = DateTime.UtcNow;
        // Log suite start to the NUnit console output — visible in CI build logs.
        Console.WriteLine("[TestHooks] Test suite starting.");
    }

    /// <summary>
    /// Runs once after the last test in the entire assembly has finished.
    /// Sends a Slack summary so the team knows the suite completed and can see
    /// the high-level pass/fail count without logging into CI.
    ///
    /// Why environment variables for counts: NUnit 3's SetUpFixture API does not
    /// aggregate pass/fail/skip counts across all tests. Instead, we rely on the CI
    /// system (GitHub Actions, Jenkins, etc.) to export those counts as environment
    /// variables after the test run. If they're not set (e.g., local run), we post "?"
    /// so the message is still useful without crashing.
    ///
    /// The method is async because SlackUtils.SendResultAsync makes an HTTP POST call.
    /// [OneTimeTearDown] supports async methods — NUnit awaits the returned Task.
    /// </summary>
    [OneTimeTearDown]
    public async Task AfterAll()
    {
        // NUnit 3 does not aggregate counts in SetUpFixture; read from environment if CI sets them,
        // otherwise post a generic completion message.
        string passed  = Environment.GetEnvironmentVariable("TESTS_PASSED")  ?? "?";
        string failed  = Environment.GetEnvironmentVariable("TESTS_FAILED")  ?? "?";
        string skipped = Environment.GetEnvironmentVariable("TESTS_SKIPPED") ?? "?";

        // Build the summary message that will appear in Slack.
        // The asterisks (*) render as bold text in Slack's mrkdwn format.
        string summary = $"*PlaywrightDotNetFramework* suite complete | " +
                         $"Passed: {passed} | Failed: {failed} | Skipped: {skipped}";

        // Echo to the console so the summary is visible in CI build logs regardless
        // of whether Slack is configured.
        Console.WriteLine($"[TestHooks] {summary}");

        // Post to Slack. SlackUtils.SendResultAsync is a no-op if the webhook URL
        // is not configured, so this call is always safe to make.
        await SlackUtils.SendResultAsync(summary);

        // Send suite-level metrics to DataDog. Parse env-var counts to integers;
        // default to 0 if not set. DataDogUtils.SendTestMetricsAsync is a no-op
        // when DD_API_KEY is absent, so this call is always safe to make.
        int.TryParse(passed,  out int passedInt);
        int.TryParse(failed,  out int failedInt);
        int.TryParse(skipped, out int skippedInt);
        long durationMs = (long)(DateTime.UtcNow - _suiteStart).TotalMilliseconds;
        await DataDogUtils.SendTestMetricsAsync(passedInt, failedInt, skippedInt, durationMs, "playwright");
    }
}
