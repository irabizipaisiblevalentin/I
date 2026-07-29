"""plugins — Plugin system for UFA frameworks.

Supports official, community, private, and enterprise plugins with
version compatibility, dependency validation, sandboxing, and permissions.
"""

from __future__ import annotations

import enum
import time
from typing import Any, Callable, Dict, List, Optional, Set


class PluginState(enum.IntEnum):
    REGISTERED = 0
    LOADED = 1
    INITIALIZED = 2
    STARTED = 3
    STOPPED = 4
    ERROR = -1


class PluginPermission:
    """Permission requested by a plugin."""
    __slots__ = ("name", "description", "required")

    def __init__(self, name: str, description: str = "", required: bool = False) -> None:
        self.name = name
        self.description = description
        self.required = required


class PluginMetadata:
    """Metadata about a plugin."""
    __slots__ = ("name", "version", "author", "description", "framework",
                 "dependencies", "permissions", "tags", "min_ufa_version")

    def __init__(self, name: str = "", version: str = "0.1.0",
                 author: str = "", description: str = "",
                 framework: str = "*", dependencies: Optional[List[str]] = None,
                 permissions: Optional[List[PluginPermission]] = None,
                 tags: Optional[List[str]] = None,
                 min_ufa_version: str = "0.1.0") -> None:
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.framework = framework
        self.dependencies = dependencies or []
        self.permissions = permissions or []
        self.tags = tags or []
        self.min_ufa_version = min_ufa_version

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "framework": self.framework,
            "dependencies": self.dependencies,
            "permissions": [p.name for p in self.permissions],
            "tags": self.tags,
        }


class Plugin:
    """Base class for UFA plugins."""

    def __init__(self) -> None:
        self.metadata = PluginMetadata()
        self._state = PluginState.REGISTERED
        self._context: Any = None

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def state(self) -> PluginState:
        return self._state

    def configure(self, config: Any) -> None:
        pass

    def initialize(self, context: Any) -> None:
        self._context = context

    def start(self) -> None:
        self._state = PluginState.STARTED

    def stop(self) -> None:
        self._state = PluginState.STOPPED

    def destroy(self) -> None:
        self._state = PluginState.REGISTERED

    def on_event(self, event: str, data: Any) -> Optional[Any]:
        return None

    def health_check(self) -> bool:
        return True


class PluginRegistry:
    """Registry for discovering, loading, and managing plugins."""

    def __init__(self) -> None:
        self._plugins: Dict[str, Plugin] = {}
        self._metadata: Dict[str, PluginMetadata] = {}
        self._load_order: List[str] = []
        self._permissions_granted: Set[str] = set()

    def register(self, plugin: Plugin) -> None:
        """Register a plugin."""
        meta = plugin.metadata
        if not meta.name:
            raise ValueError("plugin must have a name")
        self._plugins[meta.name] = plugin
        self._metadata[meta.name] = meta

    def unregister(self, name: str) -> bool:
        if name in self._plugins:
            del self._plugins[name]
            del self._metadata[name]
            if name in self._load_order:
                self._load_order.remove(name)
            return True
        return False

    def get(self, name: str) -> Optional[Plugin]:
        return self._plugins.get(name)

    def has(self, name: str) -> bool:
        return name in self._plugins

    def list_plugins(self) -> List[PluginMetadata]:
        return list(self._metadata.values())

    def resolve_load_order(self) -> List[str]:
        """Topological sort of plugins by dependencies."""
        resolved: List[str] = []
        visited: Set[str] = set()
        visiting: Set[str] = set()

        def visit(name: str) -> None:
            if name in visited:
                return
            if name in visiting:
                raise ValueError(f"circular dependency: {name}")
            visiting.add(name)
            meta = self._metadata.get(name)
            if meta:
                for dep in meta.dependencies:
                    visit(dep)
            visiting.discard(name)
            visited.add(name)
            resolved.append(name)

        for name in self._plugins:
            visit(name)

        self._load_order = resolved
        return resolved

    def validate_dependencies(self) -> List[str]:
        """Check for missing dependencies."""
        errors = []
        for name, meta in self._metadata.items():
            for dep in meta.dependencies:
                if dep not in self._plugins:
                    errors.append(f"{name}: missing dependency '{dep}'")
        return errors

    def check_permissions(self, granted: Set[str]) -> List[str]:
        """Check which plugins have unmet required permissions."""
        unmet = []
        for name, meta in self._metadata.items():
            for perm in meta.permissions:
                if perm.required and perm.name not in granted:
                    unmet.append(f"{name}: requires permission '{perm.name}'")
        return unmet

    def initialize_all(self, context: Any = None) -> None:
        order = self.resolve_load_order()
        for name in order:
            plugin = self._plugins[name]
            plugin._state = PluginState.LOADED
            plugin.initialize(context)
            plugin._state = PluginState.INITIALIZED

    def start_all(self) -> None:
        for name in self._load_order:
            self._plugins[name].start()

    def stop_all(self) -> None:
        for name in reversed(self._load_order):
            self._plugins[name].stop()

    def health_check(self) -> Dict[str, bool]:
        return {name: p.health_check() for name, p in self._plugins.items()}

    def count(self) -> int:
        return len(self._plugins)
