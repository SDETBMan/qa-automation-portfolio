package com.saucedemo.stepDefinitions;

import com.saucedemo.utils.ConfigReader;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import org.testng.Assert;

public class ApiSteps {

    private Response response;
    private String baseUrl;

    @Given("the API base URL is configured")
    public void the_api_base_url_is_configured() {
        baseUrl = ConfigReader.getProperty("api.base.url", "https://jsonplaceholder.typicode.com");
        System.out.println("[API] Base URL: " + baseUrl);
    }

    @When("I send a GET request to {string}")
    public void i_send_a_get_request_to(String path) {
        String endpoint = baseUrl + path;
        System.out.println("[API] GET " + endpoint);
        response = RestAssured.get(endpoint);
        System.out.println("[API] Status: " + response.getStatusCode());
    }

    @Then("the response status code should be {int}")
    public void the_response_status_code_should_be(int expectedStatus) {
        Assert.assertEquals(response.getStatusCode(), expectedStatus,
                "Unexpected status code. Response: " + response.getBody().asString());
    }

    @And("the response body should contain {string}")
    public void the_response_body_should_contain(String expected) {
        Assert.assertTrue(response.getBody().asString().contains(expected),
                "Response body missing expected value: " + expected);
    }
}
