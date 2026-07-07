// ──────────────────────────────────────────────────────────────────────────────
// datadog-summary.js — Post k6 SLO results to DataDog
//
// Imported by load-test.js in handleSummary(). Sends SLO pass/fail results
// as GAUGE metrics via the DataDog v2 HTTP API.
//
// Metrics:
//   k6.slo.pass       — 1 (pass) or 0 (fail) per scenario
//   k6.slo.margin_ms  — headroom in ms (actual vs threshold)
//   k6.slo.error_rate — actual error rate per scenario
//
// Graceful skip when __ENV.DD_API_KEY is absent.
// ──────────────────────────────────────────────────────────────────────────────

import http from 'k6/http';

const DD_TAGS = ['service:qa-automation-portfolio', 'env:ci'];

/**
 * Build a DataDog GAUGE metric payload.
 */
function gauge(metric, value, tags) {
  return {
    metric: metric,
    type: 3,
    points: [{ timestamp: Math.floor(Date.now() / 1000), value: value }],
    tags: tags,
  };
}

/**
 * Send SLO results to DataDog.
 *
 * @param {Array<Object>} sloResults — array of { scenario, passed, p95_actual, p95_target, error_rate }
 */
export function sendToDataDog(sloResults) {
  const apiKey = __ENV.DD_API_KEY;
  if (!apiKey) {
    console.log('[WARN] DD_API_KEY not set. Skipping DataDog SLO metrics.');
    return;
  }

  const site = __ENV.DD_SITE || 'datadoghq.com';
  const url = `https://api.${site}/api/v2/series`;

  const series = [];

  for (const r of sloResults) {
    const tags = [...DD_TAGS, `scenario:${r.scenario}`];

    series.push(gauge('k6.slo.pass', r.passed ? 1 : 0, tags));
    series.push(gauge('k6.slo.margin_ms', r.p95_target - r.p95_actual, tags));
    series.push(gauge('k6.slo.error_rate', r.error_rate, tags));
  }

  const res = http.post(url, JSON.stringify({ series: series }), {
    headers: {
      'DD-API-KEY': apiKey,
      'Content-Type': 'application/json',
    },
    timeout: '10s',
  });

  if (res.status === 200 || res.status === 202) {
    console.log('[INFO] DataDog SLO metrics sent successfully.');
  } else {
    console.log(`[WARN] DataDog SLO metrics returned HTTP ${res.status}.`);
  }
}
