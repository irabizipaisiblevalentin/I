"""package — Package management utilities for the I language.

Provides package metadata, version management, and dependency resolution stubs.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional


class PackageInfo:
    """Package metadata."""

    __slots__ = ("name", "version", "description", "dependencies", "authors")

    def __init__(self, name: str = "", version: str = "0.1.0",
                 description: str = "", dependencies: Optional[List[str]] = None,
                 authors: Optional[List[str]] = None) -> None:
        self.name = name
        self.version = version
        self.description = description
        self.dependencies = dependencies or []
        self.authors = authors or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
            "authors": self.authors,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PackageInfo:
        return cls(
            name=data.get("name", ""),
            version=data.get("version", "0.1.0"),
            description=data.get("description", ""),
            dependencies=data.get("dependencies", []),
            authors=data.get("authors", []),
        )

    def __repr__(self) -> str:
        return f"PackageInfo({self.name!r}, v{self.version})"


def parse_manifest(path: str) -> PackageInfo:
    """Parse a package manifest (JSON format)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return PackageInfo.from_dict(data)


def save_manifest(info: PackageInfo, path: str) -> None:
    """Save package manifest."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(info.to_dict(), f, indent=2)


def version_satisfies(version: str, requirement: str) -> bool:
    """Check if version satisfies a simple requirement (>=, ==, etc.)."""
    if requirement.startswith(">="):
        return version >= requirement[2:]
    if requirement.startswith("=="):
        return version == requirement[2:]
    if requirement.startswith("!="):
        return version != requirement[2:]
    return version == requirement


def resolve_deps(packages: Dict[str, PackageInfo]) -> List[str]:
    """Simple topological sort of dependencies."""
    visited: set = set()
    result: List[str] = []

    def _visit(name: str) -> None:
        if name in visited:
            return
        visited.add(name)
        if name in packages:
            for dep in packages[name].dependencies:
                _visit(dep)
        result.append(name)

    for name in packages:
        _visit(name)
    return result
