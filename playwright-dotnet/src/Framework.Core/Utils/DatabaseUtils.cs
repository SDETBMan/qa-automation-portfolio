using MySqlConnector;
using Framework.Core.Config;

namespace Framework.Core.Utils;

/// <summary>
/// Async-first MySQL helper using MySqlConnector (ADO.NET).
/// Configure <c>db:url</c>, <c>db:user</c>, and <c>db:password</c> in appsettings.json.
/// </summary>
public static class DatabaseUtils
{
    private static string BuildConnectionString()
    {
        // db:url is stored as a JDBC-style URL; extract host/port/db from it or use raw host.
        string dbUrl  = ConfigReader.GetProperty("db:url", "localhost");
        string user   = ConfigReader.GetProperty("db:user", "root");
        string pass   = ConfigReader.GetProperty("db:password", "");

        // Support plain "host:port/db" or full JDBC "jdbc:mysql://host:port/db"
        string cleaned = dbUrl.Replace("jdbc:mysql://", "");
        return $"Server={cleaned};User ID={user};Password={pass};";
    }

    /// <summary>
    /// Executes a SELECT query and returns all rows as a list of dictionaries.
    /// </summary>
    public static async Task<List<Dictionary<string, object?>>> ExecuteQueryAsync(
        string sql,
        Dictionary<string, object?>? parameters = null)
    {
        var results = new List<Dictionary<string, object?>>();

        await using var conn = new MySqlConnection(BuildConnectionString());
        await conn.OpenAsync();

        await using var cmd = new MySqlCommand(sql, conn);
        if (parameters != null)
        {
            foreach (var (key, val) in parameters)
                cmd.Parameters.AddWithValue(key, val ?? DBNull.Value);
        }

        await using var reader = await cmd.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            var row = new Dictionary<string, object?>();
            for (int i = 0; i < reader.FieldCount; i++)
                row[reader.GetName(i)] = reader.IsDBNull(i) ? null : reader.GetValue(i);
            results.Add(row);
        }

        return results;
    }

    /// <summary>Executes a non-query (INSERT/UPDATE/DELETE) and returns affected row count.</summary>
    public static async Task<int> ExecuteNonQueryAsync(
        string sql,
        Dictionary<string, object?>? parameters = null)
    {
        await using var conn = new MySqlConnection(BuildConnectionString());
        await conn.OpenAsync();

        await using var cmd = new MySqlCommand(sql, conn);
        if (parameters != null)
        {
            foreach (var (key, val) in parameters)
                cmd.Parameters.AddWithValue(key, val ?? DBNull.Value);
        }

        return await cmd.ExecuteNonQueryAsync();
    }
}
