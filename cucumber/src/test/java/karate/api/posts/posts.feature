@smoke @api @posts
Feature: Posts API Operations
  Validates CRUD operations on /posts with query filtering
  and relationship to users.

  Background:
    * url baseUrl

  Scenario: GET all posts returns 100 entries
    Given path '/posts'
    When method get
    Then status 200
    And match response == '#[100]'
    And match each response contains { userId: '#number', id: '#number', title: '#string', body: '#string' }

  Scenario: GET posts filtered by userId
    Given path '/posts'
    And param userId = 1
    When method get
    Then status 200
    And match each response contains { userId: 1 }
    And match response == '#[10]'

  Scenario: POST creates a new post
    Given path '/posts'
    And request
      """
      {
        "title": "Karate API Testing",
        "body": "Demonstrating POST with Karate DSL",
        "userId": 1
      }
      """
    When method post
    Then status 201
    And match response contains { title: 'Karate API Testing', userId: 1 }
    And match response.id == '#number'

  Scenario: GET then update - read-modify-write pattern
    # Step 1: Read the existing post
    Given path '/posts/1'
    When method get
    Then status 200
    * def originalTitle = response.title

    # Step 2: Update only the title
    Given path '/posts/1'
    And request { title: 'Modified Title', body: '#(response.body)', userId: '#(response.userId)' }
    When method put
    Then status 200
    And match response.title == 'Modified Title'
    And match response.id == 1
