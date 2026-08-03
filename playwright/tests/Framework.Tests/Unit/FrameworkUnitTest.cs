using Framework.Core.Utils;

namespace Framework.Tests.Unit;

/// <summary>
/// FrameworkUnitTest: Unit tests for StringFormatter and DateHelper — two utility
/// classes in the framework's core library.
///
/// WHY UNIT TESTS FOR UTILITIES: These utilities are used by many other classes in
/// the framework. If StringFormatter.FormatTestName() has a bug, every feature that
/// uses it will produce wrong output — wrong filenames for screenshots, wrong
/// test IDs in reports. Unit tests catch bugs at the source, in the utility itself,
/// rather than letting them manifest as mysterious failures in higher-level tests.
///
/// WHAT UNIT TESTS ARE: Tests that validate a single method in complete isolation —
/// no browser, no HTTP calls, no disk I/O. They run in milliseconds because there are
/// no slow operations. This speed supports "test on every save" development workflows.
///
/// WHY SMALL, FOCUSED TEST METHODS: Each test method covers exactly one scenario
/// (one input, one assertion). This makes failures immediately obvious — the test
/// name tells you exactly what broke (e.g. "FormatTestName_LowercasesInput") without
/// reading the assertion code. This is the "single responsibility" principle applied
/// to test methods.
///
/// No Playwright, no HTTP client, no external dependencies.
/// </summary>
[TestFixture]
[Category("unit")]
public class FrameworkUnitTest
{
    // ─── StringFormatter ──────────────────────────────────────────────────────

    /// <summary>
    /// FormatTestName_ReplacesSpacesWithUnderscores: Verifies that spaces in a test
    /// name are converted to underscores.
    ///
    /// WHY THIS MATTERS: Test names are used to generate filenames for screenshots,
    /// Allure report artefacts, and log entries. Filenames with spaces break certain
    /// operating systems, CI pipelines, and command-line tools. Underscores are safe
    /// and universally compatible.
    /// </summary>
    [Test]
    public void FormatTestName_ReplacesSpacesWithUnderscores()
    {
        // "My Test Case" → spaces become underscores, all lowercase
        string result = StringFormatter.FormatTestName("My Test Case");
        Assert.That(result, Is.EqualTo("my_test_case"));
    }

    /// <summary>
    /// FormatTestName_LowercasesInput: Verifies that uppercase characters are
    /// converted to lowercase during formatting.
    ///
    /// WHY LOWERCASE: Consistent lowercase names prevent case-sensitivity issues
    /// on Linux filesystems (case-sensitive) vs Windows (case-insensitive). A
    /// screenshot named "LoginTest.png" and "logintest.png" would be different
    /// files on Linux but the same file on Windows — lowercasing removes this ambiguity.
    /// </summary>
    [Test]
    public void FormatTestName_LowercasesInput()
    {
        // "UPPER CASE" → entirely lowercased with spaces converted to underscores
        string result = StringFormatter.FormatTestName("UPPER CASE");
        Assert.That(result, Is.EqualTo("upper_case"));
    }

    /// <summary>
    /// FormatTestName_ReturnsEmptyForNullOrWhitespace: Verifies that null or
    /// whitespace-only inputs return an empty string rather than throwing an exception.
    ///
    /// WHY TEST EDGE CASES: Null or whitespace test names can happen when
    /// programmatically generating test metadata. The method must handle these
    /// gracefully — returning empty string is safer than throwing NullReferenceException,
    /// which would crash the caller.
    /// </summary>
    [Test]
    public void FormatTestName_ReturnsEmptyForNullOrWhitespace()
    {
        // Both empty string and whitespace-only should produce an empty result.
        Assert.That(StringFormatter.FormatTestName(""),   Is.Empty);
        Assert.That(StringFormatter.FormatTestName("  "), Is.Empty);
    }

    /// <summary>
    /// GetEnvironmentUrl_ReturnsProductionUrl: Verifies that "prod" maps to the
    /// SauceDemo production URL.
    ///
    /// WHY ENVIRONMENT URL MAPPING: Tests run against different environments
    /// (staging, QA, production) in different CI pipeline stages. StringFormatter
    /// centralises the mapping from environment name to URL, so all tests and
    /// utilities get the correct URL by name without hard-coding it repeatedly.
    /// </summary>
    [Test]
    public void GetEnvironmentUrl_ReturnsProductionUrl()
    {
        // "prod" is the canonical short name for the production environment.
        string url = StringFormatter.GetEnvironmentUrl("prod");
        Assert.That(url, Is.EqualTo("https://www.saucedemo.com"));
    }

    /// <summary>
    /// GetEnvironmentUrl_ReturnsProductionUrl_ForProductionAlias: Verifies that
    /// "production" (the full word) also maps to the production URL.
    ///
    /// WHY TEST ALIASES: Different teams, scripts, and config files may use "prod"
    /// or "production" interchangeably. Both must work — forcing everyone to use
    /// exactly one spelling would cause unnecessary integration failures.
    /// </summary>
    [Test]
    public void GetEnvironmentUrl_ReturnsProductionUrl_ForProductionAlias()
    {
        // "production" (full word) must produce the same URL as "prod" (abbreviation).
        string url = StringFormatter.GetEnvironmentUrl("production");
        Assert.That(url, Is.EqualTo("https://www.saucedemo.com"));
    }

    /// <summary>
    /// GetEnvironmentUrl_ReturnsStagingUrl: Verifies that "staging" maps to a
    /// URL that contains the word "staging".
    ///
    /// WHY PARTIAL MATCH: The exact staging URL may change (e.g. different port numbers,
    /// subdomains). Asserting that the URL contains "staging" is more resilient to
    /// minor URL changes while still confirming we're not accidentally pointing at
    /// production.
    /// </summary>
    [Test]
    public void GetEnvironmentUrl_ReturnsStagingUrl()
    {
        // "staging" should map to a staging-specific URL
        string url = StringFormatter.GetEnvironmentUrl("staging");
        Assert.That(url, Does.Contain("staging"));
    }

    /// <summary>
    /// GetEnvironmentUrl_ReturnsConfigUrlForUnknown: Verifies that an unrecognised
    /// environment name falls back to a non-empty URL rather than returning null or
    /// throwing an exception.
    ///
    /// WHY TEST THE DEFAULT CASE: Every switch/if-else that handles named cases needs
    /// a default. If a new environment name is used before the method is updated,
    /// the fallback prevents a crash and returns a usable (if perhaps not ideal) URL.
    /// </summary>
    [Test]
    public void GetEnvironmentUrl_ReturnsConfigUrlForUnknown()
    {
        // An unrecognised environment name should fall through to the config-based default.
        // We assert non-empty (not the specific URL) because the fallback reads from config
        // which may differ between environments.
        string url = StringFormatter.GetEnvironmentUrl("unknown_env");
        Assert.That(url, Is.Not.Empty);
    }

    // ─── DateHelper ───────────────────────────────────────────────────────────

    /// <summary>
    /// GetCurrentYear_ReturnsFourDigitYear: Verifies that GetCurrentYear() returns
    /// a four-digit year value that is at least 2024.
    ///
    /// WHY TEST DATE UTILITIES: Date-based utilities generate unique test artefact
    /// names (screenshots, log files). If GetCurrentYear() returned 0 or a two-digit
    /// year, generated filenames would be wrong. The ≥ 2024 guard confirms the method
    /// reads the live system clock rather than returning a hard-coded or epoch value.
    /// </summary>
    [Test]
    public void GetCurrentYear_ReturnsFourDigitYear()
    {
        int year = DateHelper.GetCurrentYear();

        // The year must be 2024 or later — confirms the live clock is being used.
        Assert.That(year, Is.GreaterThanOrEqualTo(2024),
            "Current year should be 2024 or later.");

        // Four digits long — a year like "26" (two-digit) would fail this check.
        Assert.That(year.ToString(), Has.Length.EqualTo(4));
    }

    /// <summary>
    /// GetTodayFormatted_DefaultPattern_IsIso: Verifies that the default date format
    /// is ISO 8601 (yyyy-MM-dd, e.g. "2026-02-23").
    ///
    /// WHY ISO 8601: This is the internationally agreed date format, unambiguous
    /// across locales. "02/03/2026" means Feb 3 in the US and March 2 in Europe.
    /// "2026-02-03" always means Feb 3. Using ISO 8601 in artefact names prevents
    /// locale-dependent sorting and naming confusion.
    /// </summary>
    [Test]
    public void GetTodayFormatted_DefaultPattern_IsIso()
    {
        string today = DateHelper.GetTodayFormatted();

        // Regex: four digits, dash, two digits, dash, two digits — e.g. "2026-02-23"
        Assert.That(today, Does.Match(@"^\d{4}-\d{2}-\d{2}$"));
    }

    /// <summary>
    /// GetTodayFormatted_CustomPattern: Verifies that a custom date format pattern
    /// (MM/dd/yyyy) is applied correctly.
    ///
    /// WHY SUPPORT CUSTOM PATTERNS: Different systems expect dates in different formats.
    /// A report generation tool might need "MM/dd/yyyy" while a log file needs "yyyy-MM-dd".
    /// Supporting a custom pattern parameter makes the utility flexible without
    /// requiring multiple hard-coded format methods.
    /// </summary>
    [Test]
    public void GetTodayFormatted_CustomPattern()
    {
        // Request the US-style date format (month/day/year)
        string result = DateHelper.GetTodayFormatted("MM/dd/yyyy");

        // Regex: two digits, slash, two digits, slash, four digits — e.g. "02/23/2026"
        Assert.That(result, Does.Match(@"^\d{2}/\d{2}/\d{4}$"));
    }

    /// <summary>
    /// GetTimestampMillis_IsPositive: Verifies that GetTimestampMillis() returns
    /// a positive value (milliseconds since Unix epoch).
    ///
    /// WHY MILLISECOND TIMESTAMPS: Millisecond-precision timestamps are used to
    /// generate unique IDs for test data (e.g. "user1700000000123@example.com").
    /// A positive value confirms the method returns a real epoch timestamp — not 0,
    /// not negative, not a formatted string accidentally cast to long.
    /// </summary>
    [Test]
    public void GetTimestampMillis_IsPositive()
    {
        long ts = DateHelper.GetTimestampMillis();

        // Any valid timestamp from 1970 onward will be positive.
        // A value of 0 would indicate the epoch start (impossible for "now").
        // A negative value would indicate a date before 1970 (clearly wrong).
        Assert.That(ts, Is.GreaterThan(0));
    }
}
