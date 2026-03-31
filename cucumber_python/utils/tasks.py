"""
tasks.py — Screenplay Pattern: reusable Tasks that encapsulate multi-step flows.

WHAT IS THE SCREENPLAY PATTERN:
  Instead of Page Objects with 50 methods (the "God Object" problem), the
  Screenplay Pattern decomposes automation into three concepts:

    Actor       — the entity performing the test (a user, a service, a device)
    Task        — a high-level business action ("Login", "AddToCart", "Checkout")
    Interaction — a single UI/API operation that a Task orchestrates

  A Task wraps a workflow that would otherwise be duplicated across step
  definition files. When a precondition step says "Given I am logged in", it
  calls LoginTask.perform() — not a copy-pasted 3-step sequence.

WHY THIS AVOIDS GOD OBJECTS:
  LoginPage doesn't grow to hold 50 methods. Each Task is a focused unit of
  work that the Actor delegates to. New actors (admin, guest) reuse the same
  Tasks without changing Page Objects.

Tasks defined here:
  LoginTask       — Navigate + enter credentials + assert Products page
  AddToCartTask   — Add one or more products and optionally assert badge count
"""

from selenium.webdriver.remote.webdriver import WebDriver

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.inventory_page import InventoryPage
from utils import config_reader


class LoginTask:
    """Task: Perform the complete login flow for a given Actor.

    Usage:
        LoginTask(driver).perform("standard_user", "secret_sauce")

    The Task encapsulates:
      1. Navigate to login URL (if not already there)
      2. Enter username + password
      3. Click login
      4. Assert the Products page loaded

    Step definitions that need a logged-in precondition call this rather than
    duplicating the 3-step sequence, keeping step files lean.
    """

    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver
        self._login_page = LoginPage(driver)
        self._dashboard = DashboardPage(driver)

    def perform(self, username: str, password: str) -> None:
        """Execute the login workflow and assert success.

        Raises AssertionError if the Products page does not load after login.
        """
        self._login_page.login(username, password)
        # Verify landing — fail fast with a clear message rather than a
        # cryptic NoSuchElementException inside the next step
        assert self._dashboard.is_products_page_displayed(), (
            f"LoginTask failed for '{username}' — Products page not displayed after login. "
            "Check credentials or locked-out state."
        )


class AddToCartTask:
    """Task: Add one or more products to the cart and assert the badge count.

    Usage:
        AddToCartTask(driver).perform(["Sauce Labs Backpack", "Sauce Labs Bike Light"])

    Consolidates the add-loop pattern that would otherwise repeat across
    multiple inventory step definitions.
    """

    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver
        self._inventory = InventoryPage(driver)

    def perform(self, products: list[str], assert_badge: bool = False) -> None:
        """Add each product and optionally assert the badge count equals len(products).

        Args:
            products:     List of product names to add.
            assert_badge: If True, assert badge shows len(products) after all adds.
        """
        for product in products:
            self._inventory.add_product(product)

        if assert_badge:
            expected = len(products)
            actual = self._inventory.get_cart_badge_count()
            assert actual == expected, (
                f"AddToCartTask: expected badge={expected}, got {actual}"
            )
