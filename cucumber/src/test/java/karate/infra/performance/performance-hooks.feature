@infra @performance
Feature: Performance Hooks and SLA Validation
  Demonstrates response time assertions, parallel API calls,
  and performance baseline enforcement.

  Background:
    * url baseUrl

  Scenario: Single endpoint response time SLA (under 2 seconds)
    Given path '/users/1'
    When method get
    Then status 200
    And assert responseTime < 2000

  Scenario: Multiple endpoints meet SLA
    Given path '/posts/1'
    When method get
    Then status 200
    And assert responseTime < 2000

    Given path '/comments'
    And param postId = 1
    When method get
    Then status 200
    And assert responseTime < 2000

  Scenario: Parallel API calls using karate.call
    # Execute multiple API calls in parallel and validate all succeed
    * def results = karate.map([1, 2, 3, 4, 5], function(id){ return { userId: id } })
    * def fetchUser =
      """
      function(arg) {
        var result = karate.call('classpath:karate/infra/reusable/common.feature@getUser', { userId: arg.userId });
        return result.response;
      }
      """
    * def users = karate.map(results, fetchUser)
    * match users == '#[5]'
    * match each users contains { id: '#number', name: '#string' }

  Scenario: Reusable feature call with auth headers
    # Demonstrate calling the auth helper and using returned headers
    * def authResult = call read('classpath:karate/infra/reusable/auth.feature') { username: 'testuser', password: 'testpass' }
    * def authHeaders = authResult.authHeaders

    Given path '/users/1'
    And headers authHeaders
    When method get
    Then status 200
    And match response.id == 1
