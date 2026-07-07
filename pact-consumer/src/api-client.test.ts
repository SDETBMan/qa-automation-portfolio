import { PactV4, MatchersV3 } from '@pact-foundation/pact';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, it, expect } from 'vitest';
import { ApiClient } from './api-client.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const { like, eachLike, integer, decimal, string } = MatchersV3;

const provider = new PactV4({
  consumer: 'pact-consumer',
  provider: 'fastapi-service',
  dir: path.resolve(__dirname, '..', 'pacts'),
});

describe('FastAPI Service Consumer Contract Tests', () => {
  // ── Health ──────────────────────────────────────────────────────────────
  describe('GET /health', () => {
    it('returns health status', async () => {
      await provider
        .addInteraction()
        .given('the service is running')
        .uponReceiving('a request for health status')
        .withRequest('GET', '/health')
        .willRespondWith(200, (_builder) => {
          _builder.jsonBody(like({ status: 'ok' }));
        })
        .executeTest(async (mockServer) => {
          const client = new ApiClient(mockServer.url);
          const { status, body } = await client.getHealth();
          expect(status).toBe(200);
          expect(body.status).toBe('ok');
        });
    });
  });

  // ── Products ────────────────────────────────────────────────────────────
  describe('GET /products', () => {
    it('returns a list of products', async () => {
      await provider
        .addInteraction()
        .given('products exist')
        .uponReceiving('a request for all products')
        .withRequest('GET', '/products')
        .willRespondWith(200, (_builder) => {
          _builder.jsonBody(
            eachLike({
              id: integer(1),
              name: string('Sauce Labs Backpack'),
              price: decimal(29.99),
              inventory: integer(100),
            })
          );
        })
        .executeTest(async (mockServer) => {
          const client = new ApiClient(mockServer.url);
          const { status, body } = await client.getProducts();
          expect(status).toBe(200);
          expect(Array.isArray(body)).toBe(true);
          expect(body.length).toBeGreaterThan(0);
          expect(body[0]).toHaveProperty('id');
          expect(body[0]).toHaveProperty('name');
          expect(body[0]).toHaveProperty('price');
          expect(body[0]).toHaveProperty('inventory');
        });
    });
  });

  describe('GET /products/:id', () => {
    it('returns a single product', async () => {
      await provider
        .addInteraction()
        .given('product with id 1 exists')
        .uponReceiving('a request for product 1')
        .withRequest('GET', '/products/1')
        .willRespondWith(200, (_builder) => {
          _builder.jsonBody(
            like({
              id: integer(1),
              name: string('Sauce Labs Backpack'),
              price: decimal(29.99),
              inventory: integer(100),
            })
          );
        })
        .executeTest(async (mockServer) => {
          const client = new ApiClient(mockServer.url);
          const { status, body } = await client.getProduct(1);
          expect(status).toBe(200);
          expect((body as any).id).toBe(1);
        });
    });

    it('returns 404 for non-existent product', async () => {
      await provider
        .addInteraction()
        .given('product with id 9999 does not exist')
        .uponReceiving('a request for non-existent product')
        .withRequest('GET', '/products/9999')
        .willRespondWith(404, (_builder) => {
          _builder.jsonBody(like({ detail: string('Product 9999 not found') }));
        })
        .executeTest(async (mockServer) => {
          const client = new ApiClient(mockServer.url);
          const { status, body } = await client.getProduct(9999);
          expect(status).toBe(404);
          expect((body as any).detail).toBeDefined();
        });
    });
  });

  describe('POST /products', () => {
    it('creates a new product', async () => {
      const newProduct = { name: 'Test Product', price: 19.99, inventory: 50 };

      await provider
        .addInteraction()
        .given('the service accepts new products')
        .uponReceiving('a request to create a product')
        .withRequest('POST', '/products', (_builder) => {
          _builder.headers({ 'Content-Type': 'application/json' });
          _builder.jsonBody(like(newProduct));
        })
        .willRespondWith(201, (_builder) => {
          _builder.jsonBody(
            like({
              id: integer(7),
              name: string('Test Product'),
              price: decimal(19.99),
              inventory: integer(50),
            })
          );
        })
        .executeTest(async (mockServer) => {
          const client = new ApiClient(mockServer.url);
          const { status, body } = await client.createProduct(newProduct);
          expect(status).toBe(201);
          expect(body.id).toBeDefined();
          expect(body.name).toBe('Test Product');
          expect(body.price).toBe(19.99);
        });
    });
  });

  // ── Users ───────────────────────────────────────────────────────────────
  describe('GET /users', () => {
    it('returns a list of users', async () => {
      await provider
        .addInteraction()
        .given('users exist')
        .uponReceiving('a request for all users')
        .withRequest('GET', '/users')
        .willRespondWith(200, (_builder) => {
          _builder.jsonBody(
            eachLike({
              id: integer(1),
              username: string('standard_user'),
              role: string('standard_user'),
            })
          );
        })
        .executeTest(async (mockServer) => {
          const client = new ApiClient(mockServer.url);
          const { status, body } = await client.getUsers();
          expect(status).toBe(200);
          expect(Array.isArray(body)).toBe(true);
          expect(body.length).toBeGreaterThan(0);
          expect(body[0]).toHaveProperty('id');
          expect(body[0]).toHaveProperty('username');
          expect(body[0]).toHaveProperty('role');
        });
    });
  });

  describe('GET /users/:id', () => {
    it('returns a single user', async () => {
      await provider
        .addInteraction()
        .given('user with id 1 exists')
        .uponReceiving('a request for user 1')
        .withRequest('GET', '/users/1')
        .willRespondWith(200, (_builder) => {
          _builder.jsonBody(
            like({
              id: integer(1),
              username: string('standard_user'),
              role: string('standard_user'),
            })
          );
        })
        .executeTest(async (mockServer) => {
          const client = new ApiClient(mockServer.url);
          const { status, body } = await client.getUser(1);
          expect(status).toBe(200);
          expect((body as any).id).toBe(1);
        });
    });

    it('returns 404 for non-existent user', async () => {
      await provider
        .addInteraction()
        .given('user with id 9999 does not exist')
        .uponReceiving('a request for non-existent user')
        .withRequest('GET', '/users/9999')
        .willRespondWith(404, (_builder) => {
          _builder.jsonBody(like({ detail: string('User 9999 not found') }));
        })
        .executeTest(async (mockServer) => {
          const client = new ApiClient(mockServer.url);
          const { status, body } = await client.getUser(9999);
          expect(status).toBe(404);
          expect((body as any).detail).toBeDefined();
        });
    });
  });
});
