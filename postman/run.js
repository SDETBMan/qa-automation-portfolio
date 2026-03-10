'use strict';

/**
 * run.js — Newman programmatic runner with DataDog CI metrics.
 *
 * Replaces the CLI `npm test` command so we can tap into Newman's summary
 * object after the run and ship test.suite.* GAUGE metrics to DataDog.
 *
 * Exit behaviour mirrors the Newman CLI:
 *   - exits 1 if Newman itself errors or any test assertion fails
 *   - exits 0 on a clean green run
 */

const newman = require('newman');
const { sendTestMetrics } = require('./utils/datadog_reporter');

newman.run(
  {
    collection:  require('./collections/jsonplaceholder.postman_collection.json'),
    environment: require('./environments/jsonplaceholder.postman_environment.json'),
    reporters:   ['cli', 'junit'],
    reporter: {
      junit: { export: 'results/newman-results.xml' },
    },
  },
  async (err, summary) => {
    if (err) {
      console.error('Newman encountered a fatal error:', err);
      process.exit(1);
    }

    const { stats, timings, failures } = summary.run;

    const passed     = stats.assertions.total - stats.assertions.failed;
    const failed     = stats.assertions.failed;
    const skipped    = 0; // Newman has no concept of skipped assertions
    const durationMs = timings.completed - timings.started;

    await sendTestMetrics(passed, failed, skipped, durationMs);

    if (failures.length > 0) {
      process.exit(1);
    }
  },
);
