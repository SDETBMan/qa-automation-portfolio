@ignore
Feature: Reusable Common Utilities
  Callable feature file providing shared helper scenarios.
  Invoked from other features via: call read('classpath:karate/infra/reusable/common.feature@tagName')

  @createUser
  Scenario: Create a user and return the response
    * def payload = __arg || {}
    Given url baseUrl
    And path '/users'
    And request
      """
      {
        name: '#(payload.name || "Test User")',
        username: '#(payload.username || "testuser")',
        email: '#(payload.email || "test@example.com")',
        phone: '#(payload.phone || "555-0000")'
      }
      """
    When method post
    Then status 201

  @createPost
  Scenario: Create a post and return the response
    * def payload = __arg || {}
    Given url baseUrl
    And path '/posts'
    And request
      """
      {
        title: '#(payload.title || "Default Title")',
        body: '#(payload.body || "Default body content")',
        userId: '#(payload.userId || 1)'
      }
      """
    When method post
    Then status 201

  @getUser
  Scenario: Get a user by ID
    * def userId = __arg.userId || 1
    Given url baseUrl
    And path '/users', userId
    When method get
    Then status 200

  @validateJsonResponse
  Scenario: Validate common JSON response properties
    * def res = __arg.response
    * match res == '#object'
    * match res.id == '#present'
