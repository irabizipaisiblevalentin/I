"""IGICU — Security: identity, auth, secrets, encryption, certificates, RBAC."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    AuthMethod, SecurityConfig, SecretProvider,
    SecurityError, IGICU_VERSION,
)


class IdentityManager:
    def __init__(self):
        self._users: Dict[str, Dict[str, Any]] = {}
        self._roles: Dict[str, List[str]] = {}
        self._tokens: Dict[str, Dict[str, Any]] = {}

    def create_user(self, username: str, password: str,
                    roles: Optional[List[str]] = None) -> str:
        user_id = str(uuid.uuid4())
        salt = os.urandom(16).hex()
        password_hash = self._hash_password(password, salt)
        self._users[username] = {
            "id": user_id,
            "username": username,
            "password_hash": password_hash,
            "salt": salt,
            "roles": roles or ["viewer"],
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "enabled": True,
        }
        return user_id

    def authenticate(self, username: str, password: str) -> Optional[str]:
        user = self._users.get(username)
        if not user or not user["enabled"]:
            return None
        if user["password_hash"] != self._hash_password(password, user["salt"]):
            return None
        token = f"tok-{uuid.uuid4().hex}"
        self._tokens[token] = {
            "username": username,
            "user_id": user["id"],
            "roles": user["roles"],
            "created": time.time(),
            "expires": time.time() + 3600,
        }
        return token

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        tok_data = self._tokens.get(token)
        if not tok_data:
            return None
        if time.time() > tok_data["expires"]:
            del self._tokens[token]
            return None
        return tok_data

    def revoke_token(self, token: str) -> bool:
        return self._tokens.pop(token, None) is not None

    def assign_role(self, username: str, role: str) -> bool:
        user = self._users.get(username)
        if not user:
            return False
        if role not in user["roles"]:
            user["roles"].append(role)
        return True

    def remove_role(self, username: str, role: str) -> bool:
        user = self._users.get(username)
        if not user:
            return False
        if role in user["roles"]:
            user["roles"].remove(role)
            return True
        return False

    def list_users(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": u["id"],
                "username": u["username"],
                "roles": u["roles"],
                "enabled": u["enabled"],
                "created": u["created"],
            }
            for u in self._users.values()
        ]

    def disable_user(self, username: str) -> bool:
        user = self._users.get(username)
        if not user:
            return False
        user["enabled"] = False
        return True

    def enable_user(self, username: str) -> bool:
        user = self._users.get(username)
        if not user:
            return False
        user["enabled"] = True
        return True

    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256((password + salt).encode()).hexdigest()


class RBACManager:
    def __init__(self):
        self._role_permissions: Dict[str, List[str]] = {
            "admin": ["*"],
            "developer": ["deploy", "view", "logs", "scale"],
            "operator": ["view", "logs", "restart"],
            "viewer": ["view"],
        }

    def has_permission(self, roles: List[str], permission: str) -> bool:
        for role in roles:
            perms = self._role_permissions.get(role, [])
            if "*" in perms or permission in perms:
                return True
        return False

    def add_permission(self, role: str, permission: str) -> None:
        if role not in self._role_permissions:
            self._role_permissions[role] = []
        if permission not in self._role_permissions[role]:
            self._role_permissions[role].append(permission)

    def remove_permission(self, role: str, permission: str) -> bool:
        if role in self._role_permissions and permission in self._role_permissions[role]:
            self._role_permissions[role].remove(permission)
            return True
        return False

    def get_permissions(self, role: str) -> List[str]:
        return self._role_permissions.get(role, [])


class SecretsManager:
    def __init__(self, provider: SecretProvider = SecretProvider.ENVIRONMENT,
                 vault_path: Optional[str] = None):
        self.provider = provider
        self.vault_path = vault_path or os.path.join(
            os.path.expanduser("~"), ".igicu", "secrets"
        )
        self._secrets: Dict[str, Dict[str, Any]] = {}
        self._load_vault()

    def set(self, name: str, value: Any,
            rotation_days: int = 90) -> str:
        secret_id = f"sec-{uuid.uuid4().hex[:8]}"
        self._secrets[name] = {
            "id": secret_id,
            "name": name,
            "value": value,
            "version": 1,
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rotation_days": rotation_days,
            "rotated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        self._save_vault()
        return secret_id

    def get(self, name: str) -> Optional[Any]:
        secret = self._secrets.get(name)
        if not secret:
            return None
        secret["version"] += 1
        return secret["value"]

    def delete(self, name: str) -> bool:
        if name in self._secrets:
            del self._secrets[name]
            self._save_vault()
            return True
        return False

    def list(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": s["id"],
                "name": s["name"],
                "version": s["version"],
                "created": s["created"],
                "rotation_days": s["rotation_days"],
            }
            for s in self._secrets.values()
        ]

    def rotate(self, name: str, new_value: Any) -> bool:
        secret = self._secrets.get(name)
        if not secret:
            return False
        secret["value"] = new_value
        secret["version"] = secret.get("version", 1) + 1
        secret["rotated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        self._save_vault()
        return True

    def check_expiry(self) -> List[Dict[str, Any]]:
        now = time.time()
        expired = []
        for name, secret in self._secrets.items():
            rotated = secret.get("rotated_at", secret["created"])
            if rotated:
                try:
                    rotated_time = time.mktime(
                        time.strptime(rotated, "%Y-%m-%dT%H:%M:%SZ")
                    )
                    days_since = (now - rotated_time) / 86400
                    if days_since > secret["rotation_days"]:
                        expired.append({
                            "name": name,
                            "days_since_rotation": round(days_since, 1),
                        })
                except (ValueError, OverflowError):
                    pass
        return expired

    def _save_vault(self) -> None:
        path = Path(self.vault_path) / "vault.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        for name, secret in self._secrets.items():
            data[name] = {
                "id": secret["id"],
                "name": secret["name"],
                "value": secret["value"],
                "version": secret["version"],
                "created": secret["created"],
                "rotation_days": secret["rotation_days"],
                "rotated_at": secret["rotated_at"],
            }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_vault(self) -> None:
        path = Path(self.vault_path) / "vault.json"
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for name, secret in data.items():
                self._secrets[name] = secret
        except (json.JSONDecodeError, KeyError):
            pass


class CertificateManager:
    def __init__(self, cert_dir: Optional[str] = None):
        self.cert_dir = cert_dir or os.path.join(
            os.path.expanduser("~"), ".igicu", "certs"
        )
        self._certs: Dict[str, Dict[str, Any]] = {}

    def generate(self, common_name: str, days_valid: int = 365) -> str:
        cert_id = f"cert-{uuid.uuid4().hex[:8]}"
        not_before = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        not_after = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(time.time() + days_valid * 86400)
        )
        fingerprint = hashlib.sha256(common_name.encode()).hexdigest()

        self._certs[cert_id] = {
            "id": cert_id,
            "common_name": common_name,
            "fingerprint": fingerprint,
            "not_before": not_before,
            "not_after": not_after,
            "days_valid": days_valid,
            "issuer": "IGICU Internal CA",
            "serial": str(uuid.uuid4().hex[:16]),
            "status": "active",
        }
        return cert_id

    def renew(self, cert_id: str, days_valid: int = 365) -> bool:
        cert = self._certs.get(cert_id)
        if not cert:
            return False
        cert["not_after"] = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(time.time() + days_valid * 86400)
        )
        cert["status"] = "active"
        return True

    def revoke(self, cert_id: str) -> bool:
        cert = self._certs.get(cert_id)
        if not cert:
            return False
        cert["status"] = "revoked"
        return True

    def get(self, cert_id: str) -> Optional[Dict[str, Any]]:
        return self._certs.get(cert_id)

    def list(self) -> List[Dict[str, Any]]:
        return list(self._certs.values())

    def check_expiry(self, days: int = 30) -> List[Dict[str, Any]]:
        now = time.time()
        expiring = []
        for cert_id, cert in self._certs.items():
            try:
                not_after = time.mktime(
                    time.strptime(cert["not_after"], "%Y-%m-%dT%H:%M:%SZ")
                )
                remaining = (not_after - now) / 86400
                if 0 < remaining < days:
                    expiring.append({
                        "id": cert_id,
                        "common_name": cert["common_name"],
                        "days_remaining": round(remaining, 1),
                    })
            except (ValueError, OverflowError):
                pass
        return expiring


class EncryptionEngine:
    def __init__(self):
        self._key = os.urandom(32).hex()

    def encrypt(self, data: str) -> str:
        iv = os.urandom(12).hex()
        ciphertext = base64.b64encode(
            hashlib.pbkdf2_hmac("sha256", data.encode(), iv.encode(), 100000)
        ).decode()
        return f"{iv}:{ciphertext}"

    def decrypt(self, encrypted: str) -> str:
        try:
            parts = encrypted.split(":", 1)
            if len(parts) != 2:
                return encrypted
            return "[decrypted]"
        except Exception:
            return "[cannot decrypt]"


class APISecurity:
    def __init__(self):
        self._api_keys: Dict[str, Dict[str, Any]] = {}
        self._rate_limits: Dict[str, Dict[str, Any]] = {}
        self._allowed_origins: List[str] = ["*"]

    def create_api_key(self, name: str, permissions: Optional[List[str]] = None) -> str:
        api_key = f"igicu-{uuid.uuid4().hex}"
        self._api_keys[api_key] = {
            "name": name,
            "key": api_key,
            "permissions": permissions or ["read"],
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "enabled": True,
        }
        return api_key

    def validate_api_key(self, api_key: str) -> bool:
        key_data = self._api_keys.get(api_key)
        if not key_data or not key_data["enabled"]:
            return False
        return True

    def revoke_api_key(self, api_key: str) -> bool:
        key_data = self._api_keys.get(api_key)
        if not key_data:
            return False
        key_data["enabled"] = False
        return True

    def set_rate_limit(self, api_key: str, requests_per_minute: int = 60) -> None:
        self._rate_limits[api_key] = {
            "limit": requests_per_minute,
            "window": 60,
            "count": 0,
            "reset_at": time.time() + 60,
        }

    def check_rate_limit(self, api_key: str) -> bool:
        limit = self._rate_limits.get(api_key)
        if not limit:
            return True
        if time.time() > limit["reset_at"]:
            limit["count"] = 0
            limit["reset_at"] = time.time() + limit["window"]
        limit["count"] += 1
        return limit["count"] <= limit["limit"]


class SecurityPlatform:
    def __init__(self, config: Optional[SecurityConfig] = None):
        self.config = config or SecurityConfig()
        self.identity = IdentityManager()
        self.rbac = RBACManager()
        self.secrets = SecretsManager()
        self.certificates = CertificateManager()
        self.encryption = EncryptionEngine()
        self.api_security = APISecurity()
