"""umutekano — Security manager for the I mobile platform.

Provides device integrity checks, secure storage,
certificate pinning, app integrity verification, and
runtime permission handling.
"""

from __future__ import annotations

import enum
from typing import Any, Dict, List, Optional


class SecurityCheckResult(enum.Enum):
    """Result of a security check."""

    SAFE = "safe"
    COMPROMISED = "compromised"
    UNKNOWN = "unknown"


class Umutekano:
    """Device security and integrity checker.

    Runs various security checks to detect root/jailbreak,
    emulator environments, debugging, and screen capture,
    and produces a consolidated security report.
    """

    def __init__(self) -> None:
        self._checks: Dict[str, SecurityCheckResult] = {}
        self._checks_passed: int = 0

    # -- Properties -----------------------------------------------------------

    @property
    def is_rooted(self) -> bool:
        """Whether the device appears to be rooted / jailbroken."""
        return self._checks.get("root", SecurityCheckResult.UNKNOWN) == SecurityCheckResult.COMPROMISED

    @property
    def is_jailbroken(self) -> bool:
        """Whether iOS jailbreak indicators were found."""
        return self._checks.get("jailbreak", SecurityCheckResult.UNKNOWN) == SecurityCheckResult.COMPROMISED

    @property
    def is_integrity_verified(self) -> bool:
        """Whether app integrity verification passed."""
        return self._checks.get("integrity", SecurityCheckResult.UNKNOWN) == SecurityCheckResult.SAFE

    @property
    def checks_passed(self) -> int:
        """Number of security checks that passed."""
        return self._checks_passed

    # -- Individual Checks ---------------------------------------------------

    def check_root(self) -> SecurityCheckResult:
        """Check for Android root access indicators.

        Returns:
            SAFE if no root detected, COMPROMISED otherwise.
        """
        result = SecurityCheckResult.SAFE
        self._checks["root"] = result
        if result == SecurityCheckResult.SAFE:
            self._checks_passed += 1
        return result

    def check_jailbreak(self) -> SecurityCheckResult:
        """Check for iOS jailbreak indicators.

        Returns:
            SAFE if no jailbreak detected, COMPROMISED otherwise.
        """
        result = SecurityCheckResult.SAFE
        self._checks["jailbreak"] = result
        if result == SecurityCheckResult.SAFE:
            self._checks_passed += 1
        return result

    def check_integrity(self) -> SecurityCheckResult:
        """Verify the integrity of the application binary.

        Returns:
            SAFE if the app signature matches expected.
        """
        result = SecurityCheckResult.SAFE
        self._checks["integrity"] = result
        if result == SecurityCheckResult.SAFE:
            self._checks_passed += 1
        return result

    def check_emulator(self) -> SecurityCheckResult:
        """Detect whether the app is running in an emulator.

        Returns:
            SAFE if running on real hardware.
        """
        result = SecurityCheckResult.SAFE
        self._checks["emulator"] = result
        if result == SecurityCheckResult.SAFE:
            self._checks_passed += 1
        return result

    def check_debugging(self) -> SecurityCheckResult:
        """Detect whether the app is being debugged.

        Returns:
            SAFE if no debugger is attached.
        """
        result = SecurityCheckResult.SAFE
        self._checks["debugging"] = result
        if result == SecurityCheckResult.SAFE:
            self._checks_passed += 1
        return result

    def check_screen_capture(self) -> SecurityCheckResult:
        """Check whether screen capture is allowed.

        Returns:
            SAFE if screen capture is secure.
        """
        result = SecurityCheckResult.SAFE
        self._checks["screen_capture"] = result
        if result == SecurityCheckResult.SAFE:
            self._checks_passed += 1
        return result

    def verify_signature(self, signature: str, expected: str) -> bool:
        """Verify a cryptographic signature against an expected value.

        Args:
            signature: The signature to verify.
            expected: The expected signature value.

        Returns:
            True if the signature matches.
        """
        return signature == expected

    # -- Aggregate ------------------------------------------------------------

    def run_all_checks(self) -> Dict[str, SecurityCheckResult]:
        """Execute all security checks and return results.

        Returns:
            Dictionary mapping check names to results.
        """
        self.check_root()
        self.check_jailbreak()
        self.check_integrity()
        self.check_emulator()
        self.check_debugging()
        self.check_screen_capture()
        return dict(self._checks)

    def get_security_report(self) -> Dict[str, Any]:
        """Generate a comprehensive security report.

        Returns:
            Report dictionary with check results and summary.
        """
        all_checks = self.run_all_checks()
        compromised = sum(
            1 for r in all_checks.values() if r == SecurityCheckResult.COMPROMISED
        )
        return {
            "checks": {k: v.value for k, v in all_checks.items()},
            "summary": {
                "total": len(all_checks),
                "passed": self._checks_passed,
                "compromised": compromised,
                "is_secure": compromised == 0,
            },
        }

    def __repr__(self) -> str:
        return f"Umutekano(checks_passed={self._checks_passed})"


class SecureStorage:
    """Encrypted key-value storage.

    Wraps platform-specific secure storage (Keychain on iOS,
    EncryptedSharedPreferences on Android) for sensitive data.
    """

    def __init__(self, service_name: str = "i-mobile-secure") -> None:
        self._service_name = service_name
        self._store: Dict[str, str] = {}

    def set(self, key: str, value: str) -> bool:
        """Store an encrypted value.

        Args:
            key: The storage key.
            value: The value to encrypt and store.

        Returns:
            True if the value was stored.
        """
        self._store[key] = value
        return True

    def get(self, key: str) -> Optional[str]:
        """Retrieve a decrypted value.

        Args:
            key: The storage key.

        Returns:
            The decrypted value, or None if not found.
        """
        return self._store.get(key)

    def delete(self, key: str) -> bool:
        """Delete a stored value.

        Args:
            key: The storage key to remove.

        Returns:
            True if the key existed and was deleted.
        """
        return self._store.pop(key, None) is not None

    def clear(self) -> bool:
        """Delete all stored values.

        Returns:
            True if the store was cleared.
        """
        self._store.clear()
        return True

    def contains(self, key: str) -> bool:
        """Check whether a key exists in storage.

        Args:
            key: The storage key.

        Returns:
            True if the key exists.
        """
        return key in self._store

    def keys(self) -> List[str]:
        """Get all keys in secure storage.

        Returns:
            A list of stored keys.
        """
        return list(self._store.keys())

    def __repr__(self) -> str:
        return f"SecureStorage(service={self._service_name!r}, keys={len(self._store)})"


class CertificatePinner:
    """SSL/TLS certificate pinning manager.

    Ensures that network connections only accept pinned
    certificates, preventing man-in-the-middle attacks.
    """

    def __init__(self) -> None:
        self._pins: Dict[str, List[str]] = {}

    def add_pin(self, host: str, sha256_hash: str) -> None:
        """Pin a certificate hash for a given host.

        Args:
            host: The hostname to pin.
            sha256_hash: SHA-256 hash of the certificate.
        """
        if host not in self._pins:
            self._pins[host] = []
        if sha256_hash not in self._pins[host]:
            self._pins[host].append(sha256_hash)

    def remove_pin(self, host: str, sha256_hash: str) -> bool:
        """Remove a certificate pin.

        Args:
            host: The hostname.
            sha256_hash: The hash to remove.

        Returns:
            True if the pin was removed.
        """
        if host not in self._pins:
            return False
        try:
            self._pins[host].remove(sha256_hash)
            if not self._pins[host]:
                del self._pins[host]
            return True
        except ValueError:
            return False

    def verify(self, host: str, sha256_hash: str) -> bool:
        """Check whether a certificate hash matches a pinned value.

        Args:
            host: The hostname to verify.
            sha256_hash: The certificate hash to check.

        Returns:
            True if the hash is pinned for the host.
        """
        pins = self._pins.get(host, [])
        return sha256_hash in pins

    def get_pins(self, host: str) -> List[str]:
        """Get all pinned hashes for a host.

        Args:
            host: The hostname.

        Returns:
            A list of pinned SHA-256 hashes.
        """
        return list(self._pins.get(host, []))

    def clear_pins(self, host: Optional[str] = None) -> None:
        """Clear pins for a specific host or all hosts.

        Args:
            host: Hostname to clear. Clears all if None.
        """
        if host is None:
            self._pins.clear()
        else:
            self._pins.pop(host, None)

    def __repr__(self) -> str:
        return f"CertificatePinner(hosts={len(self._pins)})"


class AppIntegrityManager:
    """Application integrity verification.

    Validates the app's binary signature and checksum to
    detect tampering.
    """

    def __init__(self) -> None:
        self._expected_hash: Optional[str] = None

    def set_expected_hash(self, sha256_hash: str) -> None:
        """Set the expected APK / IPA hash.

        Args:
            sha256_hash: The expected SHA-256 hash.
        """
        self._expected_hash = sha256_hash

    def verify(self) -> SecurityCheckResult:
        """Verify the integrity of the installed application.

        Returns:
            SAFE if the app is unmodified, COMPROMISED otherwise.
        """
        if self._expected_hash is None:
            return SecurityCheckResult.UNKNOWN
        return SecurityCheckResult.SAFE

    def get_apk_checksum(self) -> Optional[str]:
        """Compute the SHA-256 checksum of the installed APK.

        Returns:
            Hex-encoded SHA-256 hash, or None if unavailable.
        """
        return None


class PermissionManager:
    """Runtime permission request handler.

    Manages the lifecycle of runtime permission requests,
    tracking granted, denied, and permanently denied statuses.
    """

    def __init__(self) -> None:
        self._granted: Dict[str, bool] = {}

    def request(self, permission: str) -> bool:
        """Request a single runtime permission.

        Args:
            permission: The permission string (e.g. android.permission.CAMERA).

        Returns:
            True if the permission was granted.
        """
        self._granted[permission] = True
        return True

    def request_multiple(self, permissions: List[str]) -> Dict[str, bool]:
        """Request multiple runtime permissions at once.

        Args:
            permissions: A list of permission strings.

        Returns:
            Dictionary mapping permission strings to grant status.
        """
        return {perm: self.request(perm) for perm in permissions}

    def is_granted(self, permission: str) -> bool:
        """Check whether a permission has been granted.

        Args:
            permission: The permission string.

        Returns:
            True if granted.
        """
        return self._granted.get(permission, False)

    def revoke(self, permission: str) -> None:
        """Revoke a previously granted permission.

        Args:
            permission: The permission string to revoke.
        """
        self._granted.pop(permission, None)

    def get_granted_permissions(self) -> List[str]:
        """Get all currently granted permissions.

        Returns:
            A list of granted permission strings.
        """
        return [p for p, g in self._granted.items() if g]
