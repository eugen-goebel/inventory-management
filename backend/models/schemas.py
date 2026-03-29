from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------

class ProductCreate(BaseModel):
    name: str
    sku: str
    category: str
    supplier_id: Optional[int] = None
    unit_price: float = Field(gt=0)
    reorder_level: int = Field(ge=0, default=10)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    supplier_id: Optional[int] = None
    unit_price: Optional[float] = Field(default=None, gt=0)
    reorder_level: Optional[int] = Field(default=None, ge=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    category: str
    supplier_id: Optional[int]
    supplier_name: Optional[str]
    unit_price: float
    reorder_level: int
    current_stock: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Stock Movement
# ---------------------------------------------------------------------------

class MovementCreate(BaseModel):
    product_id: int
    movement_type: Literal["in", "out"]
    quantity: int = Field(gt=0)
    reference: Optional[str] = None
    notes: Optional[str] = None


class MovementResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    movement_type: str
    quantity: int
    reference: Optional[str]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Supplier
# ---------------------------------------------------------------------------

class SupplierCreate(BaseModel):
    name: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None


class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_email: Optional[str]
    phone: Optional[str]
    country: Optional[str]
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
