using Framework.Core.Utils;

namespace Framework.Unit.Tests;

/// <summary>
/// Unit tests for <see cref="StringUtils"/>.
///
/// WHY UNIT TESTS FOR UTILITY CLASSES: Utility methods are called hundreds of times
/// across a test suite — a silent bug in IsValidEmail or SafeTrim would corrupt test
/// data across every test that depends on them. These tests act as a contract: any
/// refactor that breaks a utility method will immediately surface here before it
/// reaches the actual UI or API tests.
///
/// All tests in this class are pure — no network, no file I/O, no database.
/// They run in milliseconds and have zero flakiness risk.
/// </summary>
[TestFixture]
public class StringUtilsTests
{
    // ================================================================
    // GenerateRandomEmail
    // ================================================================

    [Test]
    [Category("unit")]
    public void GenerateRandomEmail_ReturnsStringInValidEmailFormat()
    {
        // The generated email should pass its own companion validator
        string email = StringUtils.GenerateRandomEmail();
        Assert.That(StringUtils.IsValidEmail(email), Is.True,
            "GenerateRandomEmail should always produce an email that passes IsValidEmail.");
    }

    [Test]
    [Category("unit")]
    public void GenerateRandomEmail_EndsWithExpectedDomain()
    {
        // RFC 2606 reserves example.com for documentation and testing
        string email = StringUtils.GenerateRandomEmail();
        Assert.That(email, Does.EndWith("@example.com"));
    }

    [Test]
    [Category("unit")]
    public void GenerateRandomEmail_StartsWithUserPrefix()
    {
        string email = StringUtils.GenerateRandomEmail();
        Assert.That(email, Does.StartWith("user"));
    }

    [Test]
    [Category("unit")]
    public void GenerateRandomEmail_TwoCallsProduceDifferentValues()
    {
        // Timestamp-based generation must produce unique values across calls.
        // A small sleep ensures the millisecond clock advances between calls.
        string first = StringUtils.GenerateRandomEmail();
        Thread.Sleep(5);
        string second = StringUtils.GenerateRandomEmail();

        Assert.That(first, Is.Not.EqualTo(second),
            "Two successive email generations should produce unique values.");
    }

    // ================================================================
    // IsValidEmail
    // ================================================================

    [TestCase("user@example.com",        true,  "standard valid email")]
    [TestCase("user+tag@domain.co.uk",   true,  "plus-tag and multi-part TLD")]
    [TestCase("user@sub.domain.io",      true,  "subdomain")]
    [TestCase("notanemail",              false, "no @ symbol")]
    [TestCase("@nodomain.com",           false, "missing local part")]
    [TestCase("missing@dot",             false, "no dot in domain")]
    [TestCase("spaces in@email.com",     false, "spaces in local part")]
    [TestCase("",                        false, "empty string")]
    [Category("unit")]
    public void IsValidEmail_ValidatesFormatCorrectly(string email, bool expected, string because)
    {
        Assert.That(StringUtils.IsValidEmail(email), Is.EqualTo(expected), because);
    }

    [Test]
    [Category("unit")]
    public void IsValidEmail_NullInput_ReturnsFalse()
    {
        // Null must never throw — IsValidEmail is called on untrusted input
        Assert.That(StringUtils.IsValidEmail(null), Is.False);
    }

    [Test]
    [Category("unit")]
    public void IsValidEmail_WhitespaceOnly_ReturnsFalse()
    {
        Assert.That(StringUtils.IsValidEmail("   "), Is.False);
    }

    // ================================================================
    // SafeTrim
    // ================================================================

    [Test]
    [Category("unit")]
    public void SafeTrim_NullInput_ReturnsEmptyStringNotNull()
    {
        // Must return empty string, not throw NullReferenceException
        string result = StringUtils.SafeTrim(null);
        Assert.That(result, Is.EqualTo(string.Empty));
    }

    [Test]
    [Category("unit")]
    public void SafeTrim_WhitespaceOnlyInput_ReturnsEmptyString()
    {
        Assert.That(StringUtils.SafeTrim("   "), Is.EqualTo(string.Empty));
    }

    [TestCase("  hello  ", "hello",     "leading and trailing spaces")]
    [TestCase("no-spaces", "no-spaces", "unchanged when no whitespace")]
    [TestCase("\t tabs \t", "tabs",     "tab characters trimmed")]
    [TestCase(" a ",        "a",        "single character with padding")]
    [Category("unit")]
    public void SafeTrim_TrimsWhitespaceCorrectly(string input, string expected, string because)
    {
        Assert.That(StringUtils.SafeTrim(input), Is.EqualTo(expected), because);
    }

    // ================================================================
    // Capitalise
    // ================================================================

    [Test]
    [Category("unit")]
    public void Capitalise_NullInput_ReturnsEmptyString()
    {
        Assert.That(StringUtils.Capitalise(null), Is.EqualTo(string.Empty));
    }

    [Test]
    [Category("unit")]
    public void Capitalise_EmptyString_ReturnsEmptyString()
    {
        Assert.That(StringUtils.Capitalise(string.Empty), Is.EqualTo(string.Empty));
    }

    [TestCase("hello",   "Hello", "lowercase word")]
    [TestCase("world",   "World", "another lowercase word")]
    [TestCase("already", "Already", "already lowercase")]
    [TestCase("A",       "A",    "single uppercase character unchanged")]
    [Category("unit")]
    public void Capitalise_UppercasesFirstCharacterOnly(string input, string expected, string because)
    {
        Assert.That(StringUtils.Capitalise(input), Is.EqualTo(expected), because);
    }

    [Test]
    [Category("unit")]
    public void Capitalise_LeavesRestOfStringUnchanged()
    {
        // Only the first character is modified — the remainder must be preserved exactly
        Assert.That(StringUtils.Capitalise("hELLO wORLD"), Is.EqualTo("HELLO wORLD"));
    }

    [Test]
    [Category("unit")]
    public void Capitalise_SingleLowercaseChar_ReturnsUppercase()
    {
        Assert.That(StringUtils.Capitalise("z"), Is.EqualTo("Z"));
    }
}
