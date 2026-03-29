"""Tests for stock movement endpoints."""

import pytest


class TestListMovements:
    """GET /api/movements"""

    def test_returns_list(self, client, seed_data):
        resp = client.get("/api/movements")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 10

    def test_filter_by_product_id(self, client, seed_data):
        product_id = seed_data["products"][0]["id"]
        resp = client.get("/api/movements", params={"product_id": product_id})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2
        for m in data:
            assert m["product_id"] == product_id

    def test_filter_by_type_in(self, client, seed_data):
        resp = client.get("/api/movements", params={"type": "in"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        for m in data:
            assert m["movement_type"] == "in"

    def test_filter_by_type_out(self, client, seed_data):
        resp = client.get("/api/movements", params={"type": "out"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        for m in data:
            assert m["movement_type"] == "out"


class TestCreateMovement:
    """POST /api/movements"""

    def test_in_movement_increases_stock(self, client, seed_data):
        product_id = seed_data["products"][0]["id"]

        before = client.get(f"/api/products/{product_id}").json()
        stock_before = before["current_stock"]

        resp = client.post("/api/movements", json={
            "product_id": product_id,
            "movement_type": "in",
            "quantity": 5,
            "reference": "TEST-IN",
        })
        assert resp.status_code == 201
        assert resp.json()["movement_type"] == "in"
        assert resp.json()["quantity"] == 5

        after = client.get(f"/api/products/{product_id}").json()
        assert after["current_stock"] == stock_before + 5

    def test_out_movement_decreases_stock(self, client, seed_data):
        product_id = seed_data["products"][0]["id"]

        before = client.get(f"/api/products/{product_id}").json()
        stock_before = before["current_stock"]

        resp = client.post("/api/movements", json={
            "product_id": product_id,
            "movement_type": "out",
            "quantity": 1,
            "reference": "TEST-OUT",
        })
        assert resp.status_code == 201

        after = client.get(f"/api/products/{product_id}").json()
        assert after["current_stock"] == stock_before - 1

    def test_out_rejects_insufficient_stock(self, client, seed_data):
        # Create a product with zero stock
        create_resp = client.post("/api/products", json={
            "name": "Leeres Produkt",
            "sku": "EMPTY-001",
            "category": "Elektronik",
            "unit_price": 10.00,
        })
        assert create_resp.status_code == 201
        pid = create_resp.json()["id"]

        resp = client.post("/api/movements", json={
            "product_id": pid,
            "movement_type": "out",
            "quantity": 1,
        })
        assert resp.status_code == 409

    def test_nonexistent_product_returns_404(self, client):
        resp = client.post("/api/movements", json={
            "product_id": 99999,
            "movement_type": "in",
            "quantity": 5,
        })
        assert resp.status_code == 404

    def test_quantity_must_be_positive(self, client, seed_data):
        product_id = seed_data["products"][0]["id"]
        resp = client.post("/api/movements", json={
            "product_id": product_id,
            "movement_type": "in",
            "quantity": 0,
        })
        assert resp.status_code == 422  # pydantic validation: gt=0

        resp_neg = client.post("/api/movements", json={
            "product_id": product_id,
            "movement_type": "in",
            "quantity": -5,
        })
        assert resp_neg.status_code == 422
