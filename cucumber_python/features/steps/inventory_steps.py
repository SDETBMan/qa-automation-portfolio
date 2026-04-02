"""
inventory_steps.py — Step definitions for inventory and cart badge scenarios.

Domain: Product catalogue, add/remove, cart badge, checkout navigation.

Replaces: InventorySteps.java + CartSteps.java (inventory-side actions)
"""

from behave import when, then
from behave.runner import Context

from utils import driver_manager
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage


def _inventory(context: Context) -> InventoryPage:
    return InventoryPage(driver_manager.get_driver())


def _cart(context: Context) -> CartPage:
    return CartPage(driver_manager.get_driver())


# ── When steps ────────────────────────────────────────────────────────────────

@when('I add "{product}" to the cart')
def step_add_product(context: Context, product: str) -> None:
    _inventory(context).add_product(product)


@when("I add the following items to the cart")
def step_add_multiple_products(context: Context) -> None:
    """Accepts a Behave table — one product name per row.

    Feature file usage:
        When I add the following items to the cart:
          | Sauce Labs Backpack   |
          | Sauce Labs Bike Light |

    Reuses a single InventoryPage across all adds and waits for the badge to
    reflect each add before proceeding.  This prevents a race condition in
    headless Chrome where rapid successive clicks on different buttons do not
    all register when the React DOM is still mutating from the previous click.
    """
    page = _inventory(context)
    for i, row in enumerate(context.table, start=1):
        page.add_product(row["product"])
        page.wait_for_badge_count(i)


@when('I remove "{product}" from the cart')
def step_remove_product(context: Context, product: str) -> None:
    _inventory(context).remove_product(product)


@when("I go to the shopping cart")
def step_go_to_cart(context: Context) -> None:
    _inventory(context).go_to_cart()


@when("I proceed to checkout")
def step_proceed_checkout(context: Context) -> None:
    _cart(context).click_checkout()


# ── Then steps ────────────────────────────────────────────────────────────────

@then("the cart badge should show {count:d}")
def step_assert_badge_count(context: Context, count: int) -> None:
    """Strategy #3 — {count:d} parses any integer, one step for all badge values."""
    page = _inventory(context)
    page.wait_for_badge_count(count)
    actual = page.get_cart_badge_count()
    assert actual == count, f"Expected cart badge {count}, got {actual}"


@then("the cart should be empty")
def step_assert_cart_empty(context: Context) -> None:
    assert _inventory(context).is_cart_empty(), (
        "Expected empty cart but badge is still visible"
    )


@then('"{product}" should be in the cart')
def step_assert_item_in_cart(context: Context, product: str) -> None:
    assert _cart(context).is_item_in_cart(product), (
        f"'{product}' not found in cart"
    )


@then("I should be on the checkout page")
def step_assert_checkout_page(context: Context) -> None:
    assert _cart(context).is_on_checkout_page(), (
        "Expected to be on checkout page but URL does not contain 'checkout'"
    )
