package com.framework.utils;

import org.testng.IAnnotationTransformer;
import org.testng.annotations.ITestAnnotation;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;

/**
 * AnnotationTransformer: Automatically applies RetryAnalyzer to every test method at runtime.
 *
 * WHY THIS CLASS EXISTS — The Retry Problem:
 * TestNG's @Test annotation has a "retryAnalyzer" attribute that controls whether a failed
 * test should be re-run. Without this class, you would need to add that attribute to every
 * single test method in every test file:
 *   @Test(retryAnalyzer = RetryAnalyzer.class)
 * With hundreds of test methods, that is extremely repetitive. If you ever need to change
 * the retry class, you'd need to update every file.
 *
 * THE SOLUTION — IAnnotationTransformer:
 * TestNG's IAnnotationTransformer interface allows the framework to modify @Test annotations
 * programmatically at test startup, before any test runs. This class implements that interface
 * and automatically sets the retryAnalyzer on every @Test method — no annotation attribute
 * needed in any individual test file.
 *
 * HOW IT GETS ACTIVATED:
 * This class is registered in the TestNG XML configuration (testng.xml) as a "listener":
 *   <listeners>
 *     <listener class-name="com.framework.utils.AnnotationTransformer"/>
 *   </listeners>
 * TestNG then calls the transform() method for every @Test annotation it finds.
 *
 * THE UNIT TEST EXCEPTION:
 * Unit tests (tagged with group "unit") are deterministic — they test pure Java logic with
 * mock objects and always produce the same result. Retrying them on failure doesn't fix
 * anything and can actually cause issues (Mockito mock objects don't reset between
 * RetryAnalyzer-triggered re-runs). So unit tests are specifically excluded from retry.
 *
 * For recruiters: Implementing IAnnotationTransformer demonstrates advanced TestNG knowledge
 * beyond basic @Test usage — this is a senior-level framework design technique.
 */
public class AnnotationTransformer implements IAnnotationTransformer {

    /**
     * Called by TestNG once for every @Test method found in the test suite, before execution begins.
     *
     * WHY THE FOUR PARAMETERS:
     * TestNG passes all contextual information about the test so the transformer can make
     * fine-grained decisions. Here we only use "annotation" (to set the retryAnalyzer) and
     * the groups inside it (to skip unit tests). The testClass, testConstructor, and
     * testMethod parameters are available for more advanced scenarios like applying different
     * retry counts per package or per class.
     *
     * @param annotation       The @Test annotation being processed — we modify this object in place
     * @param testClass        The class containing the test (null for method-level annotations)
     * @param testConstructor  The constructor of the test class (rarely used)
     * @param testMethod       The specific test method being annotated
     */
    @Override
    public void transform(ITestAnnotation annotation, Class testClass, Constructor testConstructor, Method testMethod) {

        // Unit tests are deterministic — retrying them on failure adds no value and
        // causes mock re-initialization issues when RetryAnalyzer spawns a new instance.
        // We inspect the test's group membership to identify unit tests.
        for (String group : annotation.getGroups()) {
            if ("unit".equals(group)) return; // Skip retry setup for unit tests entirely
        }

        // Attach RetryAnalyzer to all non-unit tests (UI, API, sanity, security, etc.)
        // RetryAnalyzer.class is passed here — TestNG will create an instance of it
        // for each test method that needs to be retried.
        annotation.setRetryAnalyzer(RetryAnalyzer.class);
    }
}
