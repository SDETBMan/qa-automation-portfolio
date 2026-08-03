namespace Framework.Core.Utils;

/// <summary>
/// Utility class providing date and time helper methods for use across the test framework.
///
/// Why this exists: Tests frequently need dates and timestamps for:
///   - Generating unique identifiers (e.g., "test_1700000000000@example.com")
///   - Timestamping screenshots and trace files so they don't overwrite each other
///   - Verifying that dates displayed in the UI match expected patterns
///   - Seeding database records with realistic "created at" dates
///
/// Centralising these helpers in one place ensures consistent date formatting
/// across all tests and makes it easy to swap DateTime.Now for a test-controlled
/// clock in the future if needed (e.g., to test year-boundary edge cases).
///
/// Note on DateTime.Now vs DateTimeOffset.UtcNow:
///   DateTime.Now returns the local machine time, which varies by timezone.
///   DateTimeOffset.UtcNow returns Coordinated Universal Time (UTC), which is the
///   same everywhere in the world — preferred for timestamps that need to be
///   unambiguous across CI servers in different regions.
/// </summary>
public static class DateHelper
{
    /// <summary>
    /// Returns today's date as a formatted string using the given pattern.
    /// The default pattern "yyyy-MM-dd" is the ISO 8601 standard format
    /// (e.g., "2025-03-15"), which sorts correctly alphabetically and is
    /// unambiguous across locales (unlike "03/15/25" which means different
    /// things in the US and Europe).
    ///
    /// Custom pattern examples:
    ///   "MM/dd/yyyy"  → "03/15/2025"  (US format)
    ///   "dd-MMM-yyyy" → "15-Mar-2025" (abbreviated month name)
    ///   "dddd, MMMM d, yyyy" → "Saturday, March 15, 2025" (long form)
    ///
    /// Uses DateTime.Now (local machine time). If UTC is required, use
    /// DateTimeOffset.UtcNow.ToString(pattern) directly.
    /// </summary>
    public static string GetTodayFormatted(string pattern = "yyyy-MM-dd") =>
        DateTime.Now.ToString(pattern);

    /// <summary>
    /// Returns the current calendar year as a 4-digit integer (e.g., 2025).
    /// Useful for assertions like "copyright year should equal current year"
    /// or for constructing date ranges in test data.
    /// </summary>
    public static int GetCurrentYear() => DateTime.Now.Year;

    /// <summary>
    /// Returns the current UTC time as a Unix timestamp in milliseconds.
    /// A Unix timestamp is the number of milliseconds elapsed since
    /// January 1, 1970 00:00:00 UTC (the "Unix epoch").
    ///
    /// Why milliseconds (not seconds): millisecond precision ensures uniqueness
    /// even when two calls happen within the same second, making it safe to use
    /// as a suffix in generated email addresses, file names, and test IDs.
    ///
    /// Example: 1700000000000 represents a specific point in time and will never
    /// repeat, making every generated value globally unique.
    /// </summary>
    public static long GetTimestampMillis() =>
        DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
}
