import sys
import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Ensure the backend package is importable
BACKEND_DIR = str(Path(__file__).resolve().parent.parent)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from db.database import Base, get_db
from models.orm import Product, Supplier, StockMovement, User  # noqa: F401 — import to register with Base
from agents.auth_service import hash_password, create_access_token
from main import app

# Ensure all ORM models are registered before create_all
assert User.__tablename__ == "users"


@pytest.fixture(scope="function")
def db_session(tmp_path):
    """Create a fresh in-memory SQLite database for each test."""
    db_url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


class AuthenticatedTestClient:
    """Wraps TestClient to inject an Authorization header on every request."""

    def __init__(self, tc: TestClient, token: str):
        self._tc = tc
        self._headers = {"Authorization": f"Bearer {token}"}

    def _merge(self, kwargs):
        headers = {**self._headers, **(kwargs.pop("headers", {}) or {})}
        kwargs["headers"] = headers
        return kwargs

    def get(self, url, **kw):
        return self._tc.get(url, **self._merge(kw))

    def post(self, url, **kw):
        return self._tc.post(url, **self._merge(kw))

    def put(self, url, **kw):
        return self._tc.put(url, **self._merge(kw))

    def delete(self, url, **kw):
        return self._tc.delete(url, **self._merge(kw))


@pytest.fixture(scope="function")
def raw_client(db_session):
    """Unauthenticated FastAPI TestClient for auth-specific tests."""

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with admin auth (backwards-compatible with existing tests)."""

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    # Create an admin user for existing tests
    admin = User(
        username="testadmin",
        email="testadmin@test.com",
        hashed_password=hash_password("testpass"),
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    token = create_access_token(admin.id, admin.username, admin.role)

    with TestClient(app) as tc:
        yield AuthenticatedTestClient(tc, token)
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_user(db_session):
    """Create an admin user and return (user, token)."""
    user = User(
        username="admin",
        email="admin@test.com",
        hashed_password=hash_password("adminpass"),
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user.id, user.username, user.role)
    return user, token


@pytest.fixture()
def staff_user(db_session):
    """Create a staff user and return (user, token)."""
    user = User(
        username="staff",
        email="staff@test.com",
        hashed_password=hash_password("staffpass"),
        role="staff",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user.id, user.username, user.role)
    return user, token


@pytest.fixture()
def viewer_user(db_session):
    """Create a viewer user and return (user, token)."""
    user = User(
        username="viewer",
        email="viewer@test.com",
        hashed_password=hash_password("viewerpass"),
        role="viewer",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(user.id, user.username, user.role)
    return user, token


def auth_header(token: str) -> dict:
    """Build an Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def seed_data(client, db_session):
    """
    Seed the test database with sample data:
    - 3 suppliers
    - 5 products (across different categories, some low-stock)
    - 10 stock movements
    Returns a dict with created IDs for easy reference.
    """
    suppliers = []
    supplier_payloads = [
        {"name": "TechDistri GmbH", "contact_email": "info@techdistri.de", "phone": "+49 30 12345", "country": "Deutschland"},
        {"name": "OfficeWorld AG", "contact_email": "kontakt@officeworld.de", "phone": "+49 40 67890", "country": "Deutschland"},
        {"name": "NetParts Ltd", "contact_email": "sales@netparts.co.uk", "phone": "+44 20 55555", "country": "UK"},
    ]
    for payload in supplier_payloads:
        resp = client.post("/api/suppliers", json=payload)
        assert resp.status_code == 201
        suppliers.append(resp.json())

    products = []
    product_payloads = [
        {"name": "Laptop Pro 15", "sku": "LP-001", "category": "Elektronik", "supplier_id": suppliers[0]["id"], "unit_price": 1299.99, "reorder_level": 5},
        {"name": "Schreibtischstuhl Ergo", "sku": "MS-001", "category": "Moebel", "supplier_id": suppliers[1]["id"], "unit_price": 349.00, "reorder_level": 10},
        {"name": "Cat6 Kabel 5m", "sku": "NK-001", "category": "Netzwerk", "supplier_id": suppliers[2]["id"], "unit_price": 8.50, "reorder_level": 50},
        {"name": "USB-Maus Wireless", "sku": "PE-001", "category": "Peripherie", "supplier_id": suppliers[0]["id"], "unit_price": 24.99, "reorder_level": 20},
        {"name": "Druckerpapier A4 500 Blatt", "sku": "BM-001", "category": "Bueromaterial", "supplier_id": suppliers[1]["id"], "unit_price": 4.99, "reorder_level": 100},
    ]
    for payload in product_payloads:
        resp = client.post("/api/products", json=payload)
        assert resp.status_code == 201
        products.append(resp.json())

    # Create 10 stock movements (all "in" first to build up stock)
    movements = []
    movement_payloads = [
        {"product_id": products[0]["id"], "movement_type": "in", "quantity": 20, "reference": "PO-1001", "notes": "Erstlieferung"},
        {"product_id": products[1]["id"], "movement_type": "in", "quantity": 15, "reference": "PO-1002"},
        {"product_id": products[2]["id"], "movement_type": "in", "quantity": 200, "reference": "PO-1003"},
        {"product_id": products[3]["id"], "movement_type": "in", "quantity": 50, "reference": "PO-1004"},
        {"product_id": products[4]["id"], "movement_type": "in", "quantity": 80, "reference": "PO-1005"},
        {"product_id": products[0]["id"], "movement_type": "out", "quantity": 3, "reference": "SO-2001"},
        {"product_id": products[1]["id"], "movement_type": "out", "quantity": 10, "reference": "SO-2002"},
        {"product_id": products[2]["id"], "movement_type": "in", "quantity": 100, "reference": "PO-1006"},
        {"product_id": products[3]["id"], "movement_type": "out", "quantity": 40, "reference": "SO-2003"},
        {"product_id": products[4]["id"], "movement_type": "out", "quantity": 75, "reference": "SO-2004"},
    ]
    for payload in movement_payloads:
        resp = client.post("/api/movements", json=payload)
        assert resp.status_code == 201
        movements.append(resp.json())

    return {
        "suppliers": suppliers,
        "products": products,
        "movements": movements,
    }
