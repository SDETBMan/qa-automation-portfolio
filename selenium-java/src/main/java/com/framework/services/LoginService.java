package com.framework.services;

import com.framework.pages.InventoryPage;
import com.framework.pages.LoginPage;

/**
 * LoginService: Orchestrates the login flow by coordinating LoginPage and InventoryPage.
 *
 * This service layer is the target for Mockito unit tests — its dependencies (the page
 * objects) are injected via constructor, making them trivial to mock and replace with
 * fakes in tests without spinning up a browser.
 */
public class LoginService {

    private final LoginPage loginPage;
    private final InventoryPage inventoryPage;

    public LoginService(LoginPage loginPage, InventoryPage inventoryPage) {
        this.loginPage = loginPage;
        this.inventoryPage = inventoryPage;
    }

    /**
     * Performs login and returns true if the products page loaded successfully.
     */
    public boolean loginAndVerify(String username, String password) {
        loginPage.login(username, password);
        return inventoryPage.isProductsHeaderDisplayed();
    }

    /**
     * Returns the error message text shown when login fails.
     */
    public String getLoginError() {
        return loginPage.getErrorMessage();
    }
}
