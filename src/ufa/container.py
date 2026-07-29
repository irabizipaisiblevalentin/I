"""container — Dependency Injection container.

Implements singleton, transient, scoped, and factory registrations
with automatic discovery, lazy injection, and interface-based resolution.
"""

from __future__ import annotations

import enum
import threading
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, get_type_hints

T = TypeVar("T")


class Scope(enum.IntEnum):
    SINGLETON = 0
    TRANSIENT = 1
    SCOPED = 2


class Registration:
    """A DI registration entry."""
    __slots__ = ("service_type", "implementation", "scope", "factory", "name", "tags")

    def __init__(self, service_type: Type, implementation: Any = None,
                 scope: Scope = Scope.SINGLETON, factory: Optional[Callable] = None,
                 name: str = "", tags: Optional[List[str]] = None) -> None:
        self.service_type = service_type
        self.implementation = implementation or service_type
        self.scope = scope
        self.factory = factory
        self.name = name
        self.tags = tags or []

    def __repr__(self) -> str:
        return f"Registration({self.service_type.__name__}, {self.scope.name})"


class Container:
    """Dependency Injection container."""

    def __init__(self, parent: Optional["Container"] = None) -> None:
        self._parent = parent
        self._registrations: Dict[str, Registration] = {}
        self._singletons: Dict[str, Any] = {}
        self._scoped: Dict[str, Dict[str, Any]] = {}
        self._current_scope_id: str = "default"
        self._lock = threading.Lock()

    def register(self, service_type: Type, implementation: Any = None,
                 scope: Scope = Scope.SINGLETON, factory: Optional[Callable] = None,
                 name: str = "", tags: Optional[List[str]] = None) -> None:
        """Register a service type with its implementation."""
        key = self._key(service_type, name)
        reg = Registration(service_type, implementation, scope, factory, name, tags)
        with self._lock:
            self._registrations[key] = reg

    def register_singleton(self, service_type: Type, implementation: Any = None,
                           name: str = "") -> None:
        self.register(service_type, implementation, Scope.SINGLETON, name=name)

    def register_transient(self, service_type: Type, implementation: Any = None,
                           name: str = "") -> None:
        self.register(service_type, implementation, Scope.TRANSIENT, name=name)

    def register_scoped(self, service_type: Type, implementation: Any = None,
                        name: str = "") -> None:
        self.register(service_type, implementation, Scope.SCOPED, name=name)

    def register_factory(self, service_type: Type, factory: Callable,
                         scope: Scope = Scope.SINGLETON, name: str = "") -> None:
        self.register(service_type, scope=scope, factory=factory, name=name)

    def register_instance(self, service_type: Type, instance: Any,
                          name: str = "") -> None:
        """Register a pre-created instance as a singleton."""
        key = self._key(service_type, name)
        reg = Registration(service_type, type(instance), Scope.SINGLETON, name=name)
        with self._lock:
            self._registrations[key] = reg
            self._singletons[key] = instance

    def resolve(self, service_type: Type, name: str = "") -> Any:
        """Resolve a service from the container."""
        key = self._key(service_type, name)

        with self._lock:
            if key in self._singletons:
                return self._singletons[key]
            scope_dict = self._scoped.get(self._current_scope_id, {})
            if key in scope_dict:
                return scope_dict[key]

        reg = self._find_registration(service_type, name)
        if reg is None:
            if self._parent:
                return self._parent.resolve(service_type, name)
            raise LookupError(f"no registration for {service_type.__name__}")

        instance = self._create_instance(reg)

        if reg.scope == Scope.SINGLETON:
            with self._lock:
                self._singletons[key] = instance
        elif reg.scope == Scope.SCOPED:
            with self._lock:
                scope_dict = self._scoped.setdefault(self._current_scope_id, {})
                scope_dict[key] = instance

        return instance

    def try_resolve(self, service_type: Type, name: str = "") -> Optional[Any]:
        try:
            return self.resolve(service_type, name)
        except LookupError:
            return None

    def has(self, service_type: Type, name: str = "") -> bool:
        key = self._key(service_type, name)
        if key in self._registrations:
            return True
        if self._parent and self._parent.has(service_type, name):
            return True
        return False

    def create_scope(self) -> "Container":
        """Create a child scope."""
        scope = Container(parent=self)
        scope._current_scope_id = str(id(scope))
        return scope

    def _create_instance(self, reg: Registration) -> Any:
        """Create an instance from a registration."""
        if reg.factory:
            return reg.factory(self)

        impl = reg.implementation
        if callable(impl) and not isinstance(impl, type):
            return impl(self)

        if isinstance(impl, type):
            hints = {}
            try:
                hints = get_type_hints(impl.__init__)
            except Exception:
                pass

            kwargs = {}
            for param_name, param_type in hints.items():
                if param_name == "return":
                    continue
                try:
                    kwargs[param_name] = self.resolve(param_type)
                except LookupError:
                    pass

            return impl(**kwargs) if kwargs else impl()

        return impl

    def _find_registration(self, service_type: Type, name: str = "") -> Optional[Registration]:
        key = self._key(service_type, name)
        if key in self._registrations:
            return self._registrations[key]

        for reg in self._registrations.values():
            if reg.service_type == service_type and reg.name == name:
                return reg
            try:
                if isinstance(service_type, type) and isinstance(reg.service_type, type):
                    if issubclass(service_type, reg.service_type):
                        return reg
            except TypeError:
                pass

        if self._parent:
            return self._parent._find_registration(service_type, name)
        return None

    def _key(self, service_type: Type, name: str = "") -> str:
        type_name = getattr(service_type, "__name__", str(service_type))
        return f"{type_name}:{name}" if name else type_name

    def registrations(self) -> List[Registration]:
        return list(self._registrations.values())

    def clear(self) -> None:
        with self._lock:
            self._registrations.clear()
            self._singletons.clear()
            self._scoped.clear()
