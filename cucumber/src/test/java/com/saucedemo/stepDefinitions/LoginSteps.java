package com.saucedemo.stepDefinitions;

import com.saucedemo.pages.LoginPage;
import com.saucedemo.pages.ProductsPage;
import com.saucedemo.utils.ConfigReader;
import com.saucedemo.utils.DriverManager;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.When;
import io.cucumber.java.en.Then;
import org.testng.Assert;

/**
 * LoginSteps: Cucumber step definitions for all login-related Gherkin steps.
 *
 * <p>WHAT ARE STEP DEFINITIONS: In Cucumber, feature files are written in plain
 * English using the Gherkin language (Given/When/Then). Step definitions are the
 * Java methods that Cucumber calls when it matches a line in a feature file against
 * a step definition's annotation pattern. This class is the "glue" between the
 * business-readable test scenarios and the actual browser automation code.
 *
 * <p>ANNOTATION PATTERNS: Each annotation contains a string pattern.
 * Curly-brace placeholders like {@code {string}} and {@code {int}} are Cucumber
 * expression types — Cucumber extracts the matching text from the Gherkin step and
 * passes it as a method parameter automatically. For example:
 * <pre>
 *   When I enter username "standard_user" and password "secret_sauce"
 * </pre>
 * ...is matched by {@code @When("I enter username {string} and password {string}")} and
 * Cucumber calls the method with arguments {@code ("standard_user", "secret_sauce")}.
 *
 * <p>PAGE OBJECTS: This class instantiates Page Objects at field level so they are
 * available across all step methods in the class without needing to be re-created
 * inside every method. {@code ProductsPage} is instantiated lazily (inside a step
 * method) because it is only needed after login completes.
 *
 * <p>SCENARIO OUTLINE SUPPORT: The {@code verify_login_state} step is designed to
 * work with Cucumber Scenario Outlines — a feature that runs the same scenario
 * multiple times with different data from an Examples table. The method receives
 * the expected result as a string parameter and branches accordingly, allowing one
 * step to cover both success and failure cases in the same parameterised scenario.
 */
public class LoginSteps {

    // Page objects are initialised here (field level) so all step methods in this
    // class can use them. The driver is obtained from the ThreadLocal store in
    // DriverManager, which ensures the correct driver is used in parallel test runs.
    private LoginPage loginPage = new LoginPage(DriverManager.getDriver());

    // ProductsPage is null until login succeeds — it is initialised in the assertion step
    private ProductsPage productsPage;

    /**
     * GIVEN step: Navigates the browser to the SauceDemo login page and verifies arrival.
     *
     * <p>WHY VERIFY THE URL: Simply calling {@code driver.get(url)} does not guarantee
     * the page loaded correctly. The assertion confirms the browser actually reached
     * the intended domain, catching DNS failures, redirects, or mis-configured URLs
     * early with a meaningful error message rather than a cryptic NoSuchElementException
     * later in the test.
     */
    @Given("I am on the SauceDemo login page")
    public void i_am_on_the_login_page() {
        // 1. Navigate to the website
        DriverManager.getDriver().get(ConfigReader.getProperty("url", "https://www.saucedemo.com/"));

        // 2. Verify we are actually there
        Assert.assertTrue(DriverManager.getDriver().getCurrentUrl().contains("saucedemo"),
                "Not on login page! Current URL is: " + DriverManager.getDriver().getCurrentUrl());
    }

    /**
     * WHEN step: Enters the provided username and password into the login form fields.
     *
     * <p>The {@code {string}} placeholders in the annotation are Cucumber expressions.
     * Cucumber extracts the double-quoted values from the Gherkin step and injects
     * them as the {@code username} and {@code password} parameters here.
     *
     * @param username the username value extracted from the Gherkin step text
     * @param password the password value extracted from the Gherkin step text
     */
    @When("I enter username {string} and password {string}")
    public void i_enter_credentials(String username, String password) {
        loginPage.enterUsername(username);
        loginPage.enterPassword(password);
    }

    /**
     * WHEN step: Clicks the Login button to submit the credentials entered in the previous step.
     *
     * <p>This step intentionally does not check the outcome of the click — that is
     * the responsibility of the subsequent THEN assertion steps. This separation
     * follows the Given/When/Then principle: When steps perform actions, Then steps
     * verify outcomes.
     */
    @When("I click the login button")
    public void i_click_login() {
        // If successful, this returns a ProductsPage object
        // If failure, we stay on LoginPage. We handle this logic in the assertions.
        // For simplicity, we can just void the click here or store the result.
        loginPage.clickLogin();
    }

    /**
     * THEN step: Asserts the browser landed on the Products page after a successful login.
     *
     * <p>Two assertions are made: one for visibility (the page title element exists
     * and is shown) and one for content (the title reads "Products"). Together they
     * confirm both that the navigation succeeded and that the correct screen loaded.
     */
    @Then("I should be redirected to the Products page")
    public void verify_products_page() {
        // Initialise ProductsPage here because it is only reachable after login
        productsPage = new ProductsPage(DriverManager.getDriver());
        Assert.assertTrue(productsPage.isProductsPageDisplayed(), "Products page not displayed!");
        Assert.assertEquals(productsPage.getPageTitle(), "Products");
    }

    /**
     * THEN step: Asserts that an error banner is visible on the login screen.
     *
     * <p>Used to verify that invalid credentials (locked-out user, wrong password,
     * SQL injection payload, etc.) were correctly rejected by the application and
     * that a user-facing error was displayed.
     */
    @Then("I should see an error message")
    public void verify_error_message() {
        Assert.assertTrue(loginPage.isErrorDisplayed(), "Error message was expected but not found.");
    }

    /**
     * THEN step: Routes to either the success or error assertion based on the
     * expected outcome parameter.
     *
     * <p>WHY THIS COMBINED STEP EXISTS — SCENARIO OUTLINE: Cucumber's Scenario
     * Outline feature runs the same scenario template multiple times, substituting
     * values from an Examples table. When the expected result varies (e.g., one row
     * expects "success", another expects "failure"), a single step that branches on
     * the outcome is cleaner than duplicating the entire scenario for each case.
     *
     * <p>Example feature file usage:
     * <pre>
     *   Scenario Outline: Login with various credentials
     *     Given I am on the SauceDemo login page
     *     When  I enter username "&lt;user&gt;" and password "&lt;pass&gt;"
     *     And   I click the login button
     *     Then  I should see the "&lt;result&gt;" state
     *
     *     Examples:
     *       | user           | pass         | result  |
     *       | standard_user  | secret_sauce | success |
     *       | locked_out_user| secret_sauce | failure |
     * </pre>
     *
     * @param expectedResult "success" to assert products page loaded; any other value
     *                       to assert an error message appeared
     */
    @Then("I should see the {string} state")
    public void verify_login_state(String expectedResult) {
        // Branch to the appropriate assertion based on the parameterised expected outcome
        if (expectedResult.equalsIgnoreCase("success")) {
            verify_products_page();
        } else {
            verify_error_message();
        }
    }
}
