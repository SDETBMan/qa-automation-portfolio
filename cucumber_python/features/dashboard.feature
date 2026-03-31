Feature: Dashboard Functionality
  As a logged-in user
  I want to verify dashboard state and navigation
  So that I can confirm the application behaves correctly after login

  Scenario Outline: Multiple user types can access the dashboard
    Given I am logged in as "<username>"
    Then the cart icon should be visible
    And the page header should display "Products"

    Examples:
      | username                |
      | standard_user           |
      | problem_user            |
      | performance_glitch_user |

  Scenario: User can logout from the dashboard
    Given I am logged in as "standard_user"
    When I logout
    Then I should be returned to the login page

  Scenario: Direct URL access without login redirects to login page
    Given I am on the SauceDemo login page
    When I navigate directly to "inventory.html"
    Then I should be returned to the login page
