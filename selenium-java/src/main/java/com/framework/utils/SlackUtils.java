package com.framework.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;

import java.util.Map;

/**
 * SlackUtils: Sends real-time test execution result notifications to a Slack channel.
 *
 * WHY THIS CLASS EXISTS:
 * When tests run in a CI/CD pipeline overnight or on a schedule, the team needs to know
 * immediately when results are available — without manually checking Jenkins or GitHub Actions.
 * Slack notifications bring the results directly to where the team is already working.
 *
 * This class is called by TestListener at the end of every test suite run (the onFinish event).
 * The message it sends contains the pass/fail/skip counts for immediate visibility.
 *
 * WHY SLACK WEBHOOK (NOT SLACK SDK):
 * Slack Incoming Webhooks are the simplest integration method. A Webhook URL is a special
 * HTTP endpoint Slack provides — sending a POST request to that URL with a JSON payload
 * posts a message to the configured Slack channel. No Slack SDK, OAuth tokens, or app
 * installation is required. This keeps the dependency footprint minimal.
 *
 * SECURITY DESIGN:
 * The Webhook URL is treated like a secret (it can be used to post to your Slack workspace).
 * It is stored in an environment variable (SLACK_WEBHOOK_URL), not in config.properties or
 * source code. In GitHub Actions, it would be stored as a Repository Secret.
 *
 * For recruiters: CI/CD notification integration is expected in mature QA pipelines. This
 * shows awareness of the full testing lifecycle, from test execution to stakeholder reporting.
 */
public class SlackUtils {

    /**
     * Sends a formatted message to the Slack channel configured via the Webhook URL.
     *
     * WHY FAIL-SAFE DESIGN (skip if no webhook, don't crash):
     * Not every environment where tests run will have Slack notifications configured.
     * A developer running tests locally doesn't need (or want) Slack pings. If the Webhook
     * URL is missing, we log a warning and skip silently. This prevents local test runs from
     * failing because of a missing Slack configuration that is only relevant in CI/CD.
     *
     * WHY JACKSON FOR JSON SERIALIZATION (not String concatenation):
     * The Slack API expects a JSON payload: {"text": "your message"}. Building this with
     * String concatenation is fragile — if the message contains quotes, backslashes, or
     * newline characters, the resulting JSON would be malformed and Slack would reject it.
     * Jackson's ObjectMapper.writeValueAsString() properly escapes all special characters,
     * guaranteeing valid JSON regardless of the message content.
     *
     * WHY REST ASSURED FOR THE HTTP CALL:
     * Rest Assured is already a dependency in this project (used for API testing). Reusing it
     * here avoids adding a separate HTTP client dependency just for Slack notifications.
     * The .then().statusCode(200) assertion validates that Slack accepted the message —
     * if it didn't, an assertion error is thrown and logged rather than silently ignored.
     *
     * @param message The text content to post to Slack (multi-line messages are supported)
     */
    public static void sendResult(String message) {
        // Retrieve webhook from Environment Variable (passed via GitHub Actions or Local OS)
        String webhookUrl = System.getenv("SLACK_WEBHOOK_URL");

        // If no webhook is found, log a warning and skip (prevents local crashes)
        if (webhookUrl == null || webhookUrl.isEmpty()) {
            System.out.println("[WARN] SLACK_WEBHOOK_URL not found. Skipping notification.");
            return;
        }

        try {
            // Use Jackson to safely serialize the payload — avoids broken JSON if message contains quotes or newlines
            String jsonPayload = new ObjectMapper().writeValueAsString(Map.of("text", message));

            RestAssured.given()
                    .contentType(ContentType.JSON)
                    .body(jsonPayload)
                    .post(webhookUrl)
                    .then()
                    .statusCode(200); // Slack returns 200 with body "ok" on success

            System.out.println("[INFO] Slack notification sent successfully.");
        } catch (Exception e) {
            System.err.println("[ERROR] Slack Notification failed: " + e.getMessage());
        }
    }
}
