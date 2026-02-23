package com.framework.utils;

import io.restassured.RestAssured;
import io.restassured.response.Response;

import java.io.File;

/**
 * BrowserStackUtils: Uploads mobile app binaries to the BrowserStack cloud testing platform.
 *
 * WHY THIS CLASS EXISTS:
 * BrowserStack is a cloud service that provides real Android and iOS devices for mobile
 * app testing. To run tests on BrowserStack devices, the app binary (an .apk file for
 * Android, an .ipa file for iOS) must first be uploaded to BrowserStack's servers.
 * BrowserStack then returns a URL that can be used in Appium capabilities to reference
 * the uploaded app.
 *
 * WHAT IT DEMONSTRATES:
 *   1. REST API integration using Rest Assured (the same library used for API testing)
 *   2. Multipart form upload (how you send files over HTTP)
 *   3. Credential management via environment variables (secure, not hardcoded)
 *   4. Graceful handling of missing files (the app binary might not exist in all environments)
 *   5. Custom app ID tagging (BrowserStack "custom_id" lets you reference the app by name)
 *
 * THE main() METHOD:
 * This class includes a main() method so it can be run as a standalone Java program before
 * the test suite starts — for example, as a Maven "pre-integration-test" phase step or as
 * a manual setup step before a CI/CD pipeline triggers the tests.
 *
 * For recruiters: BrowserStack is used by major enterprises for cross-device mobile testing.
 * This utility class shows familiarity with cloud testing infrastructure and REST API usage
 * beyond just testing web applications.
 */
public class BrowserStackUtils {

    // The BrowserStack App-Automate upload endpoint. This is BrowserStack's public REST API
    // for uploading app binaries. The URL is constant — it doesn't change between users.
    private static final String UPLOAD_URL = "https://api-cloud.browserstack.com/app-automate/upload";

    /**
     * Entry point for running this utility as a standalone program before the test suite.
     *
     * WHY A SKIP PROPERTY:
     * The same Maven command might be used for both local browser testing (where no app upload
     * is needed) and mobile cloud testing (where an upload IS needed). Adding "-DskipAppUpload"
     * to the Maven command allows the upload to be skipped without modifying the code,
     * making the build pipeline more flexible.
     *
     * @param args Command-line arguments (not used; configuration comes from system properties)
     */
    public static void main(String[] args) {

        // Skip logic for local or Sauce Labs execution
        if (System.getProperty("skipAppUpload") != null) {
            System.out.println("[INFO] Skipping app upload as requested via system property.");
            return;
        }

        // Relative paths to the app binaries within the project structure.
        // These files are typically gitignored (they're large binaries) and downloaded
        // separately as part of the CI pipeline setup step.
        String androidPath = "src/test/resources/apps/Android.SauceLabs.Mobile.Sample.app.2.7.1.apk";
        String iosPath = "src/test/resources/apps/iOS.RealDevice.SauceLabs.Mobile.Sample.app.2.7.1.ipa";

        System.out.println("[INFO] Initiating dual app upload to BrowserStack...");

        String user = getUsername();
        String key = getAccessKey();

        if (user == null || key == null) {
            System.err.println("[FATAL] BrowserStack credentials missing. Check environment variables.");
            return;
        }

        // Custom IDs allow the uploaded apps to be referenced by name in test capabilities,
        // rather than by the auto-generated BrowserStack URL (which changes on every upload).
        String androidAppId = ConfigReader.getProperty("browserstack.android.app.id", "QA_Director_Android_Build");
        String iosAppId     = ConfigReader.getProperty("browserstack.ios.app.id",     "QA_Director_iOS_Build");
        uploadAppIfExists(androidPath, androidAppId, user, key);
        uploadAppIfExists(iosPath, iosAppId, user, key);

        System.out.println("[INFO] Upload process finalized.");
    }

    /**
     * Uploads a single app file to BrowserStack if the file exists on the local system.
     *
     * WHY CHECK FILE EXISTENCE FIRST:
     * In a portfolio or multi-developer environment, not every machine will have the app
     * binaries downloaded. Rather than crashing with a FileNotFoundException, we log a
     * warning and skip gracefully. This keeps the utility usable even when only one platform's
     * binary is available locally.
     *
     * HOW THE REST ASSURED MULTIPART UPLOAD WORKS:
     * Multipart form data is the HTTP standard for uploading files. The request has two parts:
     *   - "file": the binary content of the .apk or .ipa file
     *   - "custom_id": a text label assigned to this upload on BrowserStack's server
     * Rest Assured's .multiPart() method handles the multipart encoding automatically.
     * Basic authentication (username:accesskey) is required by BrowserStack's API.
     *
     * @param filePath The path to the app binary file on the local file system
     * @param customId The label to assign to this app on BrowserStack (for reference in tests)
     * @param user     The BrowserStack account username
     * @param key      The BrowserStack access key (API secret)
     */
    public static void uploadAppIfExists(String filePath, String customId, String user, String key) {
        File appFile = new File(filePath);
        if (!appFile.exists()) {
            System.out.println("[WARN] File not found: " + filePath);
            return;
        }

        System.out.println("[INFO] Uploading: " + appFile.getName() + " (ID: " + customId + ")");

        try {
            Response response = RestAssured.given()
                    .auth().preemptive().basic(user, key) // BrowserStack requires HTTP Basic Auth
                    .header("Content-Type", "multipart/form-data")
                    .multiPart("file", appFile)            // The binary file to upload
                    .multiPart("custom_id", customId)      // The reference name for this upload
                    .post(UPLOAD_URL);

            if (response.getStatusCode() == 200) {
                // BrowserStack returns the "app_url" (bs://...) that can be used in Appium capabilities
                String appUrl = response.jsonPath().getString("app_url");
                System.out.println("[SUCCESS] App uploaded. URL: " + appUrl);
            } else {
                System.err.println("[ERROR] Upload failed with status: " + response.getStatusCode());
                System.err.println("[DEBUG] Response body: " + response.getBody().asString());
            }
        } catch (Exception e) {
            System.err.println("[ERROR] Exception during API call: " + e.getMessage());
        }
    }

    /**
     * Retrieves the BrowserStack username from the environment or config file.
     *
     * WHY CHECK BOTH ENVIRONMENT VARIABLE AND CONFIG:
     * In CI/CD (GitHub Actions, Jenkins), credentials are injected as environment variables
     * (BROWSERSTACK_USERNAME) for security — they are never stored in files. In local
     * development, the developer may prefer to store credentials in config.properties to
     * avoid setting environment variables manually on their machine. Checking both sources
     * supports both workflows.
     *
     * @return The BrowserStack username, or null if not found in any source
     */
    private static String getUsername() {
        String val = System.getenv("BROWSERSTACK_USERNAME");
        if (val == null) val = ConfigReader.getProperty("cloud_username");
        return (val != null) ? val.trim() : null;
    }

    /**
     * Retrieves the BrowserStack access key from the environment or config file.
     *
     * WHY TRIM():
     * Environment variables and config file values sometimes contain trailing whitespace
     * (especially if copy-pasted). A key with trailing whitespace would cause all API
     * requests to fail with an authentication error that is hard to debug. Trimming here
     * prevents that class of bugs silently.
     *
     * @return The BrowserStack access key, or null if not found in any source
     */
    private static String getAccessKey() {
        String val = System.getenv("BROWSERSTACK_ACCESS_KEY");
        if (val == null) val = ConfigReader.getProperty("cloud_key");
        return (val != null) ? val.trim() : null;
    }
}
