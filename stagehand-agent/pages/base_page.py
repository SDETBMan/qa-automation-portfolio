"""
base_page.py — Parent class for all Page Objects (Playwright sync API).

Centralises wait-then-act patterns so individual pages stay clean.
Every page inherits: page, click(), type_text(), get_text(),
wait_for_visibility(), and get_current_url().
"""

from __future__ import annotations

from playwright.sync_api import Page


class BasePage:
    """Base class providing shared wait/action wrappers for all Page Objects."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def click(self, selector: str) -> None:
        """Wait for element to be visible, then click it."""
        self.page.locator(selector).click()

    def type_text(self, selector: str, text: str) -> None:
        """Clear an input field and type text."""
        locator = self.page.locator(selector)
        locator.fill(text)

    def get_text(self, selector: str) -> str:
        """Wait for element visibility, return its text content."""
        return self.page.locator(selector).inner_text()

    def wait_for_visibility(self, selector: str, timeout: int = 10_000) -> None:
        """Wait until an element is visible on the page."""
        self.page.locator(selector).wait_for(state="visible", timeout=timeout)

    def get_current_url(self) -> str:
        """Return the current page URL."""
        return self.page.url

    def is_element_visible(self, selector: str) -> bool:
        """Return True if the element is visible; False otherwise."""
        return self.page.locator(selector).is_visible()
