Feature: Shopping Cart Functionality
  As a logged-in user
  I want to view and manage my cart
  So that I can confirm items are correctly tracked before checkout

  Background:
    Given I am logged in as "standard_user"

  Scenario: Cart reflects item added from inventory
    When I add "Sauce Labs Backpack" to the cart
    And I go to the shopping cart
    Then the cart badge should show 1
    And "Sauce Labs Backpack" should be in the cart

  Scenario: Cart persists multiple items
    When I add the following items to the cart:
      | Sauce Labs Backpack   |
      | Sauce Labs Bike Light |
    And I go to the shopping cart
    Then "Sauce Labs Backpack" should be in the cart
    And "Sauce Labs Bike Light" should be in the cart
