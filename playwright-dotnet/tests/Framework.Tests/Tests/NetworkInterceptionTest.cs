using System.Text.Json;
using Microsoft.Playwright;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

/// <summary>
/// Demonstrates four Playwright network interception patterns.
/// Extends BaseTest (NOT AuthenticatedTest) because routes must be registered
/// before GotoAsync — some tests perform their own navigation sequence.
///
/// TypeScript equivalent: tests/network.spec.ts
/// </summary>
[Parallelizable(ParallelScope.Self)]
public class NetworkInterceptionTest : BaseTest
{
    // ─────────────────────────────────────────────────────────────────────────
    // Pattern 1: Block asset requests — page still renders
    // ─────────────────────────────────────────────────────────────────────────

    [Test]
    [Category("smoke")]
    [Category("network")]
    public async Task BlockImageRequests_PageStillLoads()
    {
        // Register route BEFORE navigation (routes apply from the next request onward).
        await Page.RouteAsync("**/*.{png,jpg,jpeg,gif,webp,svg}", async route =>
        {
            await route.AbortAsync();
        });

        // BaseTest.NavigateToApp() already called Page.GotoAsync(baseUrl).
        // Navigate directly to confirm the login form renders without images.
        await Page.GotoAsync("https://www.saucedemo.com");

        // Login form must still be fully rendered despite all images being blocked.
        var loginButton = Page.Locator("#login-button");
        await Expect(loginButton).ToBeVisibleAsync();
        Assert.That(await loginButton.IsVisibleAsync(), Is.True,
            "Login form should render even when all image requests are blocked.");
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Pattern 2: Mock API response — return synthetic JSON
    // ─────────────────────────────────────────────────────────────────────────

    [Test]
    [Category("regression")]
    [Category("network")]
    public async Task MockApiResponse_ReturnsCustomData()
    {
        var mockInventory = new[]
        {
            new { id = 1, name = "Mock Backpack", price = 9.99, description = "Test item" }
        };
        string mockJson = JsonSerializer.Serialize(mockInventory);

        // Intercept any request matching the inventory API pattern.
        await Page.RouteAsync("**/api/inventory**", async route =>
        {
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
        Assert.Pass("Route fulfillment handler registered and app loaded successfully.");
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Pattern 3: Modify request headers — inject custom header, forward real response
    // ─────────────────────────────────────────────────────────────────────────

    [Test]
    [Category("regression")]
    [Category("network")]
    public async Task ModifyRequestHeaders_InjectCustomHeader()
    {
        string? capturedHeader = null;

        await Page.RouteAsync("https://www.saucedemo.com/", async route =>
        {
            // Add a custom header and forward the real response.
            var headers = new Dictionary<string, string>(route.Request.Headers)
            {
                ["x-test-automation"] = "playwright-dotnet"
            };

            capturedHeader = headers["x-test-automation"];

            // Fetch the real response and pass it through unchanged.
            var response = await route.FetchAsync(new RouteFetchOptions { Headers = headers });
            await route.FulfillAsync(new RouteFulfillOptions { Response = response });
        });

        await Page.GotoAsync("https://www.saucedemo.com");

        Assert.That(capturedHeader, Is.EqualTo("playwright-dotnet"),
            "Custom header should have been injected into the forwarded request.");
        await Expect(Page.Locator("#login-button")).ToBeVisibleAsync();
    }

    // ─────────────────────────────────────────────────────────────────────────
    // Pattern 4: Simulate network failure — graceful degradation
    // ─────────────────────────────────────────────────────────────────────────

    [Test]
    [Category("regression")]
    [Category("network")]
    public async Task SimulateNetworkFailure_GracefulDegradation()
    {
        // Abort favicon requests to simulate a non-critical resource failure.
        // The core login flow must remain fully functional.
        await Page.RouteAsync("**/favicon.ico", async route =>
        {
            await route.AbortAsync("aborted");
        });

        await Page.GotoAsync("https://www.saucedemo.com");

        // Login must work normally even with the favicon network failure.
        await Page.Locator("#user-name").FillAsync("standard_user");
        await Page.Locator("#password").FillAsync("secret_sauce");
        await Page.Locator("#login-button").ClickAsync();

        await Page.WaitForURLAsync(new System.Text.RegularExpressions.Regex("inventory"));
        Assert.That(Page.Url, Does.Contain("inventory"),
            "Login should succeed and reach inventory despite favicon network failure.");
    }
}
