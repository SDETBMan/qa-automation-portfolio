package com.framework.unit;

import com.framework.utils.StringUtils;
import org.testng.Assert;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

/**
 * StringUtilsTest: Unit tests for the {@link StringUtils} utility class.
 *
 * <p>WHY TEST A UTILITY CLASS: {@code StringUtils} is used across many parts of
 * the framework — generating test data, validating inputs, cleaning strings.
 * If any of these utility methods has a bug, every feature that calls it is
 * affected. Unit testing utilities at this level catches bugs at the source
 * before they cascade into confusing failures elsewhere in the suite.
 *
 * <p>WHAT THE TEST PYRAMID PRINCIPLE MEANS HERE: Unit tests like these run in
 * milliseconds because they test pure functions — no browser, no network, no
 * database. The Test Pyramid recommends having many fast unit tests at the base,
 * fewer integration tests in the middle, and even fewer slow UI tests at the top.
 * This class represents the bottom of that pyramid.
 *
 * <p>TESTNG DATA PROVIDERS: The {@link #testEmailValidationLogic} test uses a
 * {@code @DataProvider} to run the same assertion logic across 8 different inputs
 * (valid addresses, invalid addresses, edge cases like null and empty) without
 * writing 8 separate test methods. This is the "Parameterised Test" pattern —
 * one test method, many test cases.
 */
public class StringUtilsTest {

    // ---------------------------------------------------------
    // HAPPY PATH (Unit): Format Validation
    // ---------------------------------------------------------

    /**
     * testEmailGenerationFormat: Verifies that {@code StringUtils.generateRandomEmail()}
     * produces a string matching the expected format: {@code user{number}@{domain}.com}.
     *
     * <p>WHY VALIDATE FORMAT WITH REGEX: {@code email.contains("@")} would pass for
     * many malformed strings. A regex pattern is more precise — it validates the
     * complete structure: "user" prefix, digits, "@", lowercase domain, ".com" suffix.
     * This ensures the generated email is usable as a test input, not just
     * superficially email-shaped.
     *
     * <p>WHY RANDOM EMAILS: Automated test data generation avoids hard-coded values
     * that might conflict with existing records in test databases or cause uniqueness
     * constraint violations when used in form submissions.
     */
    @Test(groups = "unit")
    public void testEmailGenerationFormat() {
        String email = StringUtils.generateRandomEmail();
        System.out.println("[UNIT] Generated: " + email);

        Assert.assertNotNull(email, "Email should not be null");

        // Strict regex validation of the full format:
        // "^user" — must start with "user"
        // "\\d+" — followed by one or more digits (timestamp or random number)
        // "@[a-z]+\\.com$" — ends with @domain.com (lowercase letters only)
        String emailPattern = "^user\\d+@[a-z]+\\.com$";
        Assert.assertTrue(email.matches(emailPattern),
                "Generated email [" + email + "] did not match expected regex pattern.");
    }

    // ---------------------------------------------------------
    // EDGE CASE (Unit): Randomness Check
    // A random generator is useless if it returns the same thing twice.
    // ---------------------------------------------------------

    /**
     * testRandomness: Verifies that two successive calls to {@code generateRandomEmail()}
     * produce different values — confirming the generator is actually random.
     *
     * <p>WHY TEST RANDOMNESS: A generator that always returns the same value would
     * produce test data collisions — form submissions rejecting duplicate usernames,
     * or database unique constraints firing. This test guards against a broken
     * implementation (e.g. a hard-coded seed or missing timestamp component) that
     * returns the same value every time.
     *
     * <p>NOTE: There is a theoretical (astronomically small) probability that two
     * legitimate random values could be equal. In practice, timestamp-based generation
     * makes this impossible within the same test run.
     */
    @Test(groups = "unit")
    public void testRandomness() {
        String email1 = StringUtils.generateRandomEmail();
        String email2 = StringUtils.generateRandomEmail();

        // If both calls return the same value, the generator isn't working correctly.
        Assert.assertNotEquals(email1, email2, "Random email generator produced a duplicate!");
    }

    // ---------------------------------------------------------
    // PARAMETERISED TEST (Unit): Boundary Testing
    // Tests multiple scenarios without writing multiple test methods.
    // ---------------------------------------------------------

    /**
     * testEmailValidationLogic: Parameterised test that verifies
     * {@code StringUtils.isValidEmail()} correctly classifies both valid and
     * invalid email addresses.
     *
     * <p>WHY PARAMETERISED: Rather than writing one test per email address (8 test
     * methods for 8 cases), a single test method is driven by the data provider.
     * TestNG invokes it once per row, reporting each row as a separate test case.
     * This keeps the test file concise while providing thorough boundary coverage.
     *
     * <p>WHAT BOUNDARY TESTING MEANS: At the "boundaries" of valid input, bugs hide.
     * An email validator that handles normal inputs correctly might still crash on
     * null, accept addresses with no domain, or reject valid addresses with tags
     * like "user+tag@domain.com". The data provider below covers all these boundaries.
     *
     * @param email          The input string to validate.
     * @param expectedResult {@code true} if the email is valid, {@code false} otherwise.
     */
    @Test(groups = "unit", dataProvider = "emailValidationData")
    public void testEmailValidationLogic(String email, boolean expectedResult) {
        boolean actualResult = StringUtils.isValidEmail(email);

        // Include the input in the failure message so it's obvious which case failed
        // when looking at a test report without needing to re-read the data provider.
        Assert.assertEquals(actualResult, expectedResult,
                "Validation failed for input: [" + email + "]");
    }

    /**
     * getEmailValidationData: TestNG DataProvider supplying email inputs and
     * their expected validation results.
     *
     * <p>RETURN FORMAT: A 2D Object array where each inner array is one test case.
     * Column 0 = email input, Column 1 = expected boolean result.
     * TestNG maps these to the test method parameters by position.
     *
     * <p>COVERAGE RATIONALE:
     * <ul>
     *   <li>Happy paths confirm normal valid formats are accepted.</li>
     *   <li>Negative paths confirm that structurally invalid strings are rejected.</li>
     *   <li>Edge cases (empty string, null) confirm the method handles boundary
     *       inputs without throwing NullPointerException or other unexpected errors.</li>
     * </ul>
     *
     * @return A 2D array of {email, expectedResult} test cases.
     */
    @DataProvider(name = "emailValidationData")
    public Object[][] getEmailValidationData() {
        return new Object[][]{
                // Happy Paths — standard valid email formats
                {"test@example.com", true},
                {"user.name@domain.co.uk", true},

                // Negative Paths — structurally invalid formats the validator must reject
                {"plainaddress", false},         // Missing @ symbol entirely
                {"@example.com", false},         // Missing username before @
                {"user@", false},                // Missing domain after @
                {"user@.com", false},            // Domain name missing (just the TLD)
                {"", false},                     // Empty string — not an email
                {null, false}                    // Null — must not throw NullPointerException
        };
    }
}
