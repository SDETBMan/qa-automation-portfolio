package com.saucedemo.stepDefinitions;

import com.saucedemo.pages.CartPage;
import com.saucedemo.pages.ProductsPage;
import com.saucedemo.utils.DriverManager;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.testng.Assert;

/**
 * CartSteps: Cucumber step definitions for the cart-centric shopping flow.
 *
 * <p>This class covers the journey from the Products page through to the cart:
 * adding a product, verifying the badge updates, clicking the cart icon, and
 * confirming the correct item appears in the cart list.
 *
 * <p>RELATIONSHIP TO InventorySteps: There is intentional overlap between this
 * class and {@link InventorySteps} — both cover adding items and navigating to
 * the cart. They exist because different feature files (and different test scenarios)
 * were built at different stages of the portfolio. In a production framework you
 * would consolidate them; here they demonstrate that a step can be implemented in
 * multiple ways and that the framework supports both approaches correctly.
 *
 * <p>PAGE OBJECT INITIALISATION: Both {@code ProductsPage} and {@code CartPage} are
 * initialised as class-level fields. They use the active driver from DriverManager's
 * ThreadLocal store, so they are always bound to the correct browser session even
 * when tests run in parallel.
 */
public class CartSteps {

    // We initialize pages inside the methods or a setup block
    // to ensure they use the active driver

    /**
     * Represents the Products/Inventory screen where items are browsed and added to cart.
     * Initialised at field level using the current thread's driver.
     */
    ProductsPage productsPage = new ProductsPage(DriverManager.getDriver());

    /**
     * Represents the Cart screen where added items are reviewed before checkout.
     * Initialised at field level using the current thread's driver.
     */
    CartPage cartPage = new CartPage(DriverManager.getDriver());

    /**
     * WHEN step: Adds the named product to the shopping cart from the products listing.
     *
     * <p>Delegates to {@link ProductsPage#addToCart(String)}, which handles building
     * the dynamic button ID from the product name, clicking it via JavaScript, and
     * waiting for the DOM to confirm the add was processed.
     *
     * @param productName the display name of the product to add (e.g., "Sauce Labs Backpack")
     */
    @When("I add the {string} to the cart")
    public void i_add_item_to_cart(String productName) {
        productsPage.addToCart(productName);
    }

    /**
     * THEN step: Asserts the cart badge shows the expected count as a string.
     *
     * <p>NOTE: This step uses {@code {string}} (not {@code {int}}) for the count.
     * This matches the feature file syntax where the expected value is written in
     * quotes (e.g., {@code "1"}) and allows flexibility if the badge text ever
     * contains non-numeric characters (e.g., "9+" for large counts).
     *
     * @param expectedCount the string value expected on the cart badge (e.g., "1")
     */
    @Then("the cart badge should show {string}")
    public void verify_cart_badge(String expectedCount) {
        Assert.assertEquals(productsPage.getCartBadgeText(), expectedCount);
    }

    /**
     * WHEN step: Clicks the cart icon in the header to navigate to the cart screen.
     *
     * <p>Delegates to {@link ProductsPage#clickCartIcon()}, which uses BasePage's
     * standard click helper (wait for element clickable, then click). After this
     * step, the browser should be on the cart page and subsequent THEN steps can
     * use {@code cartPage} to make assertions.
     */
    @When("I click the cart icon")
    public void i_click_cart_icon() {
        productsPage.clickCartIcon();
    }

    /**
     * THEN step: Asserts the named item appears in the cart item list.
     *
     * <p>Uses {@link CartPage#getFirstItemName()} to read the name of the first
     * (or only) item in the cart and compares it to the expected value. For
     * single-item cart scenarios this is a clean, direct assertion.
     *
     * <p>For multi-item scenarios where order is not guaranteed, consider using
     * {@link CartPage#isItemInCart(String)} instead (available via InventorySteps).
     *
     * @param expectedItem the exact product name expected to appear in the cart
     */
    @Then("I should see {string} in the cart list")
    public void verify_item_in_cart(String expectedItem) {
        Assert.assertEquals(cartPage.getFirstItemName(), expectedItem);
    }
}
