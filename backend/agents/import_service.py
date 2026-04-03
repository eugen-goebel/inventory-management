"""CSV import service for bulk product creation."""

import csv
import io
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from models.orm import Product
from models.schemas import ProductCreate


MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_ROW_COUNT = 10_000

REQUIRED_COLUMNS = {"name", "sku", "category", "unit_price"}
OPTIONAL_COLUMNS = {"supplier_id", "reorder_level"}
ALL_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS


@dataclass
class ImportResult:
    imported: int = 0
    skipped: int = 0
    errors: list[dict] = field(default_factory=list)


def _sanitize(value: str) -> str:
    """Strip whitespace and remove potentially dangerous characters."""
    return value.strip().replace("\x00", "")


def import_products_from_csv(db: Session, content: bytes) -> ImportResult:
    """
    Parse a CSV byte payload and import valid rows as products.

    Expected columns: name, sku, category, unit_price
    Optional columns: supplier_id, reorder_level

    Skips rows with validation errors or duplicate SKUs.
    """
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds maximum size of {MAX_FILE_SIZE // (1024 * 1024)} MB")

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))

    if reader.fieldnames is None:
        raise ValueError("CSV file is empty or has no header row")

    headers = {h.strip().lower() for h in reader.fieldnames}
    missing = REQUIRED_COLUMNS - headers
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    result = ImportResult()
    existing_skus = {p.sku for p in db.query(Product.sku).all()}

    for row_num, row in enumerate(reader, start=2):
        if row_num - 1 > MAX_ROW_COUNT:
            result.errors.append({"row": row_num, "error": f"Exceeded maximum of {MAX_ROW_COUNT} rows"})
            break

        # Normalize keys
        row = {k.strip().lower(): _sanitize(v) if v else "" for k, v in row.items()}

        name = row.get("name", "").strip()
        sku = row.get("sku", "").strip()
        category = row.get("category", "").strip()
        price_str = row.get("unit_price", "").strip()

        # Validate required fields
        if not name or not sku or not category or not price_str:
            result.errors.append({"row": row_num, "error": "Missing required field(s)"})
            result.skipped += 1
            continue

        # Validate price
        try:
            unit_price = float(price_str)
            if unit_price <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            result.errors.append({"row": row_num, "error": f"Invalid unit_price: {price_str}"})
            result.skipped += 1
            continue

        # Check duplicate SKU
        if sku in existing_skus:
            result.errors.append({"row": row_num, "error": f"Duplicate SKU: {sku}"})
            result.skipped += 1
            continue

        # Optional fields
        supplier_id = None
        if row.get("supplier_id"):
            try:
                supplier_id = int(row["supplier_id"])
            except (ValueError, TypeError):
                result.errors.append({"row": row_num, "error": f"Invalid supplier_id: {row['supplier_id']}"})
                result.skipped += 1
                continue

        reorder_level = 10  # default
        if row.get("reorder_level"):
            try:
                reorder_level = int(row["reorder_level"])
                if reorder_level < 0:
                    raise ValueError()
            except (ValueError, TypeError):
                result.errors.append({"row": row_num, "error": f"Invalid reorder_level: {row['reorder_level']}"})
                result.skipped += 1
                continue

        product = Product(
            name=name,
            sku=sku,
            category=category,
            supplier_id=supplier_id,
            unit_price=unit_price,
            reorder_level=reorder_level,
        )
        db.add(product)
        existing_skus.add(sku)
        result.imported += 1

    if result.imported > 0:
        db.commit()

    return result
