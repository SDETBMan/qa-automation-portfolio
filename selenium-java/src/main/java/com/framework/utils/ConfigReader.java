package com.framework.utils;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

/**
 * ConfigReader: Manages framework configuration with a strict priority hierarchy.
 * Priority: 1. System Properties  (-Dkey=value)
 *           2. Explicit env var aliases (e.g. SAUCE_USERNAME for cloud_username)
 *           3. Auto-converted env var  (cloud_username -> CLOUD_USERNAME)
 *           4. Property file           (config.properties)
 */
public class ConfigReader {
    private static final Properties properties = new Properties();

    /**
     * Explicit env var name overrides for keys whose standard CI variable names
     * don't match the auto-conversion pattern (key.toUpperCase().replace('.','_')).
     * Add entries here whenever a vendor/CI system uses its own naming convention.
     */
    private static final Map<String, String> ENV_VAR_ALIASES = new HashMap<>();

    static {
        // Sauce Labs credentials use their own well-known env var names
        ENV_VAR_ALIASES.put("cloud_username", "SAUCE_USERNAME");
        ENV_VAR_ALIASES.put("cloud_key",      "SAUCE_ACCESS_KEY");

        // 1. Attempt to load from Classpath (Standard Maven/JAR execution)
        try (InputStream input = ConfigReader.class.getClassLoader().getResourceAsStream("config.properties")) {
            if (input != null) {
                properties.load(input);
                System.out.println("[INFO] Configuration loaded from Classpath.");
            } else {
                // 2. Fallback: Direct file system access (Local IDE execution)
                try (FileInputStream fileInput = new FileInputStream("src/test/resources/config.properties")) {
                    properties.load(fileInput);
                    System.out.println("[INFO] Configuration loaded from local file system.");
                } catch (Exception e) {
                    System.err.println("[FATAL] config.properties missing from both Classpath and File System.");
                }
            }
        } catch (IOException e) {
            System.err.println("[ERROR] Failed to initialize properties: " + e.getMessage());
        }
    }

    /**
     * Retrieves a property value using the priority hierarchy.
     * Returns null if the key is not found at any level.
     */
    public static String getProperty(String key) {
        // Priority 1: JVM system property  (-Dkey=value)
        String value = System.getProperty(key);
        if (value != null && !value.isEmpty()) return value;

        // Priority 2: Explicit env var alias (cloud_username -> SAUCE_USERNAME)
        String alias = ENV_VAR_ALIASES.get(key);
        if (alias != null) {
            String aliasValue = System.getenv(alias);
            if (aliasValue != null && !aliasValue.isEmpty()) return aliasValue;
        }

        // Priority 3: Auto-converted env var  (app_username -> APP_USERNAME)
        String envKey = key.toUpperCase().replace(".", "_");
        String envValue = System.getenv(envKey);
        if (envValue != null && !envValue.isEmpty()) return envValue;

        // Priority 4: config.properties file
        return properties.getProperty(key);
    }

    /**
     * Retrieves a property value, returning {@code defaultValue} instead of null
     * when the key is absent from all sources.
     */
    public static String getProperty(String key, String defaultValue) {
        String value = getProperty(key);
        return (value != null && !value.isEmpty()) ? value : defaultValue;
    }
}
