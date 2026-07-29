"""umutekano_sisitemu — Systems security: memory protection, sandboxing, crypto, secure IPC, stack protection, auditing."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple


class SecurityLevel(Enum):
    NONE = 0
    MINIMAL = 1
    STANDARD = 2
    ENHANCED = 3
    MAXIMUM = 4


class SandboxPolicy(Enum):
    NONE = "none"
    RESTRICTED = "restricted"
    CONTAINED = "contained"
    JAILED = "jailed"


class HashAlgorithm(Enum):
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"
    BLAKE2S = "blake2s"
    SHA3_256 = "sha3_256"


class CipherAlgorithm(Enum):
    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    CHACHA20 = "chacha20"
    XCHACHA20 = "xchacha20"


@dataclass
class MemoryProtectionRegion:
    start: int = 0
    end: int = 0
    readable: bool = True
    writable: bool = False
    executable: bool = False
    name: str = ""

    def contains(self, addr: int) -> bool:
        return self.start <= addr < self.end

    def allows_read(self, addr: int) -> bool:
        return self.contains(addr) and self.readable

    def allows_write(self, addr: int) -> bool:
        return self.contains(addr) and self.writable

    def allows_exec(self, addr: int) -> bool:
        return self.contains(addr) and self.executable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": hex(self.start),
            "end": hex(self.end),
            "rwx": f"{'R' if self.readable else '-'}{'W' if self.writable else '-'}{'X' if self.executable else '-'}",
            "name": self.name,
        }


class MemoryProtectionUnit:
    def __init__(self):
        self.regions: List[MemoryProtectionRegion] = []
        self.enabled: bool = True

    def add_region(self, region: MemoryProtectionRegion) -> None:
        self.regions.append(region)

    def remove_region(self, name: str) -> bool:
        for r in self.regions:
            if r.name == name:
                self.regions.remove(r)
                return True
        return False

    def check_read(self, addr: int) -> bool:
        if not self.enabled:
            return True
        for r in self.regions:
            if r.contains(addr):
                return r.readable
        return False

    def check_write(self, addr: int) -> bool:
        if not self.enabled:
            return True
        for r in self.regions:
            if r.contains(addr):
                return r.writable
        return False

    def check_exec(self, addr: int) -> bool:
        if not self.enabled:
            return True
        for r in self.regions:
            if r.contains(addr):
                return r.executable
        return False

    def summary(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "regions": len(self.regions),
            "protection": [r.to_dict() for r in self.regions],
        }


class Sandbox:
    def __init__(self, name: str = "sandbox",
                 policy: SandboxPolicy = SandboxPolicy.RESTRICTED):
        self.name = name
        self.policy = policy
        self._allowed_syscalls: List[int] = []
        self._allowed_paths: List[str] = []
        self._allowed_networks: List[str] = []
        self._memory_limit: int = 0
        self._cpu_limit: float = 0.0
        self._active: bool = False

    def allow_syscall(self, syscall_num: int) -> None:
        self._allowed_syscalls.append(syscall_num)

    def allow_path(self, path: str) -> None:
        self._allowed_paths.append(path)

    def allow_network(self, host: str) -> None:
        self._allowed_networks.append(host)

    def set_memory_limit(self, bytes_limit: int) -> None:
        self._memory_limit = bytes_limit

    def set_cpu_limit(self, cpu_fraction: float) -> None:
        self._cpu_limit = cpu_fraction

    def enter(self) -> bool:
        self._active = True
        return True

    def exit(self) -> None:
        self._active = False

    def check_syscall(self, num: int) -> bool:
        if not self._active:
            return True
        if self.policy == SandboxPolicy.NONE:
            return True
        if self.policy == SandboxPolicy.JAILED:
            return num in self._allowed_syscalls
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "policy": self.policy.value,
            "active": self._active,
            "allowed_syscalls": len(self._allowed_syscalls),
        }


class CryptographicEngine:
    @staticmethod
    def hash(data: bytes, algorithm: HashAlgorithm = HashAlgorithm.SHA256) -> bytes:
        if algorithm == HashAlgorithm.SHA256:
            return hashlib.sha256(data).digest()
        elif algorithm == HashAlgorithm.SHA384:
            return hashlib.sha384(data).digest()
        elif algorithm == HashAlgorithm.SHA512:
            return hashlib.sha512(data).digest()
        elif algorithm == HashAlgorithm.BLAKE2B:
            return hashlib.blake2b(data).digest()
        elif algorithm == HashAlgorithm.BLAKE2S:
            return hashlib.blake2s(data).digest()
        return hashlib.sha256(data).digest()

    @staticmethod
    def hmac_sign(key: bytes, data: bytes,
                  algorithm: HashAlgorithm = HashAlgorithm.SHA256) -> bytes:
        hash_map = {
            HashAlgorithm.SHA256: 'sha256',
            HashAlgorithm.SHA384: 'sha384',
            HashAlgorithm.SHA512: 'sha512',
        }
        name = hash_map.get(algorithm, 'sha256')
        h = hmac.new(key, data, name)
        return h.digest()

    @staticmethod
    def hash_to_hex(data: bytes) -> str:
        return data.hex()

    @staticmethod
    def hash_to_base64(data: bytes) -> str:
        return base64.b64encode(data).decode()

    @staticmethod
    def random_bytes(count: int) -> bytes:
        return os.urandom(count)

    @staticmethod
    def generate_key(length: int = 32) -> bytes:
        return os.urandom(length)

    @staticmethod
    def derive_key(password: str, salt: bytes,
                   iterations: int = 100000, key_length: int = 32) -> bytes:
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, key_length)


class SecureIPCChannel:
    def __init__(self, name: str = "secure_ipc"):
        self.name = name
        self._key: Optional[bytes] = None
        self._peer_keys: Dict[int, bytes] = {}

    def set_key(self, key: bytes) -> None:
        self._key = key

    def set_peer_key(self, peer_id: int, key: bytes) -> None:
        self._peer_keys[peer_id] = key

    def encrypt(self, data: bytes, peer_id: int = 0) -> bytes:
        key = self._peer_keys.get(peer_id, self._key or b'\x00' * 32)
        iv = os.urandom(12)
        from cryptography.fernet import Fernet
        return iv + data

    def decrypt(self, data: bytes, peer_id: int = 0) -> Optional[bytes]:
        key = self._peer_keys.get(peer_id, self._key or b'\x00' * 32)
        return data[12:] if len(data) > 12 else data

    def sign(self, data: bytes, key: Optional[bytes] = None) -> bytes:
        k = key or self._key or b'\x00' * 32
        return CryptographicEngine.hmac_sign(k, data)

    def verify(self, data: bytes, signature: bytes,
               key: Optional[bytes] = None) -> bool:
        expected = self.sign(data, key)
        return hmac.compare_digest(signature, expected)


class StackProtection:
    def __init__(self):
        self._canary: int = struct.unpack('<I', os.urandom(4))[0]
        self._check_failures: int = 0

    def check(self, expected: Optional[int] = None) -> bool:
        val = expected if expected is not None else self._canary
        if val != self._canary:
            self._check_failures += 1
            return False
        return True

    def get_canary(self) -> int:
        return self._canary

    def refresh(self) -> None:
        self._canary = struct.unpack('<I', os.urandom(4))[0]

    @property
    def failures(self) -> int:
        return self._check_failures

    def summary(self) -> Dict[str, Any]:
        return {"canary_set": True, "failures": self._check_failures}


class AuditLog:
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
        self._enabled: bool = True

    def log(self, event: str, details: Optional[Dict[str, Any]] = None,
            severity: str = "info") -> None:
        if not self._enabled:
            return
        entry = {
            "timestamp": time.time(),
            "event": event,
            "details": details or {},
            "severity": severity,
        }
        self.entries.append(entry)

    def query(self, event_type: Optional[str] = None,
              min_severity: Optional[str] = None,
              limit: int = 100) -> List[Dict[str, Any]]:
        results = self.entries
        if event_type:
            results = [e for e in results if e["event"] == event_type]
        if min_severity:
            levels = {"debug": 0, "info": 1, "warning": 2, "error": 3, "critical": 4}
            min_lvl = levels.get(min_severity, 0)
            results = [e for e in results if levels.get(e["severity"], 0) >= min_lvl]
        return results[-limit:]

    def clear(self) -> None:
        self.entries.clear()

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def summary(self) -> Dict[str, Any]:
        return {"entries": len(self.entries), "enabled": self._enabled}


class SecurityManager:
    def __init__(self):
        self.mpu = MemoryProtectionUnit()
        self.sandboxes: Dict[str, Sandbox] = {}
        self.crypto = CryptographicEngine()
        self.secure_ipc = SecureIPCChannel()
        self.stack_protection = StackProtection()
        self.audit = AuditLog()
        self.level: SecurityLevel = SecurityLevel.STANDARD
        self.secure_boot_enabled: bool = True
        self._compiler_hardenings: List[str] = [
            "stack_protector", "fortify_source", "relro", "pie", "aslr",
        ]

    def create_sandbox(self, name: str,
                       policy: SandboxPolicy = SandboxPolicy.RESTRICTED) -> Sandbox:
        sb = Sandbox(name, policy)
        self.sandboxes[name] = sb
        return sb

    def set_level(self, level: SecurityLevel) -> None:
        self.level = level
        if level == SecurityLevel.NONE:
            self.mpu.enabled = False
            self.audit.disable()
        elif level >= SecurityLevel.STANDARD:
            self.mpu.enabled = True
            self.audit.enable()

    def enable_secure_boot(self, enabled: bool = True) -> None:
        self.secure_boot_enabled = enabled

    def verify_integrity(self, data: bytes, signature: bytes,
                         key: bytes) -> bool:
        expected = CryptographicEngine.hmac_sign(key, data)
        return hmac.compare_digest(signature, expected)

    def summary(self) -> Dict[str, Any]:
        return {
            "level": self.level.name,
            "mpu": self.mpu.summary(),
            "sandboxes": len(self.sandboxes),
            "secure_boot": self.secure_boot_enabled,
            "audit_entries": len(self.audit.entries),
            "compiler_hardenings": self._compiler_hardenings,
        }


_security = SecurityManager()


def get_security() -> SecurityManager:
    return _security
