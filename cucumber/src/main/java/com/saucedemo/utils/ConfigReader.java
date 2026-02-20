package com.saucedemo.utils;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

/**
 * ConfigReader: Manages framework configuration with a strict priority hierarchy.
 * Priority: 1. System Properties  (-Dkey=value)
 *           2. Explicit env var aliases (e.g. BS_USER for bs_user)
 *           3. Auto-converted env var  (bs_user -> BS_USER)
 *           4. Property file           (config.properties)
 */
public class ConfigReader {
    private static final Properties properties = new Properties();

    private static final Map<String, String> ENV_VAR_ALIASES = new HashMap<>();

    static {
        ENV_VAR_ALIASES.put("bs_user", "BS_USER");
        ENV_VAR_ALIASES.put("bs_key",  "BS_KEY");

        try (InputStream input = ConfigReader.class.getClassLoader().getResourceAsStream("config.properties")) {
            if (input != null) {
                properties.load(input);
            } else {
                try (FileInputStream fileInput = new FileInputStream("src/test/resources/config.properties")) {
                    properties.load(fileInput);
                } catch (Exception e) {
                    System.err.println("[FATAL] config.properties missing from both Classpath and File System.");
                }
            }
        } catch (IOException e) {
            System.err.println("[ERROR] Failed to initialize properties: " + e.getMessage());
        }
    }

    public static String getProperty(String key) {
        String value = System.getProperty(key);
        if (value != null && !value.isEmpty()) return value;

        String alias = ENV_VAR_ALIASES.get(key);
        if (alias != null) {
            String aliasValue = System.getenv(alias);
            if (aliasValue != null && !aliasValue.isEmpty()) return aliasValue;
        }

        String envKey = key.toUpperCase().replace(".", "_");
        String envValue = System.getenv(envKey);
        if (envValue != null && !envValue.isEmpty()) return envValue;

        return properties.getProperty(key);
    }

    public static String getProperty(String key, String defaultValue) {
        String value = getProperty(key);
        return (value != null && !value.isEmpty()) ? value : defaultValue;
    }
}
