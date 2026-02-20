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
 * AiHelper: Generates dynamic test data using OpenAI.
 * Demonstrates integration of LLMs for autonomous testing capabilities.
 */
public class AiHelper {

    private static final String API_KEY = System.getenv("OPENAI_API_KEY");
    private static final boolean USE_REAL_AI = (API_KEY != null && !API_KEY.isEmpty());
    private static final String MODEL = ConfigReader.getProperty("ai.model", "gpt-4o-mini");

    /**
     * Generates test data based on a natural language prompt.
     * Priority: OpenAI API > Local Mock Data.
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

            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = jsonInput.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }

            // Read and parse response using Jackson
            Scanner scanner = new Scanner(conn.getInputStream(), StandardCharsets.UTF_8);
            String responseBody = scanner.useDelimiter("\\A").next();
            scanner.close();

            JsonNode root = mapper.readTree(responseBody);
            return root.get("choices").get(0).get("message").get("content").asText().trim();

        } catch (Exception e) {
            System.err.println("[ERROR] AI Data Generation Failed: " + e.getMessage());
            return generateMockData(prompt);
        }
    }

    /**
     * Fallback mock data to ensure test stability when API is unavailable.
     */
    private static String generateMockData(String prompt) {
        String lowerPrompt = prompt.toLowerCase();

        if (lowerPrompt.contains("email")) {
            return "test_user_" + System.currentTimeMillis() + "@example.com";
        }
        if (lowerPrompt.contains("password")) {
            return "SecurePass!" + (int) (Math.random() * 1000);
        }
        if (lowerPrompt.contains("username")) {
            return "QA_User_" + (int) (Math.random() * 1000);
        }

        return "Default_Test_Value";
    }
}
