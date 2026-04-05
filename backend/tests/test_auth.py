"""Tests for JWT authentication and role-based access control."""

import pytest

from agents.auth_service import hash_password, create_access_token
from models.orm import User


def _make_user(db_session, username, role="viewer"):
    """Create a user directly via the DB and return a signed token."""
    user = User(
        username=username,
        email=f"{username}@test.com",
        hashed_password=hash_password("secret123"),
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return create_access_token(user.id, user.username, user.role)


class TestRegister:
    def test_first_user_bootstraps_as_admin(self, raw_client):
        """The first user registered becomes admin to bootstrap the system."""
        resp = raw_client.post("/api/auth/register", json={
            "username": "firstuser",
            "email": "first@test.com",
            "password": "secret123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["username"] == "firstuser"
        assert data["user"]["role"] == "admin"

    def test_subsequent_users_are_viewers(self, raw_client):
        """After bootstrap, new users are always viewer."""
        raw_client.post("/api/auth/register", json={
            "username": "first", "email": "f@test.com", "password": "secret123",
        })
        resp = raw_client.post("/api/auth/register", json={
            "username": "second", "email": "s@test.com", "password": "secret123",
        })
        assert resp.status_code == 201
        assert resp.json()["user"]["role"] == "viewer"

    def test_client_supplied_role_is_ignored(self, raw_client):
        """Client-supplied role must never escalate privileges."""
        raw_client.post("/api/auth/register", json={
            "username": "admin", "email": "a@test.com", "password": "secret123",
        })
        resp = raw_client.post("/api/auth/register", json={
            "username": "attacker",
            "email": "atk@test.com",
            "password": "secret123",
            "role": "admin",
        })
        assert resp.status_code == 201
        assert resp.json()["user"]["role"] == "viewer"

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
    def test_viewer_can_list_products(self, raw_client, db_session):
        token = _make_user(db_session, "viewerlist", "viewer")
        resp = raw_client.get("/api/products", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200

    def test_viewer_cannot_create_product(self, raw_client, db_session):
        token = _make_user(db_session, "viewercreate", "viewer")
        resp = raw_client.post("/api/products", json={
            "name": "Test", "sku": "TST-001", "category": "Elektronik",
            "unit_price": 10.0, "reorder_level": 5,
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_staff_can_create_product(self, raw_client, db_session):
        token = _make_user(db_session, "staffcreate", "staff")
        resp = raw_client.post("/api/products", json={
            "name": "Test", "sku": "TST-002", "category": "Elektronik",
            "unit_price": 10.0, "reorder_level": 5,
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 201

    def test_staff_cannot_delete_product(self, raw_client, db_session):
        admin_token = _make_user(db_session, "admindel", "admin")
        create_resp = raw_client.post("/api/products", json={
            "name": "DelTest", "sku": "DEL-001", "category": "Elektronik",
            "unit_price": 5.0, "reorder_level": 1,
        }, headers={"Authorization": f"Bearer {admin_token}"})
        pid = create_resp.json()["id"]

        staff_token = _make_user(db_session, "staffdel", "staff")
        resp = raw_client.delete(f"/api/products/{pid}", headers={
            "Authorization": f"Bearer {staff_token}",
        })
        assert resp.status_code == 403

    def test_admin_can_delete_product(self, raw_client, db_session):
        admin_token = _make_user(db_session, "admindel2", "admin")
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
