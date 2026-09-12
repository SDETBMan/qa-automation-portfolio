"""Tests for agent/stagehand_runner.py — act()/extract() calls verified via AsyncMock."""

import pytest

from agent.stagehand_runner import StagehandRunner


@pytest.mark.asyncio
class TestStagehandRunnerLogin:
    @pytest.mark.smoke
    async def test_login_passes_when_logged_in(self, mock_stagehand_client):
        mock_stagehand_client.sessions.extract.return_value = {
            "logged_in": True,
            "current_url": "https://www.saucedemo.com/inventory.html",
            "error_message": None,
        }
        runner = StagehandRunner(mock_stagehand_client)
        result = await runner.run_login()
        assert result.passed is True
        assert result.scenario == "login"
        assert result.approach == "ai-driven"

    async def test_login_fails_when_not_logged_in(self, mock_stagehand_client):
        mock_stagehand_client.sessions.extract.return_value = {
            "logged_in": False,
            "current_url": "https://www.saucedemo.com/",
            "error_message": "Epic sadface: Username and password do not match",
        }
        runner = StagehandRunner(mock_stagehand_client)
        result = await runner.run_login()
        assert result.passed is False

    async def test_login_calls_act_and_extract(self, mock_stagehand_client):
        runner = StagehandRunner(mock_stagehand_client)
        await runner.run_login()
        # act() called for login action
        mock_stagehand_client.sessions.act.assert_called()
        # extract() called to verify login state
        mock_stagehand_client.sessions.extract.assert_called()


@pytest.mark.asyncio
class TestStagehandRunnerInventory:
    async def test_inventory_passes_with_6_products(self, mock_stagehand_client):
        mock_stagehand_client.sessions.extract.return_value = {
            "products": [{"name": f"Product {i}", "price": "$9.99"} for i in range(6)],
            "count": 6,
        }
        runner = StagehandRunner(mock_stagehand_client)
        result = await runner.run_inventory()
        assert result.passed is True
        assert result.scenario == "inventory"

    async def test_inventory_fails_with_wrong_count(self, mock_stagehand_client):
        mock_stagehand_client.sessions.extract.return_value = {
            "products": [],
            "count": 0,
        }
        runner = StagehandRunner(mock_stagehand_client)
        result = await runner.run_inventory()
        assert result.passed is False


@pytest.mark.asyncio
class TestStagehandRunnerCart:
    async def test_cart_passes_with_badge_1(self, mock_stagehand_client):
        # run_cart only calls extract() once — for the cart state
        mock_stagehand_client.sessions.extract.return_value = {
            "items": ["Sauce Labs Backpack"], "item_count": 1, "badge_count": 1,
        }
        runner = StagehandRunner(mock_stagehand_client)
        result = await runner.run_cart()
        assert result.passed is True
        assert result.scenario == "cart"

    async def test_cart_fails_with_badge_0(self, mock_stagehand_client):
        mock_stagehand_client.sessions.extract.return_value = {
            "items": [], "item_count": 0, "badge_count": 0,
        }
        runner = StagehandRunner(mock_stagehand_client)
        result = await runner.run_cart()
        assert result.passed is False


@pytest.mark.asyncio
class TestStagehandRunnerCheckout:
    async def test_checkout_passes_when_completed(self, mock_stagehand_client):
        mock_stagehand_client.sessions.extract.return_value = {
            "completed": True,
            "confirmation_text": "Thank you for your order!",
            "total": "Total: $29.99",
        }
        runner = StagehandRunner(mock_stagehand_client)
        result = await runner.run_checkout()
        assert result.passed is True
        assert result.scenario == "checkout"

    async def test_checkout_fails_when_not_completed(self, mock_stagehand_client):
        mock_stagehand_client.sessions.extract.return_value = {
            "completed": False,
            "confirmation_text": None,
            "total": None,
        }
        runner = StagehandRunner(mock_stagehand_client)
        result = await runner.run_checkout()
        assert result.passed is False


@pytest.mark.asyncio
class TestStagehandRunnerAll:
    async def test_run_all_returns_four_results(self, mock_stagehand_client):
        mock_stagehand_client.sessions.extract.return_value = {
            "logged_in": True,
            "current_url": "...",
            "count": 6,
            "products": [],
            "badge_count": 1,
            "items": ["x"],
            "item_count": 1,
            "completed": True,
            "confirmation_text": "Thank you!",
            "total": "$29.99",
            "error_message": None,
        }
        runner = StagehandRunner(mock_stagehand_client)
        results = await runner.run_all()
        assert len(results) == 4
        assert all(r.approach == "ai-driven" for r in results)

    async def test_duration_is_positive(self, mock_stagehand_client):
        runner = StagehandRunner(mock_stagehand_client)
        result = await runner.run_login()
        assert result.duration_ms > 0

    async def test_handles_exception_gracefully(self, mock_stagehand_client):
        mock_stagehand_client.sessions.act.side_effect = Exception("API timeout")
        runner = StagehandRunner(mock_stagehand_client)
        result = await runner.run_login()
        assert result.passed is False
        assert "API timeout" in result.error
