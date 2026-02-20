package com.framework.unit;

import com.framework.pages.InventoryPage;
import com.framework.pages.LoginPage;
import com.framework.services.LoginService;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

/**
 * LoginServiceTest: Demonstrates Mockito for unit testing a service layer.
 *
 * Key Mockito concepts shown:
 *   @Mock          — creates a fake object that replaces the real dependency
 *   when/thenReturn — stubs a method to return a controlled value
 *   verify()       — asserts a method was actually called during the test
 *   times(n)       — asserts exact call count
 *   doThrow()      — simulates an exception from a dependency
 *   verifyNoMoreInteractions() — asserts no unexpected method calls occurred
 *
 * No browser is launched. No network calls are made. Each test runs in milliseconds.
 */
public class LoginServiceTest {

    @Mock private LoginPage mockLoginPage;
    @Mock private InventoryPage mockInventoryPage;

    private LoginService loginService;
    private AutoCloseable mocks;

    // alwaysRun = true ensures setUp fires even when the RetryAnalyzer re-invokes a test
    // on a fresh instance — without it, @Mock fields stay null on retry runs.
    @BeforeMethod(alwaysRun = true)
    public void setUp() {
        mocks = MockitoAnnotations.openMocks(this);
        loginService = new LoginService(mockLoginPage, mockInventoryPage);
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() throws Exception {
        mocks.close();
    }

    // ---------------------------------------------------------
    // HAPPY PATH: Successful login returns true
    // ---------------------------------------------------------
    @Test(groups = "unit")
    public void testSuccessfulLoginReturnsTrue() {
        // ARRANGE: stub the page objects to simulate a successful login outcome
        when(mockInventoryPage.isProductsHeaderDisplayed()).thenReturn(true);

        // ACT
        boolean result = loginService.loginAndVerify("standard_user", "secret_sauce");

        // ASSERT: result is correct AND the right methods were called
        Assert.assertTrue(result, "loginAndVerify should return true when products page loads");
        verify(mockLoginPage).login("standard_user", "secret_sauce");
        verify(mockInventoryPage).isProductsHeaderDisplayed();
    }

    // ---------------------------------------------------------
    // NEGATIVE PATH: Failed login returns false and exposes error message
    // ---------------------------------------------------------
    @Test(groups = "unit")
    public void testFailedLoginReturnsFalse() {
        // ARRANGE: inventory page never loads; error message is available
        when(mockInventoryPage.isProductsHeaderDisplayed()).thenReturn(false);
        when(mockLoginPage.getErrorMessage()).thenReturn("Username and password do not match");

        // ACT
        boolean result   = loginService.loginAndVerify("wrong_user", "wrong_pass");
        String  error    = loginService.getLoginError();

        // ASSERT
        Assert.assertFalse(result, "loginAndVerify should return false on bad credentials");
        Assert.assertTrue(error.contains("do not match"), "Should surface the page error message");
        verify(mockLoginPage).login("wrong_user", "wrong_pass");
    }

    // ---------------------------------------------------------
    // INTERACTION VERIFICATION: login() is called exactly once
    // ---------------------------------------------------------
    @Test(groups = "unit")
    public void testLoginIsCalledExactlyOnce() {
        when(mockInventoryPage.isProductsHeaderDisplayed()).thenReturn(true);

        loginService.loginAndVerify("standard_user", "secret_sauce");

        // times(1) makes the expected call count explicit and readable
        verify(mockLoginPage, times(1)).login("standard_user", "secret_sauce");

        // verifyNoMoreInteractions ensures no unexpected LoginPage methods were called
        // (e.g. a bug that accidentally called getErrorMessage() on success)
        verifyNoMoreInteractions(mockLoginPage);
    }

    // ---------------------------------------------------------
    // EXCEPTION HANDLING: service propagates WebDriver failures correctly
    // ---------------------------------------------------------
    @Test(groups = "unit", expectedExceptions = RuntimeException.class)
    public void testLoginPropagatesWebDriverException() {
        // ARRANGE: simulate a browser crash or stale session mid-test
        doThrow(new RuntimeException("WebDriver session lost"))
                .when(mockLoginPage).login(anyString(), anyString());

        // ACT: exception should propagate — the service must not swallow it silently
        loginService.loginAndVerify("any_user", "any_pass");
    }
}
