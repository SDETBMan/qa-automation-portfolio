package com.saucedemo.stepDefinitions;

import com.saucedemo.utils.ConfigReader;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.testng.Assert;

/**
 * ApiSteps: Cucumber step definitions for REST API test scenarios.
 *
 * <p>WHY API TESTING IN A UI FRAMEWORK: Modern QA portfolios demonstrate multiple
 * testing layers. API tests are faster and more stable than UI tests because they
 * bypass the browser entirely — they send HTTP requests directly to the server and
 * inspect the responses. Including API steps in this Cucumber framework shows that
 * the same BDD (Behaviour-Driven Development) approach used for UI tests can also
 * cover backend services.
 *
 * <p>RESTASSURED: RestAssured is the industry-standard Java library for API testing.
 * It provides a fluent, readable API for building HTTP requests and asserting on
 * responses. The test target here is JSONPlaceholder (jsonplaceholder.typicode.com),
 * a free, public fake REST API designed specifically for testing and prototyping.
 *
 * <p>STATE BETWEEN STEPS: The {@code Response} object from the When step is stored
 * in a field so subsequent Then/And steps can inspect it. This is the standard pattern
 * for stateful step chains in Cucumber — each step in a scenario that needs shared
 * data stores it in a class field.
 *
 * <p>NO WEBDRIVER NEEDED: This class has no dependency on DriverManager or any page
 * objects. API tests run in-process using just HTTP — they are significantly faster
 * than browser tests and can run alongside them in the same suite.
 */
public class ApiSteps {

    /**
     * Stores the HTTP response from the most recent API call.
     * Populated by {@link #i_send_a_get_request_to(String)} and read by
     * subsequent assertion steps in the same scenario.
     */
    private Response response;

    /**
     * The base URL for API requests in this scenario.
     * Populated by {@link #the_api_base_url_is_configured()} from config.properties.
     */
    private String baseUrl;

    /**
     * GIVEN step: Reads and logs the configured API base URL.
     *
     * <p>Separating the base URL configuration into its own Given step makes
     * scenarios self-documenting: a reader of the feature file can immediately see
     * which API is being tested. It also allows different scenarios to point at
     * different base URLs by overriding the config property.
     */
    @Given("the API base URL is configured")
    public void the_api_base_url_is_configured() {
        // Read from config.properties; default to the public JSONPlaceholder API
        baseUrl = ConfigReader.getProperty("api.base.url", "https://jsonplaceholder.typicode.com");
        System.out.println("[API] Base URL: " + baseUrl);
    }

    /**
     * WHEN step: Sends an HTTP GET request to the given path and stores the response.
     *
     * <p>RestAssured's static {@code get()} method builds and sends the request in one
     * call. The response object captures the status code, headers, and body, making
     * all of them available to subsequent assertion steps without re-issuing the request.
     *
     * @param path the URL path to append to the base URL (e.g., "/posts/1")
     */
    @When("I send a GET request to {string}")
    public void i_send_a_get_request_to(String path) {
        // Build the full URL by combining the base URL and the path from the Gherkin step
        String endpoint = baseUrl + path;
        System.out.println("[API] GET " + endpoint);
        // RestAssured.get() issues the HTTP GET and returns the full Response object
        response = RestAssured.get(endpoint);
        System.out.println("[API] Status: " + response.getStatusCode());
    }

    /**
     * THEN step: Asserts the HTTP response status code matches the expected value.
     *
     * <p>The {@code {int}} Cucumber expression extracts the integer from the Gherkin
     * step automatically. The assertion message includes the full response body so
     * that if the status is unexpected, the failure output reveals exactly what the
     * server returned — saving time diagnosing failures.
     *
     * @param expectedStatus the HTTP status code expected (e.g., 200, 404, 201)
     */
    @Then("the response status code should be {int}")
    public void the_response_status_code_should_be(int expectedStatus) {
        Assert.assertEquals(response.getStatusCode(), expectedStatus,
                "Unexpected status code. Response: " + response.getBody().asString());
    }

    /**
     * AND step: Asserts the response body contains the given substring.
     *
     * <p>A simple substring check is intentionally broad — it verifies that a key
     * piece of expected data is present without requiring an exact JSON structure
     * match, making the step resilient to minor API response changes (e.g., added
     * fields). For stricter validation, JSON path extraction (available in RestAssured
     * via {@code response.jsonPath().get("fieldName")}) can be used in a custom step.
     *
     * @param expected the string that must appear somewhere in the response body
     */
    @And("the response body should contain {string}")
    public void the_response_body_should_contain(String expected) {
        Assert.assertTrue(response.getBody().asString().contains(expected),
                "Response body missing expected value: " + expected);
    }
}
