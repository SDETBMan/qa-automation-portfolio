using Framework.Core.Pages;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

/// <summary>
/// Demonstrates the C# fixture pattern via AuthenticatedTest inheritance.
///
/// Why this class exists alongside AddToCartTest.cs:
/// Both files test similar cart scenarios, but they use different setup approaches
/// to demonstrate two valid patterns side-by-side in the portfolio:
///
///   AddToCartTest.cs    — EXPLICIT setup: each test calls "await Login()" as
///                         its first line. Setup is visible in the test body.
///
///   CartFixtureTest.cs  — FIXTURE setup: AuthenticatedTest base class handles
///                         login automatically. Every test in this class starts
///                         already logged in with zero login boilerplate.
///
/// TypeScript equivalent: In Playwright TypeScript this exact pattern is implemented
/// with test.extend() in fixtures.ts (the "authenticatedPage" fixture). C# achieves
/// the same effect using class inheritance and NUnit's [SetUp] chain. The lifecycle
/// is identical:
///   TypeScript: async ({ page }, use) => { /* setup */ await use(pageObjects); /* teardown */ }
///   C# NUnit:   [SetUp] LoginBeforeEach() runs before each test automatically.
///
/// InventoryPage is available as an inherited property from AuthenticatedTest —
/// test methods use it directly without instantiating it.
///
/// [Parallelizable(ParallelScope.Self)]: re-declared here to be explicit, though
/// this is already inherited from BaseTest. Different test classes can run in
/// parallel with each other; tests within this class run sequentially.
/// </summary>
[Parallelizable(ParallelScope.Self)]
public class CartFixtureTest : AuthenticatedTest
{
    /// <summary>
    /// Smoke test: verifies that a single item add produces a cart badge count of "1".
    ///
    /// Note: there is no "await Login()" here — AuthenticatedTest.LoginBeforeEach()
    /// has already run and the browser is on inventory.html before this line executes.
    /// InventoryPage is also pre-instantiated by the fixture base class.
    /// [Category("fixture")]: labels this as a fixture-pattern test for filtering purposes.
    /// </summary>
    [Test]
    [Category("smoke")]
    [Category("fixture")]
    public async Task AddBackpackToCart_BadgeShouldShowOne()
    {
        // InventoryPage is injected by AuthenticatedTest — no "new InventoryPage(Page)" needed.
        await InventoryPage.AddItemToCart("sauce-labs-backpack");

        Assert.That(await InventoryPage.GetCartBadgeCount(), Is.EqualTo("1"),
            "Cart badge should show 1 after adding one item.");
    }

    /// <summary>
    /// Regression test: verifies that adding two items results in a badge count of "2".
    ///
    /// Demonstrates that the fixture resets state between tests — each test gets a
    /// fresh browser session from PageTest, so no items from the previous test carry
    /// over. The AuthenticatedTest [SetUp] runs fresh for each test, including login.
    /// </summary>
    [Test]
    [Category("regression")]
    [Category("fixture")]
    public async Task AddMultipleItems_BadgeShouldReflectCount()
    {
        await InventoryPage.AddItemToCart("sauce-labs-backpack");
        await InventoryPage.AddItemToCart("sauce-labs-bike-light");

        Assert.That(await InventoryPage.GetCartBadgeCount(), Is.EqualTo("2"),
            "Cart badge should show 2 after adding two items.");
    }

    /// <summary>
    /// Regression test: verifies the add-then-remove flow hides the cart badge.
    ///
    /// Uses two assertions to verify both states (after add AND after remove),
    /// making the test more diagnostic — if only the second assertion fails, the
    /// badge was never shown in the first place; if both fail, something else is wrong.
    /// </summary>
    [Test]
    [Category("regression")]
    [Category("fixture")]
    public async Task AddThenRemoveItem_CartBadgeShouldDisappear()
    {
        // Add the backpack — badge should appear.
        await InventoryPage.AddItemToCart("sauce-labs-backpack");
        Assert.That(await InventoryPage.IsCartBadgeVisible(), Is.True,
            "Cart badge should appear after adding an item.");

        // Remove the backpack — badge should disappear.
        await InventoryPage.RemoveItemFromCart("sauce-labs-backpack");
        Assert.That(await InventoryPage.IsCartBadgeVisible(), Is.False,
            "Cart badge should disappear after removing the only item.");
    }

    /// <summary>
    /// Regression test: verifies that after adding an item and navigating to the cart,
    /// the cart page shows the correct item count.
    ///
    /// CartPage is instantiated here (not in the fixture) because CartPage is only
    /// needed in this one test. Page objects are cheap to create — there is no
    /// performance benefit to pre-instantiating ones used by only a single test.
    /// </summary>
    [Test]
    [Category("regression")]
    [Category("fixture")]
    public async Task NavigateToCheckout_CartPageShouldContainItem()
    {
        // Add an item and navigate to the cart page via the cart icon.
        await InventoryPage.AddItemToCart("sauce-labs-backpack");
        await InventoryPage.GoToCart();

        // Create a CartPage object for the cart page interactions.
        var cartPage = new CartPage(Page);

        // Verify the item appears in the cart — count should be exactly 1.
        Assert.That(await cartPage.GetCartItemCount(), Is.EqualTo(1),
            "Cart page should contain one item after adding one product.");
    }
}
