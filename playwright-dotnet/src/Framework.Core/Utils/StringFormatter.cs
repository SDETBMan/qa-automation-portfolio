using Framework.Core.Config;

namespace Framework.Core.Utils;

public static class StringFormatter
{
    /// <summary>
    /// Formats a test name by replacing spaces with underscores and lower-casing.
    /// Example: "My Test Case" -> "my_test_case"
    /// </summary>
    public static string FormatTestName(string testName)
    {
        if (string.IsNullOrWhiteSpace(testName)) return string.Empty;
        return testName.Trim().ToLowerInvariant().Replace(' ', '_');
    }

    /// <summary>
    /// Returns the base URL for the given environment key.
    /// Falls back to the configured "url" property if the environment is unrecognised.
    /// </summary>
    public static string GetEnvironmentUrl(string environment)
    {
        return environment?.ToLowerInvariant() switch
        {
            "prod" or "production" => "https://www.saucedemo.com",
            "staging"              => "https://staging.saucedemo.com",
            "dev"                  => "https://dev.saucedemo.com",
            _                      => ConfigReader.GetProperty("url", "https://www.saucedemo.com")
        };
    }
}
