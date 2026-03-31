"""
slack_utils.py — Send suite result notifications to a Slack webhook.

Fail-safe: if SLACK_WEBHOOK_URL is absent, logs a warning and returns.
Mirrors SlackUtils.java.
"""

import os
import requests


def send_result(message: str) -> None:
    """Post a message to the configured Slack webhook.

    Args:
        message: The text to post (supports Slack mrkdwn formatting).
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
    if not webhook_url:
        print("[WARN] SLACK_WEBHOOK_URL not set. Skipping Slack notification.")
        return

    try:
        response = requests.post(
            webhook_url,
            json={"text": message},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if response.status_code == 200:
            print("[INFO] Slack notification sent.")
        else:
            print(f"[WARN] Slack notification returned status: {response.status_code}")
    except Exception as exc:
        print(f"[ERROR] Slack notification failed: {exc}")
