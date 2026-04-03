from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from db.database import Base

CATEGORIES = [
    "Elektronik",
    "Bueromaterial",
    "Moebel",
    "Software-Lizenzen",
    "Netzwerk",
    "Peripherie",
]


def _utcnow():
    return datetime.now(timezone.utc)


ROLES = ["admin", "staff", "viewer"]


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="viewer")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=_utcnow)

    __table_args__ = (
        CheckConstraint(
            f"role IN ({', '.join(repr(r) for r in ROLES)})",
            name="valid_role",
        ),
    )


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    country = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    products = relationship("Product", back_populates="supplier")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    unit_price = Column(Float, nullable=False)
    reorder_level = Column(Integer, nullable=False, default=10)
    current_stock = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    supplier = relationship("Supplier", back_populates="products")
    movements = relationship("StockMovement", back_populates="product")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    movement_type = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    reference = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    __table_args__ = (
        CheckConstraint("movement_type IN ('in', 'out')", name="valid_movement_type"),
        CheckConstraint("quantity > 0", name="positive_quantity"),
    )

    product = relationship("Product", back_populates="movements")
