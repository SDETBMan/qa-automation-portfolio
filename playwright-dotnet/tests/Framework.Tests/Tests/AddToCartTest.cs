using Allure.NUnit.Attributes;
using Framework.Core.Config;
using Framework.Core.Pages;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

/// <summary>
/// Test class covering the add-to-cart and cart navigation workflows on SauceDemo.
///
/// These tests represent the core e-commerce user journey: browsing the product
/// inventory and adding items to the cart before checkout. They are a mix of
/// smoke tests (does the basic flow work?) and regression tests (edge cases like
/// adding multiple items, then removing one).
///
/// Why not extend AuthenticatedTest: This class defines its own private Login() helper
/// rather than using the fixture base class. This demonstrates an alternative approach —
/// explicit login setup within the test class — which some teams prefer for its clarity.
/// CartFixtureTest.cs shows the same scenarios using the AuthenticatedTest fixture pattern.
///
/// Extends BaseTest (not AuthenticatedTest) so each test calls Login() explicitly.
/// [AllureSuite("AddToCart")]: groups these tests in the Allure report.
/// </summary>
[TestFixture]
[AllureSuite("AddToCart")]
public class AddToCartTest : BaseTest
{
    /// <summary>
    /// Private helper method to perform a standard login before tests that require it.
    ///
    /// Why private and not in a [SetUp]: Using a private async method called from each
    /// test gives explicit control — each test method shows "await Login()" as the first
    /// step, making it obvious that login is a prerequisite. A [SetUp] method would be
    /// invisible inside the test body, which can confuse readers unfamiliar with the
    /// inheritance chain.
    ///
    /// This is the explicit-setup style; compare with AuthenticatedTest which uses the
    /// fixture/inheritance style. Both are valid — this portfolio demonstrates both patterns.
    /// </summary>
    private async Task Login()
    {
        var loginPage = new LoginPage(Page);
        await loginPage.LoginAs(
            ConfigReader.GetProperty("app:username"),
            ConfigReader.GetProperty("app:password"));
    }

    /// <summary>
    /// Smoke test: verifies that adding one item to the cart causes the cart badge
    /// to appear and display the correct count of "1".
    ///
    /// This is the most fundamental cart interaction — if a user cannot add an item
    /// to the cart, the entire e-commerce flow is broken.
    ///
    /// Product slug "sauce-labs-backpack" matches the product's button ID in the HTML.
    /// Using a named slug makes the test readable without inspecting the HTML.
    /// </summary>
    [Test]
    [Category("smoke")]
    [Retry(1)]
    [AllureFeature("Cart")]
    [AllureStory("Add Sauce Labs Backpack to cart")]
    public async Task AddBackpack()
    {
        await Login();
        var inventoryPage = new InventoryPage(Page);

        // Click "Add to cart" for the Sauce Labs Backpack.
        await inventoryPage.AddItemToCart("sauce-labs-backpack");

        // Assert 1: the cart badge should now be visible in the header.
        Assert.That(await inventoryPage.IsCartBadgeVisible(), Is.True,
            "Cart badge should appear after adding an item.");

        // Assert 2: the badge count should be "1" (one item in the cart).
        Assert.That(await inventoryPage.GetCartBadgeCount(), Is.EqualTo("1"),
            "Cart badge should show count of 1.");
    }

    /// <summary>
    /// Regression test: verifies that adding two separate items results in a cart
    /// badge showing count "2".
    ///
    /// Why test multiple items: each "Add to cart" click is an independent operation.
    /// A bug could cause the second add to reset the count rather than increment it,
    /// or the badge could fail to update asynchronously. This test catches both.
    /// </summary>
    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Cart")]
    [AllureStory("Add multiple items to cart")]
    public async Task AddMultiple()
    {
        await Login();
        var inventoryPage = new InventoryPage(Page);

        // Add two different products.
        await inventoryPage.AddItemToCart("sauce-labs-backpack");
        await inventoryPage.AddItemToCart("sauce-labs-bike-light");

        // The badge must show "2" — both additions should have been counted.
        Assert.That(await inventoryPage.GetCartBadgeCount(), Is.EqualTo("2"),
            "Cart badge should show count of 2 after adding two items.");
    }

    /// <summary>
    /// Regression test: verifies that removing the only item in the cart causes
    /// the cart badge to disappear entirely.
    ///
    /// Why test remove: adding and removing is a common user action (changing one's
    /// mind while shopping). The badge should disappear (not show "0") when the cart
    /// is empty — showing "0" would be a UI bug.
    ///
    /// IsCartBadgeVisible returning false (not just checking count) ensures the
    /// badge element is completely hidden, not just showing an empty value.
    /// </summary>
    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Cart")]
    [AllureStory("Add then remove item clears cart badge")]
    public async Task AddAndRemove()
    {
        await Login();
        var inventoryPage = new InventoryPage(Page);

        // Add the backpack, then immediately remove it.
        await inventoryPage.AddItemToCart("sauce-labs-backpack");
        await inventoryPage.RemoveItemFromCart("sauce-labs-backpack");

        // The badge must be invisible when the cart is empty.
        Assert.That(await inventoryPage.IsCartBadgeVisible(), Is.False,
            "Cart badge should disappear after removing the only item.");
    }

    /// <summary>
    /// Regression test: verifies the full flow from inventory → cart → checkout entry.
    ///
    /// This is an end-to-end path through multiple pages. It exercises:
    ///   1. Adding an item (inventory page interaction)
    ///   2. Navigating to the cart (page transition via cart icon)
    ///   3. Confirming the cart page loaded (URL check)
    ///   4. Clicking Checkout (another page transition)
    ///   5. Confirming the checkout page loaded (URL check)
    ///
    /// Two page objects (InventoryPage and CartPage) are used sequentially, showing
    /// how POM objects hand off control to each other as the user navigates.
    /// </summary>
    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Cart")]
    [AllureStory("Navigate to checkout from cart page")]
    public async Task NavigateToCheckout()
    {
        await Login();
        var inventoryPage = new InventoryPage(Page);

        // Add an item and navigate to the cart page.
        await inventoryPage.AddItemToCart("sauce-labs-backpack");
        await inventoryPage.GoToCart();

        // Confirm we landed on the cart page.
        var cartPage = new CartPage(Page);
        Assert.That(await cartPage.IsOnCartPage(), Is.True, "Should be on cart page.");

        // Click the Checkout button to start the purchase flow.
        await cartPage.ClickCheckout();

        // Confirm the checkout page loaded by checking the URL.
        Assert.That(Page.Url, Does.Contain("checkout"),
            "Clicking checkout should navigate to checkout page.");
    }
}
