package com.framework.utils;

/**
 * TokenManager: Suite-scoped bearer token holder.
 *
 * <p>WHY THIS CLASS EXISTS: In test suites that hit authenticated APIs, the naive
 * approach is to call the login endpoint inside every {@code @Test} method. For a
 * suite of 100 API tests that means 100 redundant network round-trips before a
 * single real assertion runs. TokenManager solves this by acting as a shared in-memory
 * store: {@link com.framework.services.AuthService} generates the token once in
 * {@code @BeforeSuite}, writes it here, and every API test reads it for free.
 *
 * <p>WHY {@code volatile}: The {@code @BeforeSuite} write happens on the main TestNG
 * thread before any test threads start. {@code volatile} guarantees that write is
 * flushed to main memory immediately, so all parallel test threads see the token
 * rather than a stale cached copy from their local CPU cache. It is lighter-weight
 * than {@code synchronized} for a single-write / many-read pattern.
 *
 * <p>USAGE IN API TESTS:
 * <pre>{@code
 *   if (TokenManager.hasToken()) {
 *       given().header("Authorization", TokenManager.getToken())
 *              .when().get(endpoint)
 *              .then().statusCode(200);
 *   }
 * }</pre>
 */
public class TokenManager {

    // volatile: written once in @BeforeSuite, read by many parallel test threads
    private static volatile String authToken;

    private TokenManager() {}  // utility class — no instantiation

    /**
     * Stores the bearer token. Called once from
     * {@link com.framework.services.AuthService} after a successful auth response.
     * The value is expected to already include the "Bearer " prefix.
     */
    public static void setToken(String token) {
        authToken = token;
    }

    /**
     * Returns the stored bearer token in {@code "Bearer {jwt}"} format,
     * or {@code null} if no token has been generated for this suite run.
     * Always guard with {@link #hasToken()} before passing this to a header.
     */
    public static String getToken() {
        return authToken;
    }

    /**
     * Returns {@code true} if a token has been generated and is ready to use.
     * API tests should call this before attaching an Authorization header so they
     * degrade gracefully on environments where auth is not configured.
     */
    public static boolean hasToken() {
        return authToken != null && !authToken.isBlank();
    }

    /**
     * Clears the stored token. Called from {@code @AfterSuite} in BaseTest to
     * prevent a stale token from persisting if the JVM is reused across suite runs
     * (e.g. in certain IDE or Maven Surefire fork configurations).
     */
    public static void clearToken() {
        authToken = null;
    }
}
