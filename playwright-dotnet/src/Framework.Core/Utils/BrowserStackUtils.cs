using System.Net.Http.Headers;
using Framework.Core.Config;

namespace Framework.Core.Utils;

/// <summary>
/// Uploads an app binary to BrowserStack App Automate and returns the app_url.
/// Configure <c>browserstack:android_app_id</c> / <c>browserstack:ios_app_id</c> in appsettings.json.
/// </summary>
public static class BrowserStackUtils
{
    private static readonly HttpClient _http = new();
    private const string UploadUrl = "https://api-cloud.browserstack.com/app-automate/upload";

    public static async Task<string> UploadAppAsync(string filePath, string username, string accessKey)
    {
        if (!File.Exists(filePath))
            throw new FileNotFoundException($"App binary not found: {filePath}");

        using var form = new MultipartFormDataContent();
        await using var fs = File.OpenRead(filePath);
        var fileContent = new StreamContent(fs);
        fileContent.Headers.ContentType = MediaTypeHeaderValue.Parse("application/octet-stream");
        form.Add(fileContent, "file", Path.GetFileName(filePath));

        using var request = new HttpRequestMessage(HttpMethod.Post, UploadUrl) { Content = form };
        string credentials = Convert.ToBase64String(
            System.Text.Encoding.ASCII.GetBytes($"{username}:{accessKey}"));
        request.Headers.Authorization = new AuthenticationHeaderValue("Basic", credentials);

        using HttpResponseMessage response = await _http.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsStringAsync();
    }

    public static string GetAndroidAppId() =>
        ConfigReader.GetProperty("browserstack:android_app_id");

    public static string GetIosAppId() =>
        ConfigReader.GetProperty("browserstack:ios_app_id");
}
