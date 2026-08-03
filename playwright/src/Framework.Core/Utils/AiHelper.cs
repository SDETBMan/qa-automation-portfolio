using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using Framework.Core.Config;

namespace Framework.Core.Utils;

/// <summary>
/// Utility class that sends natural-language prompts to the OpenAI Chat Completions API
/// and returns the AI assistant's text response.
///
/// Why this exists in a QA framework: AI-assisted testing is an emerging practice where
/// test data, test steps, or assertions are generated or suggested by a large language
/// model (LLM). This helper shows how an SDET can integrate an LLM into automated tests
/// without requiring a dedicated AI library — just standard HTTP calls.
///
/// Practical use cases:
///   - Generate realistic test data (names, emails, addresses) that is harder to fake manually
///   - Ask the AI to suggest edge-case inputs for a form field
///   - Produce human-readable failure summaries from raw assertion output
///
/// Configuration (appsettings.json or environment variables):
///   openai:api_key  — your OpenAI secret key (never commit this to source control)
///   ai:model        — model to use, e.g. "gpt-4o-mini" (default) or "gpt-4o"
///
/// Graceful degradation: when no API key is configured (e.g., in CI without the secret),
/// AskAsync returns a descriptive string instead of throwing an exception, so tests that
/// depend on AI data can fall back to hardcoded values and still pass.
/// </summary>
public static class AiHelper
{
    // A single shared HttpClient instance is used for all requests.
    // Best practice: HttpClient is designed to be reused — creating a new one per request
    // can exhaust socket connections under load (a well-known .NET pitfall).
    private static readonly HttpClient _http = new();

    // The OpenAI Chat Completions endpoint. All models that support chat-style
    // interaction (GPT-4o, GPT-4o-mini, etc.) use this same URL.
    private const string Endpoint = "https://api.openai.com/v1/chat/completions";

    /// <summary>
    /// Sends a single-turn prompt to the configured OpenAI model and returns
    /// the assistant's text response.
    ///
    /// The method is async (returns Task) because the HTTP call is a network
    /// operation that could take seconds — using async/await keeps the test
    /// runner thread free to do other work while waiting, rather than blocking.
    ///
    /// If the API key is missing or empty the method returns an informational
    /// string (starting with "[AiHelper]") rather than throwing, so callers can
    /// detect the no-key scenario with a simple string check.
    /// </summary>
    public static async Task<string> AskAsync(string prompt)
    {
        // Read credentials and model from config so they can be changed without
        // recompiling the code (set via appsettings.json or environment variables).
        string apiKey = ConfigReader.GetProperty("openai:api_key");
        string model  = ConfigReader.GetProperty("ai:model", "gpt-4o-mini");

        // Guard: return a safe fallback instead of making a request with a missing key.
        // This allows tests to run in environments where the OpenAI key is not provisioned.
        if (string.IsNullOrWhiteSpace(apiKey))
            return $"[AiHelper] No API key configured — prompt was: {prompt}";

        // Build the JSON request body that the OpenAI API expects.
        // The "messages" array follows the chat format: role="user" means this is
        // the human's turn. The AI's reply will be role="assistant".
        var requestBody = new
        {
            model,
            messages = new[] { new { role = "user", content = prompt } }
        };

        // Serialize the anonymous object to a JSON string.
        string json = JsonSerializer.Serialize(requestBody);

        // Create the HTTP POST request with the JSON body and auth header.
        using var request = new HttpRequestMessage(HttpMethod.Post, Endpoint)
        {
            Content = new StringContent(json, Encoding.UTF8, "application/json")
        };
        // OpenAI uses Bearer token authentication: "Authorization: Bearer sk-..."
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", apiKey);

        // Send the request and wait for the response (async — does not block the thread).
        using HttpResponseMessage response = await _http.SendAsync(request);
        // EnsureSuccessStatusCode throws an exception for 4xx/5xx responses,
        // surfacing API errors (bad key, quota exceeded, etc.) immediately.
        response.EnsureSuccessStatusCode();

        // Parse the response JSON and navigate to the assistant's reply text.
        // OpenAI response structure: { choices: [ { message: { content: "..." } } ] }
        string responseJson = await response.Content.ReadAsStringAsync();
        using JsonDocument doc = JsonDocument.Parse(responseJson);
        return doc.RootElement
                  .GetProperty("choices")[0]  // First (and usually only) completion choice
                  .GetProperty("message")
                  .GetProperty("content")
                  .GetString() ?? string.Empty;
    }
}
