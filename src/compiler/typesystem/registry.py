"""
Type Registry for the I Programming Language

Central registry for all type definitions in the program.
Manages type creation, lookup, and lifecycle.
Supports incremental compilation via per-file registrations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from .types import (
    Type, TypeKind, NamedType, ClassType, StructType, EnumType,
    TraitType, InterfaceType, FunctionType, GenericType,
    TypeVariable, ModuleType,
    TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_CHAR, TYPE_STRING,
    TYPE_NONE, TYPE_ANY, TYPE_UNKNOWN, TYPE_NEVER,
)


# ══════════════════════════════════════════════════════════════════
# Type Definition Metadata
# ══════════════════════════════════════════════════════════════════


@dataclass
class MemberInfo:
    """Information about a type member (field or method)."""

    name: str
    type: Type
    is_const: bool = False
    is_static: bool = False
    is_mutable: bool = True
    visibility: str = "public"
    declaration_file: str = ""
    declaration_line: int = 0


@dataclass
class MethodSignature:
    """Full method signature."""

    name: str
    param_types: List[Type] = field(default_factory=list)
    param_names: List[str] = field(default_factory=list)
    return_type: Type = field(default_factory=lambda: TYPE_NONE)
    is_static: bool = False
    is_const: bool = False
    generic_params: List[TypeVariable] = field(default_factory=list)
    visibility: str = "public"
    declaration_file: str = ""
    declaration_line: int = 0
    has_default_body: bool = False


@dataclass
class TraitRequirement:
    """A required method or property for a trait."""

    name: str
    signature: Optional[MethodSignature] = None
    is_method: bool = True
    is_property: bool = False
    property_type: Optional[Type] = None


@dataclass
class TypeDefinition:
    """
    Complete definition of a user-defined type.

    Stores all metadata needed for type checking: members, methods,
    parent types, trait implementations, and generic parameters.
    """

    name: str
    kind: TypeKind
    type_obj: Type
    parent_name: Optional[str] = None
    implemented_traits: List[str] = field(default_factory=list)
    implemented_interfaces: List[str] = field(default_factory=list)
    generic_params: List[TypeVariable] = field(default_factory=list)
    members: Dict[str, MemberInfo] = field(default_factory=dict)
    methods: Dict[str, MethodSignature] = field(default_factory=dict)
    trait_requirements: List[TraitRequirement] = field(default_factory=list)
    is_abstract: bool = False
    is_sealed: bool = False
    declaration_file: str = ""
    declaration_line: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ══════════════════════════════════════════════════════════════════
# Type Registry
# ══════════════════════════════════════════════════════════════════


class TypeRegistry:
    """
    Central registry for all type definitions.

    The registry is the single source of truth for type information.
    It stores both built-in and user-defined types, and supports
    efficient lookup by name.
    """

    def __init__(self) -> None:
        self._types: Dict[str, TypeDefinition] = {}
        self._type_objects: Dict[str, Type] = {}
        self._file_registrations: Dict[str, Set[str]] = {}
        self._alias_map: Dict[str, str] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register all built-in types."""
        builtins = [
            ("int", TypeKind.INT, TYPE_INT),
            ("float", TypeKind.FLOAT, TYPE_FLOAT),
            ("bool", TypeKind.BOOL, TYPE_BOOL),
            ("char", TypeKind.CHAR, TYPE_CHAR),
            ("umuntu", TypeKind.STRING, TYPE_STRING),
            ("none", TypeKind.NONE_TYPE, TYPE_NONE),
            ("any", TypeKind.ANY, TYPE_ANY),
        ]

        for name, kind, type_obj in builtins:
            defn = TypeDefinition(
                name=name,
                kind=kind,
                type_obj=type_obj,
                is_sealed=True,
            )
            self._types[name] = defn
            self._type_objects[name] = type_obj

        # Bilingual aliases
        aliases = {
            "tandukanya": "float",
            "gutoranya": "float",
            "bbyte": "umuntu",
            "urutonde": "list",
            "ikarita": "map",
        }
        for alias, target in aliases.items():
            self._alias_map[alias] = target

    def register(self, defn: TypeDefinition, file: str = "") -> bool:
        """
        Register a type definition.

        Returns True if registration succeeded, False if the name
        is already registered (duplicate type).
        """
        if defn.name in self._types:
            existing = self._types[defn.name]
            if existing.is_sealed:
                return False
            if existing.declaration_file and existing.declaration_file != file:
                return False

        self._types[defn.name] = defn
        self._type_objects[defn.name] = defn.type_obj

        if file:
            if file not in self._file_registrations:
                self._file_registrations[file] = set()
            self._file_registrations[file].add(defn.name)

        return True

    def get(self, name: str) -> Optional[TypeDefinition]:
        """Look up a type definition by name."""
        resolved = self._alias_map.get(name, name)
        return self._types.get(resolved)

    def get_type(self, name: str) -> Optional[Type]:
        """Look up the Type object by name."""
        resolved = self._alias_map.get(name, name)
        return self._type_objects.get(resolved)

    def has(self, name: str) -> bool:
        """Check if a type is registered."""
        resolved = self._alias_map.get(name, name)
        return resolved in self._types

    def add_alias(self, alias: str, target: str) -> None:
        """Add a type alias."""
        self._alias_map[alias] = target

    def remove_file(self, file: str) -> List[str]:
        """Remove all types registered from a file (for incremental recompilation)."""
        if file not in self._file_registrations:
            return []
        names = self._file_registrations.pop(file)
        removed = []
        for name in names:
            if name in self._types and self._types[name].declaration_file == file:
                del self._types[name]
                self._type_objects.pop(name, None)
                removed.append(name)
        return removed

    def get_methods(self, name: str) -> Dict[str, MethodSignature]:
        """Get all methods for a type."""
        defn = self.get(name)
        if defn is None:
            return {}
        return dict(defn.methods)

    def get_members(self, name: str) -> Dict[str, MemberInfo]:
        """Get all members for a type."""
        defn = self.get(name)
        if defn is None:
            return {}
        return dict(defn.members)

    def get_parent(self, name: str) -> Optional[str]:
        """Get the parent type name."""
        defn = self.get(name)
        if defn is None:
            return None
        return defn.parent_name

    def get_traits(self, name: str) -> List[str]:
        """Get implemented traits for a type."""
        defn = self.get(name)
        if defn is None:
            return []
        return list(defn.implemented_traits)

    def get_interfaces(self, name: str) -> List[str]:
        """Get implemented interfaces for a type."""
        defn = self.get(name)
        if defn is None:
            return []
        return list(defn.implemented_interfaces)

    def is_subclass_of(self, child: str, parent: str) -> bool:
        """Check if child is a subclass of parent (transitive)."""
        current = child
        visited: Set[str] = set()
        while current and current not in visited:
            if current == parent:
                return True
            visited.add(current)
            defn = self.get(current)
            if defn is None:
                break
            current = defn.parent_name
        return False

    def get_all_type_names(self) -> List[str]:
        """Get all registered type names."""
        return list(self._types.keys())

    @property
    def registered_count(self) -> int:
        """Number of registered types."""
        return len(self._types)

    def get_all_methods(self) -> Dict[str, Dict[str, MethodSignature]]:
        """Get all methods for all types."""
        result: Dict[str, Dict[str, MethodSignature]] = {}
        for name, defn in self._types.items():
            if defn.methods:
                result[name] = dict(defn.methods)
        return result

    def get_trait_names(self) -> List[str]:
        """Get all registered trait names."""
        return [name for name, defn in self._types.items()
                if defn.kind == TypeKind.TRAIT]

    def get_interface_names(self) -> List[str]:
        """Get all registered interface names."""
        return [name for name, defn in self._types.items()
                if defn.kind == TypeKind.INTERFACE]

    def get_class_names(self) -> List[str]:
        """Get all registered class names."""
        return [name for name, defn in self._types.items()
                if defn.kind == TypeKind.CLASS]

    def get_inheritance_chain(self, name: str) -> List[str]:
        """Get the full inheritance chain from child to root."""
        chain: List[str] = []
        current = name
        visited: Set[str] = set()
        while current and current not in visited:
            chain.append(current)
            visited.add(current)
            defn = self.get(current)
            if defn is None:
                break
            current = defn.parent_name
        return chain

    def get_all_subtypes(self, parent_name: str) -> List[str]:
        """Get all types that are subclasses of parent_name."""
        result: List[str] = []
        for name in self._types:
            if self.is_subclass_of(name, parent_name) and name != parent_name:
                result.append(name)
        return result

    def implements_trait(self, type_name: str, trait_name: str) -> bool:
        """Check if a type implements a given trait."""
        defn = self.get(type_name)
        if defn is None:
            return False
        if trait_name in defn.implemented_traits:
            return True
        parent = defn.parent_name
        while parent:
            pdefn = self.get(parent)
            if pdefn and trait_name in pdefn.implemented_traits:
                return True
            parent = pdefn.parent_name if pdefn else None
        return False

    def clear(self) -> None:
        """Clear all registrations (for testing)."""
        self._types.clear()
        self._type_objects.clear()
        self._file_registrations.clear()
        self._alias_map.clear()
        self._register_builtins()

    @property
    def count(self) -> int:
        """Number of registered types."""
        return len(self._types)
