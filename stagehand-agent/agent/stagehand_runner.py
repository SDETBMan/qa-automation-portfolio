"""
stagehand_runner.py — AI-driven Stagehand runner using natural language actions.

Uses Stagehand's act(), observe(), and extract() APIs to perform the same
4 SauceDemo scenarios. Each scenario uses natural language instructions
instead of explicit selectors. Measures execution time and token usage.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from stagehand import Stagehand

from agent.schemas import (
    CartState,
    CheckoutResult,
    LoginResult,
    ProductList,
    to_json_schema,
)
from comparison.metrics import ScenarioResult


def _load_users() -> dict:
    """Load user credentials from datasets/users.json."""
    path = Path(__file__).resolve().parent.parent / "datasets" / "users.json"
    return json.loads(path.read_text(encoding="utf-8"))


class StagehandRunner:
    """Runs SauceDemo scenarios using AI-driven Stagehand actions."""

    def __init__(self, client: Stagehand, base_url: str = "https://www.saucedemo.com") -> None:
        self.client = client
        self.base_url = base_url
        self.users = _load_users()
        self._session_id: str | None = None
        self._total_tokens: int = 0

    async def _ensure_session(self) -> str:
        """Create a Stagehand session if one doesn't exist."""
        if self._session_id is None:
            session = await self.client.sessions.create()
            self._session_id = session.id
        return self._session_id

    async def _navigate(self, url: str) -> None:
        """Navigate the session to a URL."""
        session_id = await self._ensure_session()
        await self.client.sessions.navigate(session_id, url=url)

    async def _act(self, instruction: str) -> dict:
        """Perform an action via natural language."""
        session_id = await self._ensure_session()
        result = await self.client.sessions.act(session_id, input=instruction)
        if hasattr(result, "usage") and result.usage:
            self._total_tokens += getattr(result.usage, "total_tokens", 0)
        return result

    async def _extract(self, instruction: str, schema: dict) -> dict:
        """Extract structured data from the page."""
        session_id = await self._ensure_session()
        result = await self.client.sessions.extract(
            session_id, instruction=instruction, schema=schema,
        )
        if hasattr(result, "usage") and result.usage:
            self._total_tokens += getattr(result.usage, "total_tokens", 0)
        return result

    async def _login_flow(self) -> None:
        """Common login flow used before each scenario."""
        creds = self.users["standard"]
        await self._navigate(self.base_url)
        await self._act(
            f"Type '{creds['username']}' into the username field "
            f"and '{creds['password']}' into the password field, "
            f"then click the login button"
        )

    async def run_login(self) -> ScenarioResult:
        """Scenario 1: Login and verify redirect to inventory."""
        self._total_tokens = 0
        start = time.perf_counter()
        error = None
        passed = False
        try:
            await self._login_flow()
            result = await self._extract(
                "Check if the user is logged in. Get the current URL "
                "and any error message displayed.",
                to_json_schema(LoginResult),
            )
            data = result if isinstance(result, dict) else result.data
            passed = data.get("logged_in", False)
        except Exception as exc:
            error = str(exc)

        duration_ms = (time.perf_counter() - start) * 1000
        return ScenarioResult(
            scenario="login",
            approach="ai-driven",
            passed=passed,
            duration_ms=round(duration_ms, 2),
            tokens_used=self._total_tokens,
            error=error,
        )

    async def run_inventory(self) -> ScenarioResult:
        """Scenario 2: Browse inventory and extract product list."""
        self._total_tokens = 0
        start = time.perf_counter()
        error = None
        passed = False
        try:
            await self._login_flow()
            result = await self._extract(
                "Extract all products visible on the inventory page, "
                "including their names and prices. Count the total number.",
                to_json_schema(ProductList),
            )
            data = result if isinstance(result, dict) else result.data
            passed = data.get("count", 0) == 6
        except Exception as exc:
            error = str(exc)

        duration_ms = (time.perf_counter() - start) * 1000
        return ScenarioResult(
            scenario="inventory",
            approach="ai-driven",
            passed=passed,
            duration_ms=round(duration_ms, 2),
            tokens_used=self._total_tokens,
            error=error,
        )

    async def run_cart(self) -> ScenarioResult:
        """Scenario 3: Add item to cart and verify badge."""
        self._total_tokens = 0
        start = time.perf_counter()
        error = None
        passed = False
        try:
            await self._login_flow()
            await self._act(
                "Click the 'Add to cart' button for the Sauce Labs Backpack product"
            )
            result = await self._extract(
                "Get the current cart state: list all items in the cart, "
                "the item count, and the badge number on the cart icon.",
                to_json_schema(CartState),
            )
            data = result if isinstance(result, dict) else result.data
            passed = data.get("badge_count", 0) == 1
        except Exception as exc:
            error = str(exc)

        duration_ms = (time.perf_counter() - start) * 1000
        return ScenarioResult(
            scenario="cart",
            approach="ai-driven",
            passed=passed,
            duration_ms=round(duration_ms, 2),
            tokens_used=self._total_tokens,
            error=error,
        )

    async def run_checkout(self) -> ScenarioResult:
        """Scenario 4: Full checkout flow using sequential act() calls."""
        self._total_tokens = 0
        start = time.perf_counter()
        error = None
        passed = False
        try:
            await self._login_flow()
            await self._act(
                "Click the 'Add to cart' button for the Sauce Labs Backpack product"
            )
            await self._act("Click the shopping cart icon in the top right")
            await self._act("Click the 'Checkout' button")
            await self._act(
                "Fill in the checkout form: first name 'Test', "
                "last name 'User', postal code '12345', then click Continue"
            )
            await self._act("Click the 'Finish' button to complete the order")

            result = await self._extract(
                "Check if the order was completed successfully. "
                "Get the confirmation header text and the order total.",
                to_json_schema(CheckoutResult),
            )
            data = result if isinstance(result, dict) else result.data
            passed = data.get("completed", False)
        except Exception as exc:
            error = str(exc)

        duration_ms = (time.perf_counter() - start) * 1000
        return ScenarioResult(
            scenario="checkout",
            approach="ai-driven",
            passed=passed,
            duration_ms=round(duration_ms, 2),
            tokens_used=self._total_tokens,
            error=error,
        )

    async def run_all(self) -> list[ScenarioResult]:
        """Run all four scenarios and return results."""
        return [
            await self.run_login(),
            await self.run_inventory(),
            await self.run_cart(),
            await self.run_checkout(),
        ]
