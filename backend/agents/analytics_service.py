from datetime import datetime, timezone, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.orm import Product, StockMovement, Supplier
from models.schemas import AnalyticsResponse


def get_dashboard_analytics(db: Session) -> AnalyticsResponse:
    """Compute aggregate analytics for the dashboard."""

    # Total products
    total_products = db.query(func.count(Product.id)).scalar() or 0

    # Total stock value
    total_stock_value = (
        db.query(func.sum(Product.current_stock * Product.unit_price)).scalar() or 0.0
    )

    # Low stock count (current_stock <= reorder_level)
    low_stock_count = (
        db.query(func.count(Product.id))
        .filter(Product.current_stock <= Product.reorder_level)
        .scalar()
        or 0
    )

    # Movements today
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    total_movements_today = (
        db.query(func.count(StockMovement.id))
        .filter(StockMovement.created_at >= today_start)
        .scalar()
        or 0
    )

    # Stock by category
    category_rows = (
        db.query(
            Product.category,
            func.sum(Product.current_stock).label("total_stock"),
            func.sum(Product.current_stock * Product.unit_price).label("total_value"),
        )
        .group_by(Product.category)
        .all()
    )
    stock_by_category = [
        {
            "category": row.category,
            "total_stock": int(row.total_stock or 0),
            "total_value": round(float(row.total_value or 0), 2),
        }
        for row in category_rows
    ]

    # Top 10 products by stock value
    top_rows = (
        db.query(
            Product.id,
            Product.name,
            Product.sku,
            Product.current_stock,
            Product.unit_price,
            (Product.current_stock * Product.unit_price).label("stock_value"),
        )
        .order_by((Product.current_stock * Product.unit_price).desc())
        .limit(10)
        .all()
    )
    top_products = [
        {
            "id": row.id,
            "name": row.name,
            "sku": row.sku,
            "current_stock": row.current_stock,
            "unit_price": row.unit_price,
            "stock_value": round(float(row.stock_value or 0), 2),
        }
        for row in top_rows
    ]

    # Recent 10 movements
    recent_rows = (
        db.query(StockMovement)
        .order_by(StockMovement.created_at.desc())
        .limit(10)
        .all()
    )
    recent_movements = [
        {
            "id": m.id,
            "product_id": m.product_id,
            "product_name": m.product.name if m.product else None,
            "movement_type": m.movement_type,
            "quantity": m.quantity,
            "reference": m.reference,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in recent_rows
    ]

    return AnalyticsResponse(
        total_products=total_products,
        total_stock_value=round(total_stock_value, 2),
        low_stock_count=low_stock_count,
        total_movements_today=total_movements_today,
        stock_by_category=stock_by_category,
        top_products=top_products,
        recent_movements=recent_movements,
    )
