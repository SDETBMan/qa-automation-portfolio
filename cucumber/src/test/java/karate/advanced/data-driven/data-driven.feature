@advanced @data-driven
Feature: Data-Driven Testing
  Demonstrates Scenario Outline with Examples tables,
  dynamic data generation, and Karate's table syntax.

  Background:
    * url baseUrl

  Scenario Outline: Validate multiple users by ID
    Given path '/users/<userId>'
    When method get
    Then status 200
    And match response.id == <userId>
    And match response.name == '<expectedName>'
    And match response.email == '<expectedEmail>'

    Examples:
      | userId | expectedName         | expectedEmail              |
      | 1      | Leanne Graham        | Sincere@april.biz          |
      | 2      | Ervin Howell         | Shanna@melissa.tv          |
      | 3      | Clementine Bauch     | Nathan@yesenia.net         |
      | 4      | Patricia Lebsack     | Julianne.OConner@kory.org  |
      | 5      | Chelsey Dietrich     | Lucio_Hettinger@annie.name |

  Scenario Outline: Create posts with different payloads
    Given path '/posts'
    And request { title: '<title>', body: '<body>', userId: <userId> }
    When method post
    Then status 201
    And match response.title == '<title>'
    And match response.userId == <userId>

    Examples:
      | title          | body                      | userId |
      | First Post     | Body of the first post    | 1      |
      | Second Post    | Body of the second post   | 2      |
      | Third Post     | Body of the third post    | 3      |

  Scenario: Dynamic data generation with Karate expressions
    * def randomId = Math.floor(Math.random() * 10) + 1
    Given path '/users', randomId
    When method get
    Then status 200
    And match response.id == randomId
    And match response contains { name: '#string', email: '#string' }
