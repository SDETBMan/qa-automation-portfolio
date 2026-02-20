package com.saucedemo.utils;

import org.testng.IAnnotationTransformer;
import org.testng.annotations.ITestAnnotation;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;

/**
 * AnnotationTransformer: Dynamically attaches RetryAnalyzer to every scenario.
 * Registered as a TestNG listener in the Surefire plugin config — no per-test changes needed.
 */
public class AnnotationTransformer implements IAnnotationTransformer {

    @Override
    public void transform(ITestAnnotation annotation, Class testClass,
                          Constructor testConstructor, Method testMethod) {
        annotation.setRetryAnalyzer(RetryAnalyzer.class);
    }
}
