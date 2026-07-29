"""security — Authentication, authorization, and encryption.

Provides user/identity management, RBAC permissions, policy enforcement,
encryption/decryption, token management, and audit logging.
"""

from __future__ import annotations

import enum
import hashlib
import hmac
import os
import secrets
import time
from typing import Any, Callable, Dict, List, Optional, Set


class PermissionLevel(enum.IntEnum):
    NONE = 0
    READ = 1
    WRITE = 2
    ADMIN = 3
    SUPERADMIN = 4


class Identity:
    """Represents an authenticated user or service."""
    __slots__ = ("id", "username", "roles", "permissions", "metadata",
                 "authenticated_at", "expires_at")

    def __init__(self, id: str = "", username: str = "",
                 roles: Optional[List[str]] = None,
                 permissions: Optional[Set[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        self.id = id or secrets.token_hex(16)
        self.username = username
        self.roles = roles or []
        self.permissions = permissions or set()
        self.metadata = metadata or {}
        self.authenticated_at: Optional[float] = None
        self.expires_at: Optional[float] = None

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def has_permission(self, permission: str) -> bool:
        if permission in self.permissions:
            return True
        return False

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "roles": list(self.roles),
            "permissions": list(self.permissions),
        }


class Policy:
    """An authorization policy rule."""
    __slots__ = ("name", "check_fn", "description")

    def __init__(self, name: str, check_fn: Callable,
                 description: str = "") -> None:
        self.name = name
        self.check_fn = check_fn
        self.description = description

    def evaluate(self, identity: Identity, resource: Any = None,
                 action: str = "") -> bool:
        return bool(self.check_fn(identity, resource, action))


class Token:
    """An authentication token."""
    __slots__ = ("value", "identity_id", "created_at", "expires_at",
                 "token_type", "metadata")

    def __init__(self, identity_id: str, expires_in_sec: float = 3600.0,
                 token_type: str = "bearer",
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        self.value = secrets.token_urlsafe(32)
        self.identity_id = identity_id
        self.created_at = time.time()
        self.expires_at = self.created_at + expires_in_sec
        self.token_type = token_type
        self.metadata = metadata or {}

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def to_header(self) -> str:
        return f"{self.token_type} {self.value}"


class AuditEntry:
    """An audit log entry."""
    __slots__ = ("timestamp", "identity_id", "action", "resource",
                 "result", "details")

    def __init__(self, identity_id: str, action: str, resource: str = "",
                 result: str = "success",
                 details: Optional[Dict[str, Any]] = None) -> None:
        self.timestamp = time.time()
        self.identity_id = identity_id
        self.action = action
        self.resource = resource
        self.result = result
        self.details = details or {}


class SecurityManager:
    """Central security manager for auth, authz, encryption, and auditing."""

    def __init__(self) -> None:
        self._identities: Dict[str, Identity] = {}
        self._tokens: Dict[str, Token] = {}
        self._policies: Dict[str, Policy] = {}
        self._audit_log: List[AuditEntry] = []
        self._salt = secrets.token_bytes(16)

    def create_identity(self, username: str, roles: Optional[List[str]] = None,
                        permissions: Optional[Set[str]] = None) -> Identity:
        identity = Identity(username=username, roles=roles, permissions=permissions)
        self._identities[identity.id] = identity
        return identity

    def get_identity(self, identity_id: str) -> Optional[Identity]:
        return self._identities.get(identity_id)

    def authenticate_token(self, token_value: str) -> Optional[Identity]:
        token = self._tokens.get(token_value)
        if token and not token.is_expired:
            return self._identities.get(token.identity_id)
        return None

    def issue_token(self, identity_id: str,
                    expires_in_sec: float = 3600.0) -> Optional[Token]:
        if identity_id not in self._identities:
            return None
        token = Token(identity_id, expires_in_sec)
        self._tokens[token.value] = token
        self._audit(identity_id, "token_issued")
        return token

    def revoke_token(self, token_value: str) -> bool:
        if token_value in self._tokens:
            del self._tokens[token_value]
            return True
        return False

    def register_policy(self, name: str, check_fn: Callable,
                        description: str = "") -> None:
        self._policies[name] = Policy(name, check_fn, description)

    def authorize(self, identity: Identity, action: str,
                  resource: Any = None,
                  policy_name: Optional[str] = None) -> bool:
        if policy_name and policy_name in self._policies:
            result = self._policies[policy_name].evaluate(identity, resource, action)
        else:
            result = identity.has_permission(action)

        self._audit(identity.id, action,
                    result=result and "success" or "denied")
        return result

    def encrypt(self, data: str) -> str:
        key = hashlib.sha256(self._salt + data.encode()).hexdigest()
        return key

    def hash_password(self, password: str) -> str:
        salted = self._salt.hex() + password
        return hashlib.sha256(salted.encode()).hexdigest()

    def verify_password(self, password: str, hashed: str) -> bool:
        return self.hash_password(password) == hashed

    def generate_secret(self, length: int = 32) -> str:
        return secrets.token_urlsafe(length)

    def _audit(self, identity_id: str, action: str, resource: str = "",
               result: str = "success") -> None:
        entry = AuditEntry(identity_id, action, resource, result)
        self._audit_log.append(entry)

    def audit_log(self, identity_id: Optional[str] = None,
                  limit: int = 100) -> List[AuditEntry]:
        logs = self._audit_log
        if identity_id:
            logs = [e for e in logs if e.identity_id == identity_id]
        return logs[-limit:]

    def identity_count(self) -> int:
        return len(self._identities)

    def token_count(self) -> int:
        return len(self._tokens)

    def policy_count(self) -> int:
        return len(self._policies)
