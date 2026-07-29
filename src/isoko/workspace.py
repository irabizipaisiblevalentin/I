"""workspace — Workspace and monorepo support for isoko."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from isoko.manifest import Manifest, load as load_manifest


class WorkspaceConfig:
    """Workspace configuration."""
    __slots__ = ("members", "exclude", "shared_deps", "root")

    def __init__(self, root: str = "") -> None:
        self.root = root
        self.members: List[str] = []
        self.exclude: List[str] = []
        self.shared_deps: Dict[str, str] = {}


class WorkspacePackage:
    """A package within a workspace."""
    __slots__ = ("name", "path", "manifest", "dependencies")

    def __init__(self, name: str = "", path: str = "") -> None:
        self.name = name
        self.path = path
        self.manifest: Optional[Manifest] = None
        self.dependencies: List[str] = []


class Workspace:
    """Workspace manager for monorepo support."""

    def __init__(self, root: str = ".") -> None:
        self._root = os.path.abspath(root)
        self._config = WorkspaceConfig(self._root)
        self._packages: Dict[str, WorkspacePackage] = {}

    @property
    def root(self) -> str:
        return self._root

    @property
    def config(self) -> WorkspaceConfig:
        return self._config

    @property
    def packages(self) -> Dict[str, WorkspacePackage]:
        return dict(self._packages)

    def is_workspace(self) -> bool:
        """Check if the given directory is a workspace root."""
        return os.path.exists(os.path.join(self._root, "ilang-workspace.json"))

    def load(self) -> None:
        """Load workspace configuration."""
        ws_path = os.path.join(self._root, "ilang-workspace.json")
        if not os.path.exists(ws_path):
            raise FileNotFoundError(f"workspace config not found: {ws_path}")

        with open(ws_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._config.members = data.get("members", ["packages/*"])
        self._config.exclude = data.get("exclude", [])
        self._config.shared_deps = data.get("shared-dependencies", {})

        # Discover packages
        self._discover_packages()

    def save(self) -> None:
        """Save workspace configuration."""
        ws_path = os.path.join(self._root, "ilang-workspace.json")
        data = {
            "members": self._config.members,
            "exclude": self._config.exclude,
        }
        if self._config.shared_deps:
            data["shared-dependencies"] = self._config.shared_deps
        with open(ws_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _discover_packages(self) -> None:
        """Find all workspace member packages."""
        import glob as _glob

        self._packages.clear()
        for pattern in self._config.members:
            full_pattern = os.path.join(self._root, pattern)
            for match in _glob.glob(full_pattern):
                if not os.path.isdir(match):
                    continue
                # Check for manifest
                for name in ("ilang.toml", "ilang.json"):
                    manifest_path = os.path.join(match, name)
                    if os.path.exists(manifest_path):
                        try:
                            manifest = load_manifest(manifest_path)
                            pkg = WorkspacePackage(manifest.name, match)
                            pkg.manifest = manifest
                            self._packages[manifest.name] = pkg
                        except Exception:
                            pass
                        break

    def get_package(self, name: str) -> Optional[WorkspacePackage]:
        return self._packages.get(name)

    def resolve_local_deps(self) -> Dict[str, List[str]]:
        """Resolve which workspace members depend on other workspace members."""
        local_deps: Dict[str, List[str]] = {}
        all_names = set(self._packages.keys())
        for name, pkg in self._packages.items():
            if pkg.manifest is None:
                continue
            deps = []
            for dep_name in pkg.manifest.all_dependencies:
                if dep_name in all_names:
                    deps.append(dep_name)
            local_deps[name] = deps
        return local_deps

    def topological_order(self) -> List[str]:
        """Return workspace packages in dependency order."""
        local_deps = self.resolve_local_deps()
        visited: set = set()
        order: List[str] = []

        def visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            for dep in local_deps.get(name, []):
                visit(dep)
            order.append(name)

        for name in self._packages:
            visit(name)
        return order

    def create_package(self, name: str, path: str = "") -> str:
        """Create a new package in the workspace."""
        if not path:
            path = os.path.join(self._root, "packages", name)
        os.makedirs(path, exist_ok=True)

        manifest = Manifest()
        manifest.name = name
        manifest.version = "0.1.0"
        manifest.description = f"Workspace package: {name}"

        from isoko.manifest import save
        manifest_path = os.path.join(path, "ilang.json")
        save(manifest, manifest_path)

        # Create basic structure
        lib_dir = os.path.join(path, "lib")
        os.makedirs(lib_dir, exist_ok=True)
        with open(os.path.join(lib_dir, f"{name}.i"), "w") as f:
            f.write(f'// {name} package\n\n')

        self._discover_packages()
        return path
