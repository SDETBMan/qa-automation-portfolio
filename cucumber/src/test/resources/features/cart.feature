Feature: Shopping Cart Functionality

  Background:
    Given I am on the SauceDemo login page
    And I enter username "standard_user" and password "secret_sauce"
    And I click the login button

  Scenario: Add a backpack to the cart
    When I add the "Sauce Labs Backpack" to the cart
    Then the cart badge should show "1"
    And I click the cart icon
    Then I should see "Sauce Labs Backpack" in the cart list