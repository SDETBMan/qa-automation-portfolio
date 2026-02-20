package com.framework.utils;

import org.testng.IAnnotationTransformer;
import org.testng.annotations.ITestAnnotation;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;

/**
 * AnnotationTransformer: Dynamically sets the RetryAnalyzer for all tests.
 * This eliminates the need to manually add the retry parameter to every @Test annotation.
 */
public class AnnotationTransformer implements IAnnotationTransformer {

    @Override
    public void transform(ITestAnnotation annotation, Class testClass, Constructor testConstructor, Method testMethod) {

        // Unit tests are deterministic — retrying them on failure adds no value and
        // causes mock re-initialization issues when RetryAnalyzer spawns a new instance.
        for (String group : annotation.getGroups()) {
            if ("unit".equals(group)) return;
        }

        // Attach RetryAnalyzer to all non-unit tests (UI, API, sanity, etc.)
        annotation.setRetryAnalyzer(RetryAnalyzer.class);
    }
}
