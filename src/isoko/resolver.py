"""resolver — Dependency resolver for isoko.

Implements a SAT-like dependency resolver with topological ordering,
conflict detection, and deterministic output.
"""

from __future__ import annotations

import os
from collections import deque
from typing import Any, Dict, List, Optional, Set, Tuple

from isoko.semver import Range, Version, max_satisfying


class PackageNode:
    """A node in the dependency graph."""

    __slots__ = ("name", "version", "deps", "requested_by", "is_dev", "is_build", "is_optional")

    def __init__(self, name: str, version: Version, deps: Optional[Dict[str, str]] = None) -> None:
        self.name = name
        self.version = version
        self.deps: Dict[str, str] = deps or {}
        self.requested_by: List[str] = []
        self.is_dev: bool = False
        self.is_build: bool = False
        self.is_optional: bool = False

    def __repr__(self) -> str:
        return f"PackageNode({self.name}@{self.version})"


class ConflictError(Exception):
    """Raised when dependency resolution fails."""
    def __init__(self, message: str, conflicts: Optional[List[str]] = None) -> None:
        self.conflicts = conflicts or []
        super().__init__(message)


class Resolver:
    """Dependency resolver with conflict detection."""

    def __init__(self, registry: Optional[Any] = None) -> None:
        self._registry = registry
        self._resolved: Dict[str, PackageNode] = {}
        self._resolving: Set[str] = set()
        self._conflicts: List[str] = []
        self._available_cache: Dict[str, List[Version]] = {}

    def resolve(self, manifest: Any) -> Dict[str, PackageNode]:
        """Resolve all dependencies from a manifest. Returns resolved graph."""
        self._resolved.clear()
        self._resolving.clear()
        self._conflicts.clear()

        # Resolve main dependencies
        for name, spec in manifest.dependencies.items():
            self._resolve_package(name, spec, [], is_dev=False)

        # Resolve dev dependencies
        for name, spec in manifest.dev_dependencies.items():
            node = self._resolve_package(name, spec, [], is_dev=True)
            if node:
                node.is_dev = True

        # Resolve build dependencies
        for name, spec in manifest.build_dependencies.items():
            node = self._resolve_package(name, spec, [], is_build=True)
            if node:
                node.is_build = True

        # Resolve optional dependencies
        for name, spec in manifest.optional_dependencies.items():
            node = self._resolve_package(name, spec, [], is_optional=True)
            if node:
                node.is_optional = True

        if self._conflicts:
            raise ConflictError(
                f"dependency resolution failed with {len(self._conflicts)} conflict(s)",
                self._conflicts,
            )

        return dict(self._resolved)

    def _resolve_package(self, name: str, spec: str, chain: List[str],
                         is_dev: bool = False, is_build: bool = False,
                         is_optional: bool = False) -> Optional[PackageNode]:
        """Resolve a single package and its transitive dependencies."""
        # Circular dependency detection
        if name in self._resolving:
            cycle = " -> ".join(chain + [name])
            self._conflicts.append(f"circular dependency: {cycle}")
            return None

        # Already resolved — check version compatibility
        if name in self._resolved:
            existing = self._resolved[name]
            r = Range(spec)
            if r.satisfies(existing.version):
                return existing
            else:
                self._conflicts.append(
                    f"version conflict for {name}: have {existing.version}, need {spec}"
                )
                return None

        # Find best version
        available = self._get_available_versions(name)
        version = max_satisfying(available, spec)
        if version is None:
            if is_optional:
                return None
            self._conflicts.append(f"no version of {name} satisfies {spec!r}")
            return None

        # Get package metadata
        metadata = self._get_package_metadata(name, version)
        deps = metadata.get("dependencies", {}) if metadata else {}

        node = PackageNode(name, version, deps)
        node.is_dev = is_dev
        node.is_build = is_build
        node.is_optional = is_optional

        # Resolve transitive dependencies
        self._resolving.add(name)
        self._resolved[name] = node

        for dep_name, dep_spec in deps.items():
            self._resolve_package(dep_name, dep_spec, chain + [name])

        self._resolving.discard(name)
        return node

    def _get_available_versions(self, name: str) -> List[Version]:
        """Get available versions from registry or cache."""
        if name in self._available_cache:
            return self._available_cache[name]

        if self._registry:
            versions = self._registry.get_versions(name)
        else:
            versions = []

        self._available_cache[name] = versions
        return versions

    def _get_package_metadata(self, name: str, version: Version) -> Optional[Dict]:
        """Get package metadata from registry."""
        if self._registry:
            return self._registry.get_package(name, str(version))
        return {"dependencies": {}}

    def topological_sort(self, graph: Dict[str, PackageNode]) -> List[PackageNode]:
        """Return packages in topological (install) order."""
        in_degree: Dict[str, int] = {name: 0 for name in graph}
        dependents: Dict[str, List[str]] = {name: [] for name in graph}

        for name, node in graph.items():
            for dep_name in node.deps:
                if dep_name in graph:
                    in_degree[name] += 1
                    dependents[dep_name].append(name)

        queue = deque([name for name, deg in in_degree.items() if deg == 0])
        result: List[PackageNode] = []

        while queue:
            name = queue.popleft()
            result.append(graph[name])
            for dependent in dependents[name]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(graph):
            raise ConflictError("dependency graph has cycles after resolution")

        return result

    def to_dict(self, graph: Dict[str, PackageNode]) -> Dict[str, Any]:
        """Serialize resolved graph to dict."""
        return {
            name: {
                "version": str(node.version),
                "dependencies": {k: v for k, v in node.deps.items() if k in graph},
            }
            for name, node in graph.items()
        }
