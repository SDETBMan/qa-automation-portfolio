Feature: API Health and Data Integrity
  As a QA Engineer
  I want to validate backend API endpoints
  So that I can confirm data integrity independently of the UI

  Scenario: User endpoint returns correct data
    Given the API base URL is configured
    When I send a GET request to "/users/1"
    Then the response status code should be 200
    And the response body should contain "Leanne Graham"

  Scenario: Users list endpoint returns multiple records
    Given the API base URL is configured
    When I send a GET request to "/users"
    Then the response status code should be 200
    And the response body should contain "Ervin Howell"

  # Strategy #3 — one step + {string} parameter replaces N endpoint scenarios
  Scenario Outline: Multiple endpoints return expected status codes
    Given the API base URL is configured
    When I send a GET request to "<endpoint>"
    Then the response status code should be <status>

    Examples:
      | endpoint    | status |
      | /posts/1    | 200    |
      | /comments/1 | 200    |
      | /todos/1    | 200    |
      | /posts/9999 | 404    |
