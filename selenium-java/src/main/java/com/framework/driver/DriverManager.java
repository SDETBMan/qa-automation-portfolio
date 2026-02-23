package com.framework.driver;

import org.openqa.selenium.WebDriver;

/**
 * DriverManager: The thread-safe storage vault for WebDriver instances.
 *
 * WHY THIS CLASS EXISTS:
 * When tests run in parallel (multiple tests executing at the same time), each test
 * runs on its own "thread" — think of a thread as a separate worker on an assembly line.
 * Without this class, all threads would share a single WebDriver, causing them to
 * interfere with each other (one test clicking buttons meant for another test).
 *
 * HOW IT SOLVES THE PROBLEM:
 * This class uses Java's ThreadLocal mechanism. ThreadLocal gives every thread its own
 * private copy of a variable, completely isolated from all other threads. Thread 1 gets
 * its own Chrome driver; Thread 2 gets its own Firefox driver. They never overlap.
 *
 * DESIGN PATTERN — Static Utility Class:
 * All methods are static (callable without creating an instance of this class), which
 * means any test or page object in the entire framework can call DriverManager.getDriver()
 * without needing to pass the driver around manually through method parameters.
 *
 * For recruiters: This is a foundational, industry-standard pattern in parallel test
 * automation. Any framework running more than one test at a time needs this.
 */
public class DriverManager {

    // ThreadLocal acts as a separate "box" for every thread.
    // Thread 1 puts its Chrome Driver here. Thread 2 puts its Firefox Driver here.
    // They never overlap.
    // "final" means this container itself cannot be replaced, only what's inside it can change.
    private static final ThreadLocal<WebDriver> dr = new ThreadLocal<>();

    // Private constructor prevents anyone from saying "new DriverManager()"
    // This enforces the static utility pattern — you use DriverManager.getDriver(),
    // not "new DriverManager().getDriver()". There is never a need for an instance.
    private DriverManager() {
    }

    /**
     * Returns the WebDriver instance specific to the currently running thread.
     *
     * WHY: Every test method needs a browser to interact with. Rather than each test
     * receiving the driver as a method parameter (which gets messy at scale), any test
     * or page object can call this single line to get the correct driver for its thread.
     * If called from Thread 1, it returns Thread 1's driver. If called from Thread 2,
     * it returns Thread 2's driver. The caller never needs to know which thread it is on.
     */
    public static WebDriver getDriver() {
        return dr.get();
    }

    /**
     * Stores a WebDriver instance and associates it with the current thread.
     *
     * WHY: Called once at the start of each test (in BaseTest.setUp). After this call,
     * any code running on the same thread — page objects, helper utilities, listeners —
     * can retrieve this exact driver via getDriver() without it being passed around.
     *
     * @param driverRef The WebDriver instance created by DriverFactory for this test.
     */
    public static void setDriver(WebDriver driverRef) {
        dr.set(driverRef);
    }

    /**
     * Removes the ThreadLocal reference for the current thread after the test finishes.
     *
     * WHY THIS IS CRITICAL — Memory Leak Prevention:
     * ThreadLocal variables live as long as the thread lives. In thread pools (common in
     * CI/CD environments like Jenkins or GitHub Actions), threads are reused across many
     * tests. If we never call remove(), the old WebDriver reference stays in memory even
     * after the browser is closed, slowly leaking memory and potentially causing the next
     * test on that thread to pick up a stale (already-closed) driver.
     *
     * IMPORTANT: This method does NOT quit the browser — it only removes the Java reference.
     * BaseTest.tearDown() is responsible for calling driver.quit() to actually close the
     * browser window before this method is called.
     */
    public static void unload() {
        dr.remove();
    }
}
