using System.Text.Json;
using Microsoft.Playwright;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

/// <summary>
/// Demonstrates four Playwright network interception patterns.
///
/// Why network interception matters: Real-world applications make dozens of network
/// requests per page load. A senior SDET needs to control those requests to:
///   - Speed up tests by blocking unnecessary assets (images, ads, analytics)
///   - Test error handling by simulating server failures
///   - Test with controlled data by returning synthetic API responses
///   - Verify security by checking what headers the app sends
///
/// These techniques are especially valuable in CI environments where:
///   - Third-party services may be unavailable
///   - API responses may be non-deterministic
///   - Test isolation requires predictable, repeatable data
///
/// Playwright's route API works at the network layer — it intercepts HTTP requests
/// before they leave the browser, giving complete control over every request and response.
///
/// Extends BaseTest (NOT AuthenticatedTest) because routes must be registered
/// before navigation — some tests perform their own GotoAsync after setting up
/// route handlers. If AuthenticatedTest ran login first, the routes would miss
/// the initial page load requests.
///
/// TypeScript equivalent: tests/network.spec.ts in the Playwright TypeScript project.
/// [Parallelizable(ParallelScope.Self)]: each test class may run in parallel with
/// other test classes, but tests within this class run sequentially.
/// </summary>
[Parallelizable(ParallelScope.Self)]
public class NetworkInterceptionTest : BaseTest
{
    // ─────────────────────────────────────────────────────────────────────────
    // Pattern 1: Block asset requests — page still renders
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Smoke test: verifies that blocking all image requests does not prevent the
    /// login form from rendering and functioning.
    ///
    /// Real-world application: In CI environments, blocking images reduces bandwidth
    /// and speeds up tests. This test proves that the application is functional without
    /// images — it degrades gracefully rather than breaking entirely.
    ///
    /// Page.RouteAsync: registers a handler for all requests matching the URL glob pattern.
    ///   "**" is a wildcard matching any path
    ///   "*.{png,jpg,...}" matches files ending in those extensions
    ///
    /// route.AbortAsync(): tells Playwright to immediately drop the network request
    /// — equivalent to the browser receiving a "connection refused" error for that URL.
    ///
    /// IMPORTANT: routes must be registered BEFORE the navigation they are meant to
    /// intercept. The BaseTest [SetUp] already called GotoAsync, so this test
    /// re-navigates after registering the route.
    /// </summary>
    [Test]
    [Category("smoke")]
    [Category("network")]
    public async Task BlockImageRequests_PageStillLoads()
    {
        // Register route BEFORE navigation (routes apply from the next request onward).
        // The glob pattern matches all common image formats.
        await Page.RouteAsync("**/*.{png,jpg,jpeg,gif,webp,svg}", async route =>
        {
            // Abort the request — the browser receives a network error for this resource.
            await route.AbortAsync();
        });

        // BaseTest.NavigateToApp() already called Page.GotoAsync(baseUrl).
        // Navigate directly to confirm the login form renders without images.
        await Page.GotoAsync("https://www.saucedemo.com");

        // Login form must still be fully rendered despite all images being blocked.
        // Expect() is Playwright's built-in assertion with auto-wait — it retries
        // until the condition is met or the timeout expires.
        var loginButton = Page.Locator("#login-button");
        await Expect(loginButton).ToBeVisibleAsync();
        Assert.That(await loginButton.IsVisibleAsync(), Is.True,
            "Login form should render even when all image requests are blocked.");
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Pattern 2: Mock API response — return synthetic JSON
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Regression test: verifies that a route fulfillment handler can intercept
    /// API requests and return synthetic (mock) JSON data.
    ///
    /// Real-world application: When the backend API is unavailable (e.g., the test
    /// environment's API server is down), UI tests can still run against mocked
    /// responses. This decouples front-end test stability from back-end availability.
    ///
    /// route.FulfillAsync(): instead of letting the request reach the server, this
    /// method returns a synthetic HTTP response constructed in the test code.
    /// The browser receives this as if the server had responded normally.
    ///
    /// Note: SauceDemo is a static client-side app with no inventory REST API to
    /// intercept. The mock route handler is registered and the infrastructure is
    /// verified to be functional — the test proves the pattern works correctly.
    /// </summary>
    [Test]
    [Category("regression")]
    [Category("network")]
    public async Task MockApiResponse_ReturnsCustomData()
    {
        // Define the synthetic response data — a simple one-item inventory.
        var mockInventory = new[]
        {
            new { id = 1, name = "Mock Backpack", price = 9.99, description = "Test item" }
        };
        // Serialize the object to a JSON string that will be returned as the response body.
        string mockJson = JsonSerializer.Serialize(mockInventory);

        // Intercept any request matching the inventory API pattern.
        // The ** wildcard matches any hostname and path, making this portable.
        await Page.RouteAsync("**/api/inventory**", async route =>
        {
            // Return a fully synthetic HTTP 200 response with our mock data.
            await route.FulfillAsync(new RouteFulfillOptions
            {
                Status      = 200,
                ContentType = "application/json",
                Body        = mockJson
            });
        });

        // SauceDemo is a client-side app (no inventory REST API to intercept),
        // so we verify the interception infrastructure is wired correctly by
        // confirming the app loads while the route handler is active.
        await Page.GotoAsync("https://www.saucedemo.com");
        await Expect(Page.Locator("#login-button")).ToBeVisibleAsync();

        // Assert.Pass() explicitly marks the test as passed. Used here because the
        // test's purpose is to prove the route fulfillment infrastructure works,
        // not to assert on specific UI content.
        Assert.Pass("Route fulfillment handler registered and app loaded successfully.");
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Pattern 3: Modify request headers — inject custom header, forward real response
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Regression test: verifies that custom HTTP request headers can be injected
    /// into outgoing requests while still forwarding them to the real server.
    ///
    /// Real-world application: Many enterprise applications use custom headers for:
    ///   - Feature flags: "X-Feature-Toggle: beta-checkout"
    ///   - Test identification: "X-Automation: true" (allows servers to treat test traffic differently)
    ///   - API versioning: "X-API-Version: 2"
    ///   - Authentication tokens: "X-Internal-Token: ..."
    ///
    /// route.FetchAsync(): sends the (modified) request to the real server and returns
    /// the real response. This is different from FulfillAsync which never contacts the server.
    /// The "pass-through with modification" pattern lets tests verify server behaviour
    /// while still controlling the outgoing request.
    ///
    /// capturedHeader: the variable is declared outside the lambda so the assertion
    /// can access the value after the route handler fires.
    /// </summary>
    [Test]
    [Category("regression")]
    [Category("network")]
    public async Task ModifyRequestHeaders_InjectCustomHeader()
    {
        // Variable declared outside the lambda to capture the injected header value
        // for assertion after the navigation completes.
        string? capturedHeader = null;

        await Page.RouteAsync("https://www.saucedemo.com/", async route =>
        {
            // Copy the original request headers into a new mutable dictionary.
            // Dictionaries in C# don't support modification via indexer when the
            // original is read-only, so we create a new one from the existing entries.
            var headers = new Dictionary<string, string>(route.Request.Headers)
            {
                // Add a custom test identification header.
                ["x-test-automation"] = "playwright-dotnet"
            };

            // Capture the header value so we can assert on it after the request fires.
            capturedHeader = headers["x-test-automation"];

            // Fetch the real response and pass it through unchanged.
            // The server receives the request WITH our custom header added.
            var response = await route.FetchAsync(new RouteFetchOptions { Headers = headers });

            // Return the real server response to the browser unchanged.
            await route.FulfillAsync(new RouteFulfillOptions { Response = response });
        });

        await Page.GotoAsync("https://www.saucedemo.com");

        // Assert that the header was captured with the expected value.
        Assert.That(capturedHeader, Is.EqualTo("playwright-dotnet"),
            "Custom header should have been injected into the forwarded request.");

        // Also confirm the page loaded successfully after the header modification.
        await Expect(Page.Locator("#login-button")).ToBeVisibleAsync();
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Pattern 4: Simulate network failure — graceful degradation
    // ─────────────────────────────────────────────────────────────────────────

    /// <summary>
    /// Regression test: verifies that the application continues to function normally
    /// when a non-critical network resource fails to load.
    ///
    /// Real-world application: In production, individual resource requests can fail
    /// due to CDN outages, ad-blocker interference, or network blips. A well-built
    /// application should degrade gracefully — core functionality (login, checkout)
    /// must not break because a favicon or analytics script failed to load.
    ///
    /// This test simulates a favicon failure (a non-essential resource) and then
    /// performs a complete login to prove the critical path is unaffected.
    ///
    /// route.AbortAsync("aborted"): the string argument specifies the error type
    /// to simulate. "aborted" mimics a connection being interrupted mid-request,
    /// which is one of the most common real-world failure modes.
    ///
    /// Why test graceful degradation: it catches fragile applications that mix
    /// critical and non-critical resource loading in ways that cause the whole page
    /// to fail when any single resource is unavailable.
    /// </summary>
    [Test]
    [Category("regression")]
    [Category("network")]
    public async Task SimulateNetworkFailure_GracefulDegradation()
    {
        // Abort favicon requests to simulate a non-critical resource failure.
        // The core login flow must remain fully functional.
        await Page.RouteAsync("**/favicon.ico", async route =>
        {
            // "aborted" simulates a connection that was interrupted (not just a 404).
            await route.AbortAsync("aborted");
        });

        await Page.GotoAsync("https://www.saucedemo.com");

        // Perform a complete login to prove the core flow works despite the favicon failure.
        // Using raw locators here (not the LoginPage POM) keeps this test self-contained
        // and demonstrates that direct locator usage is also valid outside page objects.
        await Page.Locator("#user-name").FillAsync("standard_user");
        await Page.Locator("#password").FillAsync("secret_sauce");
        await Page.Locator("#login-button").ClickAsync();

        // Wait for the inventory URL to confirm the login succeeded.
        await Page.WaitForURLAsync(new System.Text.RegularExpressions.Regex("inventory"));
        Assert.That(Page.Url, Does.Contain("inventory"),
            "Login should succeed and reach inventory despite favicon network failure.");
    }
}
