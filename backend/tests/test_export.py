"""Tests for product CSV export endpoint."""

import csv
import io

from fastapi.testclient import TestClient

from main import app


class TestExportProducts:
    """GET /api/products/export"""

    def _parse_csv(self, body: str) -> list[dict]:
        reader = csv.DictReader(io.StringIO(body))
        return list(reader)

    def test_returns_csv_response(self, client, seed_data):
        resp = client.get("/api/products/export")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        assert "attachment" in resp.headers["content-disposition"]
        assert "products.csv" in resp.headers["content-disposition"]

    def test_csv_contains_all_products(self, client, seed_data):
        resp = client.get("/api/products/export")
        rows = self._parse_csv(resp.text)
        assert len(rows) == 5

    def test_csv_has_expected_columns(self, client, seed_data):
        resp = client.get("/api/products/export")
        rows = self._parse_csv(resp.text)
        expected = {
            "sku",
            "name",
            "category",
            "supplier_name",
            "unit_price",
            "current_stock",
            "reorder_level",
        }
        assert set(rows[0].keys()) == expected

    def test_csv_rows_include_supplier_name(self, client, seed_data):
        resp = client.get("/api/products/export")
        rows = self._parse_csv(resp.text)
        # All seed products have suppliers
        assert all(row["supplier_name"] for row in rows)

    def test_filter_by_category(self, client, seed_data):
        resp = client.get("/api/products/export", params={"category": "Elektronik"})
        rows = self._parse_csv(resp.text)
        assert len(rows) == 1
        assert rows[0]["category"] == "Elektronik"

    def test_filter_by_search(self, client, seed_data):
        resp = client.get("/api/products/export", params={"search": "Laptop"})
        rows = self._parse_csv(resp.text)
        assert len(rows) == 1
        assert rows[0]["name"] == "Laptop Pro 15"

    def test_filter_low_stock(self, client, seed_data):
        resp = client.get("/api/products/export", params={"low_stock": "true"})
        rows = self._parse_csv(resp.text)
        # Same low-stock items as the list endpoint
        for row in rows:
            assert int(row["current_stock"]) <= int(row["reorder_level"])

    def test_empty_result_returns_header_only(self, client, seed_data):
        resp = client.get("/api/products/export", params={"search": "no-such-product"})
        assert resp.status_code == 200
        rows = self._parse_csv(resp.text)
        assert rows == []
        # Header row still present
        assert "sku" in resp.text.splitlines()[0]

    def test_unauthenticated_request_rejected(self, db_session):
        """Export must require a valid token."""
        from db.database import get_db

        def _override_get_db():
            yield db_session

        app.dependency_overrides[get_db] = _override_get_db
        try:
            with TestClient(app) as tc:
                resp = tc.get("/api/products/export")
                assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()
