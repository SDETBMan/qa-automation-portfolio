package com.framework.driver;

import org.openqa.selenium.WebDriver;

/**
 * DriverManager: Thread-Safe Driver Management.
 * Uses ThreadLocal to ensure that each test thread (Parallel Execution)
 * gets its own isolated WebDriver instance.
 */
public class DriverManager {

    // ThreadLocal acts as a separate "box" for every thread.
    // Thread 1 puts its Chrome Driver here. Thread 2 puts its Firefox Driver here.
    // They never overlap.
    private static final ThreadLocal<WebDriver> dr = new ThreadLocal<>();

    // Private constructor prevents anyone from saying "new DriverManager()"
    private DriverManager() {
    }

    /**
     * Returns the WebDriver instance specific to the current thread.
     */
    public static WebDriver getDriver() {
        return dr.get();
    }

    /**
     * Stores the WebDriver instance for the current thread.
     */
    public static void setDriver(WebDriver driverRef) {
        dr.set(driverRef);
    }

    /**
     * Cleans up the ThreadLocal reference to prevent memory leaks.
     * Note: This does NOT quit the driver (BaseTest handles that).
     * This just clears the "box" for the next test.
     */
    public static void unload() {
        dr.remove();
    }
}
