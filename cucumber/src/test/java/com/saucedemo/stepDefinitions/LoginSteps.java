package com.saucedemo.stepDefinitions;

import com.saucedemo.pages.LoginPage;
import com.saucedemo.pages.ProductsPage;
import com.saucedemo.utils.ConfigReader;
import com.saucedemo.utils.DriverManager;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.When;
import io.cucumber.java.en.Then;
import org.testng.Assert;

public class LoginSteps {

    private LoginPage loginPage = new LoginPage(DriverManager.getDriver());
    private ProductsPage productsPage;

    @Given("I am on the SauceDemo login page")
    public void i_am_on_the_login_page() {
        // 1. Navigate to the website
        DriverManager.getDriver().get(ConfigReader.getProperty("url", "https://www.saucedemo.com/"));

        // 2. Verify we are actually there
        Assert.assertTrue(DriverManager.getDriver().getCurrentUrl().contains("saucedemo"),
                "Not on login page! Current URL is: " + DriverManager.getDriver().getCurrentUrl());
    }

    @When("I enter username {string} and password {string}")
    public void i_enter_credentials(String username, String password) {
        loginPage.enterUsername(username);
        loginPage.enterPassword(password);
    }

    @When("I click the login button")
    public void i_click_login() {
        // If successful, this returns a ProductsPage object
        // If failure, we stay on LoginPage. We handle this logic in the assertions.
        // For simplicity, we can just void the click here or store the result.
        loginPage.clickLogin();
    }

    @Then("I should be redirected to the Products page")
    public void verify_products_page() {
        productsPage = new ProductsPage(DriverManager.getDriver());
        Assert.assertTrue(productsPage.isProductsPageDisplayed(), "Products page not displayed!");
        Assert.assertEquals(productsPage.getPageTitle(), "Products");
    }

    @Then("I should see an error message")
    public void verify_error_message() {
        Assert.assertTrue(loginPage.isErrorDisplayed(), "Error message was expected but not found.");
    }

    @Then("I should see the {string} state")
    public void verify_login_state(String expectedResult) {
        if (expectedResult.equalsIgnoreCase("success")) {
            verify_products_page();
        } else {
            verify_error_message();
        }
    }
}
