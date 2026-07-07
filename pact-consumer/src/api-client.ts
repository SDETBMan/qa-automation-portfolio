const DEFAULT_BASE_URL = 'http://localhost:8001';

export interface Product {
  id: number;
  name: string;
  price: number;
  inventory: number;
}

export interface ProductCreate {
  name: string;
  price: number;
  inventory?: number;
}

export interface User {
  id: number;
  username: string;
  role: string;
}

export interface HealthResponse {
  status: string;
}

export interface ErrorResponse {
  detail: string;
}

export class ApiClient {
  constructor(private baseUrl: string = DEFAULT_BASE_URL) {}

  private async request<T>(path: string, options?: RequestInit): Promise<{ status: number; body: T }> {
    const res = await fetch(`${this.baseUrl}${path}`, options);
    const body = await res.json() as T;
    return { status: res.status, body };
  }

  async getHealth(): Promise<{ status: number; body: HealthResponse }> {
    return this.request<HealthResponse>('/health');
  }

  async getProducts(): Promise<{ status: number; body: Product[] }> {
    return this.request<Product[]>('/products');
  }

  async getProduct(id: number): Promise<{ status: number; body: Product | ErrorResponse }> {
    return this.request<Product | ErrorResponse>(`/products/${id}`);
  }

  async createProduct(product: ProductCreate): Promise<{ status: number; body: Product }> {
    return this.request<Product>('/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(product),
    });
  }

  async getUsers(): Promise<{ status: number; body: User[] }> {
    return this.request<User[]>('/users');
  }

  async getUser(id: number): Promise<{ status: number; body: User | ErrorResponse }> {
    return this.request<User | ErrorResponse>(`/users/${id}`);
  }
}
