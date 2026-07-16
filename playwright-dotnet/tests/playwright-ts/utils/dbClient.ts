import { createPool, Pool, PoolOptions, RowDataPacket, ResultSetHeader } from 'mysql2/promise';
import pg from 'pg';

/**
 * Async database client for test automation — TypeScript equivalent of C# DatabaseUtils.cs.
 *
 * Supports MySQL (via mysql2/promise) and PostgreSQL (via pg) with parameterized queries.
 * Connection config is read from environment variables so CI and local runs can target
 * different databases without code changes.
 *
 * Environment variables:
 *   DB_TYPE     — "mysql" (default) or "postgres"
 *   DB_HOST     — database hostname (default: "localhost")
 *   DB_PORT     — port number (default: 3306 for MySQL, 5432 for Postgres)
 *   DB_NAME     — database / schema name (default: "testdb")
 *   DB_USER     — username (default: "root")
 *   DB_PASSWORD — password (default: "")
 *
 * Why connection pooling: Even though tests are short-lived, parallel test workers can
 * open many simultaneous connections. A pool caps concurrency and reuses connections,
 * preventing "too many connections" errors on shared CI databases.
 *
 * Why parameterized queries: Prevents SQL injection — even in test code, because test
 * databases sometimes mirror production schemas and can contain sensitive data.
 */

/** Shape returned by executeQuery — each row is a plain key/value object. */
export type DbRow = Record<string, unknown>;

/** Supported database engines. */
export type DbType = 'mysql' | 'postgres';

interface DbConfig {
  type: DbType;
  host: string;
  port: number;
  database: string;
  user: string;
  password: string;
}

function readConfig(): DbConfig {
  const type = (process.env['DB_TYPE'] ?? 'mysql') as DbType;
  return {
    type,
    host: process.env['DB_HOST'] ?? 'localhost',
    port: Number(process.env['DB_PORT'] ?? (type === 'postgres' ? 5432 : 3306)),
    database: process.env['DB_NAME'] ?? 'testdb',
    user: process.env['DB_USER'] ?? 'root',
    password: process.env['DB_PASSWORD'] ?? '',
  };
}

/**
 * DbClient wraps a connection pool and exposes two methods mirroring
 * the C# DatabaseUtils API:
 *   - executeQuery(sql, params?)  → SELECT → DbRow[]
 *   - executeNonQuery(sql, params?) → INSERT/UPDATE/DELETE → affected row count
 *
 * Worker-scoped via the `dbClient` fixture (see fixtures.ts) — one instance per
 * worker process, shared across all tests in that worker. The fixture teardown
 * calls `close()` when the worker shuts down to release pool connections cleanly.
 */
export class DbClient {
  private mysqlPool: Pool | null = null;
  private pgPool: pg.Pool | null = null;
  private readonly config: DbConfig;

  constructor(config?: Partial<DbConfig>) {
    const envConfig = readConfig();
    this.config = { ...envConfig, ...config };
  }

  /** Lazy-initialise the MySQL connection pool. */
  private getMysqlPool(): Pool {
    if (!this.mysqlPool) {
      const opts: PoolOptions = {
        host: this.config.host,
        port: this.config.port,
        database: this.config.database,
        user: this.config.user,
        password: this.config.password,
        waitForConnections: true,
        connectionLimit: 5,
        queueLimit: 0,
      };
      this.mysqlPool = createPool(opts);
    }
    return this.mysqlPool;
  }

  /** Lazy-initialise the PostgreSQL connection pool. */
  private getPgPool(): pg.Pool {
    if (!this.pgPool) {
      this.pgPool = new pg.Pool({
        host: this.config.host,
        port: this.config.port,
        database: this.config.database,
        user: this.config.user,
        password: this.config.password,
        max: 5,
      });
    }
    return this.pgPool;
  }

  /**
   * Execute a SELECT query and return all matching rows.
   *
   * @param sql    — SQL query string with parameter placeholders:
   *                 MySQL: `?` positional (e.g., `WHERE id = ?`)
   *                 Postgres: `$1, $2` positional (e.g., `WHERE id = $1`)
   * @param params — Array of parameter values matching the placeholders in order.
   *
   * @returns Array of plain objects where keys are column names.
   *
   * Example (MySQL):
   *   const rows = await db.executeQuery(
   *     'SELECT email, name FROM users WHERE status = ?',
   *     ['active']
   *   );
   *
   * Example (Postgres):
   *   const rows = await db.executeQuery(
   *     'SELECT email, name FROM users WHERE status = $1',
   *     ['active']
   *   );
   */
  async executeQuery(sql: string, params?: unknown[]): Promise<DbRow[]> {
    if (this.config.type === 'postgres') {
      const pool = this.getPgPool();
      const result = await pool.query(sql, params);
      return result.rows as DbRow[];
    }

    const pool = this.getMysqlPool();
    const [rows] = await pool.execute<RowDataPacket[]>(sql, params);
    return rows as DbRow[];
  }

  /**
   * Execute an INSERT, UPDATE, or DELETE statement and return the affected row count.
   *
   * @param sql    — SQL statement with parameter placeholders.
   * @param params — Array of parameter values.
   * @returns Number of rows affected (0 if no rows matched the WHERE clause).
   *
   * Example:
   *   const affected = await db.executeNonQuery(
   *     'UPDATE users SET status = ? WHERE id = ?',
   *     ['inactive', 42]
   *   );
   */
  async executeNonQuery(sql: string, params?: unknown[]): Promise<number> {
    if (this.config.type === 'postgres') {
      const pool = this.getPgPool();
      const result = await pool.query(sql, params);
      return result.rowCount ?? 0;
    }

    const pool = this.getMysqlPool();
    const [result] = await pool.execute<ResultSetHeader>(sql, params);
    return result.affectedRows;
  }

  /**
   * Execute a SELECT that returns a single scalar value (first column of first row).
   * Convenient for COUNT(*), MAX(), or single-field lookups.
   *
   * @returns The scalar value, or null if the query returned no rows.
   *
   * Example:
   *   const count = await db.executeScalar<number>('SELECT COUNT(*) FROM orders WHERE user_id = ?', [42]);
   */
  async executeScalar<T = unknown>(sql: string, params?: unknown[]): Promise<T | null> {
    const rows = await this.executeQuery(sql, params);
    if (rows.length === 0) return null;
    const firstRow = rows[0];
    const keys = Object.keys(firstRow);
    if (keys.length === 0) return null;
    return firstRow[keys[0]] as T;
  }

  /** Close all pool connections. Call in fixture teardown. */
  async close(): Promise<void> {
    await this.mysqlPool?.end();
    await this.pgPool?.end();
    this.mysqlPool = null;
    this.pgPool = null;
  }
}
