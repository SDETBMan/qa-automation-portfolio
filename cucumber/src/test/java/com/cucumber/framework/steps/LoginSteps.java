package com.cucumber.framework.steps;

import com.cucumber.framework.driver.DriverManager;
import com.cucumber.framework.pages.LoginPage;
import com.cucumber.framework.utils.ConfigReader;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.junit.Assert;

/**
 * Step definitions for login.feature.
 *
 * Also contains the shared "I am logged in as" step used as a Background
 * in inventory.feature and cart.feature — authentication is login's concern.
 */
public class LoginSteps {

    private LoginPage loginPage;

    // ── Shared background step (used by inventory + cart features) ────────────

    @Given("I am on the login page")
    public void iAmOnTheLoginPage() {
        DriverManager.getDriver().get(ConfigReader.get("url", "https://www.saucedemo.com"));
        loginPage = new LoginPage(DriverManager.getDriver());
    }

    @Given("I am logged in as {string}")
    public void iAmLoggedInAs(String username) {
        DriverManager.getDriver().get(ConfigReader.get("url", "https://www.saucedemo.com"));
        loginPage = new LoginPage(DriverManager.getDriver());
        loginPage.login(username, ConfigReader.get("app_password", "secret_sauce"));
        Assert.assertTrue("Login failed — not on inventory page",
                DriverManager.getDriver().getCurrentUrl().contains("inventory"));
    }

    // ── Login-specific steps ──────────────────────────────────────────────────

    @When("I log in with username {string} and password {string}")
    public void iLogInWithUsernameAndPassword(String username, String password) {
        if (loginPage == null) loginPage = new LoginPage(DriverManager.getDriver());
        loginPage.login(username, password);
    }

    @Then("I should be on the inventory page")
    public void iShouldBeOnTheInventoryPage() {
        Assert.assertTrue("Expected inventory page but URL was: "
                        + DriverManager.getDriver().getCurrentUrl(),
                DriverManager.getDriver().getCurrentUrl().contains("inventory"));
    }

    @Then("I should see an error message containing {string}")
    public void iShouldSeeAnErrorMessageContaining(String expectedText) {
        if (loginPage == null) loginPage = new LoginPage(DriverManager.getDriver());
        Assert.assertTrue("Error not displayed", loginPage.isErrorDisplayed());
        Assert.assertTrue("Expected error to contain: " + expectedText,
                loginPage.getErrorMessage().toLowerCase()
                         .contains(expectedText.toLowerCase()));
    }
}
