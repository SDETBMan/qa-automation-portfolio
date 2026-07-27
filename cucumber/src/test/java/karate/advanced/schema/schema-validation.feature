@advanced @schema
Feature: JSON Schema Validation
  Demonstrates Karate's built-in schema validation markers
  for asserting response structure without hardcoding values.

  Background:
    * url baseUrl

  Scenario: Validate user schema with type markers
    Given path '/users/1'
    When method get
    Then status 200
    And match response ==
      """
      {
        id: '#number',
        name: '#string',
        username: '#string',
        email: '#string',
        address: {
          street: '#string',
          suite: '#string',
          city: '#string',
          zipcode: '#string',
          geo: { lat: '#string', lng: '#string' }
        },
        phone: '#string',
        website: '#string',
        company: {
          name: '#string',
          catchPhrase: '#string',
          bs: '#string'
        }
      }
      """

  Scenario: Validate array schema with each keyword
    Given path '/posts'
    And param userId = 1
    When method get
    Then status 200
    And match each response ==
      """
      {
        userId: '#number',
        id: '#number',
        title: '#string',
        body: '#string'
      }
      """

  Scenario: Validate optional and nullable fields
    Given path '/users/1'
    When method get
    Then status 200
    # '#present' asserts the key exists (regardless of value)
    And match response contains { id: '#present', name: '#present' }
    # '#notnull' asserts the value is not null
    And match response.email == '#notnull'
    And match response.name == '#notnull'

  Scenario: Validate with regex markers
    Given path '/users/1'
    When method get
    Then status 200
    # Email format validation using regex marker
    And match response.email == '#regex .+@.+\\..+'
    # Zipcode format (xxxxx-xxxx)
    And match response.address.zipcode == '#regex \\d{5}-\\d{4}'
    # Latitude/longitude as numeric strings
    And match response.address.geo.lat == '#regex -?\\d+\\.\\d+'
