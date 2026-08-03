using Framework.Core.Utils;

namespace Framework.Unit.Tests;

/// <summary>
/// Unit tests for <see cref="StringFormatter"/>.
///
/// FormatTestName and GetEnvironmentUrl are called at the framework level —
/// a broken slug breaks every Allure report attachment; a broken URL lookup
/// points every test at the wrong environment. These tests lock in the
/// expected behaviour so refactors surface failures immediately.
/// </summary>
[TestFixture]
public class StringFormatterTests
{
    // ================================================================
    // FormatTestName
    // ================================================================

    [TestCase("My Test Case",   "my_test_case",   "spaces replaced with underscores, lowercased")]
    [TestCase("Login Test",     "login_test",     "two-word name")]
    [TestCase("UPPER CASE",     "upper_case",     "fully uppercase input lowercased")]
    [TestCase("  padded  ",     "padded",         "surrounding whitespace trimmed before slug")]
    [TestCase("already_lower",  "already_lower",  "already formatted — unchanged")]
    [TestCase("one",            "one",            "single word — no underscores needed")]
    [Category("unit")]
    public void FormatTestName_ProducesCorrectSlug(string input, string expected, string because)
    {
        Assert.That(StringFormatter.FormatTestName(input), Is.EqualTo(expected), because);
    }

    [Test]
    [Category("unit")]
    public void FormatTestName_NullOrWhitespace_ReturnsEmptyString()
    {
        // Must not throw — Allure calls this with test context data that may be null
        Assert.That(StringFormatter.FormatTestName("   "), Is.EqualTo(string.Empty));
    }

    [Test]
    [Category("unit")]
    public void FormatTestName_ResultContainsNoSpaces()
    {
        string result = StringFormatter.FormatTestName("A Test With Many Words");
        Assert.That(result, Does.Not.Contain(" "),
            "Slugified test names must never contain spaces — spaces break file paths and URLs.");
    }

    [Test]
    [Category("unit")]
    public void FormatTestName_ResultIsLowercase()
    {
        string result = StringFormatter.FormatTestName("FULLY UPPERCASE INPUT");
        Assert.That(result, Is.EqualTo(result.ToLowerInvariant()),
            "Slugified name must be entirely lowercase.");
    }

    // ================================================================
    // GetEnvironmentUrl
    // ================================================================

    [TestCase("prod",       "https://www.saucedemo.com",     "short prod alias")]
    [TestCase("production", "https://www.saucedemo.com",     "full production name")]
    [TestCase("staging",    "https://staging.saucedemo.com", "staging environment")]
    [TestCase("dev",        "https://dev.saucedemo.com",     "dev environment")]
    [Category("unit")]
    public void GetEnvironmentUrl_KnownEnvironments_ReturnCorrectUrls(
        string env, string expectedUrl, string because)
    {
        Assert.That(StringFormatter.GetEnvironmentUrl(env), Is.EqualTo(expectedUrl), because);
    }

    [TestCase("PROD",       "https://www.saucedemo.com",     "uppercase input handled")]
    [TestCase("STAGING",    "https://staging.saucedemo.com", "uppercase staging")]
    [TestCase("Dev",        "https://dev.saucedemo.com",     "mixed case dev")]
    [Category("unit")]
    public void GetEnvironmentUrl_IsCaseInsensitive(string env, string expectedUrl, string because)
    {
        // The switch calls ToLowerInvariant() before matching — input case must not matter
        Assert.That(StringFormatter.GetEnvironmentUrl(env), Is.EqualTo(expectedUrl), because);
    }

    [Test]
    [Category("unit")]
    public void GetEnvironmentUrl_UnknownEnvironment_ReturnsNonEmptyFallback()
    {
        // Unknown envs fall back to ConfigReader which defaults to saucedemo.com
        string result = StringFormatter.GetEnvironmentUrl("unknown_xyz");
        Assert.That(result, Is.Not.Null.And.Not.Empty,
            "Unknown environment must not return null or empty — fallback must always produce a URL.");
    }
}
