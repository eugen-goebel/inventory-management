export interface Product {
  id: number;
  name: string;
  sku: string;
  category: string;
  supplier_id: number;
  supplier_name: string;
  unit_price: number;
  reorder_level: number;
  current_stock: number;
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  name: string;
  sku: string;
  category: string;
  supplier_id: number;
  unit_price: number;
  reorder_level: number;
}

export interface Movement {
  id: number;
  product_id: number;
  product_name: string;
  movement_type: "in" | "out";
  quantity: number;
  reference: string;
  notes: string;
  created_at: string;
}

export interface MovementCreate {
  product_id: number;
  movement_type: "in" | "out";
  quantity: number;
  reference: string;
  notes: string;
}

export interface Supplier {
  id: number;
  name: string;
  contact_email: string;
  phone: string;
  country: string;
  product_count: number;
  created_at: string;
}

export interface SupplierCreate {
  name: string;
  contact_email: string;
  phone: string;
  country: string;
}

export interface DashboardAnalytics {
  total_products: number;
  total_stock_value: number;
  low_stock_count: number;
  total_movements_today: number;
  stock_by_category: { category: string; total_stock: number; total_value: number }[];
  top_products: { name: string; current_stock: number; value: number }[];
  recent_movements: { product_name: string; movement_type: string; quantity: number; created_at: string }[];
}

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}
