package com.cucumber.framework.steps;

import com.cucumber.framework.driver.DriverManager;
import com.cucumber.framework.pages.CartPage;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.junit.Assert;

/**
 * Step definitions for cart.feature — cart page assertions and checkout navigation.
 */
public class CartSteps {

    private CartPage cartPage() {
        return new CartPage(DriverManager.getDriver());
    }

    @Then("I should see {string} in the cart")
    public void iShouldSeeInTheCart(String itemName) {
        Assert.assertTrue("Item '" + itemName + "' not found in cart",
                cartPage().isItemInCart(itemName));
    }

    @And("I click checkout")
    public void iClickCheckout() {
        cartPage().clickCheckout();
    }

    @Then("I should be on the checkout information page")
    public void iShouldBeOnTheCheckoutInformationPage() {
        Assert.assertTrue("Expected checkout-step-one page but URL was: "
                        + DriverManager.getDriver().getCurrentUrl(),
                DriverManager.getDriver().getCurrentUrl().contains("checkout-step-one"));
    }
}
