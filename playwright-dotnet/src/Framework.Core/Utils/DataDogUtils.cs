using System.Text;
using System.Text.Json;

namespace Framework.Core.Utils;

/// <summary>
/// DataDogUtils: Sends suite-level test metrics to DataDog via the v2 metrics API.
///
/// Four GAUGE metrics are posted after each suite run:
///   test.suite.passed, test.suite.failed, test.suite.skipped, test.suite.duration_ms
/// These power DataDog dashboards that surface pass/fail trends, flaky-test signals,
/// and duration regressions over time.
///
/// Fail-safe design: if DD_API_KEY is absent (local dev, environments without DataDog),
/// the method logs a warning and returns without throwing — mirroring the same
/// graceful-skip pattern used by SlackUtils. CI stays green without the secret set.
///
/// HTTP transport: static shared HttpClient (same pattern as SlackUtils.cs).
/// Serialization: System.Text.Json (same as SlackUtils.cs).
///
/// DataDog v2 endpoint: POST https://api.datadoghq.com/api/v2/series
/// Auth header: DD-API-KEY: <api_key>
/// Success response: HTTP 202 Accepted.
///
/// Metric type 3 = DataDog GAUGE — appropriate for point-in-time counts and
/// durations that do not accumulate across submissions.
/// </summary>
public static class DataDogUtils
{
    private static readonly HttpClient _http = new();
    private static string ApiUrl {
        get {
            string site = Environment.GetEnvironmentVariable("DD_SITE") ?? "datadoghq.com";
            return $"https://api.{site}/api/v2/series";
        }
    }

    /// <summary>
    /// Posts four suite-level metrics to DataDog after the test run completes.
    ///
    /// Called from TestHooks.AfterAll() once per assembly run. NUnit's SetUpFixture
    /// does not expose aggregate pass/fail counts, so this method reads them from the
    /// TESTS_PASSED / TESTS_FAILED / TESTS_SKIPPED environment variables (which CI
    /// runners can set after the dotnet test run completes). If not set, the values
    /// default to 0, which is still useful for recording that the suite ran.
    /// </summary>
    /// <param name="passed">Number of tests that passed.</param>
    /// <param name="failed">Number of tests that failed.</param>
    /// <param name="skipped">Number of tests that were skipped.</param>
    /// <param name="durationMs">Total suite wall-clock duration in milliseconds.</param>
    /// <param name="framework">Short framework label for the tag, e.g. "playwright-dotnet".</param>
    public static async Task SendTestMetricsAsync(int passed, int failed, int skipped, long durationMs, string framework)
    {
        string? apiKey = Environment.GetEnvironmentVariable("DD_API_KEY");

        if (string.IsNullOrWhiteSpace(apiKey))
        {
            Console.WriteLine("[WARN] DD_API_KEY not set. Skipping DataDog metrics.");
            return;
        }

        try
        {
            long timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
            string[] tags = [$"framework:{framework}", "service:qa-automation-portfolio", "env:ci"];

            var payload = new
            {
                series = new[]
                {
                    BuildSeries("test.suite.passed",      (long)passed,     timestamp, tags),
                    BuildSeries("test.suite.failed",      (long)failed,     timestamp, tags),
                    BuildSeries("test.suite.skipped",     (long)skipped,    timestamp, tags),
                    BuildSeries("test.suite.duration_ms", durationMs,       timestamp, tags)
                }
            };

            string json = JsonSerializer.Serialize(payload);
            using var content = new StringContent(json, Encoding.UTF8, "application/json");

            // DD-API-KEY must be a request header, not a query parameter
            using var request = new HttpRequestMessage(HttpMethod.Post, ApiUrl) { Content = content };
            request.Headers.Add("DD-API-KEY", apiKey);

            using HttpResponseMessage response = await _http.SendAsync(request);

            if (response.IsSuccessStatusCode)
                Console.WriteLine("[INFO] DataDog metrics sent successfully.");
            else
                Console.WriteLine($"[WARN] DataDog metrics returned {(int)response.StatusCode}.");
        }
        catch (Exception ex)
        {
            // Never crash the test run over a metrics delivery failure
            Console.WriteLine($"[ERROR] DataDog metrics failed: {ex.Message}");
        }
    }

    /// <summary>
    /// Builds a single DataDog v2 series object for one metric data point.
    /// </summary>
    private static object BuildSeries(string metric, long value, long timestamp, string[] tags) =>
        new
        {
            metric,
            type   = 3,   // 3 = GAUGE in DataDog's metric type enum
            points = new[] { new { timestamp, value } },
            tags
        };
}
