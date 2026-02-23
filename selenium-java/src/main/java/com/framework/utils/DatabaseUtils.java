package com.framework.utils;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.*;

// TODO: Integrate with User Management DB once environment is available

/**
 * DatabaseUtils: Enables direct database interaction for test data sourcing and result validation.
 *
 * WHY THIS CLASS EXISTS — Backend Validation:
 * End-to-end tests typically validate what the user SEES on the screen. But what the
 * screen shows might not match what is actually stored in the database — and that gap is
 * where subtle bugs hide. DatabaseUtils enables a critical testing technique:
 *
 *   SCREEN VALUE  ==  DATABASE VALUE  (both match = confidence the data is correct end-to-end)
 *
 * It also enables DYNAMIC TEST DATA SOURCING: instead of hardcoding test usernames in files,
 * tests can query the database for a real, currently-active user and test with that.
 *
 * KEY PATTERNS DEMONSTRATED:
 *   1. try-with-resources: Connections, Statements, and ResultSets are automatically closed
 *      even if exceptions occur — this prevents database connection pool exhaustion.
 *   2. PreparedStatement: Uses parameterized queries to prevent SQL injection attacks.
 *      Even in test code, good security habits should be demonstrated.
 *   3. Fallback values: When the DB is unreachable, methods return a safe default rather
 *      than crashing — tests can still proceed with a known fallback user.
 *   4. Complex JOIN query: The verifyPortfolioIntegrity method shows multi-table query
 *      knowledge relevant to financial application testing.
 *
 * For recruiters: Database validation demonstrates that the engineer can verify data
 * integrity at multiple layers of the application stack, not just the UI.
 */
public class DatabaseUtils {

    /**
     * Establishes and returns a connection to the configured database.
     *
     * WHY CREDENTIALS COME FROM ConfigReader:
     * Database credentials (URL, username, password) must never be hardcoded. They vary
     * between environments (dev, staging, production have different databases), and they
     * may be rotated regularly for security. ConfigReader's priority hierarchy means these
     * values can come from environment variables in CI/CD or the config file locally.
     *
     * WHY THIS METHOD IS PUBLIC:
     * Making getConnection() a separate public method allows it to be reused (and independently
     * tested) by any code that needs a database connection. Tests can also call it directly
     * to verify database connectivity as part of sanity checks.
     *
     * @return An open Connection to the database
     * @throws SQLException if the connection cannot be established (wraps and re-throws with a log)
     */
    public static Connection getConnection() throws SQLException {
        try {
            return DriverManager.getConnection(
                    ConfigReader.getProperty("db.url"),
                    ConfigReader.getProperty("db.user"),
                    ConfigReader.getProperty("db.password")
            );
        } catch (SQLException e) {
            System.err.println("[ERROR] Failed to connect to Database: " + e.getMessage());
            throw e; // Re-throw so the caller knows the connection failed and can handle it
        }
    }

    /**
     * Queries the database for a single active username to use as dynamic test data.
     *
     * WHY DYNAMIC TEST DATA FROM THE DATABASE:
     * Hardcoded test usernames become invalid when the test environment is refreshed or
     * user accounts are removed. Fetching a username from the database ensures the test
     * always uses a user that actually exists in the current environment.
     *
     * TRY-WITH-RESOURCES PATTERN EXPLAINED:
     * Java's "try-with-resources" statement automatically calls .close() on any resource
     * declared in the try() parentheses when the block finishes — whether normally or
     * via exception. This guarantees that database connections are never leaked, which is
     * critical because databases have a maximum number of simultaneous connections, and
     * leaked connections exhaust that pool, causing all subsequent tests to fail.
     *
     * WHY RETURN A FALLBACK VALUE INSTEAD OF THROWING:
     * If the database is unreachable (e.g., running tests without DB connectivity in a
     * demo/portfolio context), returning a fallback user string allows tests to continue
     * with a known default rather than crashing the entire test run.
     *
     * @return A real active username from the database; "fallback_user" if the DB is unreachable
     */
    public static String getValidUser() {
        String username = null;
        String query = "SELECT username FROM users WHERE is_active = 1 LIMIT 1";

        // Using try-with-resources to ensure Connection, Statement, and ResultSet are closed automatically
        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {

            // rs.next() moves the cursor to the first result row. Returns false if no rows exist.
            if (rs.next()) {
                username = rs.getString("username");
                System.out.println("[INFO] Dynamic Test Data Acquired: " + username);
            }
        } catch (SQLException e) {
            System.err.println("[ERROR] Database Query Failed: " + e.getMessage());
        }
        return (username != null) ? username : "fallback_user";
    }

    /**
     * Validates a user's portfolio data by joining Users, Accounts, and Holdings tables.
     *
     * SCENARIO — Fidelity-Style Backend Validation:
     * In a financial application, the UI might display a user's portfolio holdings. This
     * method demonstrates how an SDET would verify that the data shown in the UI is backed
     * by corresponding database records — a JOIN across three tables confirms the relationship
     * is intact all the way through the data model.
     *
     * WHY PREPAREDSTATEMENT INSTEAD OF STATEMENT:
     * Statement (used in getValidUser) is fine for queries with no user-supplied values.
     * PreparedStatement is required when query values come from external sources (like a
     * test parameter or user input). PreparedStatement sends the query structure and the
     * parameters SEPARATELY to the database, making it impossible for malicious values
     * in the parameter to alter the query structure (SQL injection prevention).
     *
     * The "?" placeholder is replaced by pstmt.setString(1, username), which the database
     * driver handles safely — any special characters in the username are treated as data,
     * not as SQL syntax.
     *
     * @param username The username to check for active portfolio records
     * @return true if the user has at least one joined record across Users/Accounts/Holdings; false otherwise
     */
    public static boolean verifyPortfolioIntegrity(String username) {
        String query = "SELECT u.username, a.account_type, h.symbol, h.quantity " +
                "FROM users u " +
                "JOIN accounts a ON u.id = a.user_id " +
                "JOIN holdings h ON a.id = h.account_id " +
                "WHERE u.username = ? AND u.status = 'ACTIVE'";

        try (Connection conn = getConnection();
             PreparedStatement pstmt = conn.prepareStatement(query)) {

            pstmt.setString(1, username); // Securely handling parameters to prevent SQL injection
            try (ResultSet rs = pstmt.executeQuery()) {
                return rs.next(); // Returns true if at least one matching joined record exists
            }
        } catch (SQLException e) {
            System.err.println("[ERROR] Complex Join Query Failed: " + e.getMessage());
            return false;
        }
    }
}
