using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using Framework.Core.Config;

namespace Framework.Core.Utils;

/// <summary>
/// Sends prompts to the OpenAI Chat Completions API and returns the assistant's reply.
/// Configure <c>openai:api_key</c> and <c>ai:model</c> in appsettings.json.
/// </summary>
public static class AiHelper
{
    private static readonly HttpClient _http = new();
    private const string Endpoint = "https://api.openai.com/v1/chat/completions";

    public static async Task<string> AskAsync(string prompt)
    {
        string apiKey = ConfigReader.GetProperty("openai:api_key");
        string model  = ConfigReader.GetProperty("ai:model", "gpt-4o-mini");

        if (string.IsNullOrWhiteSpace(apiKey))
            return $"[AiHelper] No API key configured — prompt was: {prompt}";

        var requestBody = new
        {
            model,
            messages = new[] { new { role = "user", content = prompt } }
        };

        string json = JsonSerializer.Serialize(requestBody);
        using var request = new HttpRequestMessage(HttpMethod.Post, Endpoint)
        {
            Content = new StringContent(json, Encoding.UTF8, "application/json")
        };
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", apiKey);

        using HttpResponseMessage response = await _http.SendAsync(request);
        response.EnsureSuccessStatusCode();

        string responseJson = await response.Content.ReadAsStringAsync();
        using JsonDocument doc = JsonDocument.Parse(responseJson);
        return doc.RootElement
                  .GetProperty("choices")[0]
                  .GetProperty("message")
                  .GetProperty("content")
                  .GetString() ?? string.Empty;
    }
}
