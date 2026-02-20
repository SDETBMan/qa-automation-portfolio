Feature: API Health and Data Integrity
  As a QA Engineer
  I want to validate backend API endpoints
  So that I can confirm data integrity independently of the UI

  Scenario: Validate user API returns 200 and correct data
    Given the API base URL is configured
    When I send a GET request to "/users/1"
    Then the response status code should be 200
    And the response body should contain "Leanne Graham"

  Scenario: Validate users list endpoint returns multiple records
    Given the API base URL is configured
    When I send a GET request to "/users"
    Then the response status code should be 200
    And the response body should contain "Ervin Howell"
