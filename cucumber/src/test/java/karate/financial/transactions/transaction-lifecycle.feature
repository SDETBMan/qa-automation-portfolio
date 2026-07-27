@financial @transactions
Feature: Transaction Lifecycle
  End-to-end payment transaction flow using Karate's built-in mock server.
  Validates state machine: PENDING -> AUTHORIZED -> CAPTURED -> REFUNDED.

  Background:
    * def mockPort = karate.start('classpath:karate/financial/mock/payment-mock.feature').port
    * url 'http://localhost:' + mockPort

  Scenario: Full transaction lifecycle - PENDING to REFUNDED
    # Step 1: Create a new transaction (PENDING)
    Given path '/api/transactions'
    And request { amount: 99.99, currency: 'USD' }
    When method post
    Then status 201
    And match response.status == 'PENDING'
    And match response.amount == 99.99
    * def txnId = response.id

    # Step 2: Authorize the transaction
    Given path '/api/transactions', txnId, 'authorize'
    When method post
    Then status 200
    And match response.status == 'AUTHORIZED'

    # Step 3: Capture the authorized transaction
    Given path '/api/transactions', txnId, 'capture'
    When method post
    Then status 200
    And match response.status == 'CAPTURED'

    # Step 4: Refund the captured transaction
    Given path '/api/transactions', txnId, 'refund'
    When method post
    Then status 200
    And match response.status == 'REFUNDED'

  Scenario: Cannot capture a PENDING transaction (invalid state transition)
    Given path '/api/transactions'
    And request { amount: 50.00 }
    When method post
    Then status 201
    * def txnId = response.id

    # Attempt to capture without authorizing first
    Given path '/api/transactions', txnId, 'capture'
    When method post
    Then status 409
    And match response.error == 'Invalid state transition'
    And match response.currentStatus == 'PENDING'

  Scenario: Cannot refund an AUTHORIZED transaction (must capture first)
    Given path '/api/transactions'
    And request { amount: 75.00 }
    When method post
    Then status 201
    * def txnId = response.id

    Given path '/api/transactions', txnId, 'authorize'
    When method post
    Then status 200

    # Attempt to refund without capturing
    Given path '/api/transactions', txnId, 'refund'
    When method post
    Then status 409
    And match response.currentStatus == 'AUTHORIZED'

  Scenario: GET a non-existent transaction returns 404
    Given path '/api/transactions/nonexistent'
    When method get
    Then status 404
    And match response.error == 'Transaction not found'
