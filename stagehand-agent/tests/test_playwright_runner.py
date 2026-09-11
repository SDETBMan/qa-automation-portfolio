"""Tests for traditional/playwright_runner.py — POM calls verified via mocked Page."""

import pytest

from traditional.playwright_runner import PlaywrightRunner


class TestPlaywrightRunnerLogin:
    @pytest.mark.smoke
    def test_login_passes_on_inventory_url(self, mock_playwright_page):
        mock_playwright_page.url = "https://www.saucedemo.com/inventory.html"
        runner = PlaywrightRunner(mock_playwright_page)
        result = runner.run_login()
        assert result.passed is True
        assert result.scenario == "login"
        assert result.approach == "traditional"
        assert result.tokens_used == 0

    def test_login_fails_on_wrong_url(self, mock_playwright_page):
        mock_playwright_page.url = "https://www.saucedemo.com/"
        runner = PlaywrightRunner(mock_playwright_page)
        result = runner.run_login()
        assert result.passed is False

    def test_login_calls_fill_and_click(self, mock_playwright_page):
        mock_playwright_page.url = "https://www.saucedemo.com/inventory.html"
        runner = PlaywrightRunner(mock_playwright_page)
        runner.run_login()
        # Verify page.goto was called
        mock_playwright_page.goto.assert_called()
        # Verify locator was called for username, password, and login button
        assert mock_playwright_page.locator.call_count >= 3


class TestPlaywrightRunnerInventory:
    def test_inventory_passes_with_6_products(self, mock_playwright_page):
        mock_playwright_page.url = "https://www.saucedemo.com/inventory.html"
        locator = mock_playwright_page.locator.return_value
        locator.count.return_value = 6
        runner = PlaywrightRunner(mock_playwright_page)
        result = runner.run_inventory()
        assert result.passed is True
        assert result.scenario == "inventory"

    def test_inventory_fails_with_wrong_count(self, mock_playwright_page):
        mock_playwright_page.url = "https://www.saucedemo.com/inventory.html"
        locator = mock_playwright_page.locator.return_value
        locator.count.return_value = 3
        runner = PlaywrightRunner(mock_playwright_page)
        result = runner.run_inventory()
        assert result.passed is False


class TestPlaywrightRunnerCart:
    def test_cart_passes_with_badge_1(self, mock_playwright_page):
        mock_playwright_page.url = "https://www.saucedemo.com/inventory.html"
        locator = mock_playwright_page.locator.return_value
        locator.is_visible.return_value = True
        locator.inner_text.return_value = "1"
        runner = PlaywrightRunner(mock_playwright_page)
        result = runner.run_cart()
        assert result.passed is True
        assert result.scenario == "cart"


class TestPlaywrightRunnerCheckout:
    def test_checkout_passes_with_thank_you(self, mock_playwright_page):
        mock_playwright_page.url = "https://www.saucedemo.com/inventory.html"
        locator = mock_playwright_page.locator.return_value
        locator.is_visible.return_value = True
        locator.inner_text.return_value = "Thank you for your order!"
        runner = PlaywrightRunner(mock_playwright_page)
        result = runner.run_checkout()
        assert result.passed is True
        assert result.scenario == "checkout"

    def test_checkout_handles_exception(self, mock_playwright_page):
        mock_playwright_page.url = "https://www.saucedemo.com/inventory.html"
        mock_playwright_page.goto.side_effect = Exception("Connection refused")
        runner = PlaywrightRunner(mock_playwright_page)
        result = runner.run_checkout()
        assert result.passed is False
        assert "Connection refused" in result.error


class TestPlaywrightRunnerAll:
    def test_run_all_returns_four_results(self, mock_playwright_page):
        mock_playwright_page.url = "https://www.saucedemo.com/inventory.html"
        locator = mock_playwright_page.locator.return_value
        locator.is_visible.return_value = True
        locator.inner_text.return_value = "Thank you for your order!"
        locator.count.return_value = 6
        runner = PlaywrightRunner(mock_playwright_page)
        results = runner.run_all()
        assert len(results) == 4
        assert all(r.approach == "traditional" for r in results)

    def test_duration_is_positive(self, mock_playwright_page):
        mock_playwright_page.url = "https://www.saucedemo.com/inventory.html"
        runner = PlaywrightRunner(mock_playwright_page)
        result = runner.run_login()
        assert result.duration_ms > 0
