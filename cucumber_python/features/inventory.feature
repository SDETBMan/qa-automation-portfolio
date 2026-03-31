Feature: Inventory Page Functionality
  As a logged-in user
  I want to add and remove products from the cart
  So that I can complete the shopping flow

  Background:
    Given I am logged in as "standard_user"

  Scenario: Add a single item to the cart
    When I add "Sauce Labs Backpack" to the cart
    Then the cart badge should show 1
    When I go to the shopping cart
    Then "Sauce Labs Backpack" should be in the cart

  Scenario: Add multiple items to the cart
    When I add the following items to the cart:
      | Sauce Labs Backpack     |
      | Sauce Labs Bike Light   |
      | Sauce Labs Bolt T-Shirt |
    Then the cart badge should show 3

  Scenario: Add then remove an item
    When I add "Sauce Labs Backpack" to the cart
    Then the cart badge should show 1
    When I remove "Sauce Labs Backpack" from the cart
    Then the cart should be empty

  Scenario: Navigate to checkout after adding an item
    When I add "Sauce Labs Backpack" to the cart
    And I go to the shopping cart
    And I proceed to checkout
    Then I should be on the checkout page
