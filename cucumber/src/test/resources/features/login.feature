Feature: Login Functionality
  As a user of the SauceDemo application
  I want to log in with different accounts
  So that I can access the product features

  Background:
    Given I am on the SauceDemo login page

  # Replaces testValidLogin
  Scenario: Successful login with valid credentials
    When I enter username "standard_user" and password "secret_sauce"
    And I click the login button
    Then I should be redirected to the Products page

  # Replaces testInvalidLogin
  Scenario: Failed login with invalid credentials
    When I enter username "locked_out_user" and password "wrong_password"
    And I click the login button
    Then I should see an error message

  # Replaces testLoginWithMultipleUsers (The Data Provider)
  Scenario Outline: Login with multiple user types
    When I enter username "<username>" and password "<password>"
    And I click the login button
    Then I should see the "<result>" state

    Examples:
      | username                | password     | result   |
      | standard_user           | secret_sauce | success  |
      | problem_user            | secret_sauce | success  |
      | locked_out_user         | secret_sauce | failure  |
      | performance_glitch_user | secret_sauce | success  |