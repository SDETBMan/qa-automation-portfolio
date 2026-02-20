using Framework.Core.Pages;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

/// <summary>
/// Demonstrates the C# fixture pattern via AuthenticatedTest inheritance.
/// Every test in this class begins already logged in on inventory.html —
/// zero login boilerplate in any test method.
///
/// TypeScript equivalent: tests using the authenticatedPage fixture from fixtures.ts.
/// </summary>
[Parallelizable(ParallelScope.Self)]
public class CartFixtureTest : AuthenticatedTest
{
    [Test]
    [Category("smoke")]
    [Category("fixture")]
    public async Task AddBackpackToCart_BadgeShouldShowOne()
    {
        await InventoryPage.AddItemToCart("sauce-labs-backpack");

        Assert.That(await InventoryPage.GetCartBadgeCount(), Is.EqualTo("1"),
            "Cart badge should show 1 after adding one item.");
    }

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

    [Test]
    [Category("regression")]
    [Category("fixture")]
    public async Task AddThenRemoveItem_CartBadgeShouldDisappear()
    {
        await InventoryPage.AddItemToCart("sauce-labs-backpack");
        Assert.That(await InventoryPage.IsCartBadgeVisible(), Is.True,
            "Cart badge should appear after adding an item.");

        await InventoryPage.RemoveItemFromCart("sauce-labs-backpack");
        Assert.That(await InventoryPage.IsCartBadgeVisible(), Is.False,
            "Cart badge should disappear after removing the only item.");
    }

    [Test]
    [Category("regression")]
    [Category("fixture")]
    public async Task NavigateToCheckout_CartPageShouldContainItem()
    {
        await InventoryPage.AddItemToCart("sauce-labs-backpack");
        await InventoryPage.GoToCart();

        var cartPage = new CartPage(Page);
        Assert.That(await cartPage.GetCartItemCount(), Is.EqualTo(1),
            "Cart page should contain one item after adding one product.");
    }
}
