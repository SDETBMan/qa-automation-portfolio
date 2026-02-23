package com.framework.utils;

/**
 * StringUtils: Provides reusable string generation and validation logic for test support.
 *
 * WHY THIS CLASS EXISTS:
 * Tests frequently need unique email addresses (to avoid collision when registering users
 * in repeated runs) and need to validate email format in both positive and negative test
 * scenarios. Centralizing this logic here means:
 *   1. The generation algorithm is tested once and trusted everywhere it's used
 *   2. The validation regex is defined in one place (no risk of different tests using
 *      different validation rules and getting inconsistent results)
 *   3. StringUtilsTest can verify this logic in milliseconds without a browser
 *
 * For recruiters: Having unit-tested utility classes for data generation shows the engineer
 * applies the same quality standards to framework code as to test code.
 */
public class StringUtils {

    /**
     * Generates a unique email address for use in test scenarios.
     *
     * WHY System.nanoTime() OVER System.currentTimeMillis():
     * currentTimeMillis() has millisecond precision. In a fast parallel test suite, two
     * threads could call this method within the same millisecond and generate identical
     * email addresses — causing test data collisions. nanoTime() has nanosecond precision
     * and is virtually guaranteed to produce different values across concurrent calls,
     * making it the correct choice for uniqueness guarantees in parallel execution.
     *
     * NOTE: nanoTime() measures elapsed time since an arbitrary reference point (not a real
     * clock time), so the digits in the generated email are not a meaningful timestamp —
     * they are purely for uniqueness. The format "user<digits>@test.com" is recognizable
     * as synthetic test data while still passing email validation checks.
     *
     * @return A unique email address in the format "user<nanoseconds>@test.com"
     */
    public static String generateRandomEmail() {
        return "user" + System.nanoTime() + "@test.com";
    }

    /**
     * Validates whether a string conforms to basic email address format rules.
     *
     * WHY EMAIL VALIDATION IN A TEST FRAMEWORK:
     * Tests that generate email addresses (like generateRandomEmail()) should verify that
     * the generated value actually looks like a real email. Additionally, tests that verify
     * application-level email validation logic use this as the expected baseline: "the app
     * should accept these formats and reject those formats."
     *
     * THE REGEX EXPLAINED (plain English):
     *   ^                   - start of string (nothing before the pattern)
     *   [A-Za-z0-9+_.-]+    - one or more characters that are letters, digits, or +_.-
     *   @                   - a literal "@" character
     *   [A-Za-z0-9.-]+      - one or more characters forming the domain name
     *   \\.                 - a literal "." (backslash escapes the dot so it doesn't
     *                         mean "any character" as it normally does in regex)
     *   [A-Za-z]{2,}        - two or more letters for the top-level domain (.com, .org, .io)
     *   $                   - end of string (nothing after the pattern)
     *
     * WHAT THIS VALIDATES:
     *   "test@example.com"        → true  (valid standard email)
     *   "user.name@domain.co.uk"  → true  (valid with subdomain TLD)
     *   "plainaddress"            → false (no @ or domain)
     *   "@example.com"            → false (missing local part before @)
     *   "user@"                   → false (missing domain)
     *   null or ""                → false (null/empty guard prevents NullPointerException)
     *
     * @param email The string to check for email format compliance
     * @return true if the string matches the expected email pattern; false otherwise
     */
    public static boolean isValidEmail(String email) {
        if (email == null || email.isEmpty()) return false;
        return email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");
    }
}
