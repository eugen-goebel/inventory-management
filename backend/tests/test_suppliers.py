"""Tests for supplier endpoints."""

import pytest


class TestListSuppliers:
    """GET /api/suppliers"""

    def test_returns_list(self, client, seed_data):
        resp = client.get("/api/suppliers")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_search_filters_by_name(self, client, seed_data):
        resp = client.get("/api/suppliers", params={"search": "Tech"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert "Tech" in data[0]["name"]


class TestGetSupplier:
    """GET /api/suppliers/{id}"""

    def test_returns_supplier_with_product_count(self, client, seed_data):
        supplier_id = seed_data["suppliers"][0]["id"]
        resp = client.get(f"/api/suppliers/{supplier_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == supplier_id
        assert data["name"] == "TechDistri GmbH"
        assert "product_count" in data
        # TechDistri has 2 products (Laptop Pro 15, USB-Maus Wireless)
        assert data["product_count"] == 2

    def test_returns_404_for_missing(self, client):
        resp = client.get("/api/suppliers/99999")
        assert resp.status_code == 404


class TestCreateSupplier:
    """POST /api/suppliers"""

    def test_creates_supplier(self, client):
        payload = {
            "name": "Neuer Lieferant",
            "contact_email": "neu@lieferant.de",
            "phone": "+49 89 11111",
            "country": "Deutschland",
        }
        resp = client.post("/api/suppliers", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Neuer Lieferant"
        assert data["contact_email"] == "neu@lieferant.de"
        assert data["product_count"] == 0


class TestUpdateSupplier:
    """PUT /api/suppliers/{id}"""

    def test_updates_supplier(self, client, seed_data):
        supplier_id = seed_data["suppliers"][0]["id"]
        resp = client.put(
            f"/api/suppliers/{supplier_id}",
            json={"name": "TechDistri International GmbH"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "TechDistri International GmbH"
        assert data["contact_email"] == "info@techdistri.de"  # unchanged


class TestDeleteSupplier:
    """DELETE /api/suppliers/{id}"""

    def test_delete_without_products_succeeds(self, client):
        # Create a supplier with no products
        create_resp = client.post("/api/suppliers", json={
            "name": "Zum Loeschen",
            "country": "Test",
        })
        assert create_resp.status_code == 201
        sid = create_resp.json()["id"]

        resp = client.delete(f"/api/suppliers/{sid}")
        assert resp.status_code == 204

        # Confirm it is gone
        get_resp = client.get(f"/api/suppliers/{sid}")
        assert get_resp.status_code == 404

    def test_delete_with_products_fails(self, client, seed_data):
        # suppliers[0] has products assigned
        supplier_id = seed_data["suppliers"][0]["id"]
        resp = client.delete(f"/api/suppliers/{supplier_id}")
        assert resp.status_code == 409
