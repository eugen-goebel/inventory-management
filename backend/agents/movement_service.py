from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.orm import StockMovement, Product
from models.schemas import MovementCreate


def create_movement(db: Session, data: MovementCreate) -> StockMovement:
    """
    Record a stock movement and update the product's current_stock.
    Raises 404 if the product does not exist.
    Raises 409 if an 'out' movement would result in negative stock.
    """
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

    if data.movement_type == "out":
        if product.current_stock < data.quantity:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Nicht genuegend Bestand. "
                    f"Verfuegbar: {product.current_stock}, Angefragt: {data.quantity}"
                ),
            )
        product.current_stock -= data.quantity
    else:
        product.current_stock += data.quantity

    db.add(product)
    movement = StockMovement(**data.model_dump())
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


def list_movements(
    db: Session,
    product_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    limit: int = 50,
) -> list[StockMovement]:
    """Return stock movements with optional filtering."""
    query = db.query(StockMovement)

    if product_id is not None:
        query = query.filter(StockMovement.product_id == product_id)

    if movement_type is not None:
        query = query.filter(StockMovement.movement_type == movement_type)

    return query.order_by(StockMovement.created_at.desc()).limit(limit).all()


def get_movement(db: Session, movement_id: int) -> StockMovement:
    """Return a single movement or raise 404."""
    movement = (
        db.query(StockMovement).filter(StockMovement.id == movement_id).first()
    )
    if not movement:
        raise HTTPException(status_code=404, detail="Bewegung nicht gefunden")
    return movement
