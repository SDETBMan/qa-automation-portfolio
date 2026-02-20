package com.saucedemo.stepDefinitions;

import com.saucedemo.pages.CartPage;
import com.saucedemo.pages.ProductsPage;
import com.saucedemo.utils.DriverManager;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.testng.Assert;

public class CartSteps {

    // We initialize pages inside the methods or a setup block
    // to ensure they use the active driver
    ProductsPage productsPage = new ProductsPage(DriverManager.getDriver());
    CartPage cartPage = new CartPage(DriverManager.getDriver());

    @When("I add the {string} to the cart")
    public void i_add_item_to_cart(String productName) {
        productsPage.addToCart(productName);
    }

    @Then("the cart badge should show {string}")
    public void verify_cart_badge(String expectedCount) {
        Assert.assertEquals(productsPage.getCartBadgeText(), expectedCount);
    }

    @When("I click the cart icon")
    public void i_click_cart_icon() {
        productsPage.clickCartIcon();
    }

    @Then("I should see {string} in the cart list")
    public void verify_item_in_cart(String expectedItem) {
        Assert.assertEquals(cartPage.getFirstItemName(), expectedItem);
    }
}
