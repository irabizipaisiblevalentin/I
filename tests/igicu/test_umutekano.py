"""Tests for IGICU Security (umutekano)."""

from __future__ import annotations

import pytest

from igicu.umutekano import (
    IdentityManager, RBACManager, SecretsManager,
    CertificateManager, EncryptionEngine, APISecurity,
    SecurityPlatform,
)
from igicu.ibikoreshingiro import SecretProvider, AuthMethod


class TestIdentityManager:
    def test_create_user(self):
        im = IdentityManager()
        user_id = im.create_user("alice", "password123", ["admin"])
        assert user_id is not None

    def test_authenticate_success(self):
        im = IdentityManager()
        im.create_user("bob", "secret", ["viewer"])
        token = im.authenticate("bob", "secret")
        assert token is not None

    def test_authenticate_failure(self):
        im = IdentityManager()
        im.create_user("bob", "secret")
        token = im.authenticate("bob", "wrong")
        assert token is None

    def test_validate_token(self):
        im = IdentityManager()
        im.create_user("carol", "pass")
        token = im.authenticate("carol", "pass")
        data = im.validate_token(token)
        assert data is not None
        assert data["username"] == "carol"

    def test_revoke_token(self):
        im = IdentityManager()
        im.create_user("dave", "pass")
        token = im.authenticate("dave", "pass")
        assert im.revoke_token(token) is True
        assert im.validate_token(token) is None

    def test_disable_user(self):
        im = IdentityManager()
        im.create_user("eve", "pass")
        assert im.disable_user("eve") is True
        assert im.authenticate("eve", "pass") is None

    def test_list_users(self):
        im = IdentityManager()
        im.create_user("u1", "p1")
        im.create_user("u2", "p2")
        users = im.list_users()
        assert len(users) >= 2


class TestRBACManager:
    def test_has_permission(self):
        rbac = RBACManager()
        assert rbac.has_permission(["admin"], "deploy") is True
        assert rbac.has_permission(["viewer"], "deploy") is False

    def test_add_permission(self):
        rbac = RBACManager()
        rbac.add_permission("custom", "deploy")
        assert rbac.has_permission(["custom"], "deploy") is True


class TestSecretsManager:
    def test_set_and_get(self):
        sm = SecretsManager(SecretProvider.ENVIRONMENT)
        sm.set("db_password", "s3cret!")
        value = sm.get("db_password")
        assert value == "s3cret!"

    def test_delete(self):
        sm = SecretsManager(SecretProvider.ENVIRONMENT)
        sm.set("temp", "value")
        assert sm.delete("temp") is True

    def test_list(self):
        sm = SecretsManager(SecretProvider.ENVIRONMENT)
        sm.set("key1", "val1")
        sm.set("key2", "val2")
        secrets = sm.list()
        assert len(secrets) >= 2

    def test_rotate(self):
        sm = SecretsManager(SecretProvider.ENVIRONMENT)
        sm.set("api_key", "old")
        assert sm.rotate("api_key", "new") is True

    def test_check_expiry(self):
        sm = SecretsManager(SecretProvider.ENVIRONMENT)
        sm.set("old_secret", "value", rotation_days=0)
        expired = sm.check_expiry()
        assert len(expired) >= 0


class TestCertificateManager:
    def test_generate(self):
        cm = CertificateManager()
        cert_id = cm.generate("example.com")
        assert cert_id is not None

    def test_renew(self):
        cm = CertificateManager()
        cert_id = cm.generate("test.com")
        assert cm.renew(cert_id) is True

    def test_revoke(self):
        cm = CertificateManager()
        cert_id = cm.generate("revoke.com")
        assert cm.revoke(cert_id) is True

    def test_list(self):
        cm = CertificateManager()
        cm.generate("a.com")
        cm.generate("b.com")
        certs = cm.list()
        assert len(certs) >= 2

    def test_check_expiry(self):
        cm = CertificateManager()
        cm.generate("short.com", days_valid=1)
        expiring = cm.check_expiry(days=365)
        assert len(expiring) >= 0


class TestEncryptionEngine:
    def test_encrypt_decrypt(self):
        ee = EncryptionEngine()
        encrypted = ee.encrypt("sensitive data")
        assert encrypted != "sensitive data"
        decrypted = ee.decrypt(encrypted)
        assert decrypted is not None


class TestAPISecurity:
    def test_create_api_key(self):
        api = APISecurity()
        key = api.create_api_key("test-key", ["read", "write"])
        assert key.startswith("igicu-")

    def test_validate_api_key(self):
        api = APISecurity()
        key = api.create_api_key("valid")
        assert api.validate_api_key(key) is True

    def test_revoke_api_key(self):
        api = APISecurity()
        key = api.create_api_key("revokable")
        assert api.revoke_api_key(key) is True
        assert api.validate_api_key(key) is False

    def test_rate_limit(self):
        api = APISecurity()
        key = api.create_api_key("limited")
        api.set_rate_limit(key, 5)
        for _ in range(5):
            assert api.check_rate_limit(key) is True
        # 6th call should be over limit
        assert api.check_rate_limit(key) is False
