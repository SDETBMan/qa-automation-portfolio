package com.saucedemo.stepDefinitions;

import com.saucedemo.pages.CartPage;
import com.saucedemo.pages.InventoryPage;
import com.saucedemo.utils.DriverManager;
import io.cucumber.java.en.And;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.testng.Assert;

/**
 * InventorySteps: Cucumber step definitions for product inventory and shopping cart scenarios.
 *
 * <p>This class covers the core e-commerce user journey: adding products to the cart,
 * verifying the cart badge count, removing products, navigating to the cart, verifying
 * cart contents, and proceeding to checkout. These steps drive the most complex
 * feature file in the suite — the shopping cart flow.
 *
 * <p>CARTPAGE HELD AS A FIELD: {@code cartPage} starts as null and is assigned when
 * the user navigates to the cart via {@code i_go_to_the_shopping_cart()}. Steps that
 * need {@code cartPage} (like {@code item_should_be_in_the_cart}) must run after
 * navigation — this is guaranteed by the Gherkin scenario's ordering.
 *
 * <p>STEP REUSE: Because Cucumber matches steps globally across all step definition
 * classes, any step defined here can be reused in any feature file without importing
 * this class. This is a key advantage over traditional TestNG/JUnit test organisation.
 *
 * <p>NOTE ON {@code @And}: Cucumber treats {@code @And} as an alias for whatever
 * the previous keyword was (Given, When, or Then). It exists purely for readability
 * in the feature file — "And I click the checkout button" reads more naturally than
 * "When I click the checkout button" following a When step.
 */
public class InventorySteps {

    // InventoryPage is always available since this step class is used from the inventory screen
    private final InventoryPage inventoryPage = new InventoryPage(DriverManager.getDriver());

    // CartPage is null until navigation to the cart occurs — see i_go_to_the_shopping_cart()
    private CartPage cartPage;

    /**
     * WHEN step: Adds the named product to the shopping cart from the inventory screen.
     *
     * <p>The product name comes from the Gherkin step (e.g.,
     * {@code When I add "Sauce Labs Backpack" to the inventory}).
     * InventoryPage translates the name to the correct button ID and handles the click.
     *
     * @param productName the display name of the product to add to the cart
     */
    @When("I add {string} to the inventory")
    public void i_add_to_the_inventory(String productName) {
        inventoryPage.addToCart(productName);
    }

    /**
     * THEN step: Asserts the cart badge shows the expected item count.
     *
     * <p>The {@code {int}} Cucumber expression type extracts an integer directly
     * from the Gherkin step — no need to call {@code Integer.parseInt()} manually.
     * The assertion confirms the badge has updated correctly after an add or remove action.
     *
     * @param expectedCount the number of items expected to appear in the cart badge
     */
    @Then("the inventory cart badge should show {int}")
    public void the_inventory_cart_badge_should_show(int expectedCount) {
        Assert.assertEquals(inventoryPage.getCartItemCount(), expectedCount,
                "Inventory cart badge count mismatch");
    }

    /**
     * WHEN step: Clicks the cart icon to navigate to the shopping cart page.
     *
     * <p>The returned {@link CartPage} object is stored in the field {@code cartPage}
     * so that subsequent THEN steps in the same scenario can use it to make assertions
     * about the cart's contents.
     *
     * <p>CHAINED PAGE OBJECTS: {@code inventoryPage.goToCart()} returns a new
     * CartPage instance only after the URL confirms the navigation completed. This
     * ensures {@code cartPage} is always in a usable state when subsequent steps run.
     */
    @When("I go to the shopping cart")
    public void i_go_to_the_shopping_cart() {
        // goToCart() navigates to the cart page and returns a CartPage object
        cartPage = inventoryPage.goToCart();
    }

    /**
     * THEN step: Asserts the named product appears in the cart item list.
     *
     * <p>Relies on {@code cartPage} being populated by the previous
     * {@link #i_go_to_the_shopping_cart()} step. In a correctly structured scenario,
     * the "I go to the shopping cart" When step always precedes this assertion.
     *
     * @param productName the product name (or partial name) to search for in the cart
     */
    @Then("{string} should be in the cart")
    public void item_should_be_in_the_cart(String productName) {
        Assert.assertTrue(cartPage.isItemInCart(productName),
                productName + " was not found in the cart");
    }

    /**
     * WHEN step: Removes the named product from the cart via the inventory screen.
     *
     * <p>This is used in scenarios that test the remove-from-cart flow: add an item,
     * verify the badge increments, remove the item, verify the badge decrements (or
     * disappears entirely). The remove action updates the badge count in the DOM,
     * and InventoryPage waits for that update before returning.
     *
     * @param productName the display name of the product to remove
     */
    @When("I remove {string} from the inventory")
    public void i_remove_from_the_inventory(String productName) {
        inventoryPage.removeFromCart(productName);
    }

    /**
     * THEN step: Asserts the cart is completely empty (badge count equals zero).
     *
     * <p>{@link InventoryPage#getCartItemCount()} returns 0 when the badge element
     * is absent from the DOM (i.e., the cart is empty), so this assertion works
     * correctly even when the badge disappears entirely after the last item is removed.
     */
    @Then("the cart should be empty")
    public void the_cart_should_be_empty() {
        Assert.assertEquals(inventoryPage.getCartItemCount(), 0,
                "Expected cart to be empty but badge still shows items");
    }

    /**
     * AND step: Clicks the Checkout button on the cart page to begin the checkout flow.
     *
     * <p>Using {@code @And} here keeps the feature file reading naturally as a
     * continuation of the previous When/Then step. Cucumber treats it identically
     * to {@code @When} at runtime.
     *
     * <p>Relies on {@code cartPage} being set by {@link #i_go_to_the_shopping_cart()}.
     */
    @And("I click the checkout button")
    public void i_click_the_checkout_button() {
        cartPage.clickCheckout();
    }

    /**
     * THEN step: Asserts the browser has navigated to the checkout information page.
     *
     * <p>URL-based assertion is used here because the checkout page does not have a
     * unique, easily identifiable header element — the URL segment "checkout-step-one"
     * is the most reliable indicator of correct navigation.
     */
    @Then("I should be on the checkout page")
    public void i_should_be_on_the_checkout_page() {
        Assert.assertTrue(
                DriverManager.getDriver().getCurrentUrl().contains("checkout-step-one"),
                "Not on checkout page. Current URL: " + DriverManager.getDriver().getCurrentUrl());
    }
}
