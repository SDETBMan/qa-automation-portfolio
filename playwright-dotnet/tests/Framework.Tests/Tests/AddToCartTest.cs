using Allure.NUnit.Attributes;
using Framework.Core.Config;
using Framework.Core.Pages;
using Framework.Tests.Base;

namespace Framework.Tests.Tests;

[TestFixture]
[AllureSuite("AddToCart")]
public class AddToCartTest : BaseTest
{
    private async Task Login()
    {
        var loginPage = new LoginPage(Page);
        await loginPage.LoginAs(
            ConfigReader.GetProperty("app:username"),
            ConfigReader.GetProperty("app:password"));
    }

    [Test]
    [Category("smoke")]
    [Retry(1)]
    [AllureFeature("Cart")]
    [AllureStory("Add Sauce Labs Backpack to cart")]
    public async Task AddBackpack()
    {
        await Login();
        var inventoryPage = new InventoryPage(Page);
        await inventoryPage.AddItemToCart("sauce-labs-backpack");

        Assert.That(await inventoryPage.IsCartBadgeVisible(), Is.True,
            "Cart badge should appear after adding an item.");
        Assert.That(await inventoryPage.GetCartBadgeCount(), Is.EqualTo("1"),
            "Cart badge should show count of 1.");
    }

    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Cart")]
    [AllureStory("Add multiple items to cart")]
    public async Task AddMultiple()
    {
        await Login();
        var inventoryPage = new InventoryPage(Page);
        await inventoryPage.AddItemToCart("sauce-labs-backpack");
        await inventoryPage.AddItemToCart("sauce-labs-bike-light");

        Assert.That(await inventoryPage.GetCartBadgeCount(), Is.EqualTo("2"),
            "Cart badge should show count of 2 after adding two items.");
    }

    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Cart")]
    [AllureStory("Add then remove item clears cart badge")]
    public async Task AddAndRemove()
    {
        await Login();
        var inventoryPage = new InventoryPage(Page);
        await inventoryPage.AddItemToCart("sauce-labs-backpack");
        await inventoryPage.RemoveItemFromCart("sauce-labs-backpack");

        Assert.That(await inventoryPage.IsCartBadgeVisible(), Is.False,
            "Cart badge should disappear after removing the only item.");
    }

    [Test]
    [Category("regression")]
    [Retry(1)]
    [AllureFeature("Cart")]
    [AllureStory("Navigate to checkout from cart page")]
    public async Task NavigateToCheckout()
    {
        await Login();
        var inventoryPage = new InventoryPage(Page);
        await inventoryPage.AddItemToCart("sauce-labs-backpack");
        await inventoryPage.GoToCart();

        var cartPage = new CartPage(Page);
        Assert.That(await cartPage.IsOnCartPage(), Is.True, "Should be on cart page.");

        await cartPage.ClickCheckout();
        Assert.That(Page.Url, Does.Contain("checkout"),
            "Clicking checkout should navigate to checkout page.");
    }
}
