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
 * LoginServiceTest: Demonstrates Mockito-based unit testing of the service layer.
 *
 * <p>WHY A SERVICE LAYER EXISTS: In a well-architected automation framework,
 * business logic (e.g. "log in and verify success") lives in service classes,
 * not in page objects (which only know how to interact with one page) and not
 * in test classes (which only orchestrate calls). {@link LoginService} encapsulates
 * the login workflow: call {@code LoginPage.login()}, check if
 * {@code InventoryPage.isProductsHeaderDisplayed()} returns true, and return
 * a boolean result. This makes the logic reusable and independently testable.
 *
 * <p>WHY MOCKITO: To test {@code LoginService} in isolation, we need to control
 * what {@code LoginPage} and {@code InventoryPage} return — without actually
 * launching a browser. Mockito creates "mock objects" (fake implementations of
 * the real classes) that return whatever values you configure. This lets us test
 * service logic at the speed of milliseconds, not seconds.
 *
 * <p>KEY MOCKITO CONCEPTS DEMONSTRATED:
 * <ul>
 *   <li>{@code @Mock} — creates a fake object that replaces the real dependency.</li>
 *   <li>{@code when/thenReturn} — programs a mock to return a specific value when
 *       a specific method is called ("when this method is called, return this value").</li>
 *   <li>{@code verify()} — asserts that a method on a mock was actually called during
 *       the test. Proves the service delegated to the right dependency.</li>
 *   <li>{@code times(n)} — used inside verify() to assert the exact call count.</li>
 *   <li>{@code doThrow()} — programs a mock to throw an exception, simulating
 *       a dependency failure (e.g. browser crash).</li>
 *   <li>{@code verifyNoMoreInteractions()} — asserts that no OTHER methods on the
 *       mock were called beyond the ones explicitly verified. Guards against
 *       unexpected side effects.</li>
 * </ul>
 *
 * <p>No browser is launched. No network calls are made. Each test runs in milliseconds.
 */
public class LoginServiceTest {

    // @Mock tells Mockito to create a fake LoginPage — same interface, but all
    // methods do nothing (return null/false/0) by default until configured with when().
    @Mock private LoginPage mockLoginPage;
    @Mock private InventoryPage mockInventoryPage;

    // The real object under test — the service that uses the mocked dependencies.
    private LoginService loginService;

    // AutoCloseable lets us safely close the mock framework after each test,
    // releasing Mockito's internal state and avoiding memory leaks.
    private AutoCloseable mocks;

    /**
     * setUp: Initialises Mockito annotations and wires the service with its mocks
     * before every test method.
     *
     * <p>WHY {@code alwaysRun = true}: The RetryAnalyzer re-runs failed tests on a
     * fresh instance — without alwaysRun, the @BeforeMethod might not fire before
     * a retry, leaving @Mock fields as null and causing confusing NullPointerExceptions
     * instead of the real failure.
     *
     * <p>WHY {@code MockitoAnnotations.openMocks(this)}: This scans the test class
     * for @Mock fields and injects Mockito-generated fake objects into them.
     * Without this call, @Mock-annotated fields remain null.
     */
    @BeforeMethod(alwaysRun = true)
    public void setUp() {
        // Activate Mockito annotations — creates mock objects for all @Mock fields.
        // Returns AutoCloseable so Mockito can clean up after the test.
        mocks = MockitoAnnotations.openMocks(this);

        // Inject the mocks into the service — the service receives fake pages,
        // so its logic runs without any real browser.
        loginService = new LoginService(mockLoginPage, mockInventoryPage);
    }

    /**
     * tearDown: Closes the Mockito session after each test.
     *
     * <p>WHY CLOSE MOCKS: Mockito holds references to the mock objects internally.
     * Closing them after each test releases those references, preventing memory
     * leaks in long test runs and ensuring a clean state for the next test.
     */
    @AfterMethod(alwaysRun = true)
    public void tearDown() throws Exception {
        mocks.close();
    }

    // ---------------------------------------------------------
    // HAPPY PATH: Successful login returns true
    // ---------------------------------------------------------

    /**
     * testSuccessfulLoginReturnsTrue: Verifies that the service returns {@code true}
     * when the inventory page confirms the login succeeded.
     *
     * <p>THE ARRANGE-ACT-ASSERT PATTERN: This is the industry-standard structure
     * for unit tests:
     * <ul>
     *   <li>ARRANGE — set up the conditions (configure mocks to simulate success).</li>
     *   <li>ACT — call the method under test.</li>
     *   <li>ASSERT — verify the result AND that the right methods were called.</li>
     * </ul>
     *
     * <p>WHY VERIFY CALLS: {@code verify(mockLoginPage).login(...)} doesn't just
     * check the return value — it checks that the service actually delegated to
     * LoginPage. If the service returned true without calling login at all (a bug),
     * the result assertion would pass but the verify would fail. Together they give
     * full confidence in the service behaviour.
     */
    @Test(groups = "unit")
    public void testSuccessfulLoginReturnsTrue() {
        // ARRANGE: program the mock to simulate a successful login outcome —
        // the inventory page "loaded" because isProductsHeaderDisplayed() returns true.
        when(mockInventoryPage.isProductsHeaderDisplayed()).thenReturn(true);

        // ACT: call the service method with test credentials.
        boolean result = loginService.loginAndVerify("standard_user", "secret_sauce");

        // ASSERT: the service must return true when the inventory page is detected.
        Assert.assertTrue(result, "loginAndVerify should return true when products page loads");

        // VERIFY: confirm the service actually called login() and checked the header.
        // This catches bugs where the service might return a hardcoded true without
        // actually executing the login flow.
        verify(mockLoginPage).login("standard_user", "secret_sauce");
        verify(mockInventoryPage).isProductsHeaderDisplayed();
    }

    // ---------------------------------------------------------
    // NEGATIVE PATH: Failed login returns false and exposes error message
    // ---------------------------------------------------------

    /**
     * testFailedLoginReturnsFalse: Verifies that the service returns {@code false}
     * and surfaces the error message when credentials are invalid.
     *
     * <p>WHY TEST BOTH RETURN VALUE AND ERROR MESSAGE: A service that returns false
     * but doesn't expose the error message forces callers to do extra work to find
     * out why. Testing that {@code getLoginError()} returns the page's error message
     * confirms the service properly bubbles up failure details from the page object.
     */
    @Test(groups = "unit")
    public void testFailedLoginReturnsFalse() {
        // ARRANGE: simulate a failed login — inventory page didn't load,
        // and the login page shows an error message.
        when(mockInventoryPage.isProductsHeaderDisplayed()).thenReturn(false);
        when(mockLoginPage.getErrorMessage()).thenReturn("Username and password do not match");

        // ACT: attempt login with bad credentials.
        boolean result   = loginService.loginAndVerify("wrong_user", "wrong_pass");
        String  error    = loginService.getLoginError();

        // ASSERT: service returns false and surfaces the page's error message.
        Assert.assertFalse(result, "loginAndVerify should return false on bad credentials");
        Assert.assertTrue(error.contains("do not match"), "Should surface the page error message");

        // VERIFY: confirm login() was actually called with the provided credentials.
        verify(mockLoginPage).login("wrong_user", "wrong_pass");
    }

    // ---------------------------------------------------------
    // INTERACTION VERIFICATION: login() is called exactly once
    // ---------------------------------------------------------

    /**
     * testLoginIsCalledExactlyOnce: Verifies that the service calls {@code LoginPage.login()}
     * exactly once — not zero times (missing the call) and not twice (duplicate call).
     *
     * <p>WHY VERIFY CALL COUNT: A service with a bug might call login() twice (retrying
     * internally without telling the caller) or zero times (returning a cached result).
     * Both are bugs that wouldn't be caught by just checking the return value.
     * {@code times(1)} makes the expected call count explicit and readable.
     *
     * <p>WHY {@code verifyNoMoreInteractions}: This asserts that ONLY the methods we
     * explicitly verified were called on the mock — no unexpected side calls like
     * {@code getErrorMessage()} being called on a successful login path (which would
     * be wasteful or indicate misunderstood logic).
     */
    @Test(groups = "unit")
    public void testLoginIsCalledExactlyOnce() {
        when(mockInventoryPage.isProductsHeaderDisplayed()).thenReturn(true);

        loginService.loginAndVerify("standard_user", "secret_sauce");

        // times(1) is explicit about the expected call count — more readable
        // than verify() alone, which defaults to times(1) but doesn't say so.
        verify(mockLoginPage, times(1)).login("standard_user", "secret_sauce");

        // Confirm no other LoginPage methods were called during a successful login.
        // For example: getErrorMessage() should NOT be called if login succeeded.
        verifyNoMoreInteractions(mockLoginPage);
    }

    // ---------------------------------------------------------
    // EXCEPTION HANDLING: service propagates WebDriver failures correctly
    // ---------------------------------------------------------

    /**
     * testLoginPropagatesWebDriverException: Verifies that if the page object throws
     * a RuntimeException (e.g. browser crash), the service lets it propagate rather
     * than swallowing it silently.
     *
     * <p>WHY TEST EXCEPTION PROPAGATION: Silent failure is one of the worst things
     * a service can do. If {@code login()} throws "WebDriver session lost" and the
     * service catches it internally and returns false, the caller thinks the login
     * just failed — they don't know the infrastructure broke. Letting exceptions
     * propagate ensures the test framework sees the failure and marks the test as
     * ERROR (infrastructure broken) rather than FAIL (test case failed).
     *
     * <p>WHY {@code expectedExceptions}: This TestNG annotation asserts that the test
     * method MUST throw the specified exception type. If the service swallows the
     * exception and the method returns normally, TestNG will FAIL the test — exactly
     * the behaviour we want to enforce.
     */
    @Test(groups = "unit", expectedExceptions = RuntimeException.class)
    public void testLoginPropagatesWebDriverException() {
        // ARRANGE: configure the mock to throw when login() is called.
        // doThrow() is used instead of when/thenThrow because thenThrow is for
        // methods with non-void return types; login() is void.
        doThrow(new RuntimeException("WebDriver session lost"))
                .when(mockLoginPage).login(anyString(), anyString());

        // ACT: call the service — it should NOT catch the RuntimeException.
        // TestNG's expectedExceptions annotation will verify the exception was thrown.
        // If no exception is thrown, the test fails (service incorrectly swallowed it).
        loginService.loginAndVerify("any_user", "any_pass");
    }
}
