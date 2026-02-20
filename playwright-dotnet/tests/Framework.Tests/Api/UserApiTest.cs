using System.Net.Http.Json;
using System.Text.Json;
using Framework.Core.Config;

namespace Framework.Tests.Api;

/// <summary>
/// REST API integration test using HttpClient + System.Text.Json.
/// Mirrors the Java UserApiTest backed by REST Assured.
/// </summary>
[TestFixture]
[Category("integration")]
public class UserApiTest
{
    private static readonly HttpClient _http = new();

    [Test]
    [Category("smoke")]
    public async Task GetUser_Returns200AndExpectedName()
    {
        string baseUrl = ConfigReader.GetProperty("api:base_url", "https://jsonplaceholder.typicode.com");
        string endpoint = $"{baseUrl}/users/1";

        using HttpResponseMessage response = await _http.GetAsync(endpoint);

        Assert.That((int)response.StatusCode, Is.EqualTo(200),
            $"GET {endpoint} should return HTTP 200.");

        string body = await response.Content.ReadAsStringAsync();
        using JsonDocument doc = JsonDocument.Parse(body);

        string? name = doc.RootElement.GetProperty("name").GetString();
        Assert.That(name, Does.Contain("Leanne Graham"),
            "Response body should contain 'Leanne Graham'.");
    }

    [Test]
    [Category("regression")]
    public async Task GetUser_ResponseContainsEmailAndUsername()
    {
        string baseUrl = ConfigReader.GetProperty("api:base_url", "https://jsonplaceholder.typicode.com");
        using HttpResponseMessage response = await _http.GetAsync($"{baseUrl}/users/1");

        Assert.That((int)response.StatusCode, Is.EqualTo(200));

        string body = await response.Content.ReadAsStringAsync();
        Assert.Multiple(() =>
        {
            Assert.That(body, Does.Contain("email"),    "Response should have an email field.");
            Assert.That(body, Does.Contain("username"), "Response should have a username field.");
        });
    }
}
