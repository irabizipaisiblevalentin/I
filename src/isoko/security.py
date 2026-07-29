"""security — Security model for isoko.

Provides package signing, checksum verification, dependency auditing,
and supply chain security features.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Checksums
# ---------------------------------------------------------------------------

def sha256(data: bytes) -> str:
    """Compute SHA-256 hex digest."""
    return hashlib.sha256(data).hexdigest()


def sha512(data: bytes) -> str:
    """Compute SHA-512 hex digest."""
    return hashlib.sha512(data).hexdigest()


def checksum_file(path: str, algorithm: str = "sha256") -> str:
    """Compute checksum of a file."""
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def verify_checksum(data: bytes, expected: str, algorithm: str = "sha256") -> bool:
    """Verify data matches expected checksum."""
    actual = hashlib.new(algorithm, data).hexdigest()
    return actual == expected


def verify_file_checksum(path: str, expected: str, algorithm: str = "sha256") -> bool:
    """Verify file checksum."""
    return checksum_file(path, algorithm) == expected


# ---------------------------------------------------------------------------
# Lock file checksums
# ---------------------------------------------------------------------------

class IntegritySet:
    """Set of checksums for a package."""

    def __init__(self) -> None:
        self.checksums: Dict[str, str] = {}

    def add(self, algorithm: str, digest: str) -> None:
        self.checksums[algorithm] = digest

    def verify(self, data: bytes) -> Tuple[bool, str]:
        """Verify data against any stored checksum. Returns (ok, algorithm)."""
        for algo, digest in self.checksums.items():
            actual = hashlib.new(algo, data).hexdigest()
            if actual == digest:
                return True, algo
        return False, ""

    def to_dict(self) -> Dict[str, str]:
        return dict(self.checksums)

    @classmethod
    def from_dict(cls, d: Dict[str, str]) -> IntegritySet:
        s = cls()
        s.checksums = dict(d)
        return s


# ---------------------------------------------------------------------------
# SBOM (Software Bill of Materials)
# ---------------------------------------------------------------------------

class SBOMEntry:
    """Single entry in a Software Bill of Materials."""
    __slots__ = ("name", "version", "license", "checksum", "source", "dependencies")

    def __init__(self, name: str = "", version: str = "", license: str = "",
                 checksum: str = "", source: str = "", dependencies: Optional[List[str]] = None) -> None:
        self.name = name
        self.version = version
        self.license = license
        self.checksum = checksum
        self.source = source
        self.dependencies = dependencies or []

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"name": self.name, "version": self.version}
        if self.license:
            d["license"] = self.license
        if self.checksum:
            d["checksum"] = self.checksum
        if self.source:
            d["source"] = self.source
        if self.dependencies:
            d["dependencies"] = self.dependencies
        return d


class SBOM:
    """Software Bill of Materials."""

    def __init__(self, project_name: str = "", project_version: str = "") -> None:
        self.project_name = project_name
        self.project_version = project_version
        self.entries: List[SBOMEntry] = []
        self.generated_at = time.time()

    def add(self, entry: SBOMEntry) -> None:
        self.entries.append(entry)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bomFormat": "isoko",
            "specVersion": "1.0",
            "project": {
                "name": self.project_name,
                "version": self.project_version,
            },
            "generatedAt": self.generated_at,
            "components": [e.to_dict() for e in self.entries],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

class AuditFinding:
    """A security audit finding."""
    __slots__ = ("severity", "package", "version", "title", "description", "recommendation")

    def __init__(self, severity: str = "info", package: str = "",
                 version: str = "", title: str = "",
                 description: str = "", recommendation: str = "") -> None:
        self.severity = severity
        self.package = package
        self.version = version
        self.title = title
        self.description = description
        self.recommendation = recommendation

    def to_dict(self) -> Dict[str, str]:
        return {
            "severity": self.severity,
            "package": self.package,
            "version": self.version,
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
        }


class AuditReport:
    """Security audit report."""
    __slots__ = ("findings", "scanned_at", "total_packages", "vulnerable_count")

    def __init__(self) -> None:
        self.findings: List[AuditFinding] = []
        self.scanned_at = time.time()
        self.total_packages = 0
        self.vulnerable_count = 0

    @property
    def is_clean(self) -> bool:
        return self.vulnerable_count == 0

    def add_finding(self, finding: AuditFinding) -> None:
        self.findings.append(finding)
        if finding.severity in ("critical", "high", "medium"):
            self.vulnerable_count += 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "totalPackages": self.total_packages,
            "vulnerablePackages": self.vulnerable_count,
            "findings": [f.to_dict() for f in self.findings],
            "scannedAt": self.scanned_at,
        }


# ---------------------------------------------------------------------------
# Trusted publishers
# ---------------------------------------------------------------------------

class TrustedPublishers:
    """Registry of trusted package publishers."""

    def __init__(self) -> None:
        self._trusted: Dict[str, List[str]] = {}  # package -> list of trusted publishers

    def add_trusted(self, package: str, publisher: str) -> None:
        self._trusted.setdefault(package, []).append(publisher)

    def is_trusted(self, package: str, publisher: str) -> bool:
        if package not in self._trusted:
            return True  # no restriction
        return publisher in self._trusted[package]

    def to_dict(self) -> Dict[str, List[str]]:
        return dict(self._trusted)

    @classmethod
    def from_dict(cls, d: Dict[str, List[str]]) -> TrustedPublishers:
        tp = cls()
        tp._trusted = dict(d)
        return tp
