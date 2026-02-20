using Framework.Core.Utils;

namespace Framework.Tests.Unit;

/// <summary>
/// Unit tests for StringFormatter and DateHelper — no Playwright or HTTP required.
/// </summary>
[TestFixture]
[Category("unit")]
public class FrameworkUnitTest
{
    // ─── StringFormatter ──────────────────────────────────────────────────────

    [Test]
    public void FormatTestName_ReplacesSpacesWithUnderscores()
    {
        string result = StringFormatter.FormatTestName("My Test Case");
        Assert.That(result, Is.EqualTo("my_test_case"));
    }

    [Test]
    public void FormatTestName_LowercasesInput()
    {
        string result = StringFormatter.FormatTestName("UPPER CASE");
        Assert.That(result, Is.EqualTo("upper_case"));
    }

    [Test]
    public void FormatTestName_ReturnsEmptyForNullOrWhitespace()
    {
        Assert.That(StringFormatter.FormatTestName(""),   Is.Empty);
        Assert.That(StringFormatter.FormatTestName("  "), Is.Empty);
    }

    [Test]
    public void GetEnvironmentUrl_ReturnsProductionUrl()
    {
        string url = StringFormatter.GetEnvironmentUrl("prod");
        Assert.That(url, Is.EqualTo("https://www.saucedemo.com"));
    }

    [Test]
    public void GetEnvironmentUrl_ReturnsProductionUrl_ForProductionAlias()
    {
        string url = StringFormatter.GetEnvironmentUrl("production");
        Assert.That(url, Is.EqualTo("https://www.saucedemo.com"));
    }

    [Test]
    public void GetEnvironmentUrl_ReturnsStagingUrl()
    {
        string url = StringFormatter.GetEnvironmentUrl("staging");
        Assert.That(url, Does.Contain("staging"));
    }

    [Test]
    public void GetEnvironmentUrl_ReturnsConfigUrlForUnknown()
    {
        // Falls through to config; config returns saucedemo base url
        string url = StringFormatter.GetEnvironmentUrl("unknown_env");
        Assert.That(url, Is.Not.Empty);
    }

    // ─── DateHelper ───────────────────────────────────────────────────────────

    [Test]
    public void GetCurrentYear_ReturnsFourDigitYear()
    {
        int year = DateHelper.GetCurrentYear();
        Assert.That(year, Is.GreaterThanOrEqualTo(2024),
            "Current year should be 2024 or later.");
        Assert.That(year.ToString(), Has.Length.EqualTo(4));
    }

    [Test]
    public void GetTodayFormatted_DefaultPattern_IsIso()
    {
        string today = DateHelper.GetTodayFormatted();
        // Should match yyyy-MM-dd
        Assert.That(today, Does.Match(@"^\d{4}-\d{2}-\d{2}$"));
    }

    [Test]
    public void GetTodayFormatted_CustomPattern()
    {
        string result = DateHelper.GetTodayFormatted("MM/dd/yyyy");
        Assert.That(result, Does.Match(@"^\d{2}/\d{2}/\d{4}$"));
    }

    [Test]
    public void GetTimestampMillis_IsPositive()
    {
        long ts = DateHelper.GetTimestampMillis();
        Assert.That(ts, Is.GreaterThan(0));
    }
}
