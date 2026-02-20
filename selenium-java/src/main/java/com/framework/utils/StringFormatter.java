package com.framework.utils;

public class StringFormatter {
    public static String formatTestName(String name) {
        if (name == null) return "";
        return name.trim().replaceAll(" ", "_").toLowerCase();
    }

    public static String getEnvironmentUrl(String env) {
        if (env == null) {
            return "https://default.example.com";
        }

        switch (env.toLowerCase()) {
            case "dev":
                return "https://dev.example.com";
            case "qa":
                return "https://qa.example.com";
            case "staging":
                return "https://staging.example.com";
            default:
                return "https://prod.example.com";
        }
    }
}
