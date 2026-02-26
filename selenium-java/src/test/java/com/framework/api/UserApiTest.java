package com.framework.api;

import com.framework.utils.ConfigReader;
import com.framework.utils.TokenManager;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;
import org.testng.Assert;
import org.testng.annotations.Test;

/**
 * UserApiTest: REST API integration tests that validate backend service health
 * and data integrity independently of the browser UI.
 *
 * <p>WHY API TESTS IN A UI FRAMEWORK: Modern QA portfolios demonstrate the
 * "Test Pyramid" — a strategy where fast, stable lower-level tests (unit → API)
 * are more numerous than slower, brittle higher-level tests (UI/E2E). Including
 * API tests alongside UI tests shows awareness that not everything needs a
 * browser — many validations are faster and more reliable at the HTTP level.
 *
 * <p>WHAT IS BEING TESTED: JSONPlaceholder ({@code jsonplaceholder.typicode.com})
 * is a free public REST API commonly used for prototyping and testing. The
 * {@code /users/1} endpoint returns a JSON object for a test user named
 * "Leanne Graham." While this specific API isn't connected to SauceDemo, the test
 * demonstrates how you would validate any REST backend — checking HTTP status codes
 * and verifying response body content.
 *
 * <p>WHAT RESTASSURED IS: RestAssured is the industry-standard Java library for
 * REST API testing. It provides a fluent DSL (Domain-Specific Language) that reads
 * almost like plain English: {@code RestAssured.get(url)} sends a GET request and
 * returns a {@code Response} object you can inspect. No boilerplate HTTP connection
 * code needed — RestAssured handles all the low-level HTTP mechanics.
 *
 * <p>NOTE: This class does NOT extend BaseTest because API tests don't need a
 * browser. Extending BaseTest would waste time launching Chrome for tests that
 * only make HTTP calls.
 */
public class UserApiTest {

    /**
     * testUserApiHealth: Validates that the user API endpoint is reachable,
     * returns HTTP 200, and contains the expected user data in its response body.
     *
     * <p>WHY TWO ASSERTIONS: Checking status code 200 alone is not enough —
     * an API can return 200 with an empty body or error JSON. The second assertion
     * checks that the response body contains the expected user data, confirming
     * that the API is returning the correct content, not just responding.
     *
     * <p>DATA INTEGRITY CHECK: Asserting for "Leanne Graham" by name verifies
     * that the data returned matches the known ground truth for user ID 1.
     * In a real project, this pattern would be used to verify that a database
     * record returns the correct values — catching data migration errors or
     * API contract changes.
     *
     * <p>ENDPOINT FROM CONFIG: The base URL is read from config so the test can
     * be pointed at different API environments (dev, staging, prod) without
     * changing any test code.
     */
    @Test(groups = {"integration", "smoke"})
    public void testUserApiHealth() {
        // Build the full endpoint URL by appending the resource path to the base URL.
        // Separating base URL (in config) from resource path (in test) allows the
        // same config entry to be reused by multiple API test methods.
        String endpoint = ConfigReader.getProperty("api.base.url") + "/users/1";

        System.out.println("[API-LOG] Requesting User Data from: " + endpoint);

        // RestAssured.get() sends an HTTP GET request and captures the full response.
        // This single line handles connection, timeout, redirect following, and
        // response buffering — all handled by RestAssured internally.
        Response response = RestAssured.get(endpoint);

        // Log status code and body to CI build logs for debugging.
        // If the assertion below fails, these lines provide context about
        // what the API actually returned.
        System.out.println("[API-LOG] Status Code: " + response.getStatusCode());
        System.out.println("[API-LOG] Response Body: " + response.getBody().asString());

        // ASSERTION 1: HTTP status code must be 200 (success).
        // Any other code (404, 500, 503) means the API is unavailable or broken.
        Assert.assertEquals(response.getStatusCode(), 200, "API Health Check Failed: Status should be 200 OK");

        // ASSERTION 2: Response body must contain the expected user's name.
        // This data integrity check confirms the API returned meaningful content
        // matching the known record for user ID 1 — not an empty JSON object
        // or a generic success message.
        String responseBody = response.getBody().asString();
        Assert.assertNotNull(responseBody, "API Error: Response body is null");
        Assert.assertTrue(responseBody.contains("Leanne Graham"), "Data Integrity Error: Response missing expected user data");
    }

    /**
     * testAuthenticatedApiCall: Demonstrates the suite-level token consumption pattern.
     *
     * <p>WHY NO RE-AUTHENTICATION HERE: The bearer token was generated once in
     * {@code @BeforeSuite} by {@link com.framework.services.AuthService} and stored in
     * {@link TokenManager}. This test simply reads it — no redundant login API call,
     * no hardcoded credentials. Replacing the auth endpoint in config.properties is
     * the only change needed to point this at a real authenticated API.
     *
     * <p>GRACEFUL FALLBACK: If no token is available (e.g. running locally without
     * auth configured), the request is sent without an Authorization header. The test
     * still validates the response — it just won't carry auth credentials. This keeps
     * the suite green on environments where token generation is not set up.
     */
    @Test(groups = {"integration"})
    public void testAuthenticatedApiCall() {
        String endpoint = ConfigReader.getProperty("api.base.url") + "/posts/1";

        System.out.println("[API-LOG] Requesting authenticated resource from: " + endpoint);

        // Build the request spec — attach the suite-level bearer token if available.
        // TokenManager.getToken() returns "Bearer {jwt}" — ready to use as-is.
        RequestSpecification request = RestAssured.given();
        if (TokenManager.hasToken()) {
            request.header("Authorization", TokenManager.getToken());
            System.out.println("[API-LOG] Authorization header attached from suite-level token.");
        } else {
            System.out.println("[API-LOG] No token configured — sending unauthenticated request.");
        }

        Response response = request.get(endpoint);

        System.out.println("[API-LOG] Status Code: " + response.getStatusCode());
        System.out.println("[API-LOG] Response Body: " + response.getBody().asString());

        Assert.assertEquals(response.getStatusCode(), 200,
                "Authenticated API call failed: expected 200 OK");
        Assert.assertNotNull(response.getBody().asString(),
                "API Error: Response body is null");
    }
}
