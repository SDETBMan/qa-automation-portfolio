package com.framework.tests;

import com.framework.base.BaseTest;
import com.framework.driver.DriverManager;
import com.framework.pages.LoginPage;
import com.framework.utils.AiHelper;
import org.testng.Assert;
import org.testng.annotations.Test;

/**
 * AiDrivenTest: Demonstrates AI-augmented test data generation integrated
 * into the Selenium test framework.
 *
 * <p>WHY AI IN TEST AUTOMATION: Traditional test data is static — the same
 * usernames and passwords are hard-coded or stored in config files. AI-generated
 * test data is dynamic and can simulate a wider variety of realistic inputs
 * without manual effort. This is an emerging SDET skill as AI becomes embedded
 * in the testing toolchain.
 *
 * <p>WHAT {@link AiHelper} DOES: {@code AiHelper.generateTestData(String prompt)}
 * calls an AI model (OpenAI GPT-4o via the API, with graceful fallback to
 * deterministic mock data when OPENAI_API_KEY is not set) with a
 * natural-language prompt describing what kind of data to generate. The AI returns
 * plausible-looking but invalid test credentials — the kind a real attacker or
 * curious user might try — that the app should reject.
 *
 * <p>WHY NEGATIVE TEST WITH AI DATA: The purpose here is not to log in successfully.
 * It's to confirm the application handles AI-generated (realistic but wrong)
 * credentials the same way it handles any invalid credentials — with a clear error
 * message, not a crash, security bypass, or silent failure.
 *
 * <p>PORTFOLIO VALUE: Including AI-driven test data generation demonstrates
 * awareness of modern tooling trends. Senior SDETs are increasingly expected to
 * integrate AI capabilities into their frameworks, and this class shows how that
 * integration would work in practice.
 *
 * <p>Extends {@link BaseTest}: inherits browser setup and teardown.
 */
public class AiDrivenTest extends BaseTest {

    /**
     * testLoginWithAiGeneratedData: Uses AI-generated credentials to attempt
     * a login and verifies the application correctly rejects them.
     *
     * <p>WHAT HAPPENS STEP BY STEP:
     * <ol>
     *   <li>Ask the AI to generate a "valid-looking" email address — something
     *       like "john.smith@company.com" that looks real but isn't in the system.</li>
     *   <li>Ask the AI to generate a "complex" password — something like
     *       "Tr0ub4dor&3" that looks legitimate but doesn't match any account.</li>
     *   <li>Attempt to log in with these AI-generated credentials.</li>
     *   <li>Assert the app shows the standard "Username and password do not match"
     *       error — it didn't crash, didn't grant access, and responded correctly.</li>
     * </ol>
     *
     * <p>WHY ASSERT THE SPECIFIC ERROR MESSAGE: The message "Username and password
     * do not match" is intentionally vague — it doesn't say which field is wrong.
     * This is a security best practice (not confirming whether the username exists),
     * and the test verifies this message is consistently returned for all invalid
     * credentials regardless of how realistic they look.
     */
    @Test(groups = {"ai", "web"})
    public void testLoginWithAiGeneratedData() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        // Step 1: Ask the AI helper to generate plausible-looking credentials.
        // The natural-language prompts describe the TYPE of data needed, not the
        // exact value — allowing the AI to produce varied, realistic test inputs.
        String aiUsername = AiHelper.generateTestData("Generate a valid looking email address");
        String aiPassword = AiHelper.generateTestData("Generate a complex password");

        // Log the generated credentials for debugging — useful in CI build logs
        // to see exactly what data was used if the test unexpectedly fails.
        System.out.println("[AI] Testing with generated credentials: " + aiUsername);

        // Step 2: Attempt login with the AI-generated credentials.
        loginPage.login(aiUsername, aiPassword);

        // Step 3: Assert the app rejected the credentials with the expected error.
        // A successful login (no error shown) would mean AI-generated data accidentally
        // matched a real account — extremely unlikely but worth guarding against.
        // A different error message or no error at all would indicate unexpected behaviour.
        String error = loginPage.getErrorMessage();

        Assert.assertTrue(error.contains("Username and password do not match"),
                "FAILURE: App accepted invalid AI data or crashed! Error displayed: " + error);

        System.out.println("[PASS] App correctly rejected invalid AI credentials.");
    }
}
