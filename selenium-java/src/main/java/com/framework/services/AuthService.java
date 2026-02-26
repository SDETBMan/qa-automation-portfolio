package com.framework.services;

import com.framework.utils.ConfigReader;
import com.framework.utils.TokenManager;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;

import java.util.Map;

/**
 * AuthService: Suite-level bearer token generation.
 *
 * <p>WHY THIS CLASS EXISTS: Enterprise applications protect their APIs with bearer
 * tokens issued by an auth endpoint (OAuth 2.0, Spring Security, Django REST, etc.).
 * Rather than re-authenticating inside every {@code @Test} method, AuthService is
 * called once in {@code @BeforeSuite} — it posts credentials to the configured auth
 * endpoint, extracts the JWT from the response, and stores it in
 * {@link TokenManager} for all API tests to share.
 *
 * <p>GRACEFUL DEGRADATION: If {@code api.auth.url} is not set in config.properties,
 * generation is silently skipped. UI tests and unauthenticated API tests are completely
 * unaffected. This keeps the framework safe to run against environments like SauceDemo
 * that have no separate auth API.
 *
 * <p>TO WIRE UP TO A REAL AUTH API:
 * <ol>
 *   <li>Set {@code api.auth.url=https://api.yourapp.com/auth/login} in config.properties
 *       (or export {@code API_AUTH_URL} as an environment variable in CI).</li>
 *   <li>Supply credentials via {@code API_AUTH_USERNAME} and {@code API_AUTH_PASSWORD}
 *       environment variables — never commit real passwords to the properties file.</li>
 *   <li>Confirm the token field name returned by your API. Common patterns are handled
 *       automatically by {@link #extractToken(Response)} — see that method for details.</li>
 * </ol>
 *
 * <p>COMMON RESPONSE FORMATS SUPPORTED:
 * <ul>
 *   <li>{@code { "token": "..." }} — Django REST Framework, simple APIs</li>
 *   <li>{@code { "access_token": "..." }} — OAuth 2.0 standard</li>
 *   <li>{@code { "accessToken": "..." }} — Spring Boot, many enterprise APIs</li>
 * </ul>
 */
public class AuthService {

    private static final String AUTH_URL     = ConfigReader.getProperty("api.auth.url");
    private static final String API_USERNAME = ConfigReader.getProperty("api.auth.username");
    private static final String API_PASSWORD = ConfigReader.getProperty("api.auth.password");

    private AuthService() {}  // utility class — no instantiation

    /**
     * Generates a bearer token and stores it in {@link TokenManager}.
     *
     * <p>Called once from {@code @BeforeSuite} in BaseTest. Fails silently if the
     * auth endpoint is not configured, so the rest of the suite continues normally.
     */
    public static void generateToken() {
        if (AUTH_URL == null || AUTH_URL.isBlank()) {
            System.out.println("[AUTH] api.auth.url not configured — skipping token generation.");
            return;
        }

        System.out.println("[AUTH] Requesting bearer token from: " + AUTH_URL);

        try {
            // POST credentials as JSON. RestAssured serialises the Map automatically
            // when ContentType.JSON is set — no manual JSON string building needed.
            Response response = RestAssured
                    .given()
                        .contentType(ContentType.JSON)
                        .body(Map.of(
                                "username", API_USERNAME != null ? API_USERNAME : "",
                                "password", API_PASSWORD != null ? API_PASSWORD : ""
                        ))
                    .when()
                        .post(AUTH_URL)
                    .then()
                        .extract()
                        .response();

            if (response.getStatusCode() != 200) {
                System.err.println("[AUTH] Auth endpoint returned HTTP "
                        + response.getStatusCode() + " — token not stored.");
                return;
            }

            String token = extractToken(response);

            if (token == null || token.isBlank()) {
                System.err.println("[AUTH] Could not extract token from response. "
                        + "Expected field: token | access_token | accessToken. "
                        + "Add the correct field name to extractToken() if your API differs.");
                return;
            }

            // Prepend "Bearer " once here so every consumer just passes getToken() directly
            // to an Authorization header without any string manipulation in the test.
            TokenManager.setToken("Bearer " + token);
            System.out.println("[AUTH] Bearer token stored successfully.");

        } catch (Exception e) {
            // Log and continue — a missing token should not abort the entire suite.
            // UI tests and unauthenticated API tests must still run.
            System.err.println("[AUTH] Token generation failed: " + e.getMessage());
        }
    }

    /**
     * Extracts the raw JWT string from the auth response.
     *
     * <p>Tries the three most common bearer token field names in order.
     * If your target API uses a different key (e.g. {@code "id_token"} or
     * {@code "jwt"}), add it here — this is the only place that needs to change.
     *
     * @param response The HTTP response from the auth endpoint.
     * @return The raw token string, or {@code null} if none of the known fields matched.
     */
    private static String extractToken(Response response) {
        String token = response.jsonPath().getString("token");
        if (token != null) return token;

        token = response.jsonPath().getString("access_token");
        if (token != null) return token;

        return response.jsonPath().getString("accessToken");
    }
}
