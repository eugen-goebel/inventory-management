"""Tests for CSV product import."""

import io
import pytest


class TestImportEndpoint:
    """POST /api/products/import"""

    def _csv_bytes(self, rows: list[str]) -> bytes:
        return "\n".join(rows).encode("utf-8")

    def test_successful_import(self, client, seed_data):
        csv = self._csv_bytes([
            "name,sku,category,unit_price,reorder_level",
            "Monitor 24,MON-001,Elektronik,299.99,5",
            "Tastatur,KB-001,Peripherie,49.99,20",
        ])
        resp = client.post(
            "/api/products/import",
            files={"file": ("products.csv", io.BytesIO(csv), "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["imported"] == 2
        assert data["skipped"] == 0

    def test_skip_duplicate_sku(self, client, seed_data):
        csv = self._csv_bytes([
            "name,sku,category,unit_price",
            "Laptop Pro 15,LP-001,Elektronik,1299.99",  # already exists
            "New Product,NEW-001,Elektronik,99.99",
        ])
        resp = client.post(
            "/api/products/import",
            files={"file": ("products.csv", io.BytesIO(csv), "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["imported"] == 1
        assert data["skipped"] == 1
        assert any("Duplicate SKU" in e["error"] for e in data["errors"])

    def test_skip_invalid_price(self, client, seed_data):
        csv = self._csv_bytes([
            "name,sku,category,unit_price",
            "Bad Product,BAD-001,Elektronik,not_a_number",
        ])
        resp = client.post(
            "/api/products/import",
            files={"file": ("products.csv", io.BytesIO(csv), "text/csv")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["imported"] == 0
        assert data["skipped"] == 1

    def test_skip_negative_price(self, client, seed_data):
        csv = self._csv_bytes([
            "name,sku,category,unit_price",
            "Bad Product,BAD-002,Elektronik,-10.0",
        ])
        resp = client.post(
            "/api/products/import",
            files={"file": ("products.csv", io.BytesIO(csv), "text/csv")},
        )
        data = resp.json()
        assert data["skipped"] == 1

    def test_missing_required_columns(self, client, seed_data):
        csv = self._csv_bytes([
            "name,sku",
            "Test,T-001",
        ])
        resp = client.post(
            "/api/products/import",
            files={"file": ("products.csv", io.BytesIO(csv), "text/csv")},
        )
        assert resp.status_code == 400

    def test_empty_csv(self, client, seed_data):
        csv = b""
        resp = client.post(
            "/api/products/import",
            files={"file": ("products.csv", io.BytesIO(csv), "text/csv")},
        )
        assert resp.status_code == 400

    def test_non_csv_rejected(self, client, seed_data):
        resp = client.post(
            "/api/products/import",
            files={"file": ("products.json", io.BytesIO(b"{}"), "application/json")},
        )
        assert resp.status_code == 400

    def test_optional_supplier_id(self, client, seed_data):
        supplier_id = seed_data["suppliers"][0]["id"]
        csv = self._csv_bytes([
            "name,sku,category,unit_price,supplier_id",
            f"With Supplier,WS-001,Elektronik,100.00,{supplier_id}",
        ])
        resp = client.post(
            "/api/products/import",
            files={"file": ("products.csv", io.BytesIO(csv), "text/csv")},
        )
        data = resp.json()
        assert data["imported"] == 1

        # Verify the product was created with the supplier
        products = client.get("/api/products", params={"search": "WS-001"}).json()
        assert len(products) == 1
        assert products[0]["supplier_id"] == supplier_id

    def test_missing_required_field_in_row(self, client, seed_data):
        csv = self._csv_bytes([
            "name,sku,category,unit_price",
            ",EMPTY-001,Elektronik,50.00",  # empty name
        ])
        resp = client.post(
            "/api/products/import",
            files={"file": ("products.csv", io.BytesIO(csv), "text/csv")},
        )
        data = resp.json()
        assert data["skipped"] == 1
        assert data["imported"] == 0

    def test_products_visible_after_import(self, client, seed_data):
        csv = self._csv_bytes([
            "name,sku,category,unit_price",
            "Imported Product,IMP-001,Elektronik,75.00",
        ])
        client.post(
            "/api/products/import",
            files={"file": ("products.csv", io.BytesIO(csv), "text/csv")},
        )
        products = client.get("/api/products", params={"search": "IMP-001"}).json()
        assert len(products) == 1
        assert products[0]["name"] == "Imported Product"
        assert products[0]["current_stock"] == 0
