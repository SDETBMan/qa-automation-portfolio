@ignore
Feature: Auth Helper
  Callable feature that simulates authentication and returns
  headers for authenticated requests. Demonstrates the pattern
  used in real APIs with OAuth2/JWT token flows.

  Scenario: Get auth headers
    * def credentials = __arg || {}
    * def username = credentials.username || 'default_user'
    * def password = credentials.password || 'default_pass'

    # Simulate a login call that returns a token
    # In a real API, this would POST to /auth/login or /oauth/token
    * def token = 'eyJhbGciOiJIUzI1NiJ9.' + java.util.Base64.getEncoder().encodeToString((username + ':' + new Date().getTime()).getBytes()) + '.mock-signature'

    * def authHeaders =
      """
      {
        'Authorization': '#("Bearer " + token)',
        'X-Authenticated-User': '#(username)'
      }
      """
