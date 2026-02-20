namespace Framework.Core.Utils;

public static class DateHelper
{
    /// <summary>
    /// Returns today's date formatted using the supplied pattern.
    /// Example patterns: "yyyy-MM-dd", "MM/dd/yyyy", "dd-MMM-yyyy"
    /// </summary>
    public static string GetTodayFormatted(string pattern = "yyyy-MM-dd") =>
        DateTime.Now.ToString(pattern);

    /// <summary>Returns the current 4-digit year as an integer.</summary>
    public static int GetCurrentYear() => DateTime.Now.Year;

    /// <summary>
    /// Returns a Unix timestamp (milliseconds since epoch) for the current UTC instant.
    /// Useful for generating unique identifiers.
    /// </summary>
    public static long GetTimestampMillis() =>
        DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
}
