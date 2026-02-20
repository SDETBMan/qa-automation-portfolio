using System.Text.RegularExpressions;
using Framework.Core.Utils;

namespace Framework.Tests.Unit;

/// <summary>
/// Unit tests for StringUtils — no Playwright or HTTP required.
/// </summary>
[TestFixture]
[Category("unit")]
public class StringUtilsTest
{
    private static readonly Regex EmailPattern =
        new(@"^user\d+@example\.com$", RegexOptions.Compiled);

    // ─── GenerateRandomEmail ──────────────────────────────────────────────────

    [Test]
    public void GenerateRandomEmail_MatchesExpectedPattern()
    {
        string email = StringUtils.GenerateRandomEmail();
        Assert.That(EmailPattern.IsMatch(email), Is.True,
            $"Email '{email}' should match pattern user{{timestamp}}@example.com");
    }

    [Test]
    public void GenerateRandomEmail_IsUniqueOnSuccessiveCalls()
    {
        // Two successive calls should produce different emails (timestamp-based)
        string email1 = StringUtils.GenerateRandomEmail();
        System.Threading.Thread.Sleep(5); // ensure different millis
        string email2 = StringUtils.GenerateRandomEmail();
        Assert.That(email1, Is.Not.EqualTo(email2),
            "Successive generated emails should be unique.");
    }

    // ─── IsValidEmail — TestCaseSource ────────────────────────────────────────

    public static IEnumerable<TestCaseData> ValidEmails()
    {
        yield return new TestCaseData("user@example.com").Returns(true);
        yield return new TestCaseData("test.user+tag@domain.org").Returns(true);
        yield return new TestCaseData("a@b.io").Returns(true);
    }

    public static IEnumerable<TestCaseData> InvalidEmails()
    {
        yield return new TestCaseData("notanemail").Returns(false);
        yield return new TestCaseData("missing@domain").Returns(false);
        yield return new TestCaseData("@nodomain.com").Returns(false);
        yield return new TestCaseData("").Returns(false);
        yield return new TestCaseData((string?)null).Returns(false);
    }

    [Test]
    [TestCaseSource(nameof(ValidEmails))]
    public bool IsValidEmail_ValidInputs(string email) =>
        StringUtils.IsValidEmail(email);

    [Test]
    [TestCaseSource(nameof(InvalidEmails))]
    public bool IsValidEmail_InvalidInputs(string? email) =>
        StringUtils.IsValidEmail(email);

    // ─── SafeTrim ─────────────────────────────────────────────────────────────

    [Test]
    public void SafeTrim_RemovesWhitespace()
    {
        Assert.That(StringUtils.SafeTrim("  hello  "), Is.EqualTo("hello"));
    }

    [Test]
    public void SafeTrim_ReturnsEmptyForNull()
    {
        Assert.That(StringUtils.SafeTrim(null), Is.Empty);
    }

    // ─── Capitalise ───────────────────────────────────────────────────────────

    [Test]
    public void Capitalise_UppercasesFirstLetter()
    {
        Assert.That(StringUtils.Capitalise("hello world"), Is.EqualTo("Hello world"));
    }

    [Test]
    public void Capitalise_ReturnsEmptyForNull()
    {
        Assert.That(StringUtils.Capitalise(null), Is.Empty);
    }
}
