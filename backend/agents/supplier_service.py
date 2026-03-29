from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.orm import Supplier, Product
from models.schemas import SupplierCreate, SupplierUpdate


def list_suppliers(db: Session, search: Optional[str] = None) -> list[Supplier]:
    """Return suppliers with optional name search."""
    query = db.query(Supplier)

    if search:
        pattern = f"%{search}%"
        query = query.filter(Supplier.name.ilike(pattern))

    return query.order_by(Supplier.name).all()


def get_supplier(db: Session, supplier_id: int) -> Supplier:
    """Return a single supplier or raise 404."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Lieferant nicht gefunden")
    return supplier


def create_supplier(db: Session, data: SupplierCreate) -> Supplier:
    """Create a new supplier."""
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def update_supplier(
    db: Session, supplier_id: int, data: SupplierUpdate
) -> Supplier:
    """Update an existing supplier."""
    supplier = get_supplier(db, supplier_id)
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)
    return supplier


def delete_supplier(db: Session, supplier_id: int) -> None:
    """Delete a supplier. Only allowed when no products are linked."""
    supplier = get_supplier(db, supplier_id)

    product_count = (
        db.query(Product).filter(Product.supplier_id == supplier_id).count()
    )
    if product_count > 0:
        raise HTTPException(
            status_code=409,
            detail="Lieferant kann nicht geloescht werden, solange Produkte zugeordnet sind",
        )

    db.delete(supplier)
    db.commit()
