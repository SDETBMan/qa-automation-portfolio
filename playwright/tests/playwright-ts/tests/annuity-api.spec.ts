/**
 * annuity-api.spec.ts — MYGA annuity domain API tests.
 *
 * Demonstrates:
 *  - Insurance-domain fluency (MYGA annuity lifecycle)
 *  - Typed API client pattern (AnnuityClient wrapping APIRequestContext)
 *  - Integer cents invariant (no IEEE 754 float contamination)
 *  - Guaranteed minimum assertion (accrued >= principal)
 *  - Policy year vs calendar year distinction
 *  - API-setup-then-verify pattern (create → project → surrender)
 *  - Decimal math validation with hand-computed expected values
 *
 * Tags: @smoke for seed data, @regression for full coverage.
 */

import { test, expect } from '@playwright/test';
import {
  AnnuityClient,
  type AnnuityCreateRequest,
} from '../utils/annuityClient';

const FASTAPI_URL =
  process.env['FASTAPI_URL'] ?? 'http://localhost:8000';

/**
 * Helper: compute expected accrued value using the same formula as the server.
 * principal * (1 + rate/10000)^years, rounded to nearest integer.
 */
function expectedAccrued(
  principalCents: number,
  rateBps: number,
  years: number,
): number {
  const rate = rateBps / 10000;
  return Math.round(principalCents * Math.pow(1 + rate, years));
}

test.describe('MYGA Annuity API', () => {
  let client: AnnuityClient;

  test.beforeEach(async ({ request }) => {
    client = new AnnuityClient(request, FASTAPI_URL);
  });

  // ── Seed Data (@smoke) ──────────────────────────────────────────────

  test.describe('Seed data', () => {
    test('MYGA-001 exists with correct fields @smoke', async () => {
      const policy = await client.getPolicy('MYGA-001');
      expect(policy.policy_id).toBe('MYGA-001');
      expect(policy.principal_cents).toBe(10_000_000);
      expect(policy.rate_bps).toBe(450);
      expect(policy.term_years).toBe(5);
      expect(policy.effective_date).toBe('2023-01-15');
      expect(policy.maturity_date).toBe('2028-01-15');
      expect(policy.surrender_schedule_bps).toEqual([500, 400, 300, 200, 100]);
    });

    test('MYGA-002 exists with correct fields @smoke', async () => {
      const policy = await client.getPolicy('MYGA-002');
      expect(policy.principal_cents).toBe(25_000_000);
      expect(policy.rate_bps).toBe(525);
      expect(policy.term_years).toBe(7);
    });

    test('MYGA-003 exists with correct fields @smoke', async () => {
      const policy = await client.getPolicy('MYGA-003');
      expect(policy.principal_cents).toBe(5_000_000);
      expect(policy.rate_bps).toBe(375);
      expect(policy.term_years).toBe(3);
    });

    test('missing policy returns 404 @smoke', async () => {
      const response = await client.getRaw('/annuities/MYGA-999');
      expect(response.status()).toBe(404);
    });
  });

  // ── Create Policy (@regression) ─────────────────────────────────────

  test.describe('Create policy', () => {
    const validBody: AnnuityCreateRequest = {
      principal_cents: 20_000_000,
      rate_bps: 400,
      term_years: 5,
      effective_date: '2025-01-01',
      surrender_schedule_bps: [500, 400, 300, 200, 100],
    };

    test('POST returns 201 with policy_id @regression', async () => {
      const response = await client.postRaw('/annuities', validBody);
      expect(response.status()).toBe(201);
      const data = await response.json();
      expect(data.policy_id).toMatch(/^MYGA-/);
      expect(data.maturity_date).toBe('2030-01-01');
    });

    test('POST then GET round-trip @regression', async () => {
      const created = await client.createPolicy(validBody);
      const fetched = await client.getPolicy(created.policy_id);
      expect(fetched).toEqual(created);
    });

    test('invalid term (4 years) returns 422 @regression', async () => {
      const response = await client.postRaw('/annuities', {
        ...validBody,
        term_years: 4,
        surrender_schedule_bps: [500, 400, 300, 200],
      });
      expect(response.status()).toBe(422);
    });

    test('mismatched schedule length returns 422 @regression', async () => {
      const response = await client.postRaw('/annuities', {
        ...validBody,
        surrender_schedule_bps: [500, 400, 300], // length 3 != term 5
      });
      expect(response.status()).toBe(422);
    });

    test('negative principal returns 422 @regression', async () => {
      const response = await client.postRaw('/annuities', {
        ...validBody,
        principal_cents: -100,
      });
      expect(response.status()).toBe(422);
    });
  });

  // ── Accrual Projection (@regression) ────────────────────────────────

  test.describe('Accrual projection', () => {
    test('0 years: accrued equals principal @regression', async () => {
      const proj = await client.getProjection('MYGA-001', '2023-01-15');
      expect(proj.completed_years).toBe(0);
      expect(proj.accrued_value_cents).toBe(10_000_000);
      expect(proj.accrued_interest_cents).toBe(0);
    });

    test('1 year: $100k * 1.045 = $104,500 @regression', async () => {
      const proj = await client.getProjection('MYGA-001', '2024-01-15');
      expect(proj.completed_years).toBe(1);
      expect(proj.accrued_value_cents).toBe(
        expectedAccrued(10_000_000, 450, 1),
      );
      expect(proj.accrued_value_cents).toBe(10_450_000);
    });

    test('2 years: $100k * 1.045^2 @regression', async () => {
      const proj = await client.getProjection('MYGA-001', '2025-01-15');
      expect(proj.completed_years).toBe(2);
      expect(proj.accrued_value_cents).toBe(
        expectedAccrued(10_000_000, 450, 2),
      );
    });

    test('mid-year equals last anniversary (annual compounding) @regression', async () => {
      // 2024-07-01 is between anniversary 1 and 2
      const proj = await client.getProjection('MYGA-001', '2024-07-01');
      expect(proj.completed_years).toBe(1);
      expect(proj.accrued_value_cents).toBe(
        expectedAccrued(10_000_000, 450, 1),
      );
    });

    test('post-maturity caps at term @regression', async () => {
      // MYGA-001 matures 2028-01-15 (5yr). Query 2030 = 7 years elapsed.
      const proj = await client.getProjection('MYGA-001', '2030-01-15');
      expect(proj.completed_years).toBe(5); // capped
      expect(proj.accrued_value_cents).toBe(
        expectedAccrued(10_000_000, 450, 5),
      );
    });

    test('pre-effective date returns 400 @regression', async () => {
      const response = await client.getRaw(
        '/annuities/MYGA-001/projection?as_of_date=2022-12-31',
      );
      expect(response.status()).toBe(400);
    });
  });

  // ── Integer Cents Invariant (@regression) ───────────────────────────

  test.describe('Integer cents invariant', () => {
    test('projection money fields are integers @regression', async () => {
      const proj = await client.getProjection('MYGA-001', '2025-01-15');
      expect(Number.isInteger(proj.principal_cents)).toBe(true);
      expect(Number.isInteger(proj.accrued_interest_cents)).toBe(true);
      expect(Number.isInteger(proj.accrued_value_cents)).toBe(true);
    });

    test('surrender money fields are integers @regression', async () => {
      const surr = await client.getSurrender('MYGA-001', '2025-01-15');
      expect(Number.isInteger(surr.accrued_value_cents)).toBe(true);
      expect(Number.isInteger(surr.surrender_charge_cents)).toBe(true);
      expect(Number.isInteger(surr.free_withdrawal_cents)).toBe(true);
      expect(Number.isInteger(surr.surrender_value_cents)).toBe(true);
    });

    test('guaranteed minimum: accrued >= principal @regression', async () => {
      const proj = await client.getProjection('MYGA-001', '2025-01-15');
      expect(proj.accrued_value_cents).toBeGreaterThanOrEqual(
        proj.principal_cents,
      );
    });
  });

  // ── Surrender Value (@regression) ───────────────────────────────────

  test.describe('Surrender value', () => {
    test('policy year 1 charge lookup @regression', async () => {
      const surr = await client.getSurrender('MYGA-001', '2023-06-01');
      expect(surr.policy_year).toBe(1);
      expect(surr.surrender_charge_bps).toBe(500);
    });

    test('policy year 3 charge lookup @regression', async () => {
      const surr = await client.getSurrender('MYGA-001', '2025-06-01');
      expect(surr.policy_year).toBe(3);
      expect(surr.surrender_charge_bps).toBe(300);
    });

    test('post-term zero charge @regression', async () => {
      const surr = await client.getSurrender('MYGA-001', '2029-01-15');
      expect(surr.policy_year).toBeGreaterThan(5);
      expect(surr.surrender_charge_bps).toBe(0);
      expect(surr.surrender_charge_cents).toBe(0);
    });

    test('free withdrawal is 10% of accrued value @regression', async () => {
      const surr = await client.getSurrender('MYGA-001', '2024-01-15');
      const expectedFree = Math.round(surr.accrued_value_cents * 0.1);
      expect(surr.free_withdrawal_cents).toBe(expectedFree);
    });

    test('surrender_value = accrued - charge @regression', async () => {
      const surr = await client.getSurrender('MYGA-001', '2024-06-01');
      expect(surr.surrender_value_cents).toBe(
        surr.accrued_value_cents - surr.surrender_charge_cents,
      );
    });
  });

  // ── API-Setup-Then-Verify (@regression) ─────────────────────────────

  test.describe('API-setup-then-verify lifecycle', () => {
    test('create → project → verify accrual @regression', async () => {
      const created = await client.createPolicy({
        principal_cents: 15_000_000,
        rate_bps: 500,
        term_years: 5,
        effective_date: '2024-01-01',
        surrender_schedule_bps: [500, 400, 300, 200, 100],
      });

      const proj = await client.getProjection(created.policy_id, '2026-01-01');
      expect(proj.completed_years).toBe(2);
      expect(proj.accrued_value_cents).toBe(
        expectedAccrued(15_000_000, 500, 2),
      );
      expect(proj.accrued_value_cents).toBeGreaterThan(15_000_000);
    });

    test('surrender charge decreases over time @regression', async () => {
      const year1 = await client.getSurrender('MYGA-001', '2023-06-01');
      const year3 = await client.getSurrender('MYGA-001', '2025-06-01');
      const year5 = await client.getSurrender('MYGA-001', '2027-06-01');

      expect(year1.surrender_charge_bps).toBeGreaterThan(
        year3.surrender_charge_bps,
      );
      expect(year3.surrender_charge_bps).toBeGreaterThan(
        year5.surrender_charge_bps,
      );
    });
  });
});
