package com.cucumber.framework.utils;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * Reads configuration from config.properties with system-property override support.
 *
 * Priority: -Dkey=value (system property) > config.properties > supplied default
 *
 * This mirrors the priority chain in selenium-java's ConfigReader and
 * playwright-dotnet's ConfigReader.cs.
 */
public class ConfigReader {

    private static final Properties props = new Properties();

    static {
        try (InputStream is = ConfigReader.class.getClassLoader()
                .getResourceAsStream("config.properties")) {
            if (is == null) throw new RuntimeException("config.properties not found on classpath");
            props.load(is);
        } catch (IOException e) {
            throw new RuntimeException("Failed to load config.properties", e);
        }
    }

    public static String get(String key) {
        return System.getProperty(key, props.getProperty(key, ""));
    }

    public static String get(String key, String defaultValue) {
        return System.getProperty(key, props.getProperty(key, defaultValue));
    }
}
