from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.database import get_db
from models.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    MovementCreate,
    MovementResponse,
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    AnalyticsResponse,
)
from agents import product_service, movement_service, supplier_service, analytics_service

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

product_router = APIRouter(prefix="/api/products", tags=["Products"])
movement_router = APIRouter(prefix="/api/movements", tags=["Movements"])
supplier_router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])
analytics_router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# ---------------------------------------------------------------------------
# Helper: build response dicts that include joined fields
# ---------------------------------------------------------------------------

def _product_response(product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "category": product.category,
        "supplier_id": product.supplier_id,
        "supplier_name": product.supplier.name if product.supplier else None,
        "unit_price": product.unit_price,
        "reorder_level": product.reorder_level,
        "current_stock": product.current_stock,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }


def _movement_response(movement) -> dict:
    return {
        "id": movement.id,
        "product_id": movement.product_id,
        "product_name": movement.product.name if movement.product else None,
        "movement_type": movement.movement_type,
        "quantity": movement.quantity,
        "reference": movement.reference,
        "notes": movement.notes,
        "created_at": movement.created_at,
    }


def _supplier_response(supplier) -> dict:
    return {
        "id": supplier.id,
        "name": supplier.name,
        "contact_email": supplier.contact_email,
        "phone": supplier.phone,
        "country": supplier.country,
        "product_count": len(supplier.products) if supplier.products else 0,
        "created_at": supplier.created_at,
    }


# ---------------------------------------------------------------------------
# Product endpoints
# ---------------------------------------------------------------------------

@product_router.get("", response_model=list[ProductResponse])
def list_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    low_stock: bool = Query(False),
    db: Session = Depends(get_db),
):
    products = product_service.list_products(db, search, category, low_stock)
    return [_product_response(p) for p in products]


@product_router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product(db, product_id)
    return _product_response(product)


@product_router.post("", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    product = product_service.create_product(db, data)
    return _product_response(product)


@product_router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, data: ProductUpdate, db: Session = Depends(get_db)
):
    product = product_service.update_product(db, product_id, data)
    return _product_response(product)


@product_router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product_service.delete_product(db, product_id)


# ---------------------------------------------------------------------------
# Movement endpoints
# ---------------------------------------------------------------------------

@movement_router.get("", response_model=list[MovementResponse])
def list_movements(
    product_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    movements = movement_service.list_movements(db, product_id, type, limit)
    return [_movement_response(m) for m in movements]


@movement_router.post("", response_model=MovementResponse, status_code=201)
def create_movement(data: MovementCreate, db: Session = Depends(get_db)):
    movement = movement_service.create_movement(db, data)
    return _movement_response(movement)


# ---------------------------------------------------------------------------
# Supplier endpoints
# ---------------------------------------------------------------------------

@supplier_router.get("", response_model=list[SupplierResponse])
def list_suppliers(
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    suppliers = supplier_service.list_suppliers(db, search)
    return [_supplier_response(s) for s in suppliers]


@supplier_router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = supplier_service.get_supplier(db, supplier_id)
    return _supplier_response(supplier)


@supplier_router.post("", response_model=SupplierResponse, status_code=201)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    supplier = supplier_service.create_supplier(db, data)
    return _supplier_response(supplier)


@supplier_router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int, data: SupplierUpdate, db: Session = Depends(get_db)
):
    supplier = supplier_service.update_supplier(db, supplier_id, data)
    return _supplier_response(supplier)


@supplier_router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier_service.delete_supplier(db, supplier_id)


# ---------------------------------------------------------------------------
# Analytics endpoints
# ---------------------------------------------------------------------------

@analytics_router.get("/dashboard", response_model=AnalyticsResponse)
def dashboard_analytics(db: Session = Depends(get_db)):
    return analytics_service.get_dashboard_analytics(db)
