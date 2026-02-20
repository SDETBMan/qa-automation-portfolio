package com.framework.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;

import java.util.Map;

/**
 * SlackUtils: Dispatches real-time test execution alerts to Slack.
 * Leverages Rest Assured to handle the API interaction efficiently.
 */
public class SlackUtils {

    /**
     * Sends a JSON payload to the configured Slack Webhook.
     * The Webhook URL should be stored in an Environment Variable for security.
     */
    public static void sendResult(String message) {
        // Retrieve webhook from Environment Variable (passed via GitHub Actions or Local OS)
        String webhookUrl = System.getenv("SLACK_WEBHOOK_URL");

        // If no webhook is found, I log a warning and skip (prevents local crashes)
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
                    .statusCode(200);

            System.out.println("[INFO] Slack notification sent successfully.");
        } catch (Exception e) {
            System.err.println("[ERROR] Slack Notification failed: " + e.getMessage());
        }
    }
}
