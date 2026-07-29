"""Tests for isoko.ideveloper.umutekano — Security."""

from __future__ import annotations

from isoko.ideveloper.umutekano import SecurityManager
from isoko.ideveloper.ibikoreshingiro import AuditSeverity


def test_security_init():
    sm = SecurityManager()
    assert sm.get_audit_log() == []


def test_mfa():
    sm = SecurityManager()
    assert sm.is_mfa_enabled("user1") is False
    sm.enable_mfa("user1")
    assert sm.is_mfa_enabled("user1") is True


def test_session_management():
    sm = SecurityManager()
    sid = sm.create_session("user1")
    assert sm.validate_session(sid) == "user1"
    assert sm.validate_session("invalid") is None
    assert sm.revoke_session(sid) is True
    assert sm.validate_session(sid) is None


def test_audit_log():
    sm = SecurityManager()
    aid = sm.add_audit_entry("package:test", AuditSeverity.WARNING, "Suspicious activity", "review")
    logs = sm.get_audit_log(target="package:test")
    assert len(logs) == 1


def test_audit_filter():
    sm = SecurityManager()
    sm.add_audit_entry("pkg:a", AuditSeverity.INFO, "Info")
    sm.add_audit_entry("pkg:b", AuditSeverity.CRITICAL, "Critical")
    critical = sm.get_audit_log(severity=AuditSeverity.CRITICAL)
    assert len(critical) == 1


def test_package_signing():
    sm = SecurityManager()
    sig = sm.sign_package("my-pkg", "1.0.0", "publisher1")
    assert sm.verify_signature("my-pkg", "1.0.0", sig, "publisher1") is True
    assert sm.verify_signature("my-pkg", "1.0.0", sig, "attacker") is False


def test_spam_report():
    sm = SecurityManager()
    report = sm.report_spam("user1", "user2", "Spamming")
    assert report["status"] == "open"


def test_abuse_report():
    sm = SecurityManager()
    report = sm.report_abuse("user1", "user2", "harassment", "Inappropriate comments")
    assert report["type"] == "harassment"


def test_api_keys():
    sm = SecurityManager()
    key_info = sm.create_api_key("user1", "My Key", ["read"])
    assert key_info["name"] == "My Key"
    assert sm.validate_api_key(key_info["key"]) is not None
    assert sm.validate_api_key("invalid") is None


def test_revoke_api_key():
    sm = SecurityManager()
    key_info = sm.create_api_key("user1", "Test", ["read"])
    assert sm.revoke_api_key(key_info["key"]) is True
    assert sm.validate_api_key(key_info["key"]) is None


def test_supply_chain_protection():
    sm = SecurityManager()
    protection = sm.get_supply_chain_protection()
    assert protection["package_signing"] is True


def test_publisher_verification():
    sm = SecurityManager()
    result = sm.verify_publisher_identity("pub1", "government_id")
    assert result["status"] == "verified"
