using System.Net.Http.Headers;
using Framework.Core.Config;

namespace Framework.Core.Utils;

/// <summary>
/// Utility class for integrating with BrowserStack App Automate.
///
/// Why this exists: BrowserStack is a cloud-based device lab that lets you run
/// mobile app tests on real physical iOS and Android devices without owning those
/// devices. Before a mobile test session can start, the app binary (.apk for Android,
/// .ipa for iOS) must be uploaded to BrowserStack's servers. This class handles
/// that upload step and provides the resulting "app_url" — a BrowserStack-internal
/// reference like "bs://abc123..." that is then passed as a capability to Appium.
///
/// Workflow:
///   1. Build the app binary in CI
///   2. Call UploadAppAsync() to upload it and get an app_url
///   3. Pass the app_url as the "app" capability when starting an Appium session
///
/// Authentication: BrowserStack uses HTTP Basic Auth with your username and access key.
/// These should be stored in environment variables (never in source code).
///
/// Configuration keys (appsettings.json or environment variables):
///   browserstack:android_app_id — the app_url returned after an Android upload
///   browserstack:ios_app_id     — the app_url returned after an iOS upload
/// </summary>
public static class BrowserStackUtils
{
    // Shared HttpClient instance — reusing one client avoids socket exhaustion
    // when uploading multiple times within the same process lifetime.
    private static readonly HttpClient _http = new();

    // The BrowserStack REST endpoint for uploading app binaries.
    // This is the App Automate upload URL documented in BrowserStack's API docs.
    private const string UploadUrl = "https://api-cloud.browserstack.com/app-automate/upload";

    /// <summary>
    /// Uploads a local app binary file to BrowserStack and returns the raw JSON
    /// response body, which contains the "app_url" needed for test sessions.
    ///
    /// The upload uses multipart/form-data — the same encoding a browser uses when
    /// you submit an HTML file upload form. This is required by the BrowserStack API.
    ///
    /// Parameters:
    ///   filePath  — absolute path to the .apk or .ipa file on disk
    ///   username  — your BrowserStack username (from Account Settings)
    ///   accessKey — your BrowserStack access key (from Account Settings)
    ///
    /// Returns: raw JSON string, e.g. {"app_url":"bs://abc123...","custom_id":null,...}
    /// Throws: FileNotFoundException if the binary does not exist at filePath.
    /// </summary>
    public static async Task<string> UploadAppAsync(string filePath, string username, string accessKey)
    {
        // Validate the file exists before making a network call — fail fast with a
        // clear message rather than getting a cryptic HTTP 400 from BrowserStack.
        if (!File.Exists(filePath))
            throw new FileNotFoundException($"App binary not found: {filePath}");

        // Build the multipart form body.
        // "using" ensures the form and file stream are disposed after the request,
        // releasing the file lock and memory promptly.
        using var form = new MultipartFormDataContent();
        await using var fs = File.OpenRead(filePath);

        // Wrap the file stream as HTTP content with the correct MIME type.
        var fileContent = new StreamContent(fs);
        fileContent.Headers.ContentType = MediaTypeHeaderValue.Parse("application/octet-stream");

        // "file" is the form field name expected by the BrowserStack upload API.
        form.Add(fileContent, "file", Path.GetFileName(filePath));

        // Attach the Basic Auth credentials.
        // Base64 encoding of "username:accessKey" is the HTTP Basic Auth standard.
        using var request = new HttpRequestMessage(HttpMethod.Post, UploadUrl) { Content = form };
        string credentials = Convert.ToBase64String(
            System.Text.Encoding.ASCII.GetBytes($"{username}:{accessKey}"));
        request.Headers.Authorization = new AuthenticationHeaderValue("Basic", credentials);

        // Send the file and wait for BrowserStack to confirm the upload.
        using HttpResponseMessage response = await _http.SendAsync(request);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsStringAsync();
    }

    /// <summary>
    /// Returns the BrowserStack app_url for the Android build configured in appsettings.json.
    /// This is typically set to the "app_url" value returned by a previous UploadAppAsync call
    /// and stored as a config property so tests can reference it without re-uploading.
    /// </summary>
    public static string GetAndroidAppId() =>
        ConfigReader.GetProperty("browserstack:android_app_id");

    /// <summary>
    /// Returns the BrowserStack app_url for the iOS build configured in appsettings.json.
    /// Same pattern as GetAndroidAppId but for iOS (.ipa) binaries.
    /// </summary>
    public static string GetIosAppId() =>
        ConfigReader.GetProperty("browserstack:ios_app_id");
}
