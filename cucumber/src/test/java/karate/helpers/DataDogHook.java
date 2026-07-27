package karate.helpers;

import com.saucedemo.utils.DataDogUtils;
import com.intuit.karate.Results;

/**
 * Karate-specific DataDog integration hook.
 *
 * <p>Reuses the existing {@link DataDogUtils#sendTestMetrics} method to post
 * suite-level GAUGE metrics after a Karate parallel run completes. Called
 * from CI scripts or can be invoked programmatically after {@code Runner.path(...).parallel()}.
 *
 * <p>Metrics are tagged with {@code framework:karate} to distinguish them from
 * Cucumber metrics on the shared DataDog dashboard.
 */
public class DataDogHook {

    private DataDogHook() {
        // utility class
    }

    /**
     * Sends Karate suite metrics to DataDog.
     *
     * @param results the {@link Results} object returned by Karate's parallel runner
     */
    public static void sendKarateMetrics(Results results) {
        int passed = results.getScenariosPassed();
        int failed = results.getScenariosFailed();
        int total = passed + failed;
        long durationMs = Double.valueOf(results.getElapsedTime()).longValue();

        DataDogUtils.sendTestMetrics(passed, failed, total - passed - failed, durationMs, "karate");
    }
}
