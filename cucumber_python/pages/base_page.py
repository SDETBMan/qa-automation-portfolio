"""
base_page.py — Parent class for all Page Objects.

Centralises wait-then-act patterns so individual pages stay clean.
Every page inherits: driver, wait, click(), send_keys(), get_text(),
javascript_click(), and is_element_present().

Replaces: BasePage.java
"""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils import config_reader


class BasePage:
    """Base class providing shared wait/action wrappers for all Page Objects."""

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        timeout = int(config_reader.get("timeouts", "explicit", "10"))
        self.wait = WebDriverWait(driver, timeout)

        try:
            driver.maximize_window()
        except Exception:
            # Headless and remote drivers may not support maximize
            pass

    # ── Core action wrappers ──────────────────────────────────────────────────

    def click(self, locator: tuple) -> None:
        """Wait for element to be clickable, then click it."""
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def send_keys(self, locator: tuple, text: str) -> None:
        """Wait for element visibility, clear it, then type text."""
        element: WebElement = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        """Wait for element visibility, return its text content."""
        return self.wait.until(EC.visibility_of_element_located(locator)).text

    def javascript_click(self, locator: tuple) -> None:
        """Click via JavaScript — bypasses intercepting overlays.

        Useful when a sticky header or cookie banner covers the target element
        and Selenium's native click raises ElementClickInterceptedException.
        """
        element = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].click();", element)

    def is_element_present(self, locator: tuple) -> bool:
        """Return True if element is visible; False if not found or hidden."""
        try:
            return self.wait.until(EC.visibility_of_element_located(locator)).is_displayed()
        except Exception:
            return False

    def wait_for_url_contains(self, fragment: str) -> bool:
        """Wait until the current URL contains the given substring."""
        try:
            return self.wait.until(EC.url_contains(fragment))
        except Exception:
            return False
