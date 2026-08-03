using Framework.Core.Utils;

namespace Framework.Unit.Tests;

/// <summary>
/// Unit tests for <see cref="DateHelper"/>.
///
/// Date helpers are used across the framework for generating unique identifiers,
/// timestamping screenshots, and validating UI date displays. A silent regression
/// here — like returning UTC instead of local time, or producing a wrong format —
/// would cause cascading failures in tests that rely on date patterns.
/// </summary>
[TestFixture]
public class DateHelperTests
{
    // ================================================================
    // GetTodayFormatted
    // ================================================================

    [Test]
    [Category("unit")]
    public void GetTodayFormatted_DefaultPattern_ReturnsIso8601Format()
    {
        // Default pattern is "yyyy-MM-dd" — the international standard that sorts
        // correctly alphabetically and is unambiguous across locales
        string result = DateHelper.GetTodayFormatted();
        Assert.That(result, Does.Match(@"^\d{4}-\d{2}-\d{2}$"),
            "Default pattern must produce yyyy-MM-dd format (ISO 8601).");
    }

    [Test]
    [Category("unit")]
    public void GetTodayFormatted_DefaultPattern_ContainsCurrentYear()
    {
        string result = DateHelper.GetTodayFormatted();
        Assert.That(result, Does.StartWith(DateTime.Now.Year.ToString()),
            "Result must begin with the current 4-digit year.");
    }

    [Test]
    [Category("unit")]
    public void GetTodayFormatted_UsFormat_ReturnsCorrectPattern()
    {
        string result = DateHelper.GetTodayFormatted("MM/dd/yyyy");
        Assert.That(result, Does.Match(@"^\d{2}/\d{2}/\d{4}$"),
            "US date format MM/dd/yyyy must produce two-digit month and day, four-digit year.");
    }

    [Test]
    [Category("unit")]
    public void GetTodayFormatted_YearOnlyPattern_ReturnsFourDigitYear()
    {
        string result = DateHelper.GetTodayFormatted("yyyy");
        Assert.That(result, Does.Match(@"^\d{4}$"),
            "Pattern 'yyyy' must return exactly four digits.");
    }

    [Test]
    [Category("unit")]
    public void GetTodayFormatted_ResultMatchesDateTime_Now()
    {
        // Both calls happen within the same test — they should resolve to the same date
        string result   = DateHelper.GetTodayFormatted("yyyy-MM-dd");
        string expected = DateTime.Now.ToString("yyyy-MM-dd");
        Assert.That(result, Is.EqualTo(expected));
    }

    // ================================================================
    // GetCurrentYear
    // ================================================================

    [Test]
    [Category("unit")]
    public void GetCurrentYear_ReturnsCurrentCalendarYear()
    {
        Assert.That(DateHelper.GetCurrentYear(), Is.EqualTo(DateTime.Now.Year));
    }

    [Test]
    [Category("unit")]
    public void GetCurrentYear_ReturnsFourDigitYear()
    {
        int year = DateHelper.GetCurrentYear();
        Assert.That(year, Is.GreaterThanOrEqualTo(2024).And.LessThan(3000),
            "Year must be a plausible 4-digit calendar year.");
    }

    // ================================================================
    // GetTimestampMillis
    // ================================================================

    [Test]
    [Category("unit")]
    public void GetTimestampMillis_ReturnsPositiveValue()
    {
        Assert.That(DateHelper.GetTimestampMillis(), Is.GreaterThan(0));
    }

    [Test]
    [Category("unit")]
    public void GetTimestampMillis_ReturnsValueAfterJanuary2024()
    {
        // Sanity check: timestamp must be after a known past date
        long jan2024 = new DateTimeOffset(2024, 1, 1, 0, 0, 0, TimeSpan.Zero)
            .ToUnixTimeMilliseconds();

        Assert.That(DateHelper.GetTimestampMillis(), Is.GreaterThan(jan2024),
            "Timestamp must be after January 1, 2024.");
    }

    [Test]
    [Category("unit")]
    public void GetTimestampMillis_TwoSuccessiveCallsAreNonDecreasing()
    {
        // Time only moves forward — second call must not return an earlier value
        long first  = DateHelper.GetTimestampMillis();
        long second = DateHelper.GetTimestampMillis();

        Assert.That(second, Is.GreaterThanOrEqualTo(first),
            "Successive timestamp calls must be non-decreasing.");
    }

    [Test]
    [Category("unit")]
    public void GetTimestampMillis_IsInMillisecondRange()
    {
        // Unix time in milliseconds is 13 digits as of 2001 and will be for centuries.
        // This catches accidental division by 1000 (which would return seconds, not ms).
        long ts = DateHelper.GetTimestampMillis();
        Assert.That(ts.ToString().Length, Is.EqualTo(13),
            "Unix timestamp in milliseconds must be 13 digits.");
    }
}
