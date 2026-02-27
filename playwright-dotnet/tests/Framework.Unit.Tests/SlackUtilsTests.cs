using Framework.Core.Utils;

namespace Framework.Unit.Tests;

/// <summary>
/// Unit tests for the pure methods of <see cref="SlackUtils"/>.
///
/// WHY ONLY BuildSummary IS TESTED HERE: SendResultAsync makes a real HTTP POST
/// to Slack's webhook endpoint — that is an integration concern, not a unit concern.
/// Unit tests must be fast, deterministic, and offline-capable. Testing HTTP calls
/// requires mocking HttpClient, which is outside the scope of this class.
///
/// BuildSummary is a pure function (no I/O, no side effects) — it takes integers
/// and returns a formatted string. That is exactly what unit tests are designed for.
/// </summary>
[TestFixture]
public class SlackUtilsTests
{
    // ================================================================
    // BuildSummary
    // ================================================================

    [Test]
    [Category("unit")]
    public void BuildSummary_ContainsAllThreeCounts()
    {
        string result = SlackUtils.BuildSummary(10, 2, 1);

        Assert.That(result, Does.Contain("10"), "Passed count must appear in summary.");
        Assert.That(result, Does.Contain("2"),  "Failed count must appear in summary.");
        Assert.That(result, Does.Contain("1"),  "Skipped count must appear in summary.");
    }

    [Test]
    [Category("unit")]
    public void BuildSummary_ContainsSlackBoldMarkers()
    {
        // Slack renders *text* as bold. The summary header must use this syntax
        // so the title stands out in the channel notification.
        string result = SlackUtils.BuildSummary(5, 0, 0);
        Assert.That(result, Does.Contain("*"),
            "BuildSummary must include Slack bold markers (*) for the header.");
    }

    [Test]
    [Category("unit")]
    public void BuildSummary_ContainsPassedLabel()
    {
        string result = SlackUtils.BuildSummary(3, 1, 2);
        Assert.That(result, Does.Contain("Passed"),
            "Summary must label the passed count.");
    }

    [Test]
    [Category("unit")]
    public void BuildSummary_ContainsFailedLabel()
    {
        string result = SlackUtils.BuildSummary(3, 1, 2);
        Assert.That(result, Does.Contain("Failed"),
            "Summary must label the failed count.");
    }

    [Test]
    [Category("unit")]
    public void BuildSummary_ContainsSkippedLabel()
    {
        string result = SlackUtils.BuildSummary(3, 1, 2);
        Assert.That(result, Does.Contain("Skipped"),
            "Summary must label the skipped count.");
    }

    [Test]
    [Category("unit")]
    public void BuildSummary_AllZeroCounts_DoesNotThrow()
    {
        // Edge case: a suite where every test was skipped is a valid state
        Assert.DoesNotThrow(() => SlackUtils.BuildSummary(0, 0, 0));
    }

    [Test]
    [Category("unit")]
    public void BuildSummary_AllZeroCounts_StillContainsLabels()
    {
        string result = SlackUtils.BuildSummary(0, 0, 0);
        Assert.That(result, Does.Contain("Passed").And.Contain("Failed").And.Contain("Skipped"));
    }

    [Test]
    [Category("unit")]
    public void BuildSummary_ReturnsNonEmptyString()
    {
        string result = SlackUtils.BuildSummary(1, 0, 0);
        Assert.That(result, Is.Not.Null.And.Not.Empty);
    }

    [Test]
    [Category("unit")]
    public void BuildSummary_LargeNumbers_FormatsCorrectly()
    {
        // Large suites (1000+ tests) must not truncate or overflow
        string result = SlackUtils.BuildSummary(1000, 500, 250);
        Assert.That(result, Does.Contain("1000").And.Contain("500").And.Contain("250"));
    }
}
