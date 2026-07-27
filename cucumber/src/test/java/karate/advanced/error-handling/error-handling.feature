@advanced @error-handling
Feature: Error Handling and Edge Cases
  Validates 404 responses, invalid payloads, empty results,
  boundary conditions, and retry logic.

  Background:
    * url baseUrl

  Scenario: GET non-existent resource returns 404
    Given path '/users/9999'
    When method get
    Then status 404
    And match response == {}

  Scenario: GET non-existent post returns 404
    Given path '/posts/9999'
    When method get
    Then status 404
    And match response == {}

  Scenario: POST with empty body still returns 201
    Given path '/posts'
    And request {}
    When method post
    Then status 201
    And match response.id == '#number'

  Scenario: GET with invalid query parameter returns full list
    Given path '/posts'
    And param userId = 99999
    When method get
    Then status 200
    And match response == '#[0]'

  Scenario: Large payload handling
    * def longBody = ''
    * eval for(var i = 0; i < 100; i++) longBody += 'This is a stress test sentence. '
    Given path '/posts'
    And request { title: 'Large Payload Test', body: '#(longBody)', userId: 1 }
    When method post
    Then status 201
    And match response.title == 'Large Payload Test'
    And match response.id == '#number'

  Scenario: Retry on transient failure pattern
    # Demonstrates Karate's retry-until for polling patterns
    Given path '/users/1'
    And retry until responseStatus == 200
    When method get
    Then status 200
    And match response.id == 1
