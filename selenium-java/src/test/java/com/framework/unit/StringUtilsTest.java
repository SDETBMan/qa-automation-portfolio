package com.framework.unit;

import com.framework.utils.StringUtils;
import org.testng.Assert;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

/**
 * StringUtilsTest: Validates utility logic in milliseconds.
 * Proves adherence to the "Test Pyramid" principle (Unit > UI).
 */
public class StringUtilsTest {

    // ---------------------------------------------------------
    // HAPPY PATH (Unit): Format Validation
    // ---------------------------------------------------------
    @Test(groups = "unit")
    public void testEmailGenerationFormat() {
        String email = StringUtils.generateRandomEmail();
        System.out.println("[UNIT] Generated: " + email);

        Assert.assertNotNull(email, "Email should not be null");

        // Use Regex for strict format validation
        // Pattern: user + numbers + @ + domain + .com
        String emailPattern = "^user\\d+@[a-z]+\\.com$";
        Assert.assertTrue(email.matches(emailPattern),
                "Generated email [" + email + "] did not match expected regex pattern.");
    }

    // ---------------------------------------------------------
    // EDGE CASE (Unit): Randomness Check
    // A random generator is useless if it returns the same thing twice.
    // ---------------------------------------------------------
    @Test(groups = "unit")
    public void testRandomness() {
        String email1 = StringUtils.generateRandomEmail();
        String email2 = StringUtils.generateRandomEmail();

        Assert.assertNotEquals(email1, email2, "Random email generator produced a duplicate!");
    }

    // ---------------------------------------------------------
    // PARAMETERIZED TEST (Unit): Boundary Testing
    // Tests multiple scenarios without writing multiple test methods.
    // ---------------------------------------------------------
    @Test(groups = "unit", dataProvider = "emailValidationData")
    public void testEmailValidationLogic(String email, boolean expectedResult) {
        boolean actualResult = StringUtils.isValidEmail(email);

        Assert.assertEquals(actualResult, expectedResult,
                "Validation failed for input: [" + email + "]");
    }

    /**
     * Data Provider for Email Validation.
     * Columns: { Input String, Expected Boolean Result }
     */
    @DataProvider(name = "emailValidationData")
    public Object[][] getEmailValidationData() {
        return new Object[][]{
                // Happy Paths
                {"test@example.com", true},
                {"user.name@domain.co.uk", true},

                // Negative Paths
                {"plainaddress", false},         // Missing @
                {"@example.com", false},         // Missing username
                {"user@", false},                // Missing domain
                {"user@.com", false},            // Missing domain name
                {"", false},                     // Empty
                {null, false}                    // Null
        };
    }
}
