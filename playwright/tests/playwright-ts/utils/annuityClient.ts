import { APIRequestContext } from '@playwright/test';

/**
 * Typed interfaces for the MYGA annuity API.
 *
 * All monetary fields are integer cents — the same invariant enforced
 * by the FastAPI backend.  Tests assert Number.isInteger() on every
 * money field to catch IEEE 754 float contamination.
 */

export interface AnnuityPolicy {
  policy_id: string;
  principal_cents: number;
  rate_bps: number;
  term_years: number;
  effective_date: string;
  maturity_date: string;
  surrender_schedule_bps: number[];
}

export interface AnnuityCreateRequest {
  principal_cents: number;
  rate_bps: number;
  term_years: number;
  effective_date: string;
  surrender_schedule_bps: number[];
}

export interface AccrualProjection {
  policy_id: string;
  as_of_date: string;
  principal_cents: number;
  accrued_interest_cents: number;
  accrued_value_cents: number;
  completed_years: number;
}

export interface SurrenderQuote {
  policy_id: string;
  as_of_date: string;
  accrued_value_cents: number;
  policy_year: number;
  surrender_charge_bps: number;
  surrender_charge_cents: number;
  free_withdrawal_cents: number;
  surrender_value_cents: number;
}

/**
 * AnnuityClient — typed HTTP client for the MYGA annuity API.
 *
 * Built on Playwright's built-in APIRequestContext (the `request` fixture
 * available in every test).  Same pattern as graphqlClient.ts — zero
 * external dependencies beyond @playwright/test.
 *
 * Usage in tests:
 *   const client = new AnnuityClient(request, baseURL);
 *   const policy = await client.getPolicy('MYGA-001');
 */
export class AnnuityClient {
  constructor(
    private readonly request: APIRequestContext,
    private readonly baseURL: string,
  ) {}

  /** POST /annuities — create a new policy. */
  async createPolicy(body: AnnuityCreateRequest): Promise<AnnuityPolicy> {
    const response = await this.request.post(`${this.baseURL}/annuities`, {
      headers: { 'Content-Type': 'application/json' },
      data: body,
    });
    if (!response.ok()) {
      throw new Error(
        `POST /annuities failed: HTTP ${response.status()} — ${await response.text()}`,
      );
    }
    return response.json() as Promise<AnnuityPolicy>;
  }

  /** GET /annuities/{policyId} — retrieve a policy. */
  async getPolicy(policyId: string): Promise<AnnuityPolicy> {
    const response = await this.request.get(
      `${this.baseURL}/annuities/${policyId}`,
    );
    if (!response.ok()) {
      throw new Error(
        `GET /annuities/${policyId} failed: HTTP ${response.status()} — ${await response.text()}`,
      );
    }
    return response.json() as Promise<AnnuityPolicy>;
  }

  /** GET /annuities/{policyId}/projection?as_of_date=... */
  async getProjection(
    policyId: string,
    asOfDate: string,
  ): Promise<AccrualProjection> {
    const response = await this.request.get(
      `${this.baseURL}/annuities/${policyId}/projection`,
      { params: { as_of_date: asOfDate } },
    );
    if (!response.ok()) {
      throw new Error(
        `GET projection failed: HTTP ${response.status()} — ${await response.text()}`,
      );
    }
    return response.json() as Promise<AccrualProjection>;
  }

  /** GET /annuities/{policyId}/surrender?as_of_date=... */
  async getSurrender(
    policyId: string,
    asOfDate: string,
  ): Promise<SurrenderQuote> {
    const response = await this.request.get(
      `${this.baseURL}/annuities/${policyId}/surrender`,
      { params: { as_of_date: asOfDate } },
    );
    if (!response.ok()) {
      throw new Error(
        `GET surrender failed: HTTP ${response.status()} — ${await response.text()}`,
      );
    }
    return response.json() as Promise<SurrenderQuote>;
  }

  /** Raw GET — returns the full APIResponse for status code assertions. */
  async getRaw(path: string) {
    return this.request.get(`${this.baseURL}${path}`);
  }

  /** Raw POST — returns the full APIResponse for status code assertions. */
  async postRaw(path: string, data: unknown) {
    return this.request.post(`${this.baseURL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      data,
    });
  }
}
