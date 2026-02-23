using System.Text.RegularExpressions;

namespace Framework.Core.Utils;

/// <summary>
/// General-purpose string utility methods for test data generation and validation.
///
/// Why this exists: Tests need realistic, unique, and valid data. Hard-coded values
/// like "test@example.com" cause failures when tests run in parallel (two tests
/// inserting the same email) or when the app enforces uniqueness constraints.
/// This class solves those problems with:
///   - GenerateRandomEmail: produces a unique email every call using a timestamp
///   - IsValidEmail: validates format without making a network call
///   - SafeTrim / Capitalise: defensive string helpers that never throw on null input
///
/// All methods are static (no instance needed) and pure (no side effects, same
/// input always produces same output) making them straightforward to unit-test.
/// See StringUtilsTest.cs for the full test suite covering these methods.
/// </summary>
public static class StringUtils
{
    // Pre-compiled regular expression for email validation.
    // RegexOptions.Compiled converts the pattern to IL bytecode at startup, making
    // subsequent calls faster. Worth the one-time compilation cost because IsValidEmail
    // may be called many times during a test run.
    //
    // Pattern breakdown:
    //   ^          — start of string (no characters before the local part)
    //   [^@\s]+    — one or more characters that are not "@" or whitespace (local part)
    //   @          — exactly one "@" symbol
    //   [^@\s]+    — one or more characters (domain name, no @ or spaces)
    //   \.         — a literal dot (escaped because "." means "any char" in regex)
    //   [^@\s]+    — one or more characters (TLD like "com", "org", "io")
    //   $          — end of string
    // This is intentionally permissive — it catches obvious non-emails without
    // rejecting valid but unusual addresses (e.g., "user+tag@sub.domain.io").
    private static readonly Regex EmailRegex =
        new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);

    /// <summary>
    /// Generates a unique email address by appending the current Unix timestamp
    /// in milliseconds to the "user" prefix.
    ///
    /// Why timestamps for uniqueness: A millisecond timestamp changes every millisecond,
    /// so even rapid successive calls produce different values. This avoids collisions
    /// in databases or APIs that enforce unique email constraints.
    ///
    /// Pattern: user{timestamp}@example.com
    /// Example: user1700000000000@example.com
    ///
    /// "example.com" is the RFC 2606-reserved domain for documentation and testing —
    /// it will never receive real email, which is appropriate for test data.
    /// </summary>
    public static string GenerateRandomEmail()
    {
        // ToUnixTimeMilliseconds() returns a long (64-bit integer) — sufficient precision
        // for uniqueness even when tests run in parallel on fast hardware.
        long ts = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        return $"user{ts}@example.com";
    }

    /// <summary>
    /// Returns true if the input string is a syntactically valid email address.
    /// Returns false for null, empty, whitespace-only, or malformed inputs.
    ///
    /// This is a format check only — it does NOT verify that the email address
    /// actually exists or can receive messages. Use it to validate user input
    /// before sending it to an API, or to assert that generated emails are valid.
    /// </summary>
    public static bool IsValidEmail(string? email)
    {
        // Early exit for null/empty/whitespace — Regex.IsMatch would return false
        // anyway, but the explicit check makes the intent clear and avoids the
        // minor overhead of invoking the regex engine on blank input.
        if (string.IsNullOrWhiteSpace(email)) return false;
        return EmailRegex.IsMatch(email);
    }

    /// <summary>
    /// Returns a trimmed version of the input string.
    /// Returns an empty string (never null) when the input is null.
    ///
    /// Why "Safe": the standard string.Trim() method throws NullReferenceException
    /// on null input. This version is null-safe, which reduces defensive null-check
    /// boilerplate in test assertion code.
    ///
    /// The ?. (null-conditional) operator returns null when value is null, and
    /// the ?? operator then substitutes the empty string fallback.
    /// </summary>
    public static string SafeTrim(string? value) => value?.Trim() ?? string.Empty;

    /// <summary>
    /// Returns the input string with its first character converted to uppercase,
    /// leaving the rest of the string unchanged.
    /// Returns an empty string (never null) when the input is null or empty.
    ///
    /// Why this exists: Some UI elements (like page titles or product names) are
    /// stored in lowercase in test data but displayed with a capital first letter.
    /// This helper normalises the comparison without changing the full string to
    /// Title Case (which would incorrectly capitalise words like "and", "the").
    ///
    /// The [1..] range syntax (C# 8+) is equivalent to Substring(1) — it means
    /// "all characters from index 1 to the end of the string".
    /// </summary>
    public static string Capitalise(string? value)
    {
        // Guard: return empty string for null or empty input.
        if (string.IsNullOrEmpty(value)) return string.Empty;

        // ToUpperInvariant on the first character ensures culture-invariant capitalisation
        // (important on CI servers that may have non-English locale settings).
        // Concatenate with the remainder of the string starting at index 1.
        return char.ToUpperInvariant(value[0]) + value[1..];
    }
}
