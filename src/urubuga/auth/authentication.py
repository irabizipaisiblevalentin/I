"""auth — Authentication and authorization system.

Supports JWT, sessions, OAuth2, API keys, RBAC, ABAC, and policy-based
authorization.
"""

from __future__ import annotations

import enum
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Callable, Dict, List, Optional, Set


class AuthMethod(enum.Enum):
    NONE = "none"
    SESSION = "session"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC = "basic"


class PermissionLevel(enum.IntEnum):
    NONE = 0
    READ = 1
    WRITE = 2
    DELETE = 3
    ADMIN = 4
    SUPERADMIN = 5


class User:
    """Represents an authenticated user."""
    __slots__ = ("id", "username", "email", "roles", "permissions",
                 "metadata", "authenticated_at", "auth_method")

    def __init__(self, id: str = "", username: str = "", email: str = "",
                 roles: Optional[List[str]] = None,
                 permissions: Optional[Set[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 auth_method: AuthMethod = AuthMethod.NONE) -> None:
        self.id = id or secrets.token_hex(16)
        self.username = username
        self.email = email
        self.roles = roles or []
        self.permissions = permissions or set()
        self.metadata = metadata or {}
        self.authenticated_at: Optional[float] = None
        self.auth_method = auth_method

    @property
    def is_authenticated(self) -> bool:
        return self.authenticated_at is not None

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_any_role(self, *roles: str) -> bool:
        return bool(set(roles) & set(self.roles))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "roles": list(self.roles),
            "permissions": list(self.permissions),
        }


class JWTConfig:
    """JWT configuration."""
    __slots__ = ("secret", "algorithm", "expires_in", "issuer",
                 "audience", "refresh_expires_in")

    def __init__(self, secret: str = "", algorithm: str = "HS256",
                 expires_in: int = 3600, issuer: str = "urubuga",
                 audience: str = "urubuga-api",
                 refresh_expires_in: int = 86400 * 7) -> None:
        self.secret = secret or secrets.token_urlsafe(64)
        self.algorithm = algorithm
        self.expires_in = expires_in
        self.issuer = issuer
        self.audience = audience
        self.refresh_expires_in = refresh_expires_in


class JWTManager:
    """JWT token creation and validation."""

    def __init__(self, config: Optional[JWTConfig] = None) -> None:
        self.config = config or JWTConfig()
        self._revoked: Set[str] = set()

    def create_token(self, user: User,
                     claims: Optional[Dict[str, Any]] = None) -> str:
        now = time.time()
        payload = {
            "sub": user.id,
            "username": user.username,
            "roles": user.roles,
            "permissions": list(user.permissions),
            "iat": now,
            "exp": now + self.config.expires_in,
            "iss": self.config.issuer,
            "aud": self.config.audience,
            "jti": secrets.token_hex(16),
        }
        if claims:
            payload.update(claims)

        return self._encode(payload)

    def create_refresh_token(self, user: User) -> str:
        now = time.time()
        payload = {
            "sub": user.id,
            "type": "refresh",
            "iat": now,
            "exp": now + self.config.refresh_expires_in,
            "iss": self.config.issuer,
            "jti": secrets.token_hex(16),
        }
        return self._encode(payload)

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        if token in self._revoked:
            return None
        try:
            payload = self._decode(token)
            if payload.get("exp", 0) < time.time():
                return None
            return payload
        except Exception:
            return None

    def extract_user(self, token: str) -> Optional[User]:
        payload = self.validate_token(token)
        if not payload:
            return None
        user = User(
            id=payload.get("sub", ""),
            username=payload.get("username", ""),
            roles=payload.get("roles", []),
            permissions=set(payload.get("permissions", [])),
        )
        user.authenticated_at = payload.get("iat")
        user.auth_method = AuthMethod.JWT
        return user

    def revoke_token(self, token: str) -> None:
        self._revoked.add(token)

    def _encode(self, payload: Dict[str, Any]) -> str:
        header = {"alg": self.config.algorithm, "typ": "JWT"}
        header_b64 = self._b64url(json.dumps(header).encode())
        payload_b64 = self._b64url(json.dumps(payload).encode())
        signing_input = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self.config.secret.encode(), signing_input.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{signing_input}.{signature}"

    def _decode(self, token: str) -> Dict[str, Any]:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("invalid token format")
        header_b64, payload_b64, signature = parts
        signing_input = f"{header_b64}.{payload_b64}"
        expected = hmac.new(
            self.config.secret.encode(), signing_input.encode(),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid signature")
        return json.loads(self._b64url_decode(payload_b64))

    @staticmethod
    def _b64url(data: bytes) -> str:
        import base64
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    @staticmethod
    def _b64url_decode(s: str) -> bytes:
        import base64
        padding = 4 - len(s) % 4
        s += "=" * padding
        return base64.urlsafe_b64decode(s)


class SessionStore:
    """In-memory session store."""

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._ttl: Dict[str, float] = {}

    def create(self, user: User, ttl: int = 3600) -> str:
        session_id = secrets.token_urlsafe(32)
        self._sessions[session_id] = {
            "user": user.to_dict(),
            "created_at": time.time(),
        }
        self._ttl[session_id] = time.time() + ttl
        return session_id

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        if session_id not in self._sessions:
            return None
        if time.time() > self._ttl.get(session_id, 0):
            self.destroy(session_id)
            return None
        return self._sessions.get(session_id)

    def destroy(self, session_id: str) -> bool:
        self._sessions.pop(session_id, None)
        self._ttl.pop(session_id, None)
        return True

    def count(self) -> int:
        return len(self._sessions)


class APIKeyManager:
    """API key management."""

    def __init__(self) -> None:
        self._keys: Dict[str, Dict[str, Any]] = {}

    def create_key(self, user_id: str, name: str = "",
                   scopes: Optional[List[str]] = None,
                   expires_in: int = 86400 * 365) -> str:
        key = f"urubuga_{secrets.token_urlsafe(32)}"
        self._keys[key] = {
            "user_id": user_id,
            "name": name,
            "scopes": scopes or ["*"],
            "created_at": time.time(),
            "expires_at": time.time() + expires_in,
        }
        return key

    def validate_key(self, key: str) -> Optional[Dict[str, Any]]:
        data = self._keys.get(key)
        if not data:
            return None
        if time.time() > data.get("expires_at", 0):
            del self._keys[key]
            return None
        return data

    def revoke_key(self, key: str) -> bool:
        return self._keys.pop(key, None) is not None

    def list_keys(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        keys = []
        for key, data in self._keys.items():
            if user_id and data.get("user_id") != user_id:
                continue
            keys.append({"key": key[:16] + "...", **data})
        return keys


class Role:
    """A role with associated permissions."""
    __slots__ = ("name", "permissions", "description")

    def __init__(self, name: str, permissions: Optional[List[str]] = None,
                 description: str = "") -> None:
        self.name = name
        self.permissions = permissions or []
        self.description = description

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions or "*" in self.permissions


class Policy:
    """An authorization policy."""
    __slots__ = ("name", "check_fn", "description")

    def __init__(self, name: str, check_fn: Callable,
                 description: str = "") -> None:
        self.name = name
        self.check_fn = check_fn
        self.description = description

    def evaluate(self, user: User, resource: Any = None,
                 action: str = "") -> bool:
        return bool(self.check_fn(user, resource, action))


class AuthorizationManager:
    """Central authorization manager with RBAC and policy support."""

    def __init__(self) -> None:
        self._roles: Dict[str, Role] = {}
        self._policies: Dict[str, Policy] = {}
        self._user_roles: Dict[str, List[str]] = {}

    def add_role(self, role: Role) -> None:
        self._roles[role.name] = role

    def add_policy(self, policy: Policy) -> None:
        self._policies[policy.name] = policy

    def assign_role(self, user_id: str, role_name: str) -> None:
        roles = self._user_roles.setdefault(user_id, [])
        if role_name not in roles:
            roles.append(role_name)

    def revoke_role(self, user_id: str, role_name: str) -> bool:
        roles = self._user_roles.get(user_id, [])
        if role_name in roles:
            roles.remove(role_name)
            return True
        return False

    def get_user_roles(self, user_id: str) -> List[str]:
        return list(self._user_roles.get(user_id, []))

    def check_permission(self, user: User, permission: str) -> bool:
        if user.has_permission(permission):
            return True
        for role_name in user.roles:
            role = self._roles.get(role_name)
            if role and role.has_permission(permission):
                return True
        return False

    def check_policy(self, user: User, policy_name: str,
                     resource: Any = None, action: str = "") -> bool:
        policy = self._policies.get(policy_name)
        if not policy:
            return False
        return policy.evaluate(user, resource, action)

    def authorize(self, user: User, action: str, resource: Any = None,
                  policy_name: Optional[str] = None) -> bool:
        if policy_name:
            return self.check_policy(user, policy_name, resource, action)
        return self.check_permission(user, action)

    def role_count(self) -> int:
        return len(self._roles)

    def policy_count(self) -> int:
        return len(self._policies)
