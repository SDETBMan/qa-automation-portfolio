"""
playwright_runner.py — Deterministic Playwright runner using POM page objects.

Runs the same 4 SauceDemo scenarios (login, inventory, cart, checkout)
using explicit locators via Page Object Model. Measures execution time.
Token count is always 0 since no LLM is involved.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import Page

from comparison.metrics import ScenarioResult
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


def _load_users() -> dict:
    """Load user credentials from datasets/users.json."""
    path = Path(__file__).resolve().parent.parent / "datasets" / "users.json"
    return json.loads(path.read_text(encoding="utf-8"))


class PlaywrightRunner:
    """Runs SauceDemo scenarios using traditional Playwright POM."""

    def __init__(self, page: Page, base_url: str = "https://www.saucedemo.com") -> None:
        self.page = page
        self.base_url = base_url
        self.users = _load_users()

    def _login(self) -> None:
        """Perform login with the standard user."""
        login_page = LoginPage(self.page)
        login_page.navigate(self.base_url)
        creds = self.users["standard"]
        login_page.login_as(creds["username"], creds["password"])

    def run_login(self) -> ScenarioResult:
        """Scenario 1: Login and verify redirect to inventory."""
        start = time.perf_counter()
        error = None
        passed = False
        try:
            login_page = LoginPage(self.page)
            login_page.navigate(self.base_url)
            creds = self.users["standard"]
            login_page.login_as(creds["username"], creds["password"])
            passed = "inventory" in self.page.url
        except Exception as exc:
            error = str(exc)

        duration_ms = (time.perf_counter() - start) * 1000
        return ScenarioResult(
            scenario="login",
            approach="traditional",
            passed=passed,
            duration_ms=round(duration_ms, 2),
            error=error,
        )

    def run_inventory(self) -> ScenarioResult:
        """Scenario 2: Browse inventory and verify product count."""
        start = time.perf_counter()
        error = None
        passed = False
        try:
            self._login()
            inventory = InventoryPage(self.page)
            count = inventory.get_product_count()
            passed = count == 6
        except Exception as exc:
            error = str(exc)

        duration_ms = (time.perf_counter() - start) * 1000
        return ScenarioResult(
            scenario="inventory",
            approach="traditional",
            passed=passed,
            duration_ms=round(duration_ms, 2),
            error=error,
        )

    def run_cart(self) -> ScenarioResult:
        """Scenario 3: Add item to cart and verify badge count."""
        start = time.perf_counter()
        error = None
        passed = False
        try:
            self._login()
            inventory = InventoryPage(self.page)
            inventory.add_item_to_cart("sauce-labs-backpack")
            passed = inventory.get_cart_badge_count() == 1
        except Exception as exc:
            error = str(exc)

        duration_ms = (time.perf_counter() - start) * 1000
        return ScenarioResult(
            scenario="cart",
            approach="traditional",
            passed=passed,
            duration_ms=round(duration_ms, 2),
            error=error,
        )

    def run_checkout(self) -> ScenarioResult:
        """Scenario 4: Full checkout flow through three page objects."""
        start = time.perf_counter()
        error = None
        passed = False
        try:
            self._login()
            inventory = InventoryPage(self.page)
            inventory.add_item_to_cart("sauce-labs-backpack")
            inventory.go_to_cart()

            cart = CartPage(self.page)
            cart.proceed_to_checkout()

            checkout = CheckoutPage(self.page)
            checkout.fill_info("Test", "User", "12345")
            checkout.continue_to_overview()
            checkout.finish_checkout()

            header = checkout.get_confirmation_header()
            passed = "thank you" in header.lower()
        except Exception as exc:
            error = str(exc)

        duration_ms = (time.perf_counter() - start) * 1000
        return ScenarioResult(
            scenario="checkout",
            approach="traditional",
            passed=passed,
            duration_ms=round(duration_ms, 2),
            error=error,
        )

    def run_all(self) -> list[ScenarioResult]:
        """Run all four scenarios and return results."""
        return [
            self.run_login(),
            self.run_inventory(),
            self.run_cart(),
            self.run_checkout(),
        ]
