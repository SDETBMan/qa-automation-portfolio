@security
Feature: Security
  As a security-aware QA engineer
  I want to verify the login surface handles malicious input safely
  So that the application does not expose internal system details or execute injected code

  Scenario: SQL injection attempt is safely rejected
    Given I am on the SauceDemo login page
    When I enter username "' OR '1'='1' --" and password "anything"
    When I click the login button
    Then I should see an error message
    Then the error message should not expose system internals

  Scenario: XSS payload in login field is handled safely
    Given I am on the SauceDemo login page
    When I enter username "<script>document.title='xss'</script>" and password "anything"
    When I click the login button
    Then I should see an error message
    Then the page title should not be "xss"

  Scenario: Security response headers are present
    Given I am on the SauceDemo login page
    Then the security response headers should be present
