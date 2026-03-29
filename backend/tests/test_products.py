"""Tests for product endpoints."""

import pytest


class TestListProducts:
    """GET /api/products"""

    def test_returns_list(self, client, seed_data):
        resp = client.get("/api/products")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 5

    def test_search_filters_by_name(self, client, seed_data):
        resp = client.get("/api/products", params={"search": "Laptop"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Laptop Pro 15"

    def test_search_filters_by_sku(self, client, seed_data):
        resp = client.get("/api/products", params={"search": "NK-001"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["sku"] == "NK-001"

    def test_filter_by_category(self, client, seed_data):
        resp = client.get("/api/products", params={"category": "Elektronik"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["category"] == "Elektronik"

    def test_filter_low_stock(self, client, seed_data):
        """Products where current_stock <= reorder_level should be returned."""
        resp = client.get("/api/products", params={"low_stock": "true"})
        assert resp.status_code == 200
        data = resp.json()
        # After seed movements:
        # Schreibtischstuhl: stock=5, reorder=10 -> low stock
        # USB-Maus: stock=10, reorder=20 -> low stock
        # Druckerpapier: stock=5, reorder=100 -> low stock
        assert len(data) >= 3
        for item in data:
            assert item["current_stock"] <= item["reorder_level"]


class TestGetProduct:
    """GET /api/products/{id}"""

    def test_returns_product(self, client, seed_data):
        product_id = seed_data["products"][0]["id"]
        resp = client.get(f"/api/products/{product_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == product_id
        assert data["name"] == "Laptop Pro 15"
        assert "supplier_name" in data

    def test_returns_404_for_missing(self, client):
        resp = client.get("/api/products/99999")
        assert resp.status_code == 404


class TestCreateProduct:
    """POST /api/products"""

    def test_creates_product(self, client, seed_data):
        payload = {
            "name": "Monitor 27 Zoll",
            "sku": "EL-002",
            "category": "Elektronik",
            "supplier_id": seed_data["suppliers"][0]["id"],
            "unit_price": 499.99,
            "reorder_level": 3,
        }
        resp = client.post("/api/products", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Monitor 27 Zoll"
        assert data["sku"] == "EL-002"
        assert data["current_stock"] == 0

    def test_rejects_duplicate_sku(self, client, seed_data):
        payload = {
            "name": "Anderes Produkt",
            "sku": "LP-001",  # already exists
            "category": "Elektronik",
            "unit_price": 100.00,
        }
        resp = client.post("/api/products", json=payload)
        assert resp.status_code == 409


class TestUpdateProduct:
    """PUT /api/products/{id}"""

    def test_updates_product(self, client, seed_data):
        product_id = seed_data["products"][0]["id"]
        resp = client.put(
            f"/api/products/{product_id}",
            json={"name": "Laptop Pro 15 (2025)"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Laptop Pro 15 (2025)"
        assert data["sku"] == "LP-001"  # unchanged

    def test_returns_404_for_missing(self, client):
        resp = client.put("/api/products/99999", json={"name": "Nope"})
        assert resp.status_code == 404


class TestDeleteProduct:
    """DELETE /api/products/{id}"""

    def test_delete_with_zero_stock_succeeds(self, client, seed_data):
        # Create a product with zero stock
        payload = {
            "name": "Zu loeschendes Produkt",
            "sku": "DEL-001",
            "category": "Elektronik",
            "unit_price": 10.00,
        }
        create_resp = client.post("/api/products", json=payload)
        assert create_resp.status_code == 201
        pid = create_resp.json()["id"]

        resp = client.delete(f"/api/products/{pid}")
        assert resp.status_code == 204

        # Confirm it is gone
        get_resp = client.get(f"/api/products/{pid}")
        assert get_resp.status_code == 404

    def test_delete_with_stock_fails(self, client, seed_data):
        # products[0] has stock > 0 after seed movements
        product_id = seed_data["products"][0]["id"]
        resp = client.delete(f"/api/products/{product_id}")
        assert resp.status_code == 409
