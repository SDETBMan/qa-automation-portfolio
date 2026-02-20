package com.framework.utils;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class DateHelper {
    public static String getTodayFormatted(String pattern) {
        return LocalDate.now().format(DateTimeFormatter.ofPattern(pattern));
    }
}
