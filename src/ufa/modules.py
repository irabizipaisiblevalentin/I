"""modules — Module system for organizing framework code.

Provides module registration, dependency resolution, lifecycle
management, and hierarchical module organization.
"""

from __future__ import annotations

import enum
import time
from typing import Any, Callable, Dict, List, Optional, Set


class ModuleState(enum.IntEnum):
    REGISTERED = 0
    LOADING = 1
    LOADED = 2
    INITIALIZING = 3
    INITIALIZED = 4
    STARTING = 5
    STARTED = 6
    STOPPING = 7
    STOPPED = 8
    ERROR = -1


class ModuleMetadata:
    """Metadata about a module."""
    __slots__ = ("name", "version", "description", "author",
                 "dependencies", "tags")

    def __init__(self, name: str = "", version: str = "0.1.0",
                 description: str = "", author: str = "",
                 dependencies: Optional[List[str]] = None,
                 tags: Optional[List[str]] = None) -> None:
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.dependencies = dependencies or []
        self.tags = tags or []


class Module:
    """Base class for UFA modules."""

    def __init__(self) -> None:
        self.metadata = ModuleMetadata()
        self._state = ModuleState.REGISTERED
        self._services: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def state(self) -> ModuleState:
        return self._state

    def configure(self, config: Any) -> None:
        pass

    def initialize(self, context: Any) -> None:
        pass

    def start(self) -> None:
        self._state = ModuleState.STARTED

    def stop(self) -> None:
        self._state = ModuleState.STOPPED

    def register_service(self, name: str, service: Any) -> None:
        self._services[name] = service

    def get_service(self, name: str) -> Optional[Any]:
        return self._services.get(name)

    def services(self) -> Dict[str, Any]:
        return dict(self._services)


class ModuleRegistry:
    """Registry for discovering, loading, and managing modules."""

    def __init__(self) -> None:
        self._modules: Dict[str, Module] = {}
        self._metadata: Dict[str, ModuleMetadata] = {}
        self._load_order: List[str] = []

    def register(self, module: Module) -> None:
        meta = module.metadata
        if not meta.name:
            raise ValueError("module must have a name")
        self._modules[meta.name] = module
        self._metadata[meta.name] = meta

    def unregister(self, name: str) -> bool:
        if name in self._modules:
            del self._modules[name]
            del self._metadata[name]
            if name in self._load_order:
                self._load_order.remove(name)
            return True
        return False

    def get(self, name: str) -> Optional[Module]:
        return self._modules.get(name)

    def has(self, name: str) -> bool:
        return name in self._modules

    def list_modules(self) -> List[ModuleMetadata]:
        return list(self._metadata.values())

    def resolve_load_order(self) -> List[str]:
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

        for name in self._modules:
            visit(name)

        self._load_order = resolved
        return resolved

    def validate_dependencies(self) -> List[str]:
        errors = []
        for name, meta in self._metadata.items():
            for dep in meta.dependencies:
                if dep not in self._modules:
                    errors.append(f"{name}: missing dependency '{dep}'")
        return errors

    def initialize_all(self, context: Any = None) -> None:
        order = self.resolve_load_order()
        for name in order:
            module = self._modules[name]
            module._state = ModuleState.LOADING
            try:
                module.configure(context)
                module._state = ModuleState.LOADED
                module.initialize(context)
                module._state = ModuleState.INITIALIZED
            except Exception:
                module._state = ModuleState.ERROR
                raise

    def start_all(self) -> None:
        for name in self._load_order:
            self._modules[name].start()

    def stop_all(self) -> None:
        for name in reversed(self._load_order):
            self._modules[name].stop()

    def module_count(self) -> int:
        return len(self._modules)
