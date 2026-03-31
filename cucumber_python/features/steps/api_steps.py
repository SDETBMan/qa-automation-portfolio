"""
api_steps.py — Step definitions for REST API scenarios.

Domain: HTTP requests, response validation, data integrity.

No WebDriver needed — these steps use requests directly, running in-process
and significantly faster than UI tests.

Replaces: ApiSteps.java
"""

import requests
from behave import given, when, then, step
from behave.runner import Context

from utils import config_reader


# ── Given steps ───────────────────────────────────────────────────────────────

@given("the API base URL is configured")
def step_api_base_url(context: Context) -> None:
    context.api_base_url = config_reader.get(
        "api", "base_url", "https://jsonplaceholder.typicode.com"
    )
    print(f"[API] Base URL: {context.api_base_url}")


# ── When steps ────────────────────────────────────────────────────────────────

@when('I send a GET request to "{path}"')
def step_get_request(context: Context, path: str) -> None:
    endpoint = f"{context.api_base_url}{path}"
    print(f"[API] GET {endpoint}")
    context.response = requests.get(endpoint, timeout=10)
    print(f"[API] Status: {context.response.status_code}")


# ── Then / And steps ──────────────────────────────────────────────────────────

@then("the response status code should be {expected_status:d}")
def step_assert_status(context: Context, expected_status: int) -> None:
    actual = context.response.status_code
    assert actual == expected_status, (
        f"Expected status {expected_status}, got {actual}. "
        f"Body: {context.response.text[:200]}"
    )


@then('the response body should contain "{expected}"')
def step_assert_body_contains(context: Context, expected: str) -> None:
    assert expected in context.response.text, (
        f"Response body missing expected value: '{expected}'"
    )
