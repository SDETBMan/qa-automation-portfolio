import { APIRequestContext } from '@playwright/test';

/**
 * Shape of every GraphQL HTTP response body.
 *
 * This interface captures a fundamental GraphQL contract that differs
 * from REST and is easy to miss when writing test assertions:
 *
 *   GraphQL ALWAYS returns HTTP 200 — even when the operation fails.
 *   Errors are reported inside response.errors[], not via HTTP status codes.
 *
 * A test that only checks `response.status() === 200` will silently pass
 * on a failed query. Always assert on `result.errors` and `result.data`.
 */
export interface GqlResponse<TData = Record<string, unknown>> {
  data?: TData;
  errors?: Array<{
    message: string;
    locations?: Array<{ line: number; column: number }>;
    path?: string[];
    extensions?: Record<string, unknown>;
  }>;
}

/**
 * GraphQLClient — typed HTTP client for GraphQL API testing.
 *
 * WHY THIS EXISTS:
 * GraphQL uses a single endpoint (POST /graphql) for every operation.
 * The only way to distinguish operations is by the JSON body:
 *   { query: string, operationName?: string, variables?: object }
 *
 * This class encapsulates that convention so test code stays readable.
 * Tests call client.query(gql, vars) rather than building POST bodies manually.
 *
 * ZERO NEW DEPENDENCIES:
 * Built on Playwright's built-in APIRequestContext (the `request` fixture
 * available in every test). Nothing to install beyond @playwright/test.
 *
 * AUTHENTICATION:
 * Pass headers via the constructor (e.g. Authorization: Bearer <token>).
 * The graphqlClient fixture in fixtures.ts injects API_TOKEN automatically
 * when set — individual tests never touch auth headers.
 *
 * IN PRODUCTION (e.g. Instinct Science):
 * Set GRAPHQL_URL to the application's GraphQL endpoint and API_TOKEN to
 * a valid session token. The fixture propagates both automatically.
 */
export class GraphQLClient {
  constructor(
    private readonly request: APIRequestContext,
    private readonly endpoint: string,
    private readonly headers: Record<string, string> = {},
  ) {}

  /**
   * Send a GraphQL query or mutation and return the parsed response body.
   *
   * @param query          GraphQL document string (query or mutation)
   * @param variables      Optional variables object matching the $var syntax in the document
   * @param operationName  Required when the document contains multiple named operations
   *
   * @throws Error if the HTTP layer returns a non-200 status (network failure,
   *         proxy error, missing endpoint). GraphQL-level errors are returned
   *         in result.errors[] and do NOT throw.
   */
  async query<TData = Record<string, unknown>>(
    query: string,
    variables?: Record<string, unknown>,
    operationName?: string,
  ): Promise<GqlResponse<TData>> {
    const response = await this.request.post(this.endpoint, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...this.headers,
      },
      data: {
        query,
        ...(variables   !== undefined && { variables }),
        ...(operationName !== undefined && { operationName }),
      },
    });

    // HTTP non-200 means the endpoint itself is broken (proxy error, auth wall,
    // missing route). Throw immediately — no GraphQL body to parse.
    if (!response.ok()) {
      throw new Error(
        `GraphQL transport error: HTTP ${response.status()} from ${this.endpoint}. ` +
        `Body: ${await response.text()}`,
      );
    }

    return response.json() as Promise<GqlResponse<TData>>;
  }
}
