@cart
Feature: Cart Page Operations
  As a logged-in user with items in my cart
  I want to view and manage my cart
  So that I can proceed to checkout

  Background:
    Given I am logged in as "standard_user"
    And I have added "sauce-labs-backpack" to the cart

  @smoke
  Scenario: Cart page displays the added item
    When I navigate to the cart
    Then I should see "Sauce Labs Backpack" in the cart

  @regression
  Scenario: Checkout button navigates to checkout information page
    When I navigate to the cart
    And I click checkout
    Then I should be on the checkout information page

  @regression
  Scenario: Cart page shows correct item count
    When I navigate to the cart
    Then I should see 1 item in the cart
