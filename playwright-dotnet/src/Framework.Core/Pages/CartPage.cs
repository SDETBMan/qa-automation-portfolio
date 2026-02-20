using Microsoft.Playwright;

namespace Framework.Core.Pages;

public class CartPage : BasePage
{
    private const string CartItems      = ".cart_item";
    private const string CheckoutButton = "#checkout";
    private const string ContinueShopping = "#continue-shopping";
    private const string ItemNameXPath  = "//div[@class='cart_item']//div[@class='inventory_item_name']";

    public CartPage(IPage page) : base(page) { }

    public async Task<int> GetCartItemCount() =>
        await Page.Locator(CartItems).CountAsync();

    public async Task ClickCheckout() =>
        await ClickAsync(CheckoutButton, "checkout button");

    public async Task ContinueShopping_() =>
        await ClickAsync(ContinueShopping, "continue shopping");

    public async Task<string> GetFirstItemName() =>
        await GetTextAsync(ItemNameXPath);

    public async Task<bool> IsOnCartPage() =>
        await WaitForUrlAsync("cart");
}
