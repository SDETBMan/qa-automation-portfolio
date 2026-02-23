using MySqlConnector;
using Framework.Core.Config;

namespace Framework.Core.Utils;

/// <summary>
/// Database utility class providing async MySQL query execution for test automation.
///
/// Why database access in a UI test framework: Modern QA practices use the database
/// as a verification layer independent of the UI. Examples:
///   - After submitting a form, verify the record was actually saved to the database
///     (not just that a success message appeared on screen).
///   - Seed test data directly into the database to set up a known state before a test.
///   - Clean up test records after a test to prevent data accumulation.
///
/// Technology choice — MySqlConnector (not MySql.Data):
///   MySqlConnector is the community-maintained, fully async ADO.NET driver.
///   The official Oracle MySql.Data package has known issues with true async behaviour,
///   making MySqlConnector the recommended choice for .NET async test code.
///
/// ADO.NET: the low-level .NET database access layer. It works with raw SQL strings,
/// unlike ORMs (Entity Framework). Raw SQL is preferred in test frameworks because
/// tests often need precise, predictable queries without ORM overhead or caching.
///
/// JDBC-URL support: The db:url config key accepts either a plain "host:port/db"
/// string or a full JDBC URL (the Java format: "jdbc:mysql://host:port/db").
/// Supporting both formats lets this C# framework share configuration files
/// with Java-based frameworks in the same portfolio.
///
/// Configuration keys (appsettings.json or environment variables):
///   db:url      — database host, port and schema (e.g., "localhost:3306/testdb")
///   db:user     — database username (default: "root")
///   db:password — database password (default: empty)
/// </summary>
public static class DatabaseUtils
{
    /// <summary>
    /// Builds a MySqlConnector connection string from config values.
    /// Called internally before each database operation — no persistent
    /// connection is held open between calls, which is appropriate for
    /// test code where connections are short-lived.
    ///
    /// Why private: the connection string contains credentials and is an
    /// implementation detail that callers do not need to see.
    /// </summary>
    private static string BuildConnectionString()
    {
        // db:url is stored as a JDBC-style URL; extract host/port/db from it or use raw host.
        string dbUrl  = ConfigReader.GetProperty("db:url", "localhost");
        string user   = ConfigReader.GetProperty("db:user", "root");
        string pass   = ConfigReader.GetProperty("db:password", "");

        // Support plain "host:port/db" or full JDBC "jdbc:mysql://host:port/db"
        // by stripping the Java-specific prefix if present.
        string cleaned = dbUrl.Replace("jdbc:mysql://", "");
        return $"Server={cleaned};User ID={user};Password={pass};";
    }

    /// <summary>
    /// Executes a SELECT query and returns all matching rows as a list of dictionaries.
    /// Each dictionary represents one row, where keys are column names and values are
    /// the cell values (or null for SQL NULL values).
    ///
    /// Why dictionaries: they allow callers to access columns by name without
    /// needing a strongly-typed model class for every table, which is practical
    /// for ad-hoc test verification queries.
    ///
    /// Parameterized queries: the optional parameters dictionary maps SQL parameter
    /// names (e.g., "@userId") to values. ALWAYS use parameters instead of string
    /// concatenation to prevent SQL injection — even in test code, because test
    /// databases sometimes mirror production schemas.
    ///
    /// Example:
    ///   var rows = await DatabaseUtils.ExecuteQueryAsync(
    ///       "SELECT * FROM users WHERE email = @email",
    ///       new Dictionary&lt;string, object?&gt; { ["@email"] = "test@example.com" });
    /// </summary>
    public static async Task<List<Dictionary<string, object?>>> ExecuteQueryAsync(
        string sql,
        Dictionary<string, object?>? parameters = null)
    {
        var results = new List<Dictionary<string, object?>>();

        // "await using" ensures the connection is closed and disposed even if an
        // exception is thrown — equivalent to try/finally conn.Close() in older code.
        await using var conn = new MySqlConnection(BuildConnectionString());
        await conn.OpenAsync();

        await using var cmd = new MySqlCommand(sql, conn);

        // Add each parameter to the command — use DBNull.Value (not null) for SQL NULL
        // because the database driver distinguishes between "no value" and SQL NULL.
        if (parameters != null)
        {
            foreach (var (key, val) in parameters)
                cmd.Parameters.AddWithValue(key, val ?? DBNull.Value);
        }

        await using var reader = await cmd.ExecuteReaderAsync();

        // Iterate over each row returned by the query.
        while (await reader.ReadAsync())
        {
            var row = new Dictionary<string, object?>();

            // Iterate over each column in the current row.
            for (int i = 0; i < reader.FieldCount; i++)
                // reader.IsDBNull(i) checks for SQL NULL; map that to C# null.
                row[reader.GetName(i)] = reader.IsDBNull(i) ? null : reader.GetValue(i);

            results.Add(row);
        }

        return results;
    }

    /// <summary>
    /// Executes a non-query SQL statement (INSERT, UPDATE, or DELETE) and returns
    /// the number of rows affected by the operation.
    ///
    /// Returns 0 if no rows matched the WHERE clause. Returns -1 for DDL statements
    /// (CREATE TABLE, etc.) which is normal SQL Server behaviour.
    ///
    /// Use cases in tests:
    ///   - INSERT: seed a specific user or record before a test
    ///   - DELETE: clean up test data created during a test run
    ///   - UPDATE: put an entity into a specific state (e.g., mark an account as locked)
    /// </summary>
    public static async Task<int> ExecuteNonQueryAsync(
        string sql,
        Dictionary<string, object?>? parameters = null)
    {
        await using var conn = new MySqlConnection(BuildConnectionString());
        await conn.OpenAsync();

        await using var cmd = new MySqlCommand(sql, conn);

        // Same parameter handling as ExecuteQueryAsync — always parameterize values.
        if (parameters != null)
        {
            foreach (var (key, val) in parameters)
                cmd.Parameters.AddWithValue(key, val ?? DBNull.Value);
        }

        // ExecuteNonQueryAsync returns the affected row count and does not return
        // a result set, making it more efficient than ExecuteQueryAsync for writes.
        return await cmd.ExecuteNonQueryAsync();
    }
}
