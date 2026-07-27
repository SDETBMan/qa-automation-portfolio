@smoke @api @comments
Feature: Comments API - Nested Resources and Request Chaining
  Demonstrates accessing nested resources (/posts/{id}/comments)
  and chaining requests where output from one call feeds the next.

  Background:
    * url baseUrl

  Scenario: GET comments for a specific post (nested resource)
    Given path '/posts/1/comments'
    When method get
    Then status 200
    And match response == '#[5]'
    And match each response contains { postId: 1, id: '#number', name: '#string', email: '#string', body: '#string' }

  Scenario: GET comments filtered by postId query param
    Given path '/comments'
    And param postId = 1
    When method get
    Then status 200
    And match each response contains { postId: 1 }
    And match response == '#[5]'

  Scenario: Request chaining - create post then add comment
    # Step 1: Create a new post
    Given path '/posts'
    And request { title: 'Chaining Demo', body: 'Post for comment chaining', userId: 1 }
    When method post
    Then status 201
    * def newPostId = response.id

    # Step 2: Add a comment to the newly created post
    Given path '/comments'
    And request
      """
      {
        "postId": #(newPostId),
        "name": "Automated Comment",
        "email": "karate@test.com",
        "body": "This comment was added via request chaining"
      }
      """
    When method post
    Then status 201
    And match response contains { postId: '#(newPostId)', name: 'Automated Comment' }
    And match response.id == '#number'
