using Framework.Core.Utils;

namespace Framework.Tests.Listeners;

/// <summary>
/// Assembly-level setup/teardown fixture — mirrors ITestListener.onFinish in Java.
/// Sends a Slack summary after the full test suite completes.
/// </summary>
[SetUpFixture]
public class TestHooks
{
    // NUnit does not expose global pass/fail counts in SetUpFixture.
    // Counts are read from environment variables set by the CI runner (or default to "?").

    [OneTimeSetUp]
    public void BeforeAll()
    {
        Console.WriteLine("[TestHooks] Test suite starting.");
    }

    [OneTimeTearDown]
    public async Task AfterAll()
    {
        // NUnit 3 does not aggregate counts in SetUpFixture; read from environment if CI sets them,
        // otherwise post a generic completion message.
        string passed  = Environment.GetEnvironmentVariable("TESTS_PASSED")  ?? "?";
        string failed  = Environment.GetEnvironmentVariable("TESTS_FAILED")  ?? "?";
        string skipped = Environment.GetEnvironmentVariable("TESTS_SKIPPED") ?? "?";

        string summary = $"*PlaywrightDotNetFramework* suite complete | " +
                         $"Passed: {passed} | Failed: {failed} | Skipped: {skipped}";

        Console.WriteLine($"[TestHooks] {summary}");
        await SlackUtils.SendResultAsync(summary);
    }
}
