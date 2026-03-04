/**
 * datadog_reporter.ts — TypeScript port of the Python GAUGE reporter.
 *
 * Sends four GAUGE metrics to the DataDog v2 HTTP API at suite finish:
 *   test.suite.passed, test.suite.failed, test.suite.skipped, test.suite.duration_ms
 *
 * Tags: framework:cypress, service:qa-automation-portfolio, env:ci
 *
 * Skips gracefully (prints [WARN], never throws) when DD_API_KEY is absent.
 */

interface MetricSeries {
  metric: string;
  type: 3; // 3 = GAUGE
  points: Array<{ timestamp: number; value: number }>;
  tags: string[];
}

interface MetricPayload {
  series: MetricSeries[];
}

function buildSeries(
  name: string,
  value: number,
  tags: string[],
): MetricSeries {
  return {
    metric: name,
    type: 3,
    points: [{ timestamp: Math.floor(Date.now() / 1000), value }],
    tags,
  };
}

export async function sendTestMetrics(
  passed: number,
  failed: number,
  skipped: number,
  durationMs: number,
  framework = 'cypress',
): Promise<void> {
  const apiKey = process.env['DD_API_KEY'];
  if (!apiKey) {
    console.warn(
      '[WARN] DD_API_KEY not set — skipping DataDog metrics submission.',
    );
    return;
  }

  const site = process.env['DD_SITE'] ?? 'datadoghq.com';
  const url = `https://api.${site}/api/v2/series`;

  const tags = [
    `framework:${framework}`,
    'service:qa-automation-portfolio',
    'env:ci',
  ];

  const payload: MetricPayload = {
    series: [
      buildSeries('test.suite.passed', passed, tags),
      buildSeries('test.suite.failed', failed, tags),
      buildSeries('test.suite.skipped', skipped, tags),
      buildSeries('test.suite.duration_ms', durationMs, tags),
    ],
  };

  try {
    const { default: fetch } = await import('node-fetch');
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
      console.warn(
        `[WARN] DataDog metrics submission failed: ${response.status} ${body}`,
      );
    } else {
      console.log(
        `[INFO] DataDog metrics sent — passed=${passed} failed=${failed} skipped=${skipped} duration=${durationMs}ms`,
      );
    }
  } catch (err) {
    console.warn('[WARN] DataDog metrics submission error:', err);
  }
}
