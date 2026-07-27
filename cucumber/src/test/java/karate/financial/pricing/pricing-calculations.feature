@financial @pricing
Feature: Pricing Calculations
  Validates tax and discount calculations using the mock pricing engine.
  Demonstrates Scenario Outline for parameterized financial calculations.

  Background:
    * def mockPort = karate.start('classpath:karate/financial/mock/payment-mock.feature').port
    * url 'http://localhost:' + mockPort

  Scenario Outline: Tax calculation with varying rates
    Given path '/api/pricing/calculate'
    And request { amount: <amount>, taxRate: <taxRate>, discountPercent: 0, currency: 'USD' }
    When method post
    Then status 200
    And match response.subtotal == <amount>
    And match response.discount == 0
    And match response.tax == <expectedTax>
    And match response.total == <expectedTotal>

    Examples:
      | amount | taxRate | expectedTax | expectedTotal |
      | 100.00 | 0.08   | 8.0         | 108.0         |
      | 100.00 | 0.10   | 10.0        | 110.0         |
      | 250.00 | 0.07   | 17.5        | 267.5         |
      | 49.99  | 0.08   | 4.0         | 53.99         |

  Scenario Outline: Discount and tax combined
    Given path '/api/pricing/calculate'
    And request { amount: <amount>, taxRate: <taxRate>, discountPercent: <discount>, currency: 'USD' }
    When method post
    Then status 200
    And match response.subtotal == <amount>
    And match response.total == '#number'
    # Verify discount reduces the taxable amount
    And assert response.taxable < response.subtotal || <discount> == 0

    Examples:
      | amount | taxRate | discount |
      | 200.00 | 0.08   | 0.10     |
      | 500.00 | 0.10   | 0.20     |
      | 100.00 | 0.05   | 0.50     |
