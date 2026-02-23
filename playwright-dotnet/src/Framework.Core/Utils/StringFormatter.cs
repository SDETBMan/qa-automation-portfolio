using Framework.Core.Config;

namespace Framework.Core.Utils;

/// <summary>
/// Utility class providing string formatting helpers used across the test framework.
///
/// Why this exists: Several framework operations need consistent string transformations:
///   - Allure and other reporting tools require test names without spaces (slugs)
///   - Tests must resolve the correct base URL based on the target environment
///     without hard-coding environment-specific URLs inside test logic
///
/// Keeping these transformations in one utility class ensures:
///   - All reporters format test names the same way
///   - Switching environments only requires changing one config value, not editing tests
///   - The logic is unit-testable in isolation (see FrameworkUnitTest.cs)
/// </summary>
public static class StringFormatter
{
    /// <summary>
    /// Converts a human-readable test name into a filesystem- and URL-safe slug.
    /// Trims surrounding whitespace, converts to lowercase, and replaces spaces
    /// with underscores.
    ///
    /// Why this is needed: Screenshot files, trace archives, and Allure report IDs
    /// must not contain spaces or uppercase letters to be safely used in file paths
    /// and URLs on all operating systems (especially Linux-based CI agents).
    ///
    /// Example: "My Test Case" → "my_test_case"
    /// Example: "  UPPER CASE  " → "upper_case"
    /// Returns an empty string for null/whitespace input rather than throwing.
    /// </summary>
    public static string FormatTestName(string testName)
    {
        // Return early for blank input — avoids NullReferenceException downstream
        // and produces a safe empty string rather than "_" or similar.
        if (string.IsNullOrWhiteSpace(testName)) return string.Empty;

        // Chain: Trim() removes leading/trailing spaces → ToLowerInvariant() lowercases
        // using culture-invariant rules (important for CI agents with non-English locales)
        // → Replace(' ', '_') converts remaining internal spaces to underscores.
        return testName.Trim().ToLowerInvariant().Replace(' ', '_');
    }

    /// <summary>
    /// Returns the base URL for the application under test based on the target environment name.
    ///
    /// Why this exists: Tests should not contain environment-specific URLs because the
    /// same test suite runs against multiple environments in a typical CI/CD pipeline:
    ///   - Developer runs against "dev" on their laptop
    ///   - Pull request CI runs against "staging" for integration testing
    ///   - Release CI runs against "prod" for smoke testing after deployment
    ///
    /// The switch expression maps well-known environment names to their URLs.
    /// For unrecognised names (e.g., a custom feature branch URL), it falls back to
    /// the "url" config key so the caller can set any URL without changing this code.
    ///
    /// The "or" pattern in the switch ("prod" or "production") handles both short
    /// and full forms of the same environment name, preventing common typo mismatches.
    /// </summary>
    public static string GetEnvironmentUrl(string environment)
    {
        // C# switch expression (introduced in C# 8) — more concise than if/else chains.
        // The ?. operator safely handles a null environment argument before ToLowerInvariant().
        return environment?.ToLowerInvariant() switch
        {
            // Both "prod" and "production" resolve to the live site URL.
            "prod" or "production" => "https://www.saucedemo.com",

            // Staging URL — used for pre-release integration testing.
            "staging"              => "https://staging.saucedemo.com",

            // Dev URL — used for feature branch or local development testing.
            "dev"                  => "https://dev.saucedemo.com",

            // Default case: for any unrecognised environment name, read the URL
            // from config. This allows CI to set any arbitrary URL via an env var
            // without requiring a code change.
            _                      => ConfigReader.GetProperty("url", "https://www.saucedemo.com")
        };
    }
}
