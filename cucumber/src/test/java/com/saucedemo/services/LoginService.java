package com.saucedemo.services;

import com.saucedemo.pages.InventoryPage;
import com.saucedemo.pages.LoginPage;

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
     * Returns true if an error message is currently displayed on the login page.
     */
    public boolean hasLoginError() {
        return loginPage.isErrorDisplayed();
    }
}
