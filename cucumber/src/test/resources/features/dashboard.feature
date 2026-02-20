Feature: Dashboard Functionality
  As a logged in user
  I want to verify the dashboard state and navigation
  So that I can confirm the application behaves correctly after login

  # Mirrors DashboardTest.testUserCanAccessDashboard (data-driven)
  Scenario Outline: Multiple user types can access the dashboard
    Given I am on the SauceDemo login page
    When I enter username "<username>" and password "secret_sauce"
    And I click the login button
    Then the cart icon should be visible
    And the products header should display "Products"

    Examples:
      | username                |
      | standard_user           |
      | problem_user            |
      | performance_glitch_user |

  # Mirrors DashboardTest.testLogoutFlow
  Scenario: User can logout from the dashboard
    Given I am on the SauceDemo login page
    When I enter username "standard_user" and password "secret_sauce"
    And I click the login button
    When I open the menu and logout
    Then I should be returned to the login page

  # Mirrors DashboardTest.testDirectAccessWithoutLogin (security test)
  Scenario: Direct URL access without login redirects to login page
    Given I am on the SauceDemo login page
    When I navigate directly to "inventory.html" without logging in
    Then I should be returned to the login page
