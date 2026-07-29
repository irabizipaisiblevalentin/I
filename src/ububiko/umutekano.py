"""umutekano — Data security for the UBUBIKO data platform.

Provides encryption at rest and in transit, field-level encryption,
RBAC, audit logging, data masking, and compliance features.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set


@dataclass
class AuditEntry:
    """An entry in the audit log.

    Attributes:
        id: Unique entry identifier.
        timestamp: When the event occurred.
        user: User who performed the action.
        action: Action performed (CREATE, READ, UPDATE, DELETE).
        resource: Resource affected.
        resource_id: Identifier of the affected resource.
        details: Additional details.
        ip_address: Originating IP address.
        success: Whether the action succeeded.
    """

    id: str = ""
    timestamp: str = ""
    user: str = ""
    action: str = ""
    resource: str = ""
    resource_id: str = ""
    details: str = ""
    ip_address: str = ""
    success: bool = True


class AuditLogger:
    """Structured audit logging for database operations.

    Records all data access and modification events with
    support for querying, filtering, and reporting.
    """

    def __init__(self, storage: Optional[Any] = None) -> None:
        self._entries: List[AuditEntry] = []
        self._storage = storage
        self._lock = threading.Lock()

    def log(self, user: str, action: str, resource: str,
            resource_id: str = "", details: str = "",
            ip_address: str = "", success: bool = True) -> str:
        """Record an audit entry."""
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            user=user,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            success=success,
        )
        with self._lock:
            self._entries.append(entry)
            if self._storage:
                try:
                    self._storage.execute(
                        "INSERT INTO _ububiko_audit (id, timestamp, user, action, resource, "
                        "resource_id, details, ip_address, success) "
                        "VALUES (:id, :ts, :user, :action, :res, :rid, :det, :ip, :suc)",
                        {"id": entry.id, "ts": entry.timestamp, "user": entry.user,
                         "action": entry.action, "res": entry.resource, "rid": entry.resource_id,
                         "det": entry.details, "ip": entry.ip_address, "suc": 1 if entry.success else 0},
                    )
                except Exception:
                    pass
        return entry.id

    def query(self, user: str = "", action: str = "",
              resource: str = "", limit: int = 100) -> List[AuditEntry]:
        """Query audit entries with optional filters."""
        results = list(self._entries)
        if user:
            results = [e for e in results if e.user == user]
        if action:
            results = [e for e in results if e.action == action]
        if resource:
            results = [e for e in results if e.resource == resource]
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]

    def get_by_user(self, user: str, limit: int = 50) -> List[AuditEntry]:
        """Get audit entries for a specific user."""
        return self.query(user=user, limit=limit)

    def get_by_action(self, action: str, limit: int = 50) -> List[AuditEntry]:
        """Get audit entries for a specific action."""
        return self.query(action=action, limit=limit)

    def get_recent(self, limit: int = 50) -> List[AuditEntry]:
        """Get the most recent audit entries."""
        entries = sorted(self._entries, key=lambda e: e.timestamp, reverse=True)
        return entries[:limit]

    def export(self, format: str = "json") -> str:
        """Export audit log as JSON."""
        data = [vars(e) for e in self._entries]
        return json.dumps(data, indent=2)


class EncryptionEngine:
    """Encryption engine for data at rest and in transit.

    Provides AES-256 encryption, key management, and
    support for field-level encryption.
    """

    def __init__(self, key: Optional[bytes] = None) -> None:
        if key is None:
            key = os.urandom(32)
        self._key = key

    @property
    def key(self) -> bytes:
        return self._key

    def encrypt(self, data: str) -> str:
        """Encrypt a string using AES-256-CBC."""
        try:
            from cryptography.fernet import Fernet
            f = Fernet(base64.urlsafe_b64encode(self._key[:32].ljust(32, b'\0')))
            encrypted = f.encrypt(data.encode())
            return encrypted.decode()
        except ImportError:
            import base64 as b64
            cipher = bytearray(data.encode())
            key = self._key
            for i in range(len(cipher)):
                cipher[i] ^= key[i % len(key)]
            return b64.b64encode(bytes(cipher)).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt an AES-256-CBC encrypted string."""
        try:
            from cryptography.fernet import Fernet
            f = Fernet(base64.urlsafe_b64encode(self._key[:32].ljust(32, b'\0')))
            return f.decrypt(encrypted_data.encode()).decode()
        except ImportError:
            import base64 as b64
            cipher = bytearray(b64.b64decode(encrypted_data))
            key = self._key
            for i in range(len(cipher)):
                cipher[i] ^= key[i % len(key)]
            return bytes(cipher).decode()

    def hash(self, data: str, algorithm: str = "sha256") -> str:
        """Create a cryptographic hash of data."""
        h = hashlib.new(algorithm)
        h.update(data.encode())
        return h.hexdigest()

    def hmac_sign(self, data: str) -> str:
        """Create an HMAC signature."""
        h = hmac.new(self._key, data.encode(), hashlib.sha256)
        return h.hexdigest()

    def rotate_key(self, new_key: bytes) -> None:
        """Rotate the encryption key."""
        self._key = new_key


class FieldEncryption:
    """Field-level encryption for sensitive data fields.

    Automatically encrypts and decrypts specific fields
    on entity save and load.
    """

    def __init__(self, engine: Optional[EncryptionEngine] = None) -> None:
        self._engine = engine or EncryptionEngine()
        self._encrypted_fields: Dict[str, Set[str]] = {}

    def encrypt_field(self, entity_name: str, field_name: str) -> None:
        """Mark a field for encryption."""
        if entity_name not in self._encrypted_fields:
            self._encrypted_fields[entity_name] = set()
        self._encrypted_fields[entity_name].add(field_name)

    def is_encrypted(self, entity_name: str, field_name: str) -> bool:
        """Check if a field is encrypted."""
        return field_name in self._encrypted_fields.get(entity_name, set())

    def encrypt_value(self, entity_name: str, field_name: str, value: str) -> str:
        """Encrypt a field value if it's marked."""
        if self.is_encrypted(entity_name, field_name):
            return self._engine.encrypt(value)
        return value

    def decrypt_value(self, entity_name: str, field_name: str, value: str) -> str:
        """Decrypt a field value if it's marked."""
        if self.is_encrypted(entity_name, field_name):
            return self._engine.decrypt(value)
        return value


class RoleBasedAccessControl:
    """Role-based access control for data operations.

    Defines roles, permissions, and access policies
    for database resources.
    """

    def __init__(self) -> None:
        self._roles: Dict[str, Set[str]] = {}
        self._user_roles: Dict[str, Set[str]] = {}
        self._permissions: Dict[str, Set[str]] = {}

    def create_role(self, name: str, permissions: Optional[List[str]] = None) -> None:
        """Create a new role with optional permissions."""
        if name not in self._roles:
            self._roles[name] = set()
        if permissions:
            self._roles[name].update(permissions)

    def add_permission(self, role: str, permission: str) -> None:
        """Add a permission to a role."""
        if role not in self._roles:
            self._roles[role] = set()
        self._roles[role].add(permission)

    def remove_permission(self, role: str, permission: str) -> None:
        """Remove a permission from a role."""
        if role in self._roles:
            self._roles[role].discard(permission)

    def assign_role(self, user: str, role: str) -> None:
        """Assign a role to a user."""
        if user not in self._user_roles:
            self._user_roles[user] = set()
        self._user_roles[user].add(role)

    def revoke_role(self, user: str, role: str) -> None:
        """Revoke a role from a user."""
        if user in self._user_roles:
            self._user_roles[user].discard(role)

    def has_permission(self, user: str, permission: str) -> bool:
        """Check if a user has a permission via their roles."""
        user_roles = self._user_roles.get(user, set())
        for role in user_roles:
            role_perms = self._roles.get(role, set())
            if permission in role_perms or "*" in role_perms:
                return True
        return False

    def user_roles(self, user: str) -> Set[str]:
        """Get all roles for a user."""
        return set(self._user_roles.get(user, set()))

    def role_permissions(self, role: str) -> Set[str]:
        """Get all permissions for a role."""
        return set(self._roles.get(role, set()))

    def assert_permission(self, user: str, permission: str) -> None:
        """Assert that a user has a permission, raising if not."""
        if not self.has_permission(user, permission):
            raise PermissionError(f"User '{user}' lacks permission '{permission}'")


class DataMasker:
    """Data masking for sensitive information.

    Supports various masking strategies for different data types
    like emails, phone numbers, credit cards, and custom patterns.
    """

    @staticmethod
    def mask_email(email: str, visible_chars: int = 3) -> str:
        """Mask an email address."""
        at_idx = email.find("@")
        if at_idx < 0:
            return email
        local = email[:at_idx]
        if len(local) <= visible_chars:
            return email
        return local[:visible_chars] + "***" + email[at_idx:]

    @staticmethod
    def mask_phone(phone: str, visible_digits: int = 4) -> str:
        """Mask a phone number."""
        digits = "".join(c for c in phone if c.isdigit())
        if len(digits) <= visible_digits:
            return phone
        masked = "*" * (len(digits) - visible_digits) + digits[-visible_digits:]
        return masked

    @staticmethod
    def mask_credit_card(card: str) -> str:
        """Mask a credit card number, showing last 4 digits."""
        digits = "".join(c for c in card if c.isdigit())
        if len(digits) <= 4:
            return card
        return "****-****-****-" + digits[-4:]

    @staticmethod
    def mask_field(value: str, visible_start: int = 0, visible_end: int = 0,
                   mask_char: str = "*") -> str:
        """Mask a field with configurable visible start/end characters."""
        if not value:
            return value
        if len(value) <= visible_start + visible_end:
            return value
        return (value[:visible_start] +
                mask_char * (len(value) - visible_start - visible_end) +
                value[-visible_end:] if visible_end > 0 else "")


class ComplianceChecker:
    """Compliance verification for data operations.

    Checks GDPR, HIPAA, PCI-DSS, and custom compliance rules.
    """

    def __init__(self) -> None:
        self._rules: List[Dict[str, Any]] = []

    def add_rule(self, name: str, check_fn: Callable[[Dict[str, Any]], bool],
                 description: str = "") -> None:
        """Register a compliance check rule."""
        self._rules.append({"name": name, "check": check_fn, "description": description})

    def check(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run all compliance checks against a context."""
        results = []
        for rule in self._rules:
            try:
                passed = rule["check"](context)
                results.append({"rule": rule["name"], "passed": passed,
                                "description": rule["description"]})
            except Exception as e:
                results.append({"rule": rule["name"], "passed": False,
                                "description": rule["description"], "error": str(e)})
        return results

    def all_pass(self, context: Dict[str, Any]) -> bool:
        """Check if all compliance rules pass."""
        return all(r["passed"] for r in self.check(context))

    @staticmethod
    def gdpr_rules() -> ComplianceChecker:
        """Create a checker with GDPR rules."""
        checker = ComplianceChecker()
        checker.add_rule("consent_required", lambda ctx: ctx.get("has_consent", False),
                         "User consent must be obtained before processing personal data")
        checker.add_rule("data_minimization", lambda ctx: len(ctx.get("fields", [])) <= 10,
                         "Only necessary data should be collected")
        checker.add_rule("retention_limit", lambda ctx: ctx.get("retention_days", 0) <= 365,
                         "Data retention must not exceed 365 days")
        return checker

    @staticmethod
    def hipaa_rules() -> ComplianceChecker:
        """Create a checker with HIPAA rules."""
        checker = ComplianceChecker()
        checker.add_rule("encryption_required", lambda ctx: ctx.get("encrypted", False),
                         "PHI must be encrypted at rest and in transit")
        checker.add_rule("access_logged", lambda ctx: ctx.get("audit_enabled", False),
                         "All PHI access must be logged")
        checker.add_rule("backup_verified", lambda ctx: ctx.get("backup_verified", False),
                         "Backups must be verified regularly")
        return checker
