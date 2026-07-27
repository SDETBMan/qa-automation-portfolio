@smoke @api @users
Feature: Users API CRUD Operations
  Full lifecycle coverage of the /users resource on JSONPlaceholder.
  Demonstrates GET, POST, PUT, PATCH, DELETE with response validation.

  Background:
    * url baseUrl

  Scenario: GET all users returns a list
    Given path '/users'
    When method get
    Then status 200
    And match response == '#[10]'
    And match each response contains { id: '#number', name: '#string', email: '#string' }

  Scenario: GET a single user by ID
    Given path '/users/1'
    When method get
    Then status 200
    And match response.id == 1
    And match response.name == 'Leanne Graham'
    And match response.email == 'Sincere@april.biz'
    And match response.address == '#object'
    And match response.company == '#object'

  Scenario: GET user with nested address validation
    Given path '/users/1'
    When method get
    Then status 200
    And match response.address contains { street: '#string', city: '#string', zipcode: '#string' }
    And match response.address.geo contains { lat: '#string', lng: '#string' }

  Scenario: POST creates a new user
    Given path '/users'
    And request { name: 'Jane Doe', username: 'janedoe', email: 'jane@test.com', phone: '555-1234' }
    When method post
    Then status 201
    And match response contains { name: 'Jane Doe', username: 'janedoe', email: 'jane@test.com' }
    And match response.id == '#number'

  Scenario: PUT replaces a user
    Given path '/users/1'
    And request { name: 'Updated Name', username: 'updateduser', email: 'updated@test.com' }
    When method put
    Then status 200
    And match response contains { name: 'Updated Name', username: 'updateduser' }
    And match response.id == 1

  Scenario: PATCH partially updates a user
    Given path '/users/1'
    And request { name: 'Patched Name' }
    When method patch
    Then status 200
    And match response.name == 'Patched Name'
    And match response.id == 1

  Scenario: DELETE removes a user
    Given path '/users/1'
    When method delete
    Then status 200
