package com.saucedemo.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;

import java.util.Map;

/**
 * SlackUtils: Dispatches real-time test execution summaries to a Slack channel.
 * Webhook URL is read from the SLACK_WEBHOOK_URL environment variable / secret.
 */
public class SlackUtils {

    public static void sendResult(String message) {
        String webhookUrl = System.getenv("SLACK_WEBHOOK_URL");

        if (webhookUrl == null || webhookUrl.isEmpty()) {
            System.out.println("[WARN] SLACK_WEBHOOK_URL not set. Skipping Slack notification.");
            return;
        }

        try {
            String jsonPayload = new ObjectMapper()
                    .writeValueAsString(Map.of("text", message));

            RestAssured.given()
                    .contentType(ContentType.JSON)
                    .body(jsonPayload)
                    .post(webhookUrl)
                    .then()
                    .statusCode(200);

            System.out.println("[INFO] Slack notification sent successfully.");
        } catch (Exception e) {
            System.err.println("[ERROR] Slack notification failed: " + e.getMessage());
        }
    }
}
