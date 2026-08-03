using System.Text;
using System.Text.Json;
using Framework.Core.Config;

namespace Framework.Core.Utils;

/// <summary>
/// Utility class for posting test result notifications to a Slack channel
/// via an Incoming Webhook URL.
///
/// Why this exists: Automated test suites in CI/CD pipelines often run unattended
/// overnight or on every pull request. Rather than requiring engineers to log into
/// CI to check results, this utility pushes a summary to a shared Slack channel
/// immediately after the suite completes. The team sees results in real time
/// without leaving their communication tool.
///
/// How Slack Incoming Webhooks work:
///   1. A Slack App is created in your workspace and granted the "Incoming Webhooks" permission.
///   2. A webhook URL is generated (looks like https://hooks.slack.com/services/T.../B.../...).
///   3. Any system that POSTs a JSON payload { "text": "..." } to that URL will
///      deliver a message to the configured Slack channel.
///   No authentication header is needed — the secret is embedded in the URL itself,
///   so treat the webhook URL as a password and store it in an environment variable.
///
/// Configuration key (appsettings.json or environment variable):
///   slack:webhook_url — the full https://hooks.slack.com/... URL
///   If not set, messages are logged to the console but not sent (graceful no-op).
/// </summary>
public static class SlackUtils
{
    // Shared HttpClient — reused across all Slack posts in the process lifetime
    // to avoid creating and discarding socket connections unnecessarily.
    private static readonly HttpClient _http = new();

    /// <summary>
    /// Posts the given message text to the configured Slack channel.
    ///
    /// Graceful degradation: if the webhook URL is not configured (common in
    /// developer local environments where Slack is not needed), the method simply
    /// logs the message to the console and returns without throwing an exception.
    /// This ensures missing Slack configuration never breaks a test run.
    ///
    /// The message supports Slack's mrkdwn (markdown-lite) syntax:
    ///   *bold*, _italic_, `code`, &lt;URL|link text&gt;
    /// </summary>
    public static async Task SendResultAsync(string message)
    {
        string webhookUrl = ConfigReader.GetProperty("slack:webhook_url");

        // Guard: no URL configured — log locally and exit without error.
        if (string.IsNullOrWhiteSpace(webhookUrl))
        {
            Console.WriteLine($"[SlackUtils] No webhook URL configured. Message: {message}");
            return;
        }

        // Slack expects a JSON body with a "text" field.
        // JsonSerializer.Serialize handles escaping special characters in the message.
        string json = JsonSerializer.Serialize(new { text = message });

        // StringContent sets the Content-Type header to "application/json; charset=utf-8"
        // which is required by the Slack webhook endpoint.
        using var content = new StringContent(json, Encoding.UTF8, "application/json");
        using HttpResponseMessage response = await _http.PostAsync(webhookUrl, content);

        // Log delivery failures without throwing — a Slack outage should not fail the test suite.
        if (!response.IsSuccessStatusCode)
        {
            Console.WriteLine($"[SlackUtils] Failed to send message. Status: {response.StatusCode}");
        }
    }

    /// <summary>
    /// Builds a formatted Slack summary message string from test result counts.
    /// The asterisks (*) around "Test Suite Result" render as bold text in Slack.
    ///
    /// This is a pure string-building method (no HTTP call) — it exists separately
    /// from SendResultAsync so callers can preview or log the summary before sending it,
    /// or format it differently for different notification channels.
    ///
    /// Example output:
    ///   *Test Suite Result* | Passed: 42 | Failed: 1 | Skipped: 3
    /// </summary>
    public static string BuildSummary(int passed, int failed, int skipped)
    {
        return $"*Test Suite Result* | Passed: {passed} | Failed: {failed} | Skipped: {skipped}";
    }
}
