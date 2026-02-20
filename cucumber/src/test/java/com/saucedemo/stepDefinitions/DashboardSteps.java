package com.saucedemo.stepDefinitions;

import com.saucedemo.pages.DashboardPage;
import com.saucedemo.pages.LoginPage;
import com.saucedemo.utils.ConfigReader;
import com.saucedemo.utils.DriverManager;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.testng.Assert;

public class DashboardSteps {

    private final DashboardPage dashboardPage = new DashboardPage(DriverManager.getDriver());
    private final LoginPage loginPage         = new LoginPage(DriverManager.getDriver());

    @Then("the cart icon should be visible")
    public void the_cart_icon_should_be_visible() {
        Assert.assertTrue(dashboardPage.isCartIconDisplayed(),
                "Cart icon was not displayed on the dashboard");
    }

    @Then("the products header should display {string}")
    public void the_products_header_should_display(String expectedHeader) {
        Assert.assertEquals(dashboardPage.getWelcomeMessageText(), expectedHeader,
                "Products header text mismatch");
    }

    @When("I open the menu and logout")
    public void i_open_the_menu_and_logout() {
        dashboardPage.clickLogoutButton();
    }

    @Then("I should be returned to the login page")
    public void i_should_be_returned_to_the_login_page() {
        Assert.assertTrue(loginPage.isLoginButtonDisplayed(),
                "Login button was not visible after logout");
    }

    @When("I navigate directly to {string} without logging in")
    public void i_navigate_directly_without_logging_in(String path) {
        String url = ConfigReader.getProperty("url", "https://www.saucedemo.com/") + path;
        DriverManager.getDriver().get(url);
    }
}
