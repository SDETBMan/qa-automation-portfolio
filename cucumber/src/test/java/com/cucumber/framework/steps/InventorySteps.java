package com.cucumber.framework.steps;

import com.cucumber.framework.driver.DriverManager;
import com.cucumber.framework.pages.CartPage;
import com.cucumber.framework.pages.InventoryPage;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.junit.Assert;

/**
 * Step definitions for inventory.feature — cart add/remove and badge assertions.
 */
public class InventorySteps {

    private InventoryPage inventoryPage() {
        return new InventoryPage(DriverManager.getDriver());
    }

    // ── Given ─────────────────────────────────────────────────────────────────

    @Given("I have added {string} to the cart")
    public void iHaveAddedToTheCart(String itemSlug) {
        inventoryPage().addItemToCart(itemSlug);
    }

    // ── When ──────────────────────────────────────────────────────────────────

    @When("I add {string} to the cart")
    public void iAddToTheCart(String itemSlug) {
        inventoryPage().addItemToCart(itemSlug);
    }

    @And("I add {string} to the cart")
    public void iAlsoAddToTheCart(String itemSlug) {
        inventoryPage().addItemToCart(itemSlug);
    }

    @When("I remove {string} from the cart")
    public void iRemoveFromTheCart(String itemSlug) {
        inventoryPage().removeItemFromCart(itemSlug);
    }

    @When("I navigate to the cart")
    public void iNavigateToTheCart() {
        inventoryPage().goToCart();
    }

    // ── Then ──────────────────────────────────────────────────────────────────

    @Then("the cart badge should show {string}")
    public void theCartBadgeShouldShow(String expectedCount) {
        Assert.assertEquals("Cart badge count mismatch",
                expectedCount, inventoryPage().getCartBadgeCount());
    }

    @Then("the cart badge should not be visible")
    public void theCartBadgeShouldNotBeVisible() {
        Assert.assertFalse("Cart badge should not be visible",
                inventoryPage().isCartBadgeVisible());
    }

    @Then("I should see {int} item(s) in the cart")
    public void iShouldSeeItemsInTheCart(int expectedCount) {
        CartPage cartPage = new CartPage(DriverManager.getDriver());
        Assert.assertEquals("Cart item count mismatch",
                expectedCount, cartPage.getCartItemCount());
    }
}
