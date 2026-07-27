@advanced @headers
Feature: Headers, Authentication, and Cookies
  Demonstrates custom header management, auth token patterns,
  cookie handling, and content-type negotiation.

  Background:
    * url baseUrl

  Scenario: Custom headers are sent with request
    Given path '/posts/1'
    And header X-Custom-Header = 'karate-test'
    And header X-Request-Id = '12345'
    When method get
    Then status 200
    And match response.id == 1

  Scenario: Bearer token authentication pattern
    # Simulate obtaining an auth token (JSONPlaceholder doesn't require auth,
    # but this demonstrates the pattern for real APIs)
    * def authToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock-token'
    Given path '/posts/1'
    And header Authorization = 'Bearer ' + authToken
    When method get
    Then status 200
    And match response.id == 1

  Scenario: Content-Type negotiation - JSON
    Given path '/posts'
    And header Content-Type = 'application/json; charset=UTF-8'
    And request { title: 'Content Type Test', body: 'Testing JSON content type', userId: 1 }
    When method post
    Then status 201
    And match response contains { title: 'Content Type Test' }

  Scenario: Multiple headers via configure
    * configure headers = { 'X-Api-Version': 'v2', 'X-Client': 'karate-suite' }
    Given path '/users/1'
    When method get
    Then status 200
    And match response.id == 1

  Scenario: Cookie handling pattern
    # Demonstrate setting cookies on request
    * cookie session_id = 'abc123'
    * cookie preferences = 'dark_mode=true'
    Given path '/users/1'
    When method get
    Then status 200
    And match response.id == 1
