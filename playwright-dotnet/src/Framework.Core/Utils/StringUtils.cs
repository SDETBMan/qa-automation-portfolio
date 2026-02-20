using System.Text.RegularExpressions;

namespace Framework.Core.Utils;

public static class StringUtils
{
    private static readonly Regex EmailRegex =
        new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);

    /// <summary>
    /// Generates a random email using the current Unix timestamp in milliseconds.
    /// Pattern: user{timestamp}@example.com
    /// </summary>
    public static string GenerateRandomEmail()
    {
        long ts = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        return $"user{ts}@example.com";
    }

    /// <summary>Returns true if the string is a well-formed email address.</summary>
    public static bool IsValidEmail(string? email)
    {
        if (string.IsNullOrWhiteSpace(email)) return false;
        return EmailRegex.IsMatch(email);
    }

    /// <summary>Returns a non-null, trimmed string; empty string if input is null.</summary>
    public static string SafeTrim(string? value) => value?.Trim() ?? string.Empty;

    /// <summary>Capitalises the first letter of a string.</summary>
    public static string Capitalise(string? value)
    {
        if (string.IsNullOrEmpty(value)) return string.Empty;
        return char.ToUpperInvariant(value[0]) + value[1..];
    }
}
