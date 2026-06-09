from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------


class ProductCreate(BaseModel):
    name: str
    sku: str
    category: str
    supplier_id: int | None = None
    unit_price: float = Field(gt=0)
    reorder_level: int = Field(ge=0, default=10)


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    category: str | None = None
    supplier_id: int | None = None
    unit_price: float | None = Field(default=None, gt=0)
    reorder_level: int | None = Field(default=None, ge=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    category: str
    supplier_id: int | None
    supplier_name: str | None
    unit_price: float
    reorder_level: int
    current_stock: int
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class PaginatedProductsResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    limit: int
    offset: int


# ---------------------------------------------------------------------------
# Stock Movement
# ---------------------------------------------------------------------------


class MovementCreate(BaseModel):
    product_id: int
    movement_type: Literal["in", "out"]
    quantity: int = Field(gt=0)
    reference: str | None = None
    notes: str | None = None


class MovementResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    movement_type: str
    quantity: int
    reference: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Supplier
# ---------------------------------------------------------------------------


class SupplierCreate(BaseModel):
    name: str
    contact_email: str | None = None
    phone: str | None = None
    country: str | None = None


class SupplierUpdate(BaseModel):
    name: str | None = None
    contact_email: str | None = None
    phone: str | None = None
    country: str | None = None


class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_email: str | None
    phone: str | None
    country: str | None
    product_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------


class AnalyticsResponse(BaseModel):
    total_products: int
    total_stock_value: float
    low_stock_count: int
    total_movements_today: int
    stock_by_category: list[dict]
    top_products: list[dict]
    recent_movements: list[dict]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=6, max_length=128)
    role: Literal["admin", "staff", "viewer"] = "viewer"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
