package com.framework.utils;

/**
 * StringFormatter: Provides string transformation utilities for test infrastructure purposes.
 *
 * WHY THIS CLASS EXISTS:
 * Throughout a test framework, strings need to be formatted in consistent, predictable ways:
 *   - Test names need to be "normalized" for use as file names (spaces replaced with underscores)
 *   - Environment names need to be mapped to their corresponding base URLs
 *
 * Centralizing these transformations in a utility class rather than repeating them inline
 * ensures consistency and makes them independently unit-testable.
 *
 * WHAT IS TESTED AGAINST THIS CLASS:
 * FrameworkUnitTest directly validates formatTestName() and getEnvironmentUrl(), including
 * edge cases like null input and case-insensitive matching. This is a good example of
 * testing pure utility logic without any browser or network dependency.
 *
 * For recruiters: Small, focused utility classes with clear unit tests are a sign of clean
 * code architecture. They show the engineer thinks about testability and reuse.
 */
public class StringFormatter {

    /**
     * Converts a test name string into a file-system-safe, normalized identifier.
     *
     * WHY THIS TRANSFORMATION:
     * Test names often contain spaces and mixed case: " Login Test Success ".
     * File names for screenshots, reports, and logs cannot contain leading/trailing spaces.
     * Allure and other reporting tools work best with lowercase, underscore-separated names.
     * This method produces: "login_test_success" — clean, unique, and file-system safe.
     *
     * THE TRANSFORMATION STEPS:
     *   1. null check → return "" (prevents NullPointerException in callers)
     *   2. trim()     → removes leading and trailing whitespace
     *   3. replaceAll(" ", "_") → converts spaces to underscores (regex: single space)
     *   4. toLowerCase()  → normalizes case for consistent naming
     *
     * @param name The raw test name, possibly with spaces and mixed case
     * @return A normalized, file-safe identifier; "" if name is null
     */
    public static String formatTestName(String name) {
        if (name == null) return "";
        return name.trim().replaceAll(" ", "_").toLowerCase();
    }

    /**
     * Maps a short environment identifier to the full base URL for that environment.
     *
     * WHY THIS PATTERN (switch/case instead of config file):
     * Environment URL mapping is a finite, well-known set of values that rarely changes.
     * For this type of mapping, a switch statement in code is cleaner and more readable
     * than a config file entry. It also makes the full set of supported environments
     * immediately visible in a single method rather than scattered across config files.
     *
     * WHY A NULL CHECK:
     * If a null environment is passed (e.g., a missing config value), we return a default URL
     * rather than crashing with a NullPointerException. Defensive null handling is especially
     * important in utility methods that may be called from many places.
     *
     * WHY env.toLowerCase() BEFORE THE SWITCH:
     * Callers might pass "QA", "qa", or "Qa" — all should map to the same URL. Normalizing to
     * lowercase before the switch ensures case-insensitive matching without needing a separate
     * case for each capitalization variant.
     *
     * @param env A short environment name: "dev", "qa", "staging", or null/anything else for prod
     * @return The full base URL for the specified environment
     */
    public static String getEnvironmentUrl(String env) {
        if (env == null) {
            return "https://default.example.com";
        }

        switch (env.toLowerCase()) {
            case "dev":
                return "https://dev.example.com";
            case "qa":
                return "https://qa.example.com";
            case "staging":
                return "https://staging.example.com";
            default:
                // Any unrecognized value falls through to production URL.
                // This is intentional — unknown environments default to the safest/most stable one.
                return "https://prod.example.com";
        }
    }
}
