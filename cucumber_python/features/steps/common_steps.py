"""
common_steps.py — Global reusable steps that do not belong to a single domain.

These steps are shared across multiple feature files.
Keeping them here prevents duplication without forcing them into a domain-specific file.

Examples: page navigation, URL assertions, generic waits.
"""

from behave import then
from behave.runner import Context

from utils import driver_manager


@then('the page title should not be "{unexpected}"')
def step_assert_title_not(context: Context, unexpected: str) -> None:
    actual = driver_manager.get_driver().title
    assert actual != unexpected, (
        f"Page title should not be '{unexpected}' but it is — possible XSS execution"
    )


@then('the current URL should contain "{fragment}"')
def step_assert_url_contains(context: Context, fragment: str) -> None:
    url = driver_manager.get_driver().current_url
    assert fragment in url, f"Expected URL to contain '{fragment}', got: {url}"
