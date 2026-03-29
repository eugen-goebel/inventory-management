"""Tests for analytics/dashboard endpoints."""

import pytest


class TestDashboardAnalytics:
    """GET /api/analytics/dashboard"""

    def test_returns_data(self, client, seed_data):
        resp = client.get("/api/analytics/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_has_all_required_fields(self, client, seed_data):
        resp = client.get("/api/analytics/dashboard")
        data = resp.json()
        required_fields = [
            "total_products",
            "total_stock_value",
            "low_stock_count",
            "total_movements_today",
            "stock_by_category",
            "top_products",
            "recent_movements",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_total_stock_value_is_correct(self, client, seed_data):
        """
        After seed movements the stock levels are:
        - Laptop Pro 15:       17 * 1299.99 = 22099.83
        - Schreibtischstuhl:    5 *  349.00 =  1745.00
        - Cat6 Kabel:         300 *    8.50 =  2550.00
        - USB-Maus:            10 *   24.99 =   249.90
        - Druckerpapier:        5 *    4.99 =    24.95
        Total = 26669.68
        """
        resp = client.get("/api/analytics/dashboard")
        data = resp.json()
        assert data["total_stock_value"] == pytest.approx(26669.68, rel=1e-2)

    def test_low_stock_count_is_correct(self, client, seed_data):
        """
        Low stock means current_stock <= reorder_level:
        - Laptop Pro 15:     17 > 5   -> NOT low
        - Schreibtischstuhl:  5 <= 10 -> LOW
        - Cat6 Kabel:       300 > 50  -> NOT low
        - USB-Maus:          10 <= 20 -> LOW
        - Druckerpapier:      5 <= 100 -> LOW
        Count = 3
        """
        resp = client.get("/api/analytics/dashboard")
        data = resp.json()
        assert data["low_stock_count"] == 3

    def test_stock_by_category_has_entries(self, client, seed_data):
        resp = client.get("/api/analytics/dashboard")
        data = resp.json()
        categories = data["stock_by_category"]
        assert isinstance(categories, list)
        assert len(categories) == 5  # 5 distinct categories in seed data
        category_names = {c["category"] for c in categories}
        assert "Elektronik" in category_names
        assert "Moebel" in category_names
