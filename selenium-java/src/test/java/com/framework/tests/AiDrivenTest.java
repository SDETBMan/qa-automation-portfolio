package com.framework.tests;

import com.framework.base.BaseTest;
import com.framework.driver.DriverManager;
import com.framework.pages.LoginPage;
import com.framework.utils.AiHelper;
import org.testng.Assert;
import org.testng.annotations.Test;

public class AiDrivenTest extends BaseTest {

    @Test(groups = {"ai", "web"})
    public void testLoginWithAiGeneratedData() {
        LoginPage loginPage = new LoginPage(DriverManager.getDriver());

        // 1. Ask "AI" to generate diverse (invalid) test data
        String aiUsername = AiHelper.generateTestData("Generate a valid looking email address");
        String aiPassword = AiHelper.generateTestData("Generate a complex password");

        System.out.println("[AI] Testing with generated credentials: " + aiUsername);

        // 2. Attempt Login with AI Data
        loginPage.login(aiUsername, aiPassword);

        // 3. Assertion: Negative Test
        String error = loginPage.getErrorMessage();

        Assert.assertTrue(error.contains("Username and password do not match"),
                "FAILURE: App accepted invalid AI data or crashed! Error displayed: " + error);

        System.out.println("[PASS] App correctly rejected invalid AI credentials.");
    }
}
