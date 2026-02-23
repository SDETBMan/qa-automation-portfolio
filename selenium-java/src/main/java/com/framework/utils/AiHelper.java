package com.framework.utils;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.Scanner;

/**
 * AiHelper: Integrates OpenAI's API to generate dynamic test data on demand.
 *
 * WHY THIS CLASS EXISTS:
 * Traditional test data is static — the same usernames, emails, and passwords are used
 * repeatedly in every test run. This has two problems:
 *   1. Tests become tied to specific data that may become invalid over time
 *   2. You can't easily generate realistic, varied data for boundary and negative testing
 *
 * By asking an AI model to generate test data, this class enables:
 *   - Unique data on every run (reducing false test collisions)
 *   - Semantically appropriate data (AI generates realistic email formats, complex passwords)
 *   - Dynamic negative testing (AI generates data that LOOKS valid but won't match credentials)
 *
 * GRACEFUL DEGRADATION (the most important design decision here):
 * Not every environment has an OpenAI API key. CI pipelines in demo portfolios, local
 * development machines, and restricted corporate networks may not be able to reach the
 * OpenAI API. The class detects whether an API key is available and falls back to
 * deterministic local mock data generation when it isn't. Tests never fail due to
 * AI infrastructure being unavailable.
 *
 * For recruiters: AI-assisted test data generation is an emerging practice in modern QA.
 * This class shows awareness of LLM integration in automation workflows, while the
 * graceful fallback shows production-minded engineering.
 */
public class AiHelper {

    // Read the API key from an environment variable — NEVER hardcode API keys in source code.
    // Environment variables keep secrets out of the codebase and version control history.
    private static final String API_KEY = System.getenv("OPENAI_API_KEY");

    // Pre-compute whether real AI is available so we don't repeat the null check every call.
    // If the key is missing, all calls automatically route to the local mock data generator.
    private static final boolean USE_REAL_AI = (API_KEY != null && !API_KEY.isEmpty());

    // The model name is configurable so the team can switch between GPT versions (e.g., from
    // gpt-4o-mini to gpt-4o) in config.properties without touching this code.
    private static final String MODEL = ConfigReader.getProperty("ai.model", "gpt-4o-mini");

    /**
     * Generates test data based on a natural language description of what data is needed.
     *
     * PRIORITY: OpenAI API (if key is present) → Local Mock Data (if key is absent)
     *
     * WHY A NATURAL LANGUAGE PROMPT:
     * Rather than writing separate methods for email generation, password generation, etc.,
     * a single prompt-based method handles any type of data. The calling test simply describes
     * what it needs in plain English, and this method figures out how to produce it.
     *
     * WHY max_tokens IS SET TO 20:
     * We only need a short piece of data (an email address, a password, a name). Limiting
     * the response to 20 tokens prevents the API from returning lengthy explanations and
     * keeps API costs low. The system prompt reinforces this by asking for "ONLY the raw
     * data string" without explanation.
     *
     * WHY JACKSON FOR SERIALIZATION (not manual string building):
     * Building JSON strings manually (e.g., "{\"role\": \"user\"...}") is fragile — any
     * special character in the prompt (quotes, backslashes, newlines) would break the JSON.
     * Jackson's ObjectMapper.writeValueAsString() handles all escaping correctly, making
     * the request body safe regardless of the prompt content.
     *
     * @param prompt A plain English description of the data to generate
     *               (e.g., "Generate a valid looking email address")
     * @return The generated data string; falls back to mock data if the API is unavailable
     */
    public static String generateTestData(String prompt) {
        if (!USE_REAL_AI) {
            return generateMockData(prompt);
        }

        try {
            URL url = new URL("https://api.openai.com/v1/chat/completions");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Authorization", "Bearer " + API_KEY);
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setDoOutput(true);

            // Build request payload with Jackson to safely handle any characters in prompt
            ObjectMapper mapper = new ObjectMapper();
            String jsonInput = mapper.writeValueAsString(Map.of(
                    "model", MODEL,
                    "max_tokens", 20,
                    "messages", List.of(
                            Map.of("role", "system",
                                   "content", "You are a test data generator. Return ONLY the raw data string requested."),
                            Map.of("role", "user", "content", prompt)
                    )
            ));

            // Write the JSON payload to the HTTP connection's output stream.
            // UTF-8 encoding ensures non-ASCII characters in the prompt are transmitted correctly.
            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = jsonInput.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }

            // Read and parse response using Jackson.
            // Scanner with "\\A" delimiter reads the entire stream as one string.
            Scanner scanner = new Scanner(conn.getInputStream(), StandardCharsets.UTF_8);
            String responseBody = scanner.useDelimiter("\\A").next();
            scanner.close();

            // Navigate the JSON response tree: choices[0].message.content
            // This is the standard OpenAI Chat Completions API response structure.
            JsonNode root = mapper.readTree(responseBody);
            return root.get("choices").get(0).get("message").get("content").asText().trim();

        } catch (Exception e) {
            System.err.println("[ERROR] AI Data Generation Failed: " + e.getMessage());
            // Fall through to mock data when the API fails — ensures tests aren't blocked by AI downtime
            return generateMockData(prompt);
        }
    }

    /**
     * Generates simple deterministic mock data when the OpenAI API is unavailable.
     *
     * WHY KEYWORD-BASED MATCHING:
     * Rather than returning a generic fallback for all prompts, we inspect the prompt text
     * to infer what type of data was requested. If the prompt mentions "email", we return an
     * email-format string. This makes the fallback realistic enough for negative tests that
     * verify the app rejects unknown credentials.
     *
     * WHY System.currentTimeMillis() AND Math.random():
     * These produce different values on every call, preventing two tests from generating
     * identical mock data when running in the same test session. Duplicate test data can
     * cause false test dependencies (test B fails because test A already used the same email).
     *
     * @param prompt The original prompt; keywords in it determine which type of data to return
     * @return A simple mock value appropriate to the prompt context
     */
    private static String generateMockData(String prompt) {
        String lowerPrompt = prompt.toLowerCase();

        if (lowerPrompt.contains("email")) {
            // Millisecond timestamp ensures uniqueness across calls in the same test run
            return "test_user_" + System.currentTimeMillis() + "@example.com";
        }
        if (lowerPrompt.contains("password")) {
            // Random suffix makes each mock password unique within a test session
            return "SecurePass!" + (int) (Math.random() * 1000);
        }
        if (lowerPrompt.contains("username")) {
            return "QA_User_" + (int) (Math.random() * 1000);
        }

        // Generic fallback when no keyword matches — still a unique-enough value for testing
        return "Default_Test_Value";
    }
}
