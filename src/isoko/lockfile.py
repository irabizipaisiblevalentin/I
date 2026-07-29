"""lockfile — Lock file (ilang.lock) for deterministic builds.

The lock file records exact resolved versions and checksums for every
dependency, ensuring reproducible installations across environments.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional

from isoko.semver import Version


# ---------------------------------------------------------------------------
# Lock file entry
# ---------------------------------------------------------------------------

class LockEntry:
    """A single locked dependency entry."""

    __slots__ = (
        "name", "version", "source", "checksum",
        "dependencies", "resolved_url", "integrity",
    )

    def __init__(self, name: str = "", version: str = "",
                 source: str = "registry", checksum: str = "",
                 dependencies: Optional[Dict[str, str]] = None,
                 resolved_url: str = "", integrity: str = "") -> None:
        self.name = name
        self.version = version
        self.source = source
        self.checksum = checksum
        self.dependencies = dependencies or {}
        self.resolved_url = resolved_url
        self.integrity = integrity

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "version": self.version,
            "source": self.source,
        }
        if self.checksum:
            d["checksum"] = self.checksum
        if self.integrity:
            d["integrity"] = self.integrity
        if self.resolved_url:
            d["resolved"] = self.resolved_url
        if self.dependencies:
            d["dependencies"] = self.dependencies
        return d

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> LockEntry:
        return cls(
            name=name,
            version=data.get("version", ""),
            source=data.get("source", "registry"),
            checksum=data.get("checksum", ""),
            dependencies=data.get("dependencies", {}),
            resolved_url=data.get("resolved", ""),
            integrity=data.get("integrity", ""),
        )

    def __repr__(self) -> str:
        return f"LockEntry({self.name}@{self.version})"


# ---------------------------------------------------------------------------
# Lock file
# ---------------------------------------------------------------------------

class LockFile:
    """ilang.lock — deterministic dependency lock file."""

    FORMAT_VERSION = "1.0"

    def __init__(self, project_name: str = "") -> None:
        self.project_name = project_name
        self.format_version = self.FORMAT_VERSION
        self.entries: Dict[str, LockEntry] = {}
        self.metadata: Dict[str, Any] = {}
        self._path: str = ""

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value

    def add(self, entry: LockEntry) -> None:
        self.entries[entry.name] = entry

    def get(self, name: str) -> Optional[LockEntry]:
        return self.entries.get(name)

    def remove(self, name: str) -> bool:
        if name in self.entries:
            del self.entries[name]
            return True
        return False

    def has(self, name: str) -> bool:
        return name in self.entries

    def is_satisfied(self, name: str, version: str) -> bool:
        entry = self.get(name)
        return entry is not None and entry.version == version

    def to_dict(self) -> Dict[str, Any]:
        packages: Dict[str, Any] = {}
        for name in sorted(self.entries):
            packages[name] = self.entries[name].to_dict()
        return {
            "format_version": self.format_version,
            "project": self.project_name,
            "generated_at": self.metadata.get("generated_at", ""),
            "packages": packages,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LockFile:
        lf = cls()
        lf.format_version = data.get("format_version", cls.FORMAT_VERSION)
        lf.project_name = data.get("project", "")
        lf.metadata = {
            "generated_at": data.get("generated_at", ""),
        }
        for name, pdata in data.get("packages", {}).items():
            lf.entries[name] = LockEntry.from_dict(name, pdata)
        return lf

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def checksum(self) -> str:
        """Compute checksum of the lock file contents for change detection."""
        content = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Load / Save
# ---------------------------------------------------------------------------

def load_lockfile(path: str) -> Optional[LockFile]:
    """Load a lock file from disk."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return LockFile.from_dict(data)
    except (json.JSONDecodeError, OSError):
        return None


def save_lockfile(lockfile: LockFile, path: str) -> None:
    """Save a lock file to disk."""
    lockfile.metadata["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(path, "w", encoding="utf-8") as f:
        f.write(lockfile.to_json())
        f.write("\n")


def find_lockfile(start: str = ".") -> Optional[str]:
    """Walk up directories to find ilang.lock."""
    current = os.path.abspath(start)
    for _ in range(50):
        path = os.path.join(current, "ilang.lock")
        if os.path.isfile(path):
            return path
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def create_from_resolved(project_name: str,
                         resolved: Dict[str, Any]) -> LockFile:
    """Create a LockFile from a resolved dependency graph."""
    lf = LockFile(project_name)
    for name, data in resolved.items():
        version = data.get("version", "0.1.0") if isinstance(data, dict) else str(data)
        deps = {}
        if isinstance(data, dict):
            deps = data.get("dependencies", {})
        lf.add(LockEntry(
            name=name,
            version=version,
            source="registry",
            dependencies=deps,
        ))
    return lf
