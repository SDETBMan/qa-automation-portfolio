package com.framework.utils;

import io.restassured.RestAssured;
import io.restassured.response.Response;

import java.io.File;

/**
 * BrowserStackUtils: Manages mobile app uploads to the BrowserStack App-Automate cloud.
 * Demonstrates proficiency in REST API automation using Rest Assured.
 */
public class BrowserStackUtils {

    private static final String UPLOAD_URL = "https://api-cloud.browserstack.com/app-automate/upload";

    public static void main(String[] args) {

        // Skip logic for local or Sauce Labs execution
        if (System.getProperty("skipAppUpload") != null) {
            System.out.println("[INFO] Skipping app upload as requested via system property.");
            return;
        }

        String androidPath = "src/test/resources/apps/Android.SauceLabs.Mobile.Sample.app.2.7.1.apk";
        String iosPath = "src/test/resources/apps/iOS.RealDevice.SauceLabs.Mobile.Sample.app.2.7.1.ipa";

        System.out.println("[INFO] Initiating dual app upload to BrowserStack...");

        String user = getUsername();
        String key = getAccessKey();

        if (user == null || key == null) {
            System.err.println("[FATAL] BrowserStack credentials missing. Check environment variables.");
            return;
        }

        // Uploading both platforms
        String androidAppId = ConfigReader.getProperty("browserstack.android.app.id", "QA_Director_Android_Build");
        String iosAppId     = ConfigReader.getProperty("browserstack.ios.app.id",     "QA_Director_iOS_Build");
        uploadAppIfExists(androidPath, androidAppId, user, key);
        uploadAppIfExists(iosPath, iosAppId, user, key);

        System.out.println("[INFO] Upload process finalized.");
    }

    /**
     * Uploads the specified file to the BrowserStack API if it exists locally.
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
                    .auth().preemptive().basic(user, key)
                    .header("Content-Type", "multipart/form-data")
                    .multiPart("file", appFile)
                    .multiPart("custom_id", customId)
                    .post(UPLOAD_URL);

            if (response.getStatusCode() == 200) {
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

    private static String getUsername() {
        String val = System.getenv("BROWSERSTACK_USERNAME");
        if (val == null) val = ConfigReader.getProperty("cloud_username");
        return (val != null) ? val.trim() : null;
    }

    private static String getAccessKey() {
        String val = System.getenv("BROWSERSTACK_ACCESS_KEY");
        if (val == null) val = ConfigReader.getProperty("cloud_key");
        return (val != null) ? val.trim() : null;
    }
}

