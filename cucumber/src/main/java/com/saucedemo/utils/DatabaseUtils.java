package com.saucedemo.utils;

import java.sql.*;

/**
 * DatabaseUtils: Backend data validation and dynamic test data sourcing.
 * Enables Frontend-to-Backend integrity checks — confirms UI reflects DB truth.
 */
public class DatabaseUtils {

    public static Connection getConnection() throws SQLException {
        try {
            return DriverManager.getConnection(
                    ConfigReader.getProperty("db.url"),
                    ConfigReader.getProperty("db.user"),
                    ConfigReader.getProperty("db.password")
            );
        } catch (SQLException e) {
            System.err.println("[ERROR] Failed to connect to database: " + e.getMessage());
            throw e;
        }
    }

    /**
     * Fetches a single active username — demonstrates dynamic test data sourcing.
     */
    public static String getValidUser() {
        String query = "SELECT username FROM users WHERE is_active = 1 LIMIT 1";

        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {

            if (rs.next()) {
                String username = rs.getString("username");
                System.out.println("[INFO] Dynamic test data acquired: " + username);
                return username;
            }
        } catch (SQLException e) {
            System.err.println("[ERROR] Database query failed: " + e.getMessage());
        }
        return "fallback_user";
    }

    /**
     * Validates that a user's account and holdings exist — UI-to-DB integrity check.
     */
    public static boolean verifyPortfolioIntegrity(String username) {
        String query = "SELECT u.username, a.account_type, h.symbol, h.quantity " +
                "FROM users u " +
                "JOIN accounts a ON u.id = a.user_id " +
                "JOIN holdings h ON a.id = h.account_id " +
                "WHERE u.username = ? AND u.status = 'ACTIVE'";

        try (Connection conn = getConnection();
             PreparedStatement pstmt = conn.prepareStatement(query)) {

            pstmt.setString(1, username);
            try (ResultSet rs = pstmt.executeQuery()) {
                return rs.next();
            }
        } catch (SQLException e) {
            System.err.println("[ERROR] Integrity check query failed: " + e.getMessage());
            return false;
        }
    }
}
