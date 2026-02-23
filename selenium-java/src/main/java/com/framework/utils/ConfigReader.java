package com.framework.utils;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

/**
 * ConfigReader: The single source of truth for all framework configuration values.
 *
 * WHY THIS CLASS EXISTS:
 * A professional automation framework never hardcodes configuration values (URLs, credentials,
 * timeouts) directly in test files. When the test environment changes or credentials rotate,
 * you would need to find and update every hardcoded value across dozens of test files.
 * ConfigReader solves this by providing one centralized place to read configuration, while
 * supporting multiple sources so the framework works correctly in every environment.
 *
 * THE PRIORITY HIERARCHY (most trusted to least trusted):
 *   1. JVM System Properties (-Dkey=value on the command line or in Maven POM)
 *      Example: mvn test -Dbrowser=firefox overrides the config file's browser setting
 *   2. Explicit environment variable aliases (for vendor-specific naming conventions)
 *      Example: Sauce Labs uses "SAUCE_USERNAME" rather than "CLOUD_USERNAME"
 *   3. Auto-converted environment variable names (config key → UPPERCASE_WITH_UNDERSCORES)
 *      Example: "app_username" in config → looks for "APP_USERNAME" environment variable
 *   4. config.properties file (the fallback default values)
 *
 * WHY THIS HIERARCHY MATTERS:
 * CI/CD pipelines (GitHub Actions, Jenkins) inject secrets as environment variables — they
 * never write passwords to files. The hierarchy ensures those injected values take priority
 * over the defaults in config.properties, keeping credentials out of source code.
 *
 * STATIC INITIALIZATION BLOCK:
 * The "static { ... }" block runs exactly once when the JVM first loads this class — before
 * any test calls getProperty(). This pre-loads the config file so every subsequent call
 * to getProperty() is an instant in-memory lookup rather than a file read.
 */
public class ConfigReader {

    // "static final" means this Properties object is shared by the entire JVM (one copy for
    // all tests) and cannot be replaced. It acts like a shared key-value dictionary loaded once.
    private static final Properties properties = new Properties();

    /**
     * Explicit environment variable name overrides for keys whose standard CI variable names
     * don't match the auto-conversion pattern (key.toUpperCase().replace('.','_')).
     *
     * WHY A MAP OF ALIASES:
     * Sauce Labs credentials use environment variable names defined by Sauce Labs themselves
     * (SAUCE_USERNAME, SAUCE_ACCESS_KEY). These don't match the auto-conversion of the config
     * keys "cloud_username" → "CLOUD_USERNAME". Rather than renaming our config keys to match
     * Sauce Labs (which would break readability), we maintain a mapping from our key names
     * to the vendor's environment variable names.
     *
     * To add support for a new vendor's naming convention, simply add an entry here.
     */
    private static final Map<String, String> ENV_VAR_ALIASES = new HashMap<>();

    static {
        // Sauce Labs credentials use their own well-known env var names
        ENV_VAR_ALIASES.put("cloud_username", "SAUCE_USERNAME");
        ENV_VAR_ALIASES.put("cloud_key",      "SAUCE_ACCESS_KEY");

        // 1. Attempt to load from Classpath (Standard Maven/JAR execution)
        // getResourceAsStream() searches the compiled classpath — Maven copies
        // src/test/resources/ files to target/test-classes/ at build time,
        // making config.properties available as a classpath resource.
        try (InputStream input = ConfigReader.class.getClassLoader().getResourceAsStream("config.properties")) {
            if (input != null) {
                properties.load(input);
                System.out.println("[INFO] Configuration loaded from Classpath.");
            } else {
                // 2. Fallback: Direct file system access (Local IDE execution)
                // When running a test directly from IntelliJ IDEA (not via Maven), the classpath
                // might not include the resources folder. This fallback reads the file directly
                // from its source location so developers can run tests without a Maven build.
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
     * Retrieves a configuration value using the full priority hierarchy.
     *
     * THE RESOLUTION CHAIN:
     * Each level is tried in order. As soon as a non-empty value is found, it is returned
     * immediately without checking lower-priority sources. This ensures command-line
     * overrides always win, environment variables override file values, etc.
     *
     * @param key The configuration key to look up (e.g., "url", "browser", "timeout.explicit")
     * @return The value for the key from the highest-priority source; null if not found anywhere
     */
    public static String getProperty(String key) {
        // Priority 1: JVM system property (-Dkey=value)
        // Set via Maven: mvn test -Durl=https://staging.example.com
        String value = System.getProperty(key);
        if (value != null && !value.isEmpty()) return value;

        // Priority 2: Explicit env var alias (cloud_username -> SAUCE_USERNAME)
        // Handles vendor-specific environment variable naming conventions.
        String alias = ENV_VAR_ALIASES.get(key);
        if (alias != null) {
            String aliasValue = System.getenv(alias);
            if (aliasValue != null && !aliasValue.isEmpty()) return aliasValue;
        }

        // Priority 3: Auto-converted env var (app_username -> APP_USERNAME)
        // Replaces dots with underscores because environment variable names cannot contain dots.
        String envKey = key.toUpperCase().replace(".", "_");
        String envValue = System.getenv(envKey);
        if (envValue != null && !envValue.isEmpty()) return envValue;

        // Priority 4: config.properties file
        // Returns null if the key is not in the file — callers should use the overload
        // with a defaultValue when null would cause a crash.
        return properties.getProperty(key);
    }

    /**
     * Retrieves a configuration value, returning a default if the key is not found.
     *
     * WHY THIS OVERLOAD EXISTS:
     * Many configuration values have sensible defaults (e.g., a 20-second wait timeout).
     * Rather than forcing every caller to write null checks, this overload returns the
     * default value when the key is absent. This makes caller code cleaner and prevents
     * NullPointerExceptions for optional configuration keys.
     *
     * @param key          The configuration key to look up
     * @param defaultValue The value to return if the key is not found in any source
     * @return The resolved configuration value, or defaultValue if not found
     */
    public static String getProperty(String key, String defaultValue) {
        String value = getProperty(key);
        return (value != null && !value.isEmpty()) ? value : defaultValue;
    }
}
