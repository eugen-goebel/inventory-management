"""CSV export service for products."""

import csv
import io
from typing import Optional

from sqlalchemy.orm import Session

from agents import product_service


CSV_COLUMNS = [
    "sku",
    "name",
    "category",
    "supplier_name",
    "unit_price",
    "current_stock",
    "reorder_level",
]


def export_products_to_csv(
    db: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    low_stock_only: bool = False,
) -> str:
    """Return a CSV string of products matching the given filters."""
    products = product_service.list_products(db, search, category, low_stock_only)

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS)
    writer.writeheader()

    for product in products:
        writer.writerow({
            "sku": product.sku,
            "name": product.name,
            "category": product.category,
            "supplier_name": product.supplier.name if product.supplier else "",
            "unit_price": f"{product.unit_price:.2f}",
            "current_stock": product.current_stock,
            "reorder_level": product.reorder_level,
        })

    return buffer.getvalue()
