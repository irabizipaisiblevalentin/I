"""Tests for urubuga authentication and authorization."""

import pytest
from urubuga.auth.authentication import (
    User, JWTManager, JWTConfig, SessionStore, APIKeyManager,
    Role, Policy, AuthorizationManager, AuthMethod,
)


class TestUser:
    def test_create(self):
        u = User(id="1", username="alice", email="alice@test.com")
        assert u.username == "alice"
        assert u.is_authenticated is False

    def test_has_permission(self):
        u = User(permissions={"read", "write"})
        assert u.has_permission("read")
        assert not u.has_permission("delete")

    def test_has_role(self):
        u = User(roles=["admin", "user"])
        assert u.has_role("admin")
        assert not u.has_role("superadmin")

    def test_has_any_role(self):
        u = User(roles=["editor"])
        assert u.has_any_role("admin", "editor")
        assert not u.has_any_role("admin", "superadmin")

    def test_to_dict(self):
        u = User(id="1", username="alice", roles=["admin"])
        d = u.to_dict()
        assert d["id"] == "1"
        assert "admin" in d["roles"]


class TestJWTManager:
    def test_create_and_validate(self):
        jwt = JWTManager(JWTConfig(secret="test-secret"))
        user = User(id="1", username="alice", roles=["admin"])
        token = jwt.create_token(user)
        payload = jwt.validate_token(token)
        assert payload is not None
        assert payload["sub"] == "1"

    def test_invalid_token(self):
        jwt = JWTManager(JWTConfig(secret="test"))
        assert jwt.validate_token("invalid.token.here") is None

    def test_extract_user(self):
        jwt = JWTManager(JWTConfig(secret="test"))
        user = User(id="1", username="alice", roles=["admin"],
                     permissions={"read"})
        token = jwt.create_token(user)
        extracted = jwt.extract_user(token)
        assert extracted is not None
        assert extracted.id == "1"
        assert extracted.auth_method == AuthMethod.JWT

    def test_revoke_token(self):
        jwt = JWTManager(JWTConfig(secret="test"))
        user = User(id="1", username="alice")
        token = jwt.create_token(user)
        jwt.revoke_token(token)
        assert jwt.validate_token(token) is None

    def test_refresh_token(self):
        jwt = JWTManager(JWTConfig(secret="test"))
        user = User(id="1", username="alice")
        refresh = jwt.create_refresh_token(user)
        payload = jwt.validate_token(refresh)
        assert payload is not None
        assert payload.get("type") == "refresh"

    def test_user_from_token(self):
        jwt = JWTManager(JWTConfig(secret="test-secret"))
        user = User(id="1", username="alice", roles=["admin"],
                     permissions={"read", "write"})
        token = jwt.create_token(user)
        extracted = jwt.extract_user(token)
        assert extracted.has_role("admin")
        assert extracted.has_permission("read")
        assert extracted.has_permission("write")


class TestSessionStore:
    def test_create_and_get(self):
        store = SessionStore()
        user = User(id="1", username="alice")
        sid = store.create(user)
        session = store.get(sid)
        assert session is not None
        assert session["user"]["username"] == "alice"

    def test_destroy(self):
        store = SessionStore()
        sid = store.create(User(id="1"))
        assert store.destroy(sid)
        assert store.get(sid) is None

    def test_count(self):
        store = SessionStore()
        store.create(User(id="1"))
        store.create(User(id="2"))
        assert store.count() == 2

    def test_expired(self):
        store = SessionStore()
        sid = store.create(User(id="1"), ttl=-1)
        assert store.get(sid) is None


class TestAPIKeyManager:
    def test_create_and_validate(self):
        mgr = APIKeyManager()
        key = mgr.create_key("user1", name="test-key")
        data = mgr.validate_key(key)
        assert data is not None
        assert data["user_id"] == "user1"

    def test_revoke(self):
        mgr = APIKeyManager()
        key = mgr.create_key("user1")
        assert mgr.revoke_key(key)
        assert mgr.validate_key(key) is None

    def test_expired(self):
        mgr = APIKeyManager()
        key = mgr.create_key("user1", expires_in=-1)
        assert mgr.validate_key(key) is None

    def test_list_keys(self):
        mgr = APIKeyManager()
        mgr.create_key("user1", name="k1")
        mgr.create_key("user1", name="k2")
        keys = mgr.list_keys("user1")
        assert len(keys) == 2


class TestRole:
    def test_has_permission(self):
        role = Role("admin", permissions=["read", "write", "delete"])
        assert role.has_permission("read")
        assert not role.has_permission("superadmin")

    def test_wildcard(self):
        role = Role("superadmin", permissions=["*"])
        assert role.has_permission("anything")


class TestPolicy:
    def test_evaluate(self):
        policy = Policy("is_admin", lambda u, r, a: "admin" in u.roles)
        user = User(roles=["admin"])
        assert policy.evaluate(user)
        user2 = User(roles=["user"])
        assert not policy.evaluate(user2)


class TestAuthorizationManager:
    def test_add_role(self):
        am = AuthorizationManager()
        am.add_role(Role("admin", permissions=["read", "write"]))
        assert am.role_count() == 1

    def test_check_permission(self):
        am = AuthorizationManager()
        am.add_role(Role("admin", permissions=["read", "write"]))
        user = User(roles=["admin"])
        assert am.check_permission(user, "read")
        assert not am.check_permission(user, "delete")

    def test_user_permission(self):
        am = AuthorizationManager()
        user = User(permissions={"custom"})
        assert am.check_permission(user, "custom")

    def test_add_policy(self):
        am = AuthorizationManager()
        am.add_policy(Policy("owner", lambda u, r, a: u.id == "1"))
        user = User(id="1")
        assert am.check_policy(user, "owner")
        user2 = User(id="2")
        assert not am.check_policy(user2, "owner")

    def test_assign_revoke_role(self):
        am = AuthorizationManager()
        am.assign_role("user1", "admin")
        assert "admin" in am.get_user_roles("user1")
        am.revoke_role("user1", "admin")
        assert "admin" not in am.get_user_roles("user1")

    def test_authorize_with_policy(self):
        am = AuthorizationManager()
        am.add_policy(Policy("owner", lambda u, r, a: u.id == "1"))
        user = User(id="1")
        assert am.authorize(user, "edit", policy_name="owner")

    def test_policy_count(self):
        am = AuthorizationManager()
        am.add_policy(Policy("p1", lambda u, r, a: True))
        assert am.policy_count() == 1
