package com.saucedemo.stepDefinitions;

import com.saucedemo.pages.DashboardPage;
import com.saucedemo.pages.LoginPage;
import com.saucedemo.utils.ConfigReader;
import com.saucedemo.utils.DriverManager;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.testng.Assert;

/**
 * DashboardSteps: Cucumber step definitions for dashboard and navigation scenarios.
 *
 * <p>This class covers Gherkin steps related to the main dashboard header elements
 * (cart icon, page title) and user session management (logout). It also includes a
 * step for direct URL navigation, which is used in security test scenarios that verify
 * access control — confirming that unauthenticated users cannot bypass the login screen
 * by typing a protected URL directly into the browser address bar.
 *
 * <p>STEP DEFINITION SCOPE: Each step definition class in a Cucumber suite is
 * instantiated once per scenario by Cucumber's Dependency Injection (DI) container.
 * Page objects stored as fields are therefore fresh for each scenario, which means
 * they always use the current scenario's driver instance from DriverManager.
 *
 * <p>SHARED STEPS: Steps defined in this class can be freely referenced in any
 * feature file — Cucumber loads all glue classes from the configured package and
 * matches steps globally, so there is no need to import or link step definition
 * classes together explicitly.
 */
public class DashboardSteps {

    // Both page objects are initialised at field level using the current thread's driver.
    // This ensures they reference the correct browser session in parallel test runs.
    private final DashboardPage dashboardPage = new DashboardPage(DriverManager.getDriver());
    private final LoginPage loginPage         = new LoginPage(DriverManager.getDriver());

    /**
     * THEN step: Asserts the shopping cart icon is visible in the page header.
     *
     * <p>Presence of the cart icon indicates the user is authenticated and on the
     * dashboard. This step is commonly used as a post-login verification alternative
     * to checking the URL or page title.
     */
    @Then("the cart icon should be visible")
    public void the_cart_icon_should_be_visible() {
        Assert.assertTrue(dashboardPage.isCartIconDisplayed(),
                "Cart icon was not displayed on the dashboard");
    }

    /**
     * THEN step: Asserts the main products header text matches the expected value.
     *
     * <p>The {@code {string}} placeholder is replaced by Cucumber with the value
     * from the feature file step (e.g., {@code "Products"}). Using a parameterised
     * step rather than a hard-coded assertion means this step can verify the header
     * on any page, not just the inventory screen.
     *
     * @param expectedHeader the exact text expected in the page header (e.g., "Products")
     */
    @Then("the products header should display {string}")
    public void the_products_header_should_display(String expectedHeader) {
        Assert.assertEquals(dashboardPage.getWelcomeMessageText(), expectedHeader,
                "Products header text mismatch");
    }

    /**
     * WHEN step: Opens the hamburger navigation menu and clicks the logout link.
     *
     * <p>The actual multi-step navigation (open menu → wait for animation →
     * click logout link) is encapsulated in {@link DashboardPage#clickLogoutButton()}.
     * The step definition remains a single clean line, delegating complexity to
     * the page object — this is the core benefit of the Page Object Model.
     */
    @When("I open the menu and logout")
    public void i_open_the_menu_and_logout() {
        dashboardPage.clickLogoutButton();
    }

    /**
     * THEN step: Asserts the browser is back on the login page by verifying the
     * login button is visible.
     *
     * <p>After logout, the application should redirect to the login screen. Checking
     * for the login button's visibility is a reliable, element-based assertion that
     * does not depend on the URL (which could vary across environments).
     */
    @Then("I should be returned to the login page")
    public void i_should_be_returned_to_the_login_page() {
        Assert.assertTrue(loginPage.isLoginButtonDisplayed(),
                "Login button was not visible after logout");
    }

    /**
     * WHEN step: Directly navigates to a path on the SauceDemo domain without
     * going through the login flow.
     *
     * <p>WHY THIS STEP EXISTS (Access Control Testing): A well-secured web application
     * should redirect unauthenticated users back to the login page when they try to
     * access protected URLs directly. This step simulates that attack vector — it skips
     * login and goes straight to a path like "inventory.html" or "cart.html". A
     * subsequent THEN step then verifies the application responded correctly
     * (e.g., redirected to login).
     *
     * <p>The base URL is read from config so the same step works in all environments
     * without hard-coding a URL in the feature file.
     *
     * @param path the path relative to the base URL to navigate to (e.g., "inventory.html")
     */
    @When("I navigate directly to {string} without logging in")
    public void i_navigate_directly_without_logging_in(String path) {
        // Concatenate the configured base URL with the path from the Gherkin step
        String url = ConfigReader.getProperty("url", "https://www.saucedemo.com/") + path;
        DriverManager.getDriver().get(url);
    }
}
