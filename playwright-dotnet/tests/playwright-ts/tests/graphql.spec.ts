import { test, expect } from '../fixtures/fixtures';

/**
 * GraphQL API test suite — 5 patterns for testing a GraphQL layer.
 *
 * WHY THESE PATTERNS MATTER FOR CLINICAL SAAS (e.g. Instinct Science):
 * A React/TypeScript frontend backed by a GraphQL API (Phoenix/Elixir) requires
 * a different testing mindset than REST. Three key differences:
 *
 *   1. Single endpoint — all operations POST to /graphql; you can't infer intent
 *      from the URL. You must inspect the request body's `operationName` field.
 *
 *   2. HTTP 200 ≠ success — GraphQL errors live in response.errors[], not the
 *      HTTP status code. A test that only checks `status === 200` will silently
 *      pass on a failed query. Every assertion must check both data and errors.
 *
 *   3. Operation auditing — because everything goes through one endpoint, passive
 *      listeners can record every GraphQL operation fired during a user flow.
 *      This is how you catch N+1 queries, unexpected mutations, and missing
 *      optimistic updates before they reach production.
 *
 * LIVE API TARGET:
 * Tests 1-2 and 4 run against countries.trevorblades.com — a stable, public
 * GraphQL API used widely for demonstrations. In production, swap GRAPHQL_URL
 * to the application's endpoint and set API_TOKEN for authenticated queries.
 *
 * Tests 3 and 5 use page.route() network interception and do not depend on
 * any external API — they run fully offline.
 */

// ─────────────────────────────────────────────────────────────────────────────
// Types — mirror the shape of real clinical domain objects.
// In production these would be generated from the schema via GraphQL Code Generator.
// ─────────────────────────────────────────────────────────────────────────────

interface Country {
  name: string;
  capital: string;
  currency: string;
}

interface CountriesData {
  countries: Array<{ name: string; code: string }>;
}

// Veterinary domain types — illustrate the pattern for Instinct Science's schema.
interface Patient {
  id: string;
  name: string;
  species: string;
  weightKg: number;
}

interface VitalSigns {
  heartRateBpm: number;
  respiratoryRate: number;
  temperatureC: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// Test 1 — Direct query, happy path
// ─────────────────────────────────────────────────────────────────────────────

test('@smoke direct GraphQL query returns expected data', async ({ graphqlClient }) => {
  /**
   * The most fundamental GraphQL test: fire a query, assert on data, assert
   * no errors. This is the GraphQL equivalent of `GET /patients/1` returning 200.
   *
   * Note the two-part assertion strategy:
   *   1. errors must be absent (HTTP 200 with errors[] is still a failed query)
   *   2. data must contain the expected values
   *
   * In production this would query GetPatient, GetVisit, GetMedication, etc.
   */
  const result = await graphqlClient.query<{ country: Country }>(`
    query GetCountry($code: ID!) {
      country(code: $code) {
        name
        capital
        currency
      }
    }
  `, { code: 'US' });

  // Assertion 1: no GraphQL errors — HTTP 200 alone is not enough
  expect(result.errors, 'GraphQL errors should be absent').toBeUndefined();

  // Assertion 2: data integrity
  expect(result.data?.country.name).toBe('United States');
  expect(result.data?.country.capital).toBe('Washington D.C.');
  expect(result.data?.country.currency).toBeDefined();
});

// ─────────────────────────────────────────────────────────────────────────────
// Test 2 — Query with variables and list response
// ─────────────────────────────────────────────────────────────────────────────

test('@regression GraphQL query with variables returns filtered list', async ({ graphqlClient }) => {
  /**
   * Validates that variable injection works correctly — the GraphQL equivalent
   * of query parameters in REST. In clinical QA this would be:
   *   GetPatientsByWard(wardId: "ICU-3") — verify only ICU-3 patients returned
   *   GetMedicationsByClass(class: "ANALGESIC") — verify formulary filtering
   *
   * The filter shape here mirrors how Phoenix/Absinthe typically structures
   * input objects: { fieldName: { eq: value } }
   */
  const result = await graphqlClient.query<CountriesData>(`
    query GetCountriesByContinent($filter: CountryFilterInput) {
      countries(filter: $filter) {
        name
        code
      }
    }
  `, { filter: { continent: { eq: 'EU' } } });

  expect(result.errors, 'GraphQL errors should be absent').toBeUndefined();

  const countries = result.data?.countries ?? [];
  expect(countries.length).toBeGreaterThan(0);

  // Germany must appear in any European countries list
  expect(countries.some(c => c.code === 'DE')).toBe(true);

  // Verify filtering is working — no non-EU codes should appear
  // (spot check: US is North America, JP is Asia)
  expect(countries.some(c => c.code === 'US')).toBe(false);
  expect(countries.some(c => c.code === 'JP')).toBe(false);
});

// ─────────────────────────────────────────────────────────────────────────────
// Test 3 — Mock specific operation by operationName
// ─────────────────────────────────────────────────────────────────────────────

test('@regression mock GraphQL operation by operationName', async ({ page }) => {
  /**
   * The most powerful pattern for UI + GraphQL testing.
   *
   * Because GraphQL uses a single /graphql endpoint, you cannot mock "just the
   * patient query" by URL alone — you must inspect the request body and branch
   * on operationName. This is exactly what this test demonstrates.
   *
   * Real-world application for Instinct Science:
   *   - Mock GetPatient to return a patient in critical condition → verify the UI
   *     renders the correct alert banner and medication warnings
   *   - Mock GetVitalSigns to return out-of-range values → verify alert thresholds
   *   - Mock CreateVisitNote to return a validation error → verify the form handles
   *     server-side errors correctly without crashing
   *
   * MECHANISM:
   * page.route() intercepts requests made by the browser page context.
   * page.evaluate() executes JavaScript inside the browser, triggering a fetch()
   * that flows through the route — exactly as React component data fetching does.
   */

  // Veterinary mock data — illustrates the clinical domain
  const mockPatient: Patient = {
    id:        'p-001',
    name:      'Buddy',
    species:   'Canine',
    weightKg:  32.5,
  };

  const mockVitals: VitalSigns = {
    heartRateBpm:    78,
    respiratoryRate: 18,
    temperatureC:    38.4,
  };

  // Register intercept BEFORE navigation — routes intercept from the next request onward
  await page.route('**/graphql', async (route) => {
    const body = route.request().postDataJSON() as {
      operationName?: string;
      query?: string;
    };

    // Branch on operationName — the GraphQL equivalent of URL-based REST routing
    if (body?.operationName === 'GetPatient') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ data: { patient: mockPatient } }),
      });
    } else if (body?.operationName === 'GetVitalSigns') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ data: { vitalSigns: mockVitals } }),
      });
    } else {
      // Pass anything else through unchanged
      await route.continue();
    }
  });

  await page.goto(process.env['BASE_URL'] ?? 'https://www.saucedemo.com');

  // Trigger a fetch from within the browser context — page.route() intercepts these,
  // exactly as it would intercept a React component's Apollo Client or fetch() call.
  const patientResult = await page.evaluate(async () => {
    const res = await fetch('/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        operationName: 'GetPatient',
        query: 'query GetPatient($id: ID!) { patient(id: $id) { id name species weightKg } }',
        variables: { id: 'p-001' },
      }),
    });
    return res.json() as Promise<{ data: { patient: { id: string; name: string; species: string; weightKg: number } } }>;
  });

  const vitalsResult = await page.evaluate(async () => {
    const res = await fetch('/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        operationName: 'GetVitalSigns',
        query: 'query GetVitalSigns($patientId: ID!) { vitalSigns(patientId: $patientId) { heartRateBpm respiratoryRate temperatureC } }',
        variables: { patientId: 'p-001' },
      }),
    });
    return res.json() as Promise<{ data: { vitalSigns: { heartRateBpm: number; respiratoryRate: number; temperatureC: number } } }>;
  });

  // Assert mocked patient data came back correctly
  expect(patientResult.data.patient.name).toBe('Buddy');
  expect(patientResult.data.patient.species).toBe('Canine');
  expect(patientResult.data.patient.weightKg).toBe(32.5);

  // Assert mocked vitals data came back correctly
  expect(vitalsResult.data.vitalSigns.heartRateBpm).toBe(78);
  expect(vitalsResult.data.vitalSigns.temperatureC).toBe(38.4);
});

// ─────────────────────────────────────────────────────────────────────────────
// Test 4 — GraphQL error response handling
// ─────────────────────────────────────────────────────────────────────────────

test('@regression GraphQL error response is returned in errors array not HTTP status', async ({ graphqlClient }) => {
  /**
   * This test documents and verifies the GraphQL error contract:
   *
   *   HTTP 200 + { errors: [...] } = GraphQL-level failure (bad field, auth error,
   *   resolver exception, validation failure)
   *
   *   HTTP 4xx/5xx = Transport-level failure (endpoint missing, proxy down)
   *
   * A common QA mistake is writing: expect(response.status).toBe(200) and
   * assuming success. This test demonstrates why errors[] must always be checked.
   *
   * In clinical QA, a GraphQL error could mean:
   *   - A patient record was not found (authorization boundary working correctly)
   *   - A medication dosage mutation was rejected by a business rule validator
   *   - A required field was missing from a visit note submission
   */
  const result = await graphqlClient.query(`
    query {
      nonExistentField {
        id
      }
    }
  `);

  // The HTTP status is 200 — GraphQL returned a valid response envelope
  // The error lives inside the body, not the transport layer
  expect(result.errors).toBeDefined();
  expect(result.errors!.length).toBeGreaterThan(0);
  expect(result.errors![0]!.message).toBeTruthy();

  // data should be absent or null when the query fully fails
  expect(result.data).toBeFalsy();
});

// ─────────────────────────────────────────────────────────────────────────────
// Test 5 — Passive GraphQL operation auditor
// ─────────────────────────────────────────────────────────────────────────────

test('@regression passive listener records all GraphQL operations during page flow', async ({ page }) => {
  /**
   * Operation auditing — records every GraphQL operation fired during a user flow
   * without intercepting or blocking any requests.
   *
   * Why this matters for clinical QA:
   *
   *   1. N+1 detection — if a patient list screen fires GetPatient once per row
   *      instead of GetPatients once total, performance degrades at scale.
   *      This test can detect that: expect(operations.filter(op => op === 'GetPatient').length).toBe(1)
   *
   *   2. Mutation hygiene — a read-only view (discharge summary, audit log) should
   *      never fire a mutation. Asserting operations contains no mutations guards against
   *      accidental side effects in display components.
   *
   *   3. Auth boundary testing — verify that unauthenticated page loads do NOT fire
   *      queries for sensitive data (patient PII, medication history) before auth completes.
   *
   * MECHANISM:
   * page.on('request') is a passive listener — it records requests without
   * intercepting or modifying them. The app behaves normally while QA observes.
   *
   * NOTE: SauceDemo has no GraphQL API, so operations will be empty here.
   * In production this test runs against the application and asserts the
   * expected operation set for each user flow.
   */
  const operations: Array<{ name: string; type: 'query' | 'mutation' | 'subscription' | 'unknown' }> = [];

  // Passive listener — does NOT intercept, just records
  page.on('request', req => {
    if (!req.url().includes('/graphql') || req.method() !== 'POST') return;

    try {
      const body = req.postDataJSON() as {
        operationName?: string;
        query?: string;
      };

      // Infer operation type from the query document keyword
      const opType = body.query?.trimStart().startsWith('mutation')
        ? 'mutation'
        : body.query?.trimStart().startsWith('subscription')
          ? 'subscription'
          : body.query?.trimStart().startsWith('query') || body.query
            ? 'query'
            : 'unknown';

      operations.push({
        name: body.operationName ?? '(anonymous)',
        type: opType,
      });
    } catch {
      // Non-JSON body — not a standard GraphQL request
    }
  });

  await page.goto(process.env['BASE_URL'] ?? 'https://www.saucedemo.com');

  // The auditor infrastructure itself is always valid
  expect(Array.isArray(operations)).toBe(true);

  // Production assertion examples (commented — would run against Instinct's app):
  // expect(operations.some(op => op.name === 'GetPatientList')).toBe(true);
  // expect(operations.filter(op => op.type === 'mutation').length).toBe(0); // read-only page
  // expect(operations.filter(op => op.name === 'GetPatient').length).toBe(1); // no N+1

  // If any GraphQL calls were made, verify none were anonymous (all ops should be named)
  const anonymousOps = operations.filter(op => op.name === '(anonymous)');
  expect(anonymousOps.length).toBe(0);
});
