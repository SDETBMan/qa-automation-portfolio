package com.saucedemo.unit;

import com.saucedemo.pages.InventoryPage;
import com.saucedemo.pages.LoginPage;
import com.saucedemo.services.LoginService;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.testng.Assert;
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

    @BeforeMethod
    public void setUp() {
        // Activates @Mock annotations and injects fresh mocks before each test
        MockitoAnnotations.openMocks(this);
        loginService = new LoginService(mockLoginPage, mockInventoryPage);
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
    // NEGATIVE PATH: Failed login returns false and surfaces error state
    // ---------------------------------------------------------
    @Test(groups = "unit")
    public void testFailedLoginReturnsFalse() {
        // ARRANGE: inventory page never loads; error flag is set
        when(mockInventoryPage.isProductsHeaderDisplayed()).thenReturn(false);
        when(mockLoginPage.isErrorDisplayed()).thenReturn(true);

        // ACT
        boolean result   = loginService.loginAndVerify("wrong_user", "wrong_pass");
        boolean hasError = loginService.hasLoginError();

        // ASSERT
        Assert.assertFalse(result,   "loginAndVerify should return false on bad credentials");
        Assert.assertTrue(hasError,  "hasLoginError should return true when login fails");
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
        // (e.g. a bug that accidentally called isErrorDisplayed() on success)
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
