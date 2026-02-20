package com.framework.api;

import com.framework.utils.ConfigReader;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.testng.Assert;
import org.testng.annotations.Test;

/**
 * UserApiTest: Validates backend service health and data integrity.
 */
public class UserApiTest {

    @Test(groups = {"integration", "smoke"})
    public void testUserApiHealth() {
        // Base URL from config; resource path appended here so other tests
        // can reuse api.base.url without duplicating the full URL.
        String endpoint = ConfigReader.getProperty("api.base.url") + "/users/1";

        System.out.println("[API-LOG] Requesting User Data from: " + endpoint);

        // Execute GET request
        Response response = RestAssured.get(endpoint);

        // Standardized Logging for CI/CD visibility
        System.out.println("[API-LOG] Status Code: " + response.getStatusCode());
        System.out.println("[API-LOG] Response Body: " + response.getBody().asString());

        // Assertions
        Assert.assertEquals(response.getStatusCode(), 200, "API Health Check Failed: Status should be 200 OK");

        String responseBody = response.getBody().asString();
        Assert.assertNotNull(responseBody, "API Error: Response body is null");
        Assert.assertTrue(responseBody.contains("Leanne Graham"), "Data Integrity Error: Response missing expected user data");
    }
}
