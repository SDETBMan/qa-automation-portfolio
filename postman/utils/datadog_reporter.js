/**
 * datadog_reporter.js — Newman DataDog GAUGE metric reporter.
 *
 * Sends four GAUGE metrics to the DataDog v2 HTTP API after a Newman run:
 *   test.suite.passed, test.suite.failed, test.suite.skipped, test.suite.duration_ms
 *
 * Tags: framework:postman-newman, service:qa-automation-portfolio, env:ci
 *
 * Skips gracefully (prints [WARN], never throws) when DD_API_KEY is absent.
 * Uses the global fetch available in Node 20+ — no extra dependencies needed.
 */

'use strict';

function buildSeries(name, value, tags) {
  return {
    metric: name,
    type: 3, // 3 = GAUGE
    points: [{ timestamp: Math.floor(Date.now() / 1000), value }],
    tags,
  };
}

async function sendTestMetrics(passed, failed, skipped, durationMs, framework = 'postman-newman') {
  const apiKey = process.env['DD_API_KEY'];
  if (!apiKey) {
    console.warn('[WARN] DD_API_KEY not set — skipping DataDog metrics submission.');
    return;
  }

  const site = process.env['DD_SITE'] ?? 'datadoghq.com';
  const url = `https://api.${site}/api/v2/series`;

  const tags = [
    `framework:${framework}`,
    'service:qa-automation-portfolio',
    'env:ci',
  ];

  const payload = {
    series: [
      buildSeries('test.suite.passed',      passed,     tags),
      buildSeries('test.suite.failed',      failed,     tags),
      buildSeries('test.suite.skipped',     skipped,    tags),
      buildSeries('test.suite.duration_ms', durationMs, tags),
    ],
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'DD-API-KEY': apiKey,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const body = await response.text();
      console.warn(`[WARN] DataDog metrics submission failed: ${response.status} ${body}`);
    } else {
      console.log(`[INFO] DataDog metrics sent — passed=${passed} failed=${failed} skipped=${skipped} duration=${durationMs}ms`);
    }
  } catch (err) {
    console.warn('[WARN] DataDog metrics submission error:', err);
  }
}

module.exports = { sendTestMetrics };
