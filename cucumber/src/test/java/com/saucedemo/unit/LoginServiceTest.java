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
 * LoginServiceTest: Unit tests for {@link LoginService} using Mockito mocks.
 *
 * <p>WHAT IS A UNIT TEST: A unit test validates a single class or method in
 * complete isolation — no browser, no network, no database. Here, "isolation"
 * is achieved by replacing the real {@link LoginPage} and {@link InventoryPage}
 * (which require a running Selenium WebDriver) with Mockito mock objects that
 * behave exactly as we instruct them to.
 *
 * <p>WHY THIS FILE EXISTS IN A SELENIUM PORTFOLIO: SDETs are expected to understand
 * multiple testing layers. Including unit tests with Mockito alongside Selenium/Cucumber
 * integration tests demonstrates the "testing pyramid" — the idea that a healthy suite
 * has many fast unit tests at the base, fewer integration tests in the middle, and even
 * fewer slow E2E UI tests at the top.
 *
 * <p>Key Mockito concepts shown:
 * <ul>
 *   <li>{@code @Mock} — marks a field as a mock object. Mockito creates a fake instance
 *       that returns default values (null, false, 0) for all methods unless stubbed.</li>
 *   <li>{@code when(...).thenReturn(...)} — stubs a specific method call to return
 *       a controlled value, simulating a particular application state.</li>
 *   <li>{@code verify(...)} — asserts that a specific method was actually called on the
 *       mock during the test. This proves the system-under-test uses its dependencies
 *       correctly, not just that it returns the right value.</li>
 *   <li>{@code times(n)} — used with {@code verify} to assert an exact call count.</li>
 *   <li>{@code doThrow(...)} — configures a mock method to throw an exception, simulating
 *       error conditions like a crashed browser session.</li>
 *   <li>{@code verifyNoMoreInteractions(...)} — asserts no unexpected method calls were
 *       made beyond those explicitly verified, catching accidental side-effects.</li>
 * </ul>
 *
 * <p>No browser is launched. No network calls are made. Each test runs in milliseconds.
 */
public class LoginServiceTest {

    /**
     * Mock of LoginPage — replaces the real Selenium-backed page object.
     * All method calls on this mock return false/null by default unless stubbed
     * with {@code when(...).thenReturn(...)}.
     */
    @Mock private LoginPage mockLoginPage;

    /**
     * Mock of InventoryPage — replaces the real Selenium-backed page object.
     * Used to simulate whether the products page loaded after login.
     */
    @Mock private InventoryPage mockInventoryPage;

    /**
     * The system under test: LoginService receives the mocks via constructor injection,
     * so it operates on the fakes rather than real browser-backed objects.
     */
    private LoginService loginService;

    /**
     * Runs before every test method to set up a fresh, clean set of mocks.
     *
     * <p>WHY RESET BEFORE EACH TEST: If mocks were reused across tests, a stubbing
     * from test A could accidentally affect test B. {@code MockitoAnnotations.openMocks(this)}
     * initialises the {@code @Mock} fields fresh, and a new {@code LoginService} is
     * constructed with those clean mocks. Each test therefore starts from a known
     * zero state.
     *
     * <p>{@link MockitoAnnotations#openMocks(Object)} is the modern replacement for
     * the deprecated {@code initMocks()} — it activates the {@code @Mock} annotations
     * by scanning the current test instance's fields.
     */
    @BeforeMethod
    public void setUp() {
        // Activates @Mock annotations and injects fresh mocks before each test
        MockitoAnnotations.openMocks(this);
        loginService = new LoginService(mockLoginPage, mockInventoryPage);
    }

    // ---------------------------------------------------------
    // HAPPY PATH: Successful login returns true
    // ---------------------------------------------------------

    /**
     * Verifies that {@code loginAndVerify} returns {@code true} when the inventory
     * page header is present after login.
     *
     * <p>PATTERN — ARRANGE / ACT / ASSERT (AAA): This is the standard unit test
     * structure used across all major testing frameworks:
     * <ul>
     *   <li>ARRANGE: configure the mocks to simulate the desired application state.</li>
     *   <li>ACT: call the method being tested.</li>
     *   <li>ASSERT: verify the return value AND the interactions with dependencies.</li>
     * </ul>
     */
    @Test(groups = "unit")
    public void testSuccessfulLoginReturnsTrue() {
        // ARRANGE: stub the page objects to simulate a successful login outcome
        when(mockInventoryPage.isProductsHeaderDisplayed()).thenReturn(true);

        // ACT
        boolean result = loginService.loginAndVerify("standard_user", "secret_sauce");

        // ASSERT: result is correct AND the right methods were called
        Assert.assertTrue(result, "loginAndVerify should return true when products page loads");
        // verify() confirms that loginPage.login() was actually called with the correct arguments
        verify(mockLoginPage).login("standard_user", "secret_sauce");
        // verify() confirms that inventoryPage.isProductsHeaderDisplayed() was checked after login
        verify(mockInventoryPage).isProductsHeaderDisplayed();
    }

    // ---------------------------------------------------------
    // NEGATIVE PATH: Failed login returns false and surfaces error state
    // ---------------------------------------------------------

    /**
     * Verifies that {@code loginAndVerify} returns {@code false} and
     * {@code hasLoginError} returns {@code true} when credentials are invalid.
     *
     * <p>This test simulates what happens at the Selenium level when bad credentials
     * are submitted: the products page never loads (header is not displayed) and the
     * login page shows an error. By stubbing both mocks accordingly, this test validates
     * that LoginService correctly reads and propagates both states.
     */
    @Test(groups = "unit")
    public void testFailedLoginReturnsFalse() {
        // ARRANGE: inventory page never loads; error flag is set
        when(mockInventoryPage.isProductsHeaderDisplayed()).thenReturn(false);
        when(mockLoginPage.isErrorDisplayed()).thenReturn(true);

        // ACT: call both methods under test
        boolean result   = loginService.loginAndVerify("wrong_user", "wrong_pass");
        boolean hasError = loginService.hasLoginError();

        // ASSERT: both return values reflect the simulated failure state
        Assert.assertFalse(result,   "loginAndVerify should return false on bad credentials");
        Assert.assertTrue(hasError,  "hasLoginError should return true when login fails");
        // Confirm the login attempt was actually made with the provided credentials
        verify(mockLoginPage).login("wrong_user", "wrong_pass");
    }

    // ---------------------------------------------------------
    // INTERACTION VERIFICATION: login() is called exactly once
    // ---------------------------------------------------------

    /**
     * Verifies that {@code login()} is called exactly once per {@code loginAndVerify}
     * invocation — not zero times, not twice.
     *
     * <p>WHY THIS TEST: A bug could cause login to be called multiple times (e.g.,
     * a retry loop) or not at all (e.g., a short-circuit return). {@code verify(..., times(1))}
     * catches both cases. {@code verifyNoMoreInteractions} catches any additional,
     * unexpected calls to the mock (e.g., accidentally calling {@code isErrorDisplayed}
     * on a successful login path).
     */
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

    /**
     * Verifies that a RuntimeException thrown by the LoginPage mock propagates
     * out of LoginService without being silently swallowed.
     *
     * <p>WHY THIS MATTERS: A service layer that catches and suppresses all exceptions
     * hides failures. If the browser crashes mid-test (stale session, out-of-memory,
     * network error), the test should fail loudly with a clear message — not return
     * {@code false} and pretend nothing happened. This test confirms that LoginService
     * does NOT wrap or suppress runtime exceptions from its dependencies.
     *
     * <p>{@code expectedExceptions = RuntimeException.class} in the {@code @Test}
     * annotation tells TestNG that this test PASSES only if the specified exception
     * is thrown. If no exception is thrown, the test fails.
     *
     * <p>{@code doThrow(...).when(mock).method()} is used instead of
     * {@code when(mock.method()).thenThrow()} because the latter cannot be used for
     * void methods. Although {@code login()} is void here, this form is shown to
     * demonstrate the correct pattern for void method stubbing.
     */
    @Test(groups = "unit", expectedExceptions = RuntimeException.class)
    public void testLoginPropagatesWebDriverException() {
        // ARRANGE: simulate a browser crash or stale session mid-test
        doThrow(new RuntimeException("WebDriver session lost"))
                .when(mockLoginPage).login(anyString(), anyString());

        // ACT: exception should propagate — the service must not swallow it silently
        // anyString() matches any non-null String argument, making this a flexible stub
        loginService.loginAndVerify("any_user", "any_pass");
    }
}
