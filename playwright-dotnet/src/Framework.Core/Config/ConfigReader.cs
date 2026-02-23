using Microsoft.Extensions.Configuration;

namespace Framework.Core.Config;

/// <summary>
/// Central configuration reader for the entire test framework.
///
/// Why this exists: Tests need to run in multiple environments (local dev, CI, staging,
/// production) without changing any code. This class reads settings from a JSON file
/// and allows environment variables to override those values at runtime — the standard
/// "12-factor app" pattern used in professional CI/CD pipelines.
///
/// Priority order (highest wins):
///   1. Environment variable  — set by CI/CD (e.g., GitHub Actions, Jenkins)
///   2. appsettings.json      — checked into the repo as a safe default
///   3. defaultValue argument — hardcoded fallback inside calling code
///
/// Usage examples:
///   ConfigReader.GetProperty("url")                  → base app URL
///   ConfigReader.GetProperty("app:username")         → nested JSON key (colon = hierarchy)
///   ConfigReader.GetInt("retry:max", 1)              → integer with a default of 1
///   Environment var override: APP__USERNAME=myuser   → double-underscore replaces colon
/// </summary>
public static class ConfigReader
{
    // IConfiguration is Microsoft's standard abstraction for reading config from
    // multiple sources (JSON, env vars, Azure Key Vault, etc.). We build it once
    // at startup (static constructor) and reuse the single instance across all tests.
    private static readonly IConfiguration _config;

    /// <summary>
    /// Static constructor — runs exactly once when the class is first used.
    /// Builds the configuration pipeline by layering sources in priority order:
    ///   1. appsettings.json (optional = won't crash if the file is missing)
    ///   2. Environment variables (added last so they override the JSON file)
    /// AppContext.BaseDirectory points to the test output folder where the JSON
    /// file is copied by MSBuild, so no hardcoded path is needed.
    /// </summary>
    static ConfigReader()
    {
        _config = new ConfigurationBuilder()
            .SetBasePath(AppContext.BaseDirectory)
            .AddJsonFile("appsettings.json", optional: true, reloadOnChange: false)
            .AddEnvironmentVariables()
            .Build();
    }

    /// <summary>
    /// Returns the string value for the given configuration key.
    /// Returns <paramref name="defaultValue"/> (empty string by default) when the
    /// key is not found in either the JSON file or environment variables.
    ///
    /// Key format: colon-separated hierarchy mirrors the JSON structure.
    ///   JSON:   { "app": { "username": "standard_user" } }
    ///   Key:    "app:username"
    ///   EnvVar: APP__USERNAME  (double-underscore replaces the colon on most OSes)
    /// </summary>
    public static string GetProperty(string key, string defaultValue = "")
    {
        // The null-coalescing operator (??) returns defaultValue when _config[key] is null.
        return _config[key] ?? defaultValue;
    }

    /// <summary>
    /// Returns the configuration value parsed as an integer.
    /// Falls back to <paramref name="defaultValue"/> when the key is missing or
    /// cannot be parsed as a number (e.g., someone accidentally set it to "yes").
    /// Useful for numeric settings like timeouts and retry counts.
    /// </summary>
    public static int GetInt(string key, int defaultValue = 0)
    {
        var value = _config[key];
        // int.TryParse is safe — it never throws; it returns false on bad input.
        return int.TryParse(value, out var result) ? result : defaultValue;
    }

    /// <summary>
    /// Returns the configuration value parsed as a boolean.
    /// Falls back to <paramref name="defaultValue"/> when the key is missing or
    /// the value is not "true"/"false" (case-insensitive).
    /// Useful for feature flags such as headless mode or screenshot-on-pass.
    /// </summary>
    public static bool GetBool(string key, bool defaultValue = false)
    {
        var value = _config[key];
        // bool.TryParse accepts "true"/"false" (case-insensitive); anything else returns false.
        return bool.TryParse(value, out var result) ? result : defaultValue;
    }
}
