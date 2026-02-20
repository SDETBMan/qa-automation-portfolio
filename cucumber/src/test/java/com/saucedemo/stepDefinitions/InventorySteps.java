package com.saucedemo.stepDefinitions;

import com.saucedemo.pages.CartPage;
import com.saucedemo.pages.InventoryPage;
import com.saucedemo.utils.DriverManager;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.testng.Assert;

public class InventorySteps {

    private final InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());
    private CartPage cartPage;

    @When("I add {string} to the inventory")
    public void i_add_to_the_inventory(String productName) {
        inventoryPage.addToCart(productName);
    }

    @Then("the inventory cart badge should show {int}")
    public void the_inventory_cart_badge_should_show(int expectedCount) {
        Assert.assertEquals(inventoryPage.getCartItemCount(), expectedCount,
                "Inventory cart badge count mismatch");
    }

    @When("I go to the shopping cart")
    public void i_go_to_the_shopping_cart() {
        cartPage = inventoryPage.goToCart();
    }

    @Then("{string} should be in the cart")
    public void item_should_be_in_the_cart(String productName) {
        Assert.assertTrue(cartPage.isItemInCart(productName),
                productName + " was not found in the cart");
    }

    @When("I remove {string} from the inventory")
    public void i_remove_from_the_inventory(String productName) {
        inventoryPage.removeFromCart(productName);
    }

    @Then("the cart should be empty")
    public void the_cart_should_be_empty() {
        Assert.assertEquals(inventoryPage.getCartItemCount(), 0,
                "Expected cart to be empty but badge still shows items");
    }

    @And("I click the checkout button")
    public void i_click_the_checkout_button() {
        cartPage.clickCheckout();
    }

    @Then("I should be on the checkout page")
    public void i_should_be_on_the_checkout_page() {
        Assert.assertTrue(
                DriverManager.getDriver().getCurrentUrl().contains("checkout-step-one"),
                "Not on checkout page. Current URL: " + DriverManager.getDriver().getCurrentUrl());
    }
}
