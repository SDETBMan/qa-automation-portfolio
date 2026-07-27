@ignore
Feature: Payment Processing Mock Server
  Stateful mock server simulating a payment gateway.
  Provides transaction lifecycle and pricing endpoints.
  Started by Karate's built-in mock server — no external dependencies.

  Background:
    * def transactions = {}
    * def nextId = { value: 1000 }

  # ── Transaction Endpoints ──────────────────────────────────────────

  Scenario: pathMatches('/api/transactions') && methodIs('post')
    * def txnId = '' + nextId.value
    * eval nextId.value = nextId.value + 1
    * def txn =
      """
      {
        id: '#(txnId)',
        amount: '#(request.amount)',
        currency: '#(request.currency || "USD")',
        status: 'PENDING',
        createdAt: '#(new Date().toISOString())'
      }
      """
    * eval transactions[txnId] = txn
    * def response = txn
    * def responseStatus = 201

  Scenario: pathMatches('/api/transactions/{id}') && methodIs('get')
    * def txn = transactions[pathParams.id]
    * def responseStatus = txn ? 200 : 404
    * def response = txn || { error: 'Transaction not found' }

  Scenario: pathMatches('/api/transactions/{id}/authorize') && methodIs('post')
    * def txn = transactions[pathParams.id]
    * def result = {}
    * eval if (txn == null) { result.status = 404; result.body = { error: 'Transaction not found' } } else if (txn.status != 'PENDING') { result.status = 409; result.body = { error: 'Invalid state transition', currentStatus: txn.status } } else { txn.status = 'AUTHORIZED'; result.status = 200; result.body = txn }
    * def responseStatus = result.status
    * def response = result.body

  Scenario: pathMatches('/api/transactions/{id}/capture') && methodIs('post')
    * def txn = transactions[pathParams.id]
    * def result = {}
    * eval if (txn == null) { result.status = 404; result.body = { error: 'Transaction not found' } } else if (txn.status != 'AUTHORIZED') { result.status = 409; result.body = { error: 'Invalid state transition', currentStatus: txn.status } } else { txn.status = 'CAPTURED'; result.status = 200; result.body = txn }
    * def responseStatus = result.status
    * def response = result.body

  Scenario: pathMatches('/api/transactions/{id}/refund') && methodIs('post')
    * def txn = transactions[pathParams.id]
    * def result = {}
    * eval if (txn == null) { result.status = 404; result.body = { error: 'Transaction not found' } } else if (txn.status != 'CAPTURED') { result.status = 409; result.body = { error: 'Invalid state transition', currentStatus: txn.status } } else { txn.status = 'REFUNDED'; result.status = 200; result.body = txn }
    * def responseStatus = result.status
    * def response = result.body

  # ── Pricing Endpoints ──────────────────────────────────────────────

  Scenario: pathMatches('/api/pricing/calculate') && methodIs('post')
    * def subtotal = request.amount || 0
    * def taxRate = request.taxRate || 0.08
    * def discountPct = request.discountPercent || 0
    * def discount = Math.round(subtotal * discountPct * 100) / 100
    * def taxable = subtotal - discount
    * def tax = Math.round(taxable * taxRate * 100) / 100
    * def total = Math.round((taxable + tax) * 100) / 100
    * def response =
      """
      {
        subtotal: '#(subtotal)',
        discount: '#(discount)',
        taxable: '#(taxable)',
        tax: '#(tax)',
        total: '#(total)',
        currency: '#(request.currency || "USD")'
      }
      """
    * def responseStatus = 200

  # ── Catch-all ──────────────────────────────────────────────────────

  Scenario:
    * def responseStatus = 404
    * def response = { error: 'Endpoint not found' }
