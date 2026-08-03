using System.Text.RegularExpressions;
using Framework.Core.Utils;

namespace Framework.Tests.Unit;

/// <summary>
/// StringUtilsTest: Unit tests for the StringUtils utility class.
///
/// WHY TEST STRING UTILITIES: StringUtils provides reusable string operations
/// (email generation, email validation, string trimming, capitalisation) that are
/// used across the framework for test data generation and input validation. Bugs in
/// these methods affect every caller. Unit tests catch issues at the source —
/// in the utility itself — rather than as confusing downstream failures.
///
/// TESTCASESOURCE PATTERN: Instead of writing separate test methods for each valid
/// and invalid email address, this file uses NUnit's [TestCaseSource] attribute.
/// Static methods (ValidEmails, InvalidEmails) return collections of test cases,
/// and NUnit runs the test method once per case — all reported individually in the
/// test output. This is NUnit's equivalent of TestNG's @DataProvider in Java.
///
/// WHY RETURN BOOL DIRECTLY: The IsValidEmail tests use an expression-bodied method
/// that returns a bool directly (=> StringUtils.IsValidEmail(email)) and marks it
/// with [Test]. NUnit treats the return value as the assertion when [TestCaseSource]
/// cases use .Returns() — a compact pattern that removes the need for explicit
/// Assert.That() inside the method body.
///
/// No Playwright, no HTTP calls, no browser required.
/// </summary>
[TestFixture]
[Category("unit")]
public class StringUtilsTest
{
    // Pre-compiled regex for verifying generated email format.
    // Compiled = the regex is compiled to bytecode once at class load time,
    // making repeated IsMatch() calls faster — important in a data-driven test
    // that runs the same regex for multiple inputs.
    private static readonly Regex EmailPattern =
        new(@"^user\d+@example\.com$", RegexOptions.Compiled);

    // ─── GenerateRandomEmail ──────────────────────────────────────────────────

    /// <summary>
    /// GenerateRandomEmail_MatchesExpectedPattern: Verifies that the generated email
    /// follows the expected format: user{timestamp}@example.com.
    ///
    /// WHY VALIDATE FORMAT WITH REGEX: A simple Contains("@") check would pass for
    /// malformed strings like "@" or "@@@@". The full regex validates the complete
    /// structure: "user" prefix, digits (timestamp), "@example.com" suffix.
    /// This ensures the generated email is usable as valid-format test input for
    /// form fields that apply email pattern validation.
    /// </summary>
    [Test]
    public void GenerateRandomEmail_MatchesExpectedPattern()
    {
        string email = StringUtils.GenerateRandomEmail();

        // Verify the full format: starts with "user", has digits, ends with @example.com
        Assert.That(EmailPattern.IsMatch(email), Is.True,
            $"Email '{email}' should match pattern user{{timestamp}}@example.com");
    }

    /// <summary>
    /// GenerateRandomEmail_IsUniqueOnSuccessiveCalls: Verifies that two calls
    /// to GenerateRandomEmail() produce different values.
    ///
    /// WHY TEST UNIQUENESS: If the generator always returned the same value,
    /// tests using it for form registration would hit database unique constraints,
    /// and tests checking "did anything change" would produce false positives.
    /// The 5ms sleep ensures the calls happen at different millisecond timestamps
    /// (assuming timestamp-based generation) — making duplicates impossible in practice.
    /// </summary>
    [Test]
    public void GenerateRandomEmail_IsUniqueOnSuccessiveCalls()
    {
        string email1 = StringUtils.GenerateRandomEmail();

        // Small sleep ensures different millisecond timestamps for timestamp-based generation.
        System.Threading.Thread.Sleep(5);

        string email2 = StringUtils.GenerateRandomEmail();

        // Both calls must produce distinct values — not the same string twice.
        Assert.That(email1, Is.Not.EqualTo(email2),
            "Successive generated emails should be unique.");
    }

    // ─── IsValidEmail — TestCaseSource ────────────────────────────────────────

    /// <summary>
    /// ValidEmails: NUnit TestCaseSource providing known-valid email addresses.
    ///
    /// WHY USE YIELD RETURN: yield return is C#'s lazy iterator syntax. Rather than
    /// building a full list and returning it, the method produces one item at a time
    /// as NUnit requests them. This is slightly more memory-efficient and reads cleanly.
    ///
    /// .Returns(true) tells NUnit that when this input is passed to the test method,
    /// the expected return value is true — so the test passes only if IsValidEmail
    /// returns true for that input.
    /// </summary>
    public static IEnumerable<TestCaseData> ValidEmails()
    {
        // Standard format — the most common valid email shape
        yield return new TestCaseData("user@example.com").Returns(true);

        // With dot and plus-tag — both are valid per RFC 5321 and used by Gmail, etc.
        yield return new TestCaseData("test.user+tag@domain.org").Returns(true);

        // Minimal valid format — shortest possible but syntactically correct
        yield return new TestCaseData("a@b.io").Returns(true);
    }

    /// <summary>
    /// InvalidEmails: NUnit TestCaseSource providing known-invalid email addresses
    /// and edge cases that the validator must reject.
    ///
    /// COVERAGE RATIONALE: Each case tests a specific rule of email validation:
    ///   "notanemail"    → missing @ entirely
    ///   "missing@domain" → missing TLD (.com, .org, etc.)
    ///   "@nodomain.com" → missing local part before @
    ///   ""              → empty string
    ///   null            → null reference (must not throw NullReferenceException)
    /// </summary>
    public static IEnumerable<TestCaseData> InvalidEmails()
    {
        yield return new TestCaseData("notanemail").Returns(false);       // No @ symbol
        yield return new TestCaseData("missing@domain").Returns(false);   // No TLD
        yield return new TestCaseData("@nodomain.com").Returns(false);    // No local part
        yield return new TestCaseData("").Returns(false);                  // Empty string
        yield return new TestCaseData((string?)null).Returns(false);      // Null — must not crash
    }

    /// <summary>
    /// IsValidEmail_ValidInputs: Parameterised test that verifies IsValidEmail()
    /// returns true for all known-valid email addresses from ValidEmails().
    ///
    /// EXPRESSION-BODIED METHOD: The => syntax means this method body is just
    /// a single expression (the method call). NUnit uses the bool return value
    /// directly as the test result when paired with .Returns() in TestCaseData.
    /// </summary>
    [Test]
    [TestCaseSource(nameof(ValidEmails))]
    public bool IsValidEmail_ValidInputs(string email) =>
        StringUtils.IsValidEmail(email);

    /// <summary>
    /// IsValidEmail_InvalidInputs: Parameterised test that verifies IsValidEmail()
    /// returns false for all known-invalid inputs including null.
    ///
    /// WHY string? (NULLABLE STRING): The null test case requires the parameter
    /// to be nullable (string?) rather than non-nullable (string). Without the ?,
    /// the compiler would warn that null can't be assigned to a non-nullable parameter.
    /// The ? makes the null handling explicit and intentional.
    /// </summary>
    [Test]
    [TestCaseSource(nameof(InvalidEmails))]
    public bool IsValidEmail_InvalidInputs(string? email) =>
        StringUtils.IsValidEmail(email);

    // ─── SafeTrim ─────────────────────────────────────────────────────────────

    /// <summary>
    /// SafeTrim_RemovesWhitespace: Verifies that SafeTrim() removes leading and
    /// trailing whitespace from a string.
    ///
    /// WHY SAFE TRIM EXISTS: Standard string.Trim() throws NullReferenceException if
    /// called on null. SafeTrim() wraps Trim() with a null check, returning an empty
    /// string for null input. This prevents defensive null checks throughout the
    /// codebase — callers can always trust SafeTrim() to return a string, never null.
    /// </summary>
    [Test]
    public void SafeTrim_RemovesWhitespace()
    {
        // Leading and trailing spaces must be removed; inner content preserved.
        Assert.That(StringUtils.SafeTrim("  hello  "), Is.EqualTo("hello"));
    }

    /// <summary>
    /// SafeTrim_ReturnsEmptyForNull: Verifies that SafeTrim(null) returns empty
    /// string rather than throwing NullReferenceException.
    ///
    /// WHY THIS MATTERS: Test data pipelines often pass string values that may be
    /// null (from JSON parsing, config files, or API responses). If SafeTrim throws
    /// on null, every call site needs a null check. Returning empty string for null
    /// is the "null object" pattern — safer and simpler for callers.
    /// </summary>
    [Test]
    public void SafeTrim_ReturnsEmptyForNull()
    {
        // null input must return empty string, not throw an exception.
        Assert.That(StringUtils.SafeTrim(null), Is.Empty);
    }

    // ─── Capitalise ───────────────────────────────────────────────────────────

    /// <summary>
    /// Capitalise_UppercasesFirstLetter: Verifies that only the first character
    /// of the string is uppercased, with the rest left unchanged.
    ///
    /// WHY CAPITALISE: Used to format display values — environment names, user-facing
    /// labels — where only the first letter should be uppercase. "hello world" → "Hello world"
    /// is a common UX pattern (sentence case) that differs from ToUpper() which would
    /// produce "HELLO WORLD".
    /// </summary>
    [Test]
    public void Capitalise_UppercasesFirstLetter()
    {
        // Only the first 'h' should become 'H'; the rest of the string is unchanged.
        Assert.That(StringUtils.Capitalise("hello world"), Is.EqualTo("Hello world"));
    }

    /// <summary>
    /// Capitalise_ReturnsEmptyForNull: Verifies that Capitalise(null) returns
    /// empty string rather than throwing NullReferenceException.
    ///
    /// CONSISTENT NULL HANDLING: StringUtils methods follow a consistent contract —
    /// null input produces empty string output, never exceptions. This makes the
    /// library safe to use without defensive null checks at every call site.
    /// </summary>
    [Test]
    public void Capitalise_ReturnsEmptyForNull()
    {
        // null must return empty string — consistent with SafeTrim's null behaviour.
        Assert.That(StringUtils.Capitalise(null), Is.Empty);
    }
}
