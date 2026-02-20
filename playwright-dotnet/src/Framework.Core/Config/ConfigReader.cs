using Microsoft.Extensions.Configuration;

namespace Framework.Core.Config;

/// <summary>
/// Reads configuration from appsettings.json with environment variable override support.
/// Priority: ENV VAR > appsettings.json > supplied default.
/// </summary>
public static class ConfigReader
{
    private static readonly IConfiguration _config;

    static ConfigReader()
    {
        _config = new ConfigurationBuilder()
            .SetBasePath(AppContext.BaseDirectory)
            .AddJsonFile("appsettings.json", optional: true, reloadOnChange: false)
            .AddEnvironmentVariables()
            .Build();
    }

    /// <summary>
    /// Returns the value for the given key, or <paramref name="defaultValue"/> if not found.
    /// Supports colon-separated hierarchy (e.g. "timeout:explicit").
    /// Environment variables use double-underscore as separator (e.g. timeout__explicit).
    /// </summary>
    public static string GetProperty(string key, string defaultValue = "")
    {
        return _config[key] ?? defaultValue;
    }

    public static int GetInt(string key, int defaultValue = 0)
    {
        var value = _config[key];
        return int.TryParse(value, out var result) ? result : defaultValue;
    }

    public static bool GetBool(string key, bool defaultValue = false)
    {
        var value = _config[key];
        return bool.TryParse(value, out var result) ? result : defaultValue;
    }
}
