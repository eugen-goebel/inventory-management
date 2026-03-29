from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.orm import Product
from models.schemas import ProductCreate, ProductUpdate


def list_products(
    db: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    low_stock_only: bool = False,
) -> list[Product]:
    """Return products with optional filtering."""
    query = db.query(Product)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(pattern)) | (Product.sku.ilike(pattern))
        )

    if category:
        query = query.filter(Product.category == category)

    if low_stock_only:
        query = query.filter(Product.current_stock <= Product.reorder_level)

    return query.order_by(Product.name).all()


def get_product(db: Session, product_id: int) -> Product:
    """Return a single product or raise 404."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    return product


def create_product(db: Session, data: ProductCreate) -> Product:
    """Create a new product. Raises 409 if SKU already exists."""
    existing = db.query(Product).filter(Product.sku == data.sku).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"SKU '{data.sku}' ist bereits vergeben",
        )

    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    """Update an existing product. Validates unique SKU if changed."""
    product = get_product(db, product_id)
    update_data = data.model_dump(exclude_unset=True)

    if "sku" in update_data and update_data["sku"] != product.sku:
        existing = db.query(Product).filter(Product.sku == update_data["sku"]).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"SKU '{update_data['sku']}' ist bereits vergeben",
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    """Delete a product. Only allowed when current_stock is 0."""
    product = get_product(db, product_id)

    if product.current_stock != 0:
        raise HTTPException(
            status_code=409,
            detail="Produkt kann nicht geloescht werden, solange Bestand vorhanden ist",
        )

    db.delete(product)
    db.commit()
