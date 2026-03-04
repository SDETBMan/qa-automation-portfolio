package com.saucedemo.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.restassured.RestAssured;
import io.restassured.http.ContentType;

import java.time.Instant;
import java.util.List;
import java.util.Map;

/**
 * DataDogUtils: Sends suite-level test metrics to DataDog via the v2 metrics API.
 *
 * <p>Four GAUGE metrics are posted after each suite run:
 * {@code test.suite.passed}, {@code test.suite.failed}, {@code test.suite.skipped},
 * and {@code test.suite.duration_ms}. These power DataDog dashboards that surface
 * pass/fail trends, flaky-test signals, and duration regressions over time.
 *
 * <p>FAIL-SAFE DESIGN: If {@code DD_API_KEY} is absent (local dev, environments
 * without DataDog), the method logs a warning and returns without throwing —
 * mirroring the graceful-skip pattern used by {@link SlackUtils}. CI stays green.
 *
 * <p>HTTP transport reuses RestAssured (already in pom.xml) and Jackson for JSON
 * serialization, consistent with how {@link SlackUtils#sendResult(String)} works.
 *
 * <p>DataDog v2 metrics API endpoint: {@code POST https://api.datadoghq.com/api/v2/series}
 * Authentication header: {@code DD-API-KEY: <api_key>}
 * Success response: HTTP 202 Accepted.
 *
 * <p>Metric type {@code 3} = DataDog GAUGE — correct for point-in-time counts and
 * durations that do not accumulate across submissions.
 */
public class DataDogUtils {

    private static String ddApiUrl() {
        String site = System.getenv("DD_SITE");
        if (site == null || site.isBlank()) site = "datadoghq.com";
        return "https://api." + site + "/api/v2/series";
    }

    /**
     * Posts four suite-level metrics to DataDog after a test run completes.
     *
     * <p>Called from {@code TestListener.onFinish()} so metrics are sent once per
     * suite, not once per test — keeping DataDog usage within free-tier limits and
     * making the resulting time-series human-readable on dashboards.
     *
     * @param passed     number of tests that passed in this suite run
     * @param failed     number of tests that failed
     * @param skipped    number of tests that were skipped
     * @param durationMs total suite wall-clock duration in milliseconds
     * @param framework  short label for the framework tag, e.g. {@code "cucumber"}
     */
    public static void sendTestMetrics(int passed, int failed, int skipped, long durationMs, String framework) {
        String apiKey = System.getenv("DD_API_KEY");

        if (apiKey == null || apiKey.isEmpty()) {
            System.out.println("[WARN] DD_API_KEY not set. Skipping DataDog metrics.");
            return;
        }

        try {
            long timestamp = Instant.now().getEpochSecond();
            List<String> tags = List.of(
                    "framework:" + framework,
                    "service:qa-automation-portfolio",
                    "env:ci"
            );

            Map<String, Object> payload = Map.of(
                    "series", List.of(
                            buildSeries("test.suite.passed",      passed,     timestamp, tags),
                            buildSeries("test.suite.failed",      failed,     timestamp, tags),
                            buildSeries("test.suite.skipped",     skipped,    timestamp, tags),
                            buildSeries("test.suite.duration_ms", durationMs, timestamp, tags)
                    )
            );

            // Use Jackson for safe serialization — handles any special characters in tags
            String jsonPayload = new ObjectMapper().writeValueAsString(payload);

            int status = RestAssured.given()
                    .contentType(ContentType.JSON)
                    .header("DD-API-KEY", apiKey)
                    .body(jsonPayload)
                    .post(ddApiUrl())
                    .getStatusCode();

            if (status == 202) {
                System.out.println("[INFO] DataDog metrics sent successfully.");
            } else {
                System.out.println("[WARN] DataDog metrics returned unexpected status: " + status);
            }
        } catch (Exception e) {
            // Never crash the test run over a metrics delivery failure
            System.err.println("[ERROR] DataDog metrics failed: " + e.getMessage());
        }
    }

    /**
     * Builds a single DataDog v2 series entry for one metric.
     *
     * @param metric    the fully-qualified metric name, e.g. {@code "test.suite.passed"}
     * @param value     the numeric value to record
     * @param timestamp Unix epoch seconds for the data point
     * @param tags      list of tag strings in {@code key:value} format
     * @return a Map that Jackson will serialize to a valid DataDog series object
     */
    private static Map<String, Object> buildSeries(String metric, long value, long timestamp, List<String> tags) {
        return Map.of(
                "metric", metric,
                "type",   3,                // 3 = GAUGE in DataDog's type enum
                "points", List.of(Map.of("timestamp", timestamp, "value", value)),
                "tags",   tags
        );
    }
}
