// ──────────────────────────────────────────────────────────────────────────────
// k6 Load Test — fastapi-service
//
// Four scenarios exercising the FastAPI REST endpoints under load.
// Run locally:
//   cd fastapi-service
//   uvicorn app.main:app --port 8001 &
//   k6 run k6/load-test.js
//
// Override base URL:
//   k6 run -e BASE_URL=http://staging:8001 k6/load-test.js
//
// Export JSON results:
//   k6 run k6/load-test.js --out json=k6-results.json
// ──────────────────────────────────────────────────────────────────────────────

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Trend } from 'k6/metrics';

// ── Custom metrics (per-scenario p95/p99) ────────────────────────────────────
const healthDuration = new Trend('health_req_duration', true);
const readDuration   = new Trend('read_req_duration', true);
const crudDuration   = new Trend('crud_req_duration', true);

// ── Configuration ────────────────────────────────────────────────────────────
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8001';

// Seed data IDs matching fastapi-service's in-memory store
const PRODUCT_IDS = [1, 2, 3, 4, 5, 6];
const USER_IDS    = [1, 2, 3, 4, 5];

// Treat intentional 404s (error_handling scenario) as expected, not failures.
// Without this, GET /products/9999 would inflate http_req_failed.
http.setResponseCallback(http.expectedStatuses(200, 201, 204, 404));

// ── Thresholds ───────────────────────────────────────────────────────────────
export const options = {
  thresholds: {
    http_req_duration:     ['p(95)<200'],   // Global: 95th percentile < 200ms
    http_req_failed:       ['rate<0.05'],   // Global: < 5% failure rate
    checks:                ['rate>0.95'],   // Global: > 95% checks pass
    health_req_duration:   ['p(95)<100', 'p(99)<150'],
    read_req_duration:     ['p(95)<250', 'p(99)<350'],
    crud_req_duration:     ['p(95)<300', 'p(99)<500'],
  },

  // ── Scenarios ──────────────────────────────────────────────────────────────
  scenarios: {
    // 1. Baseline latency: single VU hitting /health for 30 seconds
    health_baseline: {
      executor:  'constant-vus',
      vus:       1,
      duration:  '30s',
      exec:      'healthBaseline',
      tags:      { scenario: 'health_baseline' },
    },

    // 2. Read-heavy traffic: ramp 0→10→10→0 VUs across products + users
    read_heavy: {
      executor: 'ramping-vus',
      stages: [
        { duration: '15s', target: 10 },  // ramp up
        { duration: '25s', target: 10 },  // sustain
        { duration: '15s', target: 0 },   // ramp down
      ],
      exec:       'readHeavy',
      startTime:  '5s',
      tags:       { scenario: 'read_heavy' },
    },

    // 3. CRUD workflow: 5 VUs each running 3 full create→read→update→delete cycles
    crud_workflow: {
      executor:     'per-vu-iterations',
      vus:          5,
      iterations:   3,
      exec:         'crudWorkflow',
      startTime:    '10s',
      tags:         { scenario: 'crud_workflow' },
    },

    // 4. Error handling: 2 VUs requesting invalid IDs for 20 seconds
    error_handling: {
      executor:  'constant-vus',
      vus:       2,
      duration:  '20s',
      exec:      'errorHandling',
      startTime: '5s',
      tags:      { scenario: 'error_handling' },
    },
  },
};

// ── Helpers ───────────────────────────────────────────────────────────────────
function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

const jsonHeaders = { headers: { 'Content-Type': 'application/json' } };

// ── Scenario Functions ───────────────────────────────────────────────────────

// Scenario 1: Health baseline
export function healthBaseline() {
  group('health_baseline', () => {
    const res = http.get(`${BASE_URL}/health`);
    healthDuration.add(res.timings.duration);
    check(res, {
      'health: status 200':       (r) => r.status === 200,
      'health: body has status':  (r) => r.json('status') !== undefined,
    });
  });
  sleep(0.5);
}

// Scenario 2: Read-heavy traffic
export function readHeavy() {
  group('read_products', () => {
    const listRes = http.get(`${BASE_URL}/products`);
    readDuration.add(listRes.timings.duration);
    check(listRes, {
      'products list: status 200': (r) => r.status === 200,
      'products list: is array':   (r) => Array.isArray(r.json()),
    });

    const id = pick(PRODUCT_IDS);
    const detailRes = http.get(`${BASE_URL}/products/${id}`);
    readDuration.add(detailRes.timings.duration);
    check(detailRes, {
      'product detail: status 200': (r) => r.status === 200,
      'product detail: has id':     (r) => r.json('id') === id,
    });
  });

  group('read_users', () => {
    const listRes = http.get(`${BASE_URL}/users`);
    readDuration.add(listRes.timings.duration);
    check(listRes, {
      'users list: status 200': (r) => r.status === 200,
      'users list: is array':   (r) => Array.isArray(r.json()),
    });

    const id = pick(USER_IDS);
    const detailRes = http.get(`${BASE_URL}/users/${id}`);
    readDuration.add(detailRes.timings.duration);
    check(detailRes, {
      'user detail: status 200': (r) => r.status === 200,
      'user detail: has id':     (r) => r.json('id') === id,
    });
  });

  sleep(0.5);
}

// Scenario 3: Full CRUD workflow on /products
export function crudWorkflow() {
  let createdId;

  group('crud_create', () => {
    const payload = JSON.stringify({
      name:        `k6-product-${Date.now()}-${__VU}`,
      description: 'Load test product',
      price:       19.99,
      image_url:   'https://example.com/img.png',
    });

    const res = http.post(`${BASE_URL}/products`, payload, jsonHeaders);
    crudDuration.add(res.timings.duration);
    check(res, {
      'create: status 201':  (r) => r.status === 201,
      'create: has id':      (r) => r.json('id') !== undefined,
    });
    createdId = res.json('id');
  });

  group('crud_read', () => {
    if (!createdId) return;
    const res = http.get(`${BASE_URL}/products/${createdId}`);
    crudDuration.add(res.timings.duration);
    check(res, {
      'read created: status 200': (r) => r.status === 200,
      'read created: id matches': (r) => r.json('id') === createdId,
    });
  });

  group('crud_update', () => {
    if (!createdId) return;
    const payload = JSON.stringify({
      name:        `k6-updated-${Date.now()}`,
      description: 'Updated by k6 load test',
      price:       29.99,
      image_url:   'https://example.com/updated.png',
    });

    const res = http.put(`${BASE_URL}/products/${createdId}`, payload, jsonHeaders);
    crudDuration.add(res.timings.duration);
    check(res, {
      'update: status 200':       (r) => r.status === 200,
      'update: price updated':    (r) => r.json('price') === 29.99,
    });
  });

  group('crud_delete', () => {
    if (!createdId) return;
    const res = http.del(`${BASE_URL}/products/${createdId}`);
    crudDuration.add(res.timings.duration);
    check(res, {
      'delete: status 204': (r) => r.status === 204,
    });

    // Confirm deletion
    const verify = http.get(`${BASE_URL}/products/${createdId}`);
    check(verify, {
      'delete verified: status 404': (r) => r.status === 404,
    });
  });

  sleep(1);
}

// Scenario 4: Error handling — intentional 404s for invalid IDs
export function errorHandling() {
  group('error_invalid_product', () => {
    const res = http.get(`${BASE_URL}/products/9999`);
    check(res, {
      'invalid product: status 404':   (r) => r.status === 404,
      'invalid product: has detail':   (r) => r.json('detail') !== undefined,
    });
  });

  group('error_invalid_user', () => {
    const res = http.get(`${BASE_URL}/users/9999`);
    check(res, {
      'invalid user: status 404':  (r) => r.status === 404,
      'invalid user: has detail':  (r) => r.json('detail') !== undefined,
    });
  });

  sleep(0.5);
}
