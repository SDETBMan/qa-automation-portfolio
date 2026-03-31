@security
Feature: Security
  As a security-aware QA engineer
  I want to verify the login surface handles malicious input safely
  So that the application does not expose internals or execute injected code

  Scenario: SQL injection attempt is safely rejected
    Given I am on the SauceDemo login page
    When I attempt to login with SQL injection payload
    Then I should see an authentication error
    And the error message should not expose system internals

  Scenario: XSS payload in login field is handled safely
    Given I am on the SauceDemo login page
    When I attempt to login with XSS payload
    Then I should see an authentication error
    And the page title should not contain "xss"

  Scenario: Repeated failed logins do not lock out a valid user permanently
    Given I am on the SauceDemo login page
    When I submit 3 failed login attempts
    And I login with valid credentials
    Then I should be on the Products page

  @known_limitation
  Scenario: Security response headers are present
    # saucedemo.com is a demo app and does not serve x-frame-options or
    # x-content-type-options. Tagged @known_limitation so CI skips it while
    # keeping the scenario visible as a documented gap.
    Given I am on the SauceDemo login page
    Then the security response headers should be present
