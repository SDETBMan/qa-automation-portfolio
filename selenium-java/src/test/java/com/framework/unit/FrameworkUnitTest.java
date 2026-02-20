package com.framework.unit;

import com.framework.utils.StringFormatter;
import com.framework.utils.DateHelper;
import org.testng.Assert;
import org.testng.annotations.Test;

public class FrameworkUnitTest {

    @Test
    public void testStringFormatting() {
        String input = " Login Test Success ";
        String expected = "login_test_success";
        Assert.assertEquals(StringFormatter.formatTestName(input), expected);
    }

    @Test
    public void testDateGenerator() {
        String date = DateHelper.getTodayFormatted("yyyy");
        Assert.assertTrue(date.contains("2026")); // It's 2026!
    }

    @Test
    public void testGetEnvironmentUrl() {
        // We are only testing ONE branch here to see the "Partial Coverage" in the report
        String url = StringFormatter.getEnvironmentUrl("qa");
        Assert.assertEquals(url, "https://qa.example.com");
    }

    @Test
    public void testGetEnvironmentUrlBranches() {
        // Test Null Case (Hits the 'if' branch)
        Assert.assertEquals(StringFormatter.getEnvironmentUrl(null), "https://default.example.com");

        // Test Case Insensitivity & Dev Branch
        Assert.assertEquals(StringFormatter.getEnvironmentUrl("DEV"), "https://dev.example.com");

        // Test Staging Branch
        Assert.assertEquals(StringFormatter.getEnvironmentUrl("staging"), "https://staging.example.com");

        // Test Default/Prod Branch (Hits the 'default' case)
        Assert.assertEquals(StringFormatter.getEnvironmentUrl("production"), "https://prod.example.com");
    }
}
