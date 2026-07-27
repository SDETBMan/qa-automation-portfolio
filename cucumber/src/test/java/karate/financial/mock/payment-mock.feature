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
    * if (txn == null) { def responseStatus = 404; def response = { error: 'Transaction not found' } }
    * if (txn != null && txn.status != 'PENDING') { def responseStatus = 409; def response = { error: 'Invalid state transition', currentStatus: txn.status } }
    * if (txn != null && txn.status == 'PENDING') { eval txn.status = 'AUTHORIZED'; def responseStatus = 200; def response = txn }

  Scenario: pathMatches('/api/transactions/{id}/capture') && methodIs('post')
    * def txn = transactions[pathParams.id]
    * if (txn == null) { def responseStatus = 404; def response = { error: 'Transaction not found' } }
    * if (txn != null && txn.status != 'AUTHORIZED') { def responseStatus = 409; def response = { error: 'Invalid state transition', currentStatus: txn.status } }
    * if (txn != null && txn.status == 'AUTHORIZED') { eval txn.status = 'CAPTURED'; def responseStatus = 200; def response = txn }

  Scenario: pathMatches('/api/transactions/{id}/refund') && methodIs('post')
    * def txn = transactions[pathParams.id]
    * if (txn == null) { def responseStatus = 404; def response = { error: 'Transaction not found' } }
    * if (txn != null && txn.status != 'CAPTURED') { def responseStatus = 409; def response = { error: 'Invalid state transition', currentStatus: txn.status } }
    * if (txn != null && txn.status == 'CAPTURED') { eval txn.status = 'REFUNDED'; def responseStatus = 200; def response = txn }

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
