"""Tests for UFA security module."""

import pytest
from ufa.security import SecurityManager, Identity, Token


class TestSecurityManager:
    def test_create_identity(self):
        sm = SecurityManager()
        ident = sm.create_identity("alice", roles=["admin"])
        assert ident.username == "alice"
        assert "admin" in ident.roles

    def test_get_identity(self):
        sm = SecurityManager()
        ident = sm.create_identity("bob")
        assert sm.get_identity(ident.id) is ident

    def test_issue_token(self):
        sm = SecurityManager()
        ident = sm.create_identity("carol")
        token = sm.issue_token(ident.id)
        assert token is not None
        assert not token.is_expired

    def test_authenticate_token(self):
        sm = SecurityManager()
        ident = sm.create_identity("dave")
        token = sm.issue_token(ident.id)
        authed = sm.authenticate_token(token.value)
        assert authed is not None
        assert authed.id == ident.id

    def test_authenticate_expired_token(self):
        sm = SecurityManager()
        ident = sm.create_identity("eve")
        token = sm.issue_token(ident.id, expires_in_sec=-1)
        authed = sm.authenticate_token(token.value)
        assert authed is None

    def test_revoke_token(self):
        sm = SecurityManager()
        ident = sm.create_identity("frank")
        token = sm.issue_token(ident.id)
        sm.revoke_token(token.value)
        authed = sm.authenticate_token(token.value)
        assert authed is None

    def test_register_policy(self):
        sm = SecurityManager()
        sm.register_policy("admin_only", lambda i, r, a: "admin" in i.roles)
        ident = sm.create_identity("grace", roles=["admin"])
        assert sm.authorize(ident, "delete", policy_name="admin_only")

    def test_authorize_no_policy(self):
        sm = SecurityManager()
        ident = sm.create_identity("hank", permissions={"read"})
        assert sm.authorize(ident, "read")
        assert not sm.authorize(ident, "write")

    def test_encrypt(self):
        sm = SecurityManager()
        encrypted = sm.encrypt("secret")
        assert encrypted != "secret"
        assert sm.encrypt("secret") == encrypted

    def test_hash_password(self):
        sm = SecurityManager()
        hashed = sm.hash_password("mypassword")
        assert sm.verify_password("mypassword", hashed)
        assert not sm.verify_password("wrong", hashed)

    def test_generate_secret(self):
        sm = SecurityManager()
        s1 = sm.generate_secret()
        s2 = sm.generate_secret()
        assert s1 != s2
        assert len(s1) == 43

    def test_audit_log(self):
        sm = SecurityManager()
        ident = sm.create_identity("ivan")
        sm.authorize(ident, "read")
        logs = sm.audit_log(ident.id)
        assert len(logs) >= 1

    def test_token_header(self):
        token = Token("id1")
        header = token.to_header()
        assert header.startswith("bearer ")

    def test_identity_to_dict(self):
        ident = Identity(username="test", roles=["r1"])
        d = ident.to_dict()
        assert d["username"] == "test"

    def test_identity_expiry(self):
        ident = Identity()
        ident.expires_at = -1
        assert ident.is_expired
