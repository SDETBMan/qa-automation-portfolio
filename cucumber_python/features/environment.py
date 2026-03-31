"""
environment.py — Behave lifecycle hooks (replaces Hooks.java).

Behave automatically discovers this file in the features/ directory.
These hooks fire around every scenario and the entire test suite.

Suite-level metrics are collected here and sent to DataDog at the end of the
full run, mirroring TestListener.onFinish() from the Java framework.
"""

import time
from behave.runner import Context
from behave.model import Scenario, Feature

from utils import driver_manager
from utils.datadog_utils import send_test_metrics
from utils.slack_utils import send_result


# ── Suite-level counters (mirrors TestListener.java) ──────────────────────────

_suite_start: float = 0.0
_passed: int = 0
_failed: int = 0
_skipped: int = 0


def before_all(context: Context) -> None:
    """Called once before the entire test suite begins."""
    global _suite_start
    _suite_start = time.time()
    print("\n[INFO] ========================================")
    print("[INFO] cucumber-python suite starting")
    print("[INFO] ========================================\n")


def before_scenario(context: Context, scenario: Scenario) -> None:
    """Called before each scenario — driver is lazily initialized on first use.

    We do NOT create the driver here; DriverManager initializes it lazily
    when a step first calls driver_manager.get_driver(). This keeps scenarios
    that don't need a browser (e.g., pure API scenarios) from opening one.
    """
    context.driver = None  # Will be set by steps that need a browser


def after_scenario(context: Context, scenario: Scenario) -> None:
    """Called after each scenario — screenshot on failure, then quit driver."""
    global _passed, _failed, _skipped

    # Track outcome for DataDog metrics
    if scenario.status.name == "passed":
        _passed += 1
    elif scenario.status.name == "failed":
        _failed += 1
    else:
        _skipped += 1

    # Screenshot on failure — attached inline to the Allure / Behave report
    driver = driver_manager._local.__dict__.get("driver")
    if scenario.status.name == "failed" and driver is not None:
        try:
            screenshot = driver.get_screenshot_as_png()
            context.embed("image/png", screenshot, name="Failure Screenshot")
        except Exception as exc:
            print(f"[WARN] Could not capture failure screenshot: {exc}")

    # Always quit the driver after each scenario
    driver_manager.quit_driver()


def after_all(context: Context) -> None:
    """Called once after the entire suite finishes.

    Sends metrics to DataDog and a Slack notification on failure, mirroring
    TestListener.onFinish() + SlackUtils in the Java framework.
    """
    duration_ms = int((time.time() - _suite_start) * 1000)

    print(f"\n[INFO] Suite complete — passed={_passed} failed={_failed} skipped={_skipped} "
          f"duration={duration_ms}ms\n")

    # DataDog custom metrics (gracefully skips if DD_API_KEY is absent)
    send_test_metrics(
        passed=_passed,
        failed=_failed,
        skipped=_skipped,
        duration_ms=duration_ms,
        framework="cucumber-python",
    )

    # Slack notification on failure
    if _failed > 0:
        send_result(
            f":red_circle: *cucumber-python* suite finished with {_failed} failure(s). "
            f"Passed: {_passed} | Skipped: {_skipped} | Duration: {duration_ms}ms"
        )
