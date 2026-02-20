@inventory
Feature: Shopping Cart Management
  As a logged-in user
  I want to add and remove items from my cart
  So that I can manage my purchases

  Background:
    Given I am logged in as "standard_user"

  @smoke
  Scenario: Add a single item to cart updates badge
    When I add "sauce-labs-backpack" to the cart
    Then the cart badge should show "1"

  @regression
  Scenario: Add multiple items reflects correct count
    When I add "sauce-labs-backpack" to the cart
    And I add "sauce-labs-bike-light" to the cart
    Then the cart badge should show "2"

  @regression
  Scenario: Remove item from cart clears badge
    Given I have added "sauce-labs-backpack" to the cart
    When I remove "sauce-labs-backpack" from the cart
    Then the cart badge should not be visible

  @regression
  Scenario: Navigate to cart shows added item
    Given I have added "sauce-labs-backpack" to the cart
    When I navigate to the cart
    Then I should see 1 item in the cart
