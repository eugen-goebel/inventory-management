import type {
  Product,
  ProductCreate,
  Movement,
  MovementCreate,
  Supplier,
  SupplierCreate,
  DashboardAnalytics,
} from "../types";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(body || res.statusText, res.status);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

async function get<T>(url: string): Promise<T> {
  return request<T>(url);
}

async function post<T>(url: string, body: unknown): Promise<T> {
  return request<T>(url, { method: "POST", body: JSON.stringify(body) });
}

async function put<T>(url: string, body: unknown): Promise<T> {
  return request<T>(url, { method: "PUT", body: JSON.stringify(body) });
}

async function del(url: string): Promise<void> {
  await request<void>(url, { method: "DELETE" });
}

// Products

export function fetchProducts(params?: {
  search?: string;
  category?: string;
  low_stock?: boolean;
}): Promise<Product[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set("search", params.search);
  if (params?.category) query.set("category", params.category);
  if (params?.low_stock) query.set("low_stock", "true");
  const qs = query.toString();
  return get<Product[]>(`/api/products${qs ? `?${qs}` : ""}`);
}

export function fetchProduct(id: number): Promise<Product> {
  return get<Product>(`/api/products/${id}`);
}

export function createProduct(data: ProductCreate): Promise<Product> {
  return post<Product>("/api/products", data);
}

export function updateProduct(
  id: number,
  data: ProductCreate
): Promise<Product> {
  return put<Product>(`/api/products/${id}`, data);
}

export function deleteProduct(id: number): Promise<void> {
  return del(`/api/products/${id}`);
}

export interface ImportResult {
  imported: number;
  skipped: number;
  errors: { row: number; error: string }[];
}

export async function importProductsCsv(file: File): Promise<ImportResult> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch("/api/products/import", {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new ApiError(body || res.statusText, res.status);
  }
  return res.json();
}

// Movements

export function fetchMovements(params?: {
  product_id?: number;
  movement_type?: string;
}): Promise<Movement[]> {
  const query = new URLSearchParams();
  if (params?.product_id) query.set("product_id", String(params.product_id));
  if (params?.movement_type && params.movement_type !== "all")
    query.set("type", params.movement_type);
  const qs = query.toString();
  return get<Movement[]>(`/api/movements${qs ? `?${qs}` : ""}`);
}

export function createMovement(data: MovementCreate): Promise<Movement> {
  return post<Movement>("/api/movements", data);
}

// Suppliers

export function fetchSuppliers(params?: {
  search?: string;
}): Promise<Supplier[]> {
  const query = new URLSearchParams();
  if (params?.search) query.set("search", params.search);
  const qs = query.toString();
  return get<Supplier[]>(`/api/suppliers${qs ? `?${qs}` : ""}`);
}

export function fetchSupplier(id: number): Promise<Supplier> {
  return get<Supplier>(`/api/suppliers/${id}`);
}

export function createSupplier(data: SupplierCreate): Promise<Supplier> {
  return post<Supplier>("/api/suppliers", data);
}

export function updateSupplier(
  id: number,
  data: SupplierCreate
): Promise<Supplier> {
  return put<Supplier>(`/api/suppliers/${id}`, data);
}

export function deleteSupplier(id: number): Promise<void> {
  return del(`/api/suppliers/${id}`);
}

// Analytics

export function fetchAnalytics(): Promise<DashboardAnalytics> {
  return get<DashboardAnalytics>("/api/analytics/dashboard");
}

export { ApiError };
