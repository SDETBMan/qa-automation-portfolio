using System.Text;
using System.Text.Json;
using Framework.Core.Config;

namespace Framework.Core.Utils;

/// <summary>
/// Posts a message to a Slack Incoming Webhook.
/// Configure <c>slack:webhook_url</c> in appsettings.json or as an environment variable.
/// </summary>
public static class SlackUtils
{
    private static readonly HttpClient _http = new();

    public static async Task SendResultAsync(string message)
    {
        string webhookUrl = ConfigReader.GetProperty("slack:webhook_url");

        if (string.IsNullOrWhiteSpace(webhookUrl))
        {
            Console.WriteLine($"[SlackUtils] No webhook URL configured. Message: {message}");
            return;
        }

        string json = JsonSerializer.Serialize(new { text = message });
        using var content = new StringContent(json, Encoding.UTF8, "application/json");
        using HttpResponseMessage response = await _http.PostAsync(webhookUrl, content);

        if (!response.IsSuccessStatusCode)
        {
            Console.WriteLine($"[SlackUtils] Failed to send message. Status: {response.StatusCode}");
        }
    }

    /// <summary>Builds a standard test-suite summary string.</summary>
    public static string BuildSummary(int passed, int failed, int skipped)
    {
        return $"*Test Suite Result* | Passed: {passed} | Failed: {failed} | Skipped: {skipped}";
    }
}
