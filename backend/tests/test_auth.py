"""Tests for JWT authentication and role-based access control."""

import pytest


class TestRegister:
    def test_register_success(self, raw_client):
        resp = raw_client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "secret123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["username"] == "newuser"
        assert data["user"]["role"] == "viewer"

    def test_register_with_role(self, raw_client):
        resp = raw_client.post("/api/auth/register", json={
            "username": "staffuser",
            "email": "staff@test.com",
            "password": "secret123",
            "role": "staff",
        })
        assert resp.status_code == 201
        assert resp.json()["user"]["role"] == "staff"

    def test_register_duplicate_username(self, raw_client):
        raw_client.post("/api/auth/register", json={
            "username": "dupe", "email": "a@test.com", "password": "secret123",
        })
        resp = raw_client.post("/api/auth/register", json={
            "username": "dupe", "email": "b@test.com", "password": "secret123",
        })
        assert resp.status_code == 400
        assert "already taken" in resp.json()["detail"]

    def test_register_duplicate_email(self, raw_client):
        raw_client.post("/api/auth/register", json={
            "username": "user1", "email": "same@test.com", "password": "secret123",
        })
        resp = raw_client.post("/api/auth/register", json={
            "username": "user2", "email": "same@test.com", "password": "secret123",
        })
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"]

    def test_register_short_password(self, raw_client):
        resp = raw_client.post("/api/auth/register", json={
            "username": "short", "email": "s@test.com", "password": "123",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, raw_client):
        raw_client.post("/api/auth/register", json={
            "username": "loginuser", "email": "login@test.com", "password": "mypassword",
        })
        resp = raw_client.post("/api/auth/login", json={
            "username": "loginuser", "password": "mypassword",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["username"] == "loginuser"

    def test_login_wrong_password(self, raw_client):
        raw_client.post("/api/auth/register", json={
            "username": "wrongpw", "email": "wp@test.com", "password": "correct",
        })
        resp = raw_client.post("/api/auth/login", json={
            "username": "wrongpw", "password": "incorrect",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, raw_client):
        resp = raw_client.post("/api/auth/login", json={
            "username": "ghost", "password": "anything",
        })
        assert resp.status_code == 401


class TestMe:
    def test_me_with_token(self, raw_client):
        reg = raw_client.post("/api/auth/register", json={
            "username": "meuser", "email": "me@test.com", "password": "secret123",
        })
        token = reg.json()["access_token"]
        resp = raw_client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200
        assert resp.json()["username"] == "meuser"

    def test_me_without_token(self, raw_client):
        resp = raw_client.get("/api/auth/me")
        assert resp.status_code in (401, 403)

    def test_me_with_invalid_token(self, raw_client):
        resp = raw_client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid.token.here",
        })
        assert resp.status_code == 401


class TestRoleBasedAccess:
    def _register_and_get_token(self, raw_client, username, role="viewer"):
        resp = raw_client.post("/api/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": "secret123",
            "role": role,
        })
        return resp.json()["access_token"]

    def test_viewer_can_list_products(self, raw_client):
        token = self._register_and_get_token(raw_client, "viewerlist", "viewer")
        resp = raw_client.get("/api/products", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200

    def test_viewer_cannot_create_product(self, raw_client):
        token = self._register_and_get_token(raw_client, "viewercreate", "viewer")
        resp = raw_client.post("/api/products", json={
            "name": "Test", "sku": "TST-001", "category": "Elektronik",
            "unit_price": 10.0, "reorder_level": 5,
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_staff_can_create_product(self, raw_client):
        token = self._register_and_get_token(raw_client, "staffcreate", "staff")
        resp = raw_client.post("/api/products", json={
            "name": "Test", "sku": "TST-002", "category": "Elektronik",
            "unit_price": 10.0, "reorder_level": 5,
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 201

    def test_staff_cannot_delete_product(self, raw_client):
        # Admin creates product first
        admin_token = self._register_and_get_token(raw_client, "admindel", "admin")
        create_resp = raw_client.post("/api/products", json={
            "name": "DelTest", "sku": "DEL-001", "category": "Elektronik",
            "unit_price": 5.0, "reorder_level": 1,
        }, headers={"Authorization": f"Bearer {admin_token}"})
        pid = create_resp.json()["id"]

        staff_token = self._register_and_get_token(raw_client, "staffdel", "staff")
        resp = raw_client.delete(f"/api/products/{pid}", headers={
            "Authorization": f"Bearer {staff_token}",
        })
        assert resp.status_code == 403

    def test_admin_can_delete_product(self, raw_client):
        admin_token = self._register_and_get_token(raw_client, "admindel2", "admin")
        create_resp = raw_client.post("/api/products", json={
            "name": "DelTest2", "sku": "DEL-002", "category": "Elektronik",
            "unit_price": 5.0, "reorder_level": 1,
        }, headers={"Authorization": f"Bearer {admin_token}"})
        pid = create_resp.json()["id"]

        resp = raw_client.delete(f"/api/products/{pid}", headers={
            "Authorization": f"Bearer {admin_token}",
        })
        assert resp.status_code == 204

    def test_unauthenticated_cannot_access(self, raw_client):
        resp = raw_client.get("/api/products")
        assert resp.status_code in (401, 403)
