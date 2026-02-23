package com.framework.utils;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

/**
 * DateHelper: Provides date formatting utilities for use in tests and test data generation.
 *
 * WHY THIS CLASS EXISTS:
 * Tests frequently need date values — for filtering, sorting, verifying timestamps, or
 * generating dated test artifacts (like screenshot filenames or report entries). Rather
 * than scattering date-formatting logic across test files, this utility centralizes it.
 *
 * WHY java.time (NOT java.util.Date):
 * Java 8 introduced the java.time package (LocalDate, DateTimeFormatter, etc.) as a
 * replacement for the older java.util.Date and SimpleDateFormat classes. The old classes
 * are mutable and not thread-safe — two threads formatting dates simultaneously could
 * corrupt each other's results. java.time classes are immutable and thread-safe by design,
 * making them safe for use in parallel test execution.
 *
 * For recruiters: Using modern Java APIs (java.time over java.util.Date) demonstrates
 * current language knowledge and awareness of thread safety in parallel test frameworks.
 */
public class DateHelper {

    /**
     * Returns today's date as a string formatted according to the specified pattern.
     *
     * WHY A FORMAT PARAMETER:
     * Different contexts need different date formats. Test report filenames might use
     * "yyyy-MM-dd" (2026-02-23), a UI date picker might expect "MM/dd/yyyy" (02/23/2026),
     * and a year-only check might use "yyyy" (2026). By accepting the pattern as a parameter,
     * one method serves all these cases rather than needing a separate method for each format.
     *
     * HOW DateTimeFormatter.ofPattern() WORKS:
     * The pattern string uses placeholder letters that Java replaces with real date parts:
     *   yyyy = 4-digit year  (2026)
     *   MM   = 2-digit month (02)
     *   dd   = 2-digit day   (23)
     * Letters are case-sensitive: "MM" = month, "mm" = minutes; "dd" = day, "DD" = day-of-year.
     *
     * @param pattern A date format pattern string (e.g., "yyyy-MM-dd", "MM/dd/yyyy", "yyyy")
     * @return Today's date as a formatted string matching the given pattern
     */
    public static String getTodayFormatted(String pattern) {
        return LocalDate.now().format(DateTimeFormatter.ofPattern(pattern));
    }
}
