package com.framework.utils;

/**
 * StringUtils: Provides logic for string manipulation and random data generation.
 */
public class StringUtils {

    /**
     * Generates a random test email.
     * Uses System.nanoTime() to avoid collisions in parallel runs.
     * @return a string formatted as user<digits>@test.com
     */
    public static String generateRandomEmail() {
        return "user" + System.nanoTime() + "@test.com";
    }

    /**
     * Reusable logic for string validation.
     * Requires a valid local part, @, domain with at least one label, and a TLD of 2+ chars.
     */
    public static boolean isValidEmail(String email) {
        if (email == null || email.isEmpty()) return false;
        return email.matches("^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$");
    }
}
