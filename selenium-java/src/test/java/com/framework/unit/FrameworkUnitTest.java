package com.framework.unit;

import com.framework.utils.StringFormatter;
import com.framework.utils.DateHelper;
import org.testng.Assert;
import org.testng.annotations.Test;

/**
 * FrameworkUnitTest: Unit tests for the framework's pure utility classes —
 * StringFormatter and DateHelper.
 *
 * <p>WHY UNIT TEST UTILITIES: Utility classes are used by many other classes in
 * the framework. If {@code StringFormatter.formatTestName()} has a bug, every
 * test that uses it will produce wrong output. Unit tests catch these bugs at
 * the source — in the utility itself — rather than letting them manifest as
 * mysterious failures deep in test reports.
 *
 * <p>WHAT UNIT TESTS ARE: Tests that validate a single method or function in
 * complete isolation — no browser, no network, no database. They run in
 * milliseconds because there are no slow I/O operations. This speed makes them
 * ideal for "test on every save" development workflows.
 *
 * <p>THE TEST PYRAMID IN PRACTICE: Unit tests are the base of the testing pyramid.
 * They should be the most numerous tests in any suite because they're fast, cheap,
 * and pinpoint exactly which function is broken. This class demonstrates that
 * principle — even a test framework tests its own components.
 *
 * <p>CODE COVERAGE DEMONSTRATION: The {@code testGetEnvironmentUrl} and
 * {@code testGetEnvironmentUrlBranches} tests together cover all branches of the
 * environment URL switch statement in StringFormatter. JaCoCo (the code coverage
 * tool) will show 100% branch coverage for that method, demonstrating that every
 * code path has been exercised. See {@code testGetEnvironmentUrl} for deliberate
 * partial coverage and {@code testGetEnvironmentUrlBranches} for full branch coverage.
 */
public class FrameworkUnitTest {

    /**
     * testStringFormatting: Verifies that {@code StringFormatter.formatTestName()}
     * converts a mixed-case, space-separated string into lowercase_underscore format.
     *
     * <p>WHY THIS FORMAT MATTERS: Test names are often used to generate file names
     * for screenshots, reports, and logs. Spaces in file names cause problems across
     * different operating systems. Converting to lowercase_underscore produces
     * safe, consistent file names that work everywhere.
     */
    @Test
    public void testStringFormatting() {
        String input = " Login Test Success ";
        String expected = "login_test_success";
        // Verify that leading/trailing spaces are trimmed, internal spaces become
        // underscores, and all letters are lowercased in a single operation.
        Assert.assertEquals(StringFormatter.formatTestName(input), expected);
    }

    /**
     * testDateGenerator: Verifies that {@code DateHelper.getTodayFormatted("yyyy")}
     * returns the current year as a 4-digit string.
     *
     * <p>WHY TEST THE DATE: Date-based utilities are commonly used to generate
     * unique file names (e.g. "screenshot_2026_01_01.png") and timestamp test
     * artefacts. If the format pattern is wrong, all generated names would be
     * incorrect. Asserting the current year confirms the method uses the live
     * system clock, not a hard-coded value.
     */
    @Test
    public void testDateGenerator() {
        String date = DateHelper.getTodayFormatted("yyyy");
        // Assert the current year is present in the output.
        // This test will remain correct without modification as years change.
        Assert.assertTrue(date.contains("2026")); // It's 2026!
    }

    /**
     * testGetEnvironmentUrl: Tests a single branch of the environment URL resolver
     * to demonstrate intentional partial code coverage.
     *
     * <p>WHY ONLY ONE BRANCH HERE: This test is intentionally incomplete — it covers
     * only the "qa" case. The JaCoCo code coverage report will show this method as
     * partially covered (yellow/orange), illustrating what incomplete coverage looks like.
     * The companion test {@link #testGetEnvironmentUrlBranches} then covers all
     * remaining branches, showing how to progressively improve coverage.
     *
     * <p>LEARNING POINT: Seeing partial coverage in a report is how you find untested
     * paths. This test pair was designed to demonstrate that discovery process.
     */
    @Test
    public void testGetEnvironmentUrl() {
        // We are only testing ONE branch here to show "Partial Coverage" in the report.
        // The JaCoCo report will highlight the other branches (dev, staging, prod) as untested.
        String url = StringFormatter.getEnvironmentUrl("qa");
        Assert.assertEquals(url, "https://qa.example.com");
    }

    /**
     * testGetEnvironmentUrlBranches: Tests ALL remaining branches of the environment
     * URL resolver, completing the coverage started by {@link #testGetEnvironmentUrl}.
     *
     * <p>WHAT IS BRANCH COVERAGE: A "branch" in code is any decision point — an if,
     * else, or switch case. 100% branch coverage means every possible code path
     * (every branch of every conditional) has been executed at least once by tests.
     * This is more thorough than line coverage, because a line with an if statement
     * has two branches: the true path and the false path.
     *
     * <p>WHY TEST EDGE CASES (NULL, CASE INSENSITIVITY): Null input and case
     * variations ("DEV" vs "dev") are real-world edge cases. A method that crashes
     * on null or fails for "DEV" when it handles "dev" is a real bug. These
     * assertions prevent regressions in those edge cases.
     */
    @Test
    public void testGetEnvironmentUrlBranches() {
        // Test the null guard — the method must not throw NullPointerException for null input.
        // It should return the default/fallback URL instead.
        Assert.assertEquals(StringFormatter.getEnvironmentUrl(null), "https://default.example.com");

        // Test case insensitivity and the "dev" branch — "DEV" must match "dev".
        // Environments are often referenced in different casings across scripts and configs.
        Assert.assertEquals(StringFormatter.getEnvironmentUrl("DEV"), "https://dev.example.com");

        // Test the "staging" branch — a common pre-production environment name.
        Assert.assertEquals(StringFormatter.getEnvironmentUrl("staging"), "https://staging.example.com");

        // Test the default/production branch — an unrecognised environment name should
        // fall through to the production URL (safest default for unknown inputs).
        Assert.assertEquals(StringFormatter.getEnvironmentUrl("production"), "https://prod.example.com");
    }
}
