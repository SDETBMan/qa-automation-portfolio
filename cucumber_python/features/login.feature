Feature: Login Functionality
  As a user of the SauceDemo application
  I want to log in with different account types
  So that I can access the product catalogue

  Background:
    Given I am on the SauceDemo login page

  # Declarative: the "How" (click, type) lives in the Login Task, not here
  Scenario: Successful login with valid credentials
    When I login with valid credentials
    Then I should be on the Products page

  Scenario: Failed login with invalid credentials
    When I login with invalid credentials
    Then I should see an authentication error

  # Data-driven: one Scenario Outline replaces N separate scenarios
  # Strategy #3 — one step handles every outcome via the {outcome} parameter
  Scenario Outline: Login with multiple user types
    When I login as "<username>"
    Then I should see the "<outcome>" state

    Examples:
      | username                | outcome |
      | standard_user           | success |
      | problem_user            | success |
      | locked_out_user         | failure |
      | performance_glitch_user | success |
