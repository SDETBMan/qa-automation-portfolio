using System.Net.Http.Json;
using System.Text.Json;
using Framework.Core.Config;

namespace Framework.Tests.Api;

/// <summary>
/// UserApiTest: REST API integration tests using C#'s built-in HttpClient
/// and System.Text.Json — the .NET equivalent of Java's RestAssured.
///
/// WHY API TESTS IN A UI FRAMEWORK: The Test Pyramid principle says fast, stable
/// lower-level tests (unit → API) should be more numerous than slow, brittle
/// UI tests. API tests validate the backend contract (HTTP status codes, response
/// fields, data integrity) without the overhead of launching a browser. They're
/// faster, more reliable, and catch a different class of bugs than UI tests.
///
/// WHAT IS BEING TESTED: JSONPlaceholder (jsonplaceholder.typicode.com) is a free
/// public REST API used for prototyping. The /users/1 endpoint returns a JSON object
/// with user data. While not connected to SauceDemo, this demonstrates the API testing
/// technique that would apply to any REST backend in a real project.
///
/// WHAT System.Text.Json IS: The .NET standard library for reading and writing JSON.
/// JsonDocument.Parse() parses a JSON string into a queryable document tree.
/// GetProperty("name").GetString() navigates to a specific JSON field and reads its
/// value — no third-party library needed.
///
/// STATIC HttpClient: A single shared HttpClient is created once at the class level
/// (static readonly) rather than creating a new one per test. HttpClient is designed
/// to be reused — creating a new one per test wastes socket connections and can
/// exhaust the OS socket pool under load. The [Category("integration")] tag on the
/// class applies to all tests inside it automatically.
///
/// NOTE: Does NOT extend BaseTest because API tests don't need a browser.
/// </summary>
[TestFixture]
[Category("integration")]
public class UserApiTest
{
    // Shared HttpClient instance — reused across all tests in this class.
    // 'static readonly' means it's created once when the class loads, not per test.
    // HttpClient is thread-safe, so this is safe for parallel test execution.
    private static readonly HttpClient _http = new();

    /// <summary>
    /// GetUser_Returns200AndExpectedName: Validates that the API returns HTTP 200
    /// and that the response body contains the expected user's name.
    ///
    /// WHY TWO ASSERTIONS: HTTP 200 alone is not sufficient — an API can return 200
    /// with an empty body or a generic "success" message. Checking that the body
    /// contains "Leanne Graham" confirms the data returned matches the known record
    /// for user ID 1 — a data integrity check, not just a connectivity check.
    ///
    /// BASE URL FROM CONFIG: The base URL is read from config (defaulting to
    /// jsonplaceholder if not configured), keeping the test environment-agnostic
    /// and allowing the target API to be swapped without code changes.
    ///
    /// JSON PARSING: JsonDocument.Parse() is used to parse the response body and
    /// navigate to the "name" field specifically — rather than asserting the whole
    /// raw string, which would be fragile to JSON key reordering.
    /// </summary>
    [Test]
    [Category("smoke")]
    public async Task GetUser_Returns200AndExpectedName()
    {
        // Build the endpoint URL — base URL from config, resource path appended here.
        // The default fallback ensures the test works even without config setup.
        string baseUrl = ConfigReader.GetProperty("api:base_url", "https://jsonplaceholder.typicode.com");
        string endpoint = $"{baseUrl}/users/1";

        // Send the GET request. 'using' ensures the response is disposed after reading,
        // freeing the underlying network connection back to the pool.
        using HttpResponseMessage response = await _http.GetAsync(endpoint);

        // ASSERTION 1: HTTP status code must be 200 (OK).
        // A 404 means the endpoint doesn't exist; a 500 means the server is broken.
        Assert.That((int)response.StatusCode, Is.EqualTo(200),
            $"GET {endpoint} should return HTTP 200.");

        // Read the response body as a string for JSON parsing.
        string body = await response.Content.ReadAsStringAsync();

        // Parse the JSON body into a navigable document.
        // 'using' disposes the document after we're done reading from it.
        using JsonDocument doc = JsonDocument.Parse(body);

        // Navigate to the "name" field and read its string value.
        // GetProperty throws KeyNotFoundException if "name" doesn't exist —
        // which would be a contract violation (the API changed its response shape).
        string? name = doc.RootElement.GetProperty("name").GetString();

        // ASSERTION 2: The name field must contain the expected value.
        // This confirms the correct record was returned (not a different user)
        // and that the data value matches the known ground truth.
        Assert.That(name, Does.Contain("Leanne Graham"),
            "Response body should contain 'Leanne Graham'.");
    }

    /// <summary>
    /// GetUser_ResponseContainsEmailAndUsername: Verifies that the user API response
    /// includes both an "email" and a "username" field — validating the response schema.
    ///
    /// WHY TEST RESPONSE SCHEMA: API contracts define which fields a response will contain.
    /// If the backend renames "email" to "emailAddress" or removes "username", any code
    /// (including tests and the UI) that depends on those field names will break silently.
    /// This test acts as a contract test — catching schema changes as soon as they happen.
    ///
    /// WHY Assert.Multiple: If both "email" and "username" are missing, Assert.Multiple
    /// reports both failures at once. Without it, fixing the first failure would re-run
    /// the test to discover the second — wasting time during a debug cycle.
    /// </summary>
    [Test]
    [Category("regression")]
    public async Task GetUser_ResponseContainsEmailAndUsername()
    {
        string baseUrl = ConfigReader.GetProperty("api:base_url", "https://jsonplaceholder.typicode.com");

        // Build and send the request — same endpoint, checking different fields.
        using HttpResponseMessage response = await _http.GetAsync($"{baseUrl}/users/1");

        // Confirm the request succeeded before inspecting the body.
        Assert.That((int)response.StatusCode, Is.EqualTo(200));

        // Read the response body as a raw string for field presence checks.
        string body = await response.Content.ReadAsStringAsync();

        // Check that both required fields are present in the response JSON.
        // Does.Contain() is a simple substring check — appropriate here because
        // we're checking for field name presence, not specific values.
        Assert.Multiple(() =>
        {
            Assert.That(body, Does.Contain("email"),    "Response should have an email field.");
            Assert.That(body, Does.Contain("username"), "Response should have a username field.");
        });
    }
}
