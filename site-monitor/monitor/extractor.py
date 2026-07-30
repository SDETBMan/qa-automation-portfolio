"""extractor.py — Parse HTML + JS to extract DOM selectors."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from bs4 import BeautifulSoup


def extract_from_html(html: str) -> dict[str, set[str]]:
    """Use BeautifulSoup to find all id, class, and data-test attributes."""
    soup = BeautifulSoup(html, "html.parser")

    ids: set[str] = set()
    classes: set[str] = set()
    data_test: set[str] = set()

    for element in soup.find_all(True):
        # IDs
        if element.get("id"):
            ids.add(element["id"])

        # Classes
        if element.get("class"):
            for cls in element["class"]:
                classes.add(cls)

        # data-test attributes
        if element.get("data-test"):
            data_test.add(element["data-test"])

    return {"ids": ids, "classes": classes, "data_test": data_test}


def extract_from_js(js_content: str) -> dict[str, set[str]]:
    """Regex scan JS bundle for selectors.

    SauceDemo uses a Vite-bundled React app with backtick template literals,
    so we scan for patterns like:
      id:`user-name`
      className:`inventory_item`
      "data-test":`error`
      getElementById(`react-burger-menu-btn`)
    """
    ids: set[str] = set()
    classes: set[str] = set()
    data_test: set[str] = set()

    # getElementById with quotes or backticks
    for match in re.finditer(r'getElementById\([`"\']([^`"\']+)[`"\']\)', js_content):
        ids.add(match.group(1))

    # querySelector('#id') with quotes or backticks
    for match in re.finditer(r'querySelector(?:All)?\([`"\']#([^`"\'#\s.]+)[`"\']\)', js_content):
        ids.add(match.group(1))

    # querySelector('.class') with quotes or backticks
    for match in re.finditer(r'querySelector(?:All)?\([`"\']\.([^`"\'#\s.]+)[`"\']\)', js_content):
        classes.add(match.group(1))

    # id:` ` or id:" " or id:' ' (JSX/Vite bundle pattern)
    for match in re.finditer(r'\bid[=:]\s*[`"\']([a-zA-Z][a-zA-Z0-9_-]+)[`"\']', js_content):
        val = match.group(1)
        # Filter out common non-selector values
        if val not in ("root",) and not val.startswith("http"):
            ids.add(val)

    # className with backticks, quotes (React/Vite bundled JSX)
    for match in re.finditer(r'className[=:]\s*[`"\']([^`"\']+)[`"\']', js_content):
        for cls in match.group(1).split():
            # Only include meaningful class names (with _ or -)
            # Exclude template literal fragments (contain ${)
            if ("_" in cls or "-" in cls) and "${" not in cls:
                classes.add(cls)

    # "data-test":` ` or "data-test":" " (JSX attribute pattern in bundled code)
    for match in re.finditer(r'["\']?data-test["\']?\s*[=:]\s*[`"\']([^`"\']+)[`"\']', js_content):
        val = match.group(1)
        # Exclude template literal fragments (dynamic selectors like inventory-item-${s})
        if "${" not in val:
            data_test.add(val)

    # testId:` ` pattern (React testing convention used by SauceDemo)
    for match in re.finditer(r'testId[=:]\s*[`"\']([^`"\']+)[`"\']', js_content):
        # testId maps to data-testid but SauceDemo uses it for data-test
        data_test.add(match.group(1))

    # Backtick string literals matching known ID patterns
    for match in re.finditer(r'[`"\']([a-z][a-z0-9]*(?:-[a-z0-9]+)+)[`"\']', js_content):
        val = match.group(1)
        if not val.startswith("http") and "/" not in val and ":" not in val:
            if any(
                known in val
                for known in [
                    "login-button", "add-to-cart", "remove-sauce",
                    "continue-shopping", "react-burger-menu",
                    "logout-sidebar", "checkout",
                ]
            ):
                ids.add(val)

    # Class names with underscores in backtick strings (inventory_item, cart_item, etc.)
    for match in re.finditer(r'[`"\']([a-z][a-z0-9]*(?:_[a-z0-9]+)+)[`"\']', js_content):
        val = match.group(1)
        if any(
            known in val
            for known in [
                "inventory_", "cart_", "shopping_cart",
                "header_", "footer_",
            ]
        ):
            classes.add(val)

    return {"ids": ids, "classes": classes, "data_test": data_test}


def build_snapshot(
    html_selectors: dict[str, set[str]],
    js_selectors: dict[str, set[str]],
    url: str,
    js_bundle_url: str = "",
) -> dict:
    """Merge and deduplicate into a structured snapshot."""
    merged_ids = sorted(html_selectors["ids"] | js_selectors["ids"])
    merged_classes = sorted(html_selectors["classes"] | js_selectors["classes"])
    merged_data_test = sorted(html_selectors["data_test"] | js_selectors["data_test"])

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": url,
        "ids": merged_ids,
        "classes": merged_classes,
        "data_test": merged_data_test,
        "meta": {"js_bundle_url": js_bundle_url},
    }
