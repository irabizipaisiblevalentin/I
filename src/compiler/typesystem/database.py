"""
Type Database for the I Programming Language

Stores computed type information, subtype relationships,
trait implementations, and type compatibility matrices.
Provides efficient caching for incremental type checking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Optional, Set, Tuple

from .types import Type, TypeKind, TypeVariable, FunctionType, OptionalType


# ══════════════════════════════════════════════════════════════════
# Type Relationship Cache
# ══════════════════════════════════════════════════════════════════


@dataclass
class SubtypeRelation:
    """Records a subtype relationship between two types."""

    subtype: str
    supertype: str
    file: str = ""
    line: int = 0


@dataclass
class TraitImplementation:
    """Records that a type implements a trait."""

    type_name: str
    trait_name: str
    file: str = ""
    line: int = 0
    method_mappings: Dict[str, str] = field(default_factory=dict)


# ══════════════════════════════════════════════════════════════════
# Type Database
# ══════════════════════════════════════════════════════════════════


class TypeDatabase:
    """
    Stores computed type information and relationships.

    Provides:
    - Subtype relationship caching
    - Trait implementation tracking
    - Compatibility matrix for fast checks
    - Per-file invalidation for incremental compilation
    """

    def __init__(self) -> None:
        self._subtype_cache: Dict[Tuple[str, str], bool] = {}
        self._compatible_cache: Dict[Tuple[str, str], bool] = {}
        self._trait_impls: Dict[str, List[TraitImplementation]] = {}
        self._trait_providers: Dict[str, Set[str]] = {}
        self._file_dependencies: Dict[str, Set[str]] = {}
        self._file_types: Dict[str, Set[str]] = {}
        self._constraint_cache: Dict[str, List[Type]] = {}

    def record_subtype(self, subtype: str, supertype: str,
                       file: str = "", line: int = 0) -> None:
        """Record that subtype is a subtype of supertype."""
        key = (subtype, supertype)
        self._subtype_cache[key] = True

        relation = SubtypeRelation(subtype, supertype, file, line)
        if file:
            if file not in self._file_dependencies:
                self._file_dependencies[file] = set()
            self._file_dependencies[file].add(subtype)

    def is_subtype_cached(self, subtype: str, supertype: str) -> Optional[bool]:
        """Check the subtype cache. Returns None if not cached."""
        key = (subtype, supertype)
        return self._subtype_cache.get(key)

    def record_compatible(self, source: str, target: str) -> None:
        """Record that source is compatible with target."""
        key = (source, target)
        self._compatible_cache[key] = True

    def is_compatible_cached(self, source: str, target: str) -> Optional[bool]:
        """Check compatibility cache. Returns None if not cached."""
        key = (source, target)
        return self._compatible_cache.get(key)

    def record_trait_impl(self, impl: TraitImplementation) -> None:
        """Record a trait implementation."""
        if impl.type_name not in self._trait_impls:
            self._trait_impls[impl.type_name] = []
        self._trait_impls[impl.type_name].append(impl)

        if impl.trait_name not in self._trait_providers:
            self._trait_providers[impl.trait_name] = set()
        self._trait_providers[impl.trait_name].add(impl.type_name)

    def implements_trait(self, type_name: str, trait_name: str) -> Optional[bool]:
        """Check if a type implements a trait. None if unknown."""
        impls = self._trait_impls.get(type_name, [])
        for impl in impls:
            if impl.trait_name == trait_name:
                return True
        return None

    def get_trait_providers(self, trait_name: str) -> Set[str]:
        """Get all types that implement a given trait."""
        return self._trait_providers.get(trait_name, set()).copy()

    def get_trait_impls(self, type_name: str) -> List[TraitImplementation]:
        """Get all trait implementations for a type."""
        return list(self._trait_impls.get(type_name, []))

    def record_file_type(self, file: str, type_name: str) -> None:
        """Record that a type is defined in a file."""
        if file not in self._file_types:
            self._file_types[file] = set()
        self._file_types[file].add(type_name)

    def invalidate_file(self, file: str) -> List[str]:
        """
        Invalidate all data associated with a file.
        Returns list of type names that were invalidated.
        """
        types = self._file_types.pop(file, set())
        deps = self._file_dependencies.pop(file, set())

        for name in types:
            self._subtype_cache = {
                k: v for k, v in self._subtype_cache.items()
                if k[0] != name and k[1] != name
            }
            self._compatible_cache = {
                k: v for k, v in self._compatible_cache.items()
                if k[0] != name and k[1] != name
            }

        return list(types | deps)

    def record_type_constraints(self, name: str, constraints: List[Type]) -> None:
        """Record type variable constraints."""
        self._constraint_cache[name] = constraints

    def get_type_constraints(self, name: str) -> List[Type]:
        """Get recorded constraints for a type variable."""
        return list(self._constraint_cache.get(name, []))

    def clear(self) -> None:
        """Clear all cached data."""
        self._subtype_cache.clear()
        self._compatible_cache.clear()
        self._trait_impls.clear()
        self._trait_providers.clear()
        self._file_dependencies.clear()
        self._file_types.clear()
        self._constraint_cache.clear()

    def invalidate_types(self, type_names: List[str]) -> None:
        """Invalidate all data associated with specific type names."""
        for name in type_names:
            self._subtype_cache = {
                k: v for k, v in self._subtype_cache.items()
                if k[0] != name and k[1] != name
            }
            self._compatible_cache = {
                k: v for k, v in self._compatible_cache.items()
                if k[0] != name and k[1] != name
            }

    def get_subtype_chain(self, subtype: str, supertype: str,
                          max_depth: int = 10) -> Optional[List[str]]:
        """Find the chain from subtype to supertype. Returns None if no path."""
        if subtype == supertype:
            return [subtype]
        visited: Set[str] = set()
        queue: List[List[str]] = [[subtype]]
        while queue:
            path = queue.pop(0)
            current = path[-1]
            if current in visited:
                continue
            visited.add(current)
            for (s, sup), val in self._subtype_cache.items():
                if s == current and val:
                    new_path = path + [sup]
                    if sup == supertype:
                        return new_path
                    if len(new_path) <= max_depth:
                        queue.append(new_path)
        return None

    def get_constraint_stats(self) -> Dict[str, int]:
        """Get statistics about cached constraints."""
        return {
            "total_constraints": len(self._constraint_cache),
            "types_with_constraints": sum(
                1 for v in self._constraint_cache.values() if v
            ),
        }

    @property
    def stats(self) -> Dict[str, int]:
        """Get database statistics."""
        return {
            "subtype_relations": len(self._subtype_cache),
            "compatible_relations": len(self._compatible_cache),
            "trait_implementations": sum(
                len(v) for v in self._trait_impls.values()
            ),
            "file_dependencies": len(self._file_dependencies),
            "cached_constraints": len(self._constraint_cache),
            "unique_trait_providers": len(self._trait_providers),
        }
