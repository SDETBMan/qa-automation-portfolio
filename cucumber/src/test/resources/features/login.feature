@login
Feature: User Authentication
  As a SauceDemo user
  I want to log in to the application
  So that I can access the product catalog

  Background:
    Given I am on the login page

  @smoke
  Scenario: Valid login navigates to inventory
    When I log in with username "standard_user" and password "secret_sauce"
    Then I should be on the inventory page

  @regression
  Scenario: Locked out user sees error message
    When I log in with username "locked_out_user" and password "secret_sauce"
    Then I should see an error message containing "locked out"

  @regression
  Scenario: Empty credentials show username validation error
    When I log in with username "" and password ""
    Then I should see an error message containing "Username is required"

  @regression
  Scenario: Wrong password shows error message
    When I log in with username "standard_user" and password "wrong_password"
    Then I should see an error message containing "Username and password do not match"

  @regression
  Scenario Outline: Multiple standard personas can log in successfully
    When I log in with username "<username>" and password "secret_sauce"
    Then I should be on the inventory page

    Examples:
      | username                |
      | standard_user           |
      | problem_user            |
      | performance_glitch_user |
