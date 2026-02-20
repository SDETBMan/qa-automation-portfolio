Feature: Inventory Page Functionality
  As a logged in user
  I want to add, remove, and purchase products from the inventory
  So that I can complete the full shopping flow

  Background:
    Given I am on the SauceDemo login page
    And I enter username "standard_user" and password "secret_sauce"
    And I click the login button

  # Mirrors AddToCartTest.testAddBackpackToCart
  Scenario: Add a single item to the cart
    When I add "Sauce Labs Backpack" to the inventory
    Then the inventory cart badge should show 1
    When I go to the shopping cart
    Then "Sauce Labs Backpack" should be in the cart

  # Mirrors AddToCartTest.testAddMultipleItemsToCart
  Scenario: Add multiple items to the cart
    When I add "Sauce Labs Backpack" to the inventory
    And I add "Sauce Labs Bike Light" to the inventory
    And I add "Sauce Labs Bolt T-Shirt" to the inventory
    Then the inventory cart badge should show 3

  # Mirrors AddToCartTest.testAddAndRemoveItem
  Scenario: Add and then remove an item from the cart
    When I add "Sauce Labs Backpack" to the inventory
    Then the inventory cart badge should show 1
    When I remove "Sauce Labs Backpack" from the inventory
    Then the cart should be empty

  # Mirrors AddToCartTest.testNavigateToCheckout
  Scenario: Navigate to checkout after adding an item
    When I add "Sauce Labs Backpack" to the inventory
    And I go to the shopping cart
    And I click the checkout button
    Then I should be on the checkout page
