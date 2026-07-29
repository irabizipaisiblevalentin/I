"""
Trait / Interface Resolver for the I Programming Language

Validates trait and interface implementations, checks method
requirements, default implementations, and structural conformance.

Supports:
- Trait definitions and implementation checking
- Method requirement validation
- Default implementation verification
- Trait bound checking for generics
- Future extension traits
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .types import (
    Type, TypeKind, TypeVariable, FunctionType,
    TYPE_NONE, TYPE_ANY, TYPE_UNKNOWN,
)
from .registry import TypeRegistry, TypeDefinition, MethodSignature, TraitRequirement
from .diagnostics import TypeDiagnostics, TypeErrorCode, TypeLocation


# ══════════════════════════════════════════════════════════════════
# Trait / Interface Definition
# ══════════════════════════════════════════════════════════════════


@dataclass
class TraitDefinition:
    """Complete definition of a trait."""

    name: str
    methods: Dict[str, MethodSignature] = field(default_factory=dict)
    required_methods: Dict[str, MethodSignature] = field(default_factory=dict)
    default_methods: Dict[str, MethodSignature] = field(default_factory=dict)
    required_properties: Dict[str, Type] = field(default_factory=dict)
    super_traits: List[str] = field(default_factory=list)
    generic_params: List[TypeVariable] = field(default_factory=list)
    is_sealed: bool = False
    declaration_file: str = ""
    declaration_line: int = 0


@dataclass
class InterfaceDefinition:
    """Complete definition of an interface."""

    name: str
    methods: Dict[str, MethodSignature] = field(default_factory=dict)
    required_methods: Dict[str, MethodSignature] = field(default_factory=dict)
    properties: Dict[str, Type] = field(default_factory=dict)
    super_interfaces: List[str] = field(default_factory=list)
    declaration_file: str = ""
    declaration_line: int = 0


# ══════════════════════════════════════════════════════════════════
# Implementation Record
# ══════════════════════════════════════════════════════════════════


@dataclass
class ImplementationCheck:
    """Result of checking a trait/interface implementation."""

    type_name: str
    trait_name: str
    is_satisfied: bool
    missing_methods: List[str] = field(default_factory=list)
    mismatched_signatures: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


# ══════════════════════════════════════════════════════════════════
# Trait / Interface Resolver
# ══════════════════════════════════════════════════════════════════


class TraitResolver:
    """
    Validates trait and interface implementations.

    Checks that all required methods are implemented, signatures match,
    and all trait constraints are satisfied.
    """

    def __init__(
        self,
        registry: TypeRegistry,
        diagnostics: TypeDiagnostics,
    ) -> None:
        self.registry = registry
        self.diagnostics = diagnostics
        self._trait_defs: Dict[str, TraitDefinition] = {}
        self._interface_defs: Dict[str, InterfaceDefinition] = {}
        self._impl_cache: Dict[str, List[ImplementationCheck]] = {}

    # ── Registration ──────────────────────────────────────────────

    def register_trait(self, defn: TraitDefinition) -> None:
        """Register a trait definition."""
        self._trait_defs[defn.name] = defn

    def register_interface(self, defn: InterfaceDefinition) -> None:
        """Register an interface definition."""
        self._interface_defs[defn.name] = defn

    def get_trait(self, name: str) -> Optional[TraitDefinition]:
        return self._trait_defs.get(name)

    def get_interface(self, name: str) -> Optional[InterfaceDefinition]:
        return self._interface_defs.get(name)

    # ── Trait Implementation Checking ─────────────────────────────

    def check_trait_implementation(
        self,
        type_name: str,
        trait_name: str,
        location: TypeLocation,
    ) -> ImplementationCheck:
        """
        Check that a type fully implements a trait.

        Returns an ImplementationCheck with details about any violations.
        """
        trait_def = self._trait_defs.get(trait_name)
        if trait_def is None:
            self.diagnostics.error(
                TypeErrorCode.TYP256_UNDEFINED_TRAIT,
                location,
                trait_name,
            )
            return ImplementationCheck(
                type_name=type_name,
                trait_name=trait_name,
                is_satisfied=False,
                errors=[f"Trait '{trait_name}' not found"],
            )

        check = ImplementationCheck(
            type_name=type_name,
            trait_name=trait_name,
            is_satisfied=True,
        )

        type_methods = self.registry.get_methods(type_name)

        # Check required methods
        for method_name, required_sig in trait_def.required_methods.items():
            if method_name not in type_methods:
                check.missing_methods.append(method_name)
                check.is_satisfied = False
                self.diagnostics.error(
                    TypeErrorCode.TYP350_MISSING_TRAIT_METHOD,
                    location,
                    type_name, method_name, trait_name,
                    related_symbols=[type_name, trait_name],
                )
            else:
                actual_sig = type_methods[method_name]
                if not self._signatures_match(required_sig, actual_sig):
                    msg = f"Method '{method_name}' signature mismatch"
                    check.mismatched_signatures.append(msg)
                    check.is_satisfied = False
                    self.diagnostics.error(
                        TypeErrorCode.TYP351_TRAIT_METHOD_SIGNATURE_MISMATCH,
                        location,
                        method_name, trait_name,
                        related_symbols=[type_name, trait_name],
                    )

        # Check super traits
        for super_trait in trait_def.super_traits:
            super_check = self.check_trait_implementation(
                type_name, super_trait, location,
            )
            if not super_check.is_satisfied:
                check.is_satisfied = False
                check.errors.extend(super_check.errors)

        # Cache the result
        if type_name not in self._impl_cache:
            self._impl_cache[type_name] = []
        self._impl_cache[type_name].append(check)

        return check

    def _signatures_match(
        self,
        required: MethodSignature,
        actual: MethodSignature,
    ) -> bool:
        """Check if two method signatures are compatible."""
        if len(required.param_types) != len(actual.param_types):
            return False

        # Skip first param if it's 'self'
        start = 0
        if (required.param_names and required.param_names[0] == "self") or \
           (actual.param_names and actual.param_names[0] == "self"):
            start = 1

        for req_pt, act_pt in zip(required.param_types[start:], actual.param_types[start:]):
            if req_pt.kind != act_pt.kind:
                if not (req_pt.kind == TypeKind.ANY or act_pt.kind == TypeKind.ANY):
                    return False

        if required.return_type.kind != actual.return_type.kind:
            if not (required.return_type.kind == TypeKind.ANY or
                    actual.return_type.kind == TypeKind.ANY):
                return False

        return True

    # ── Interface Implementation Checking ─────────────────────────

    def check_interface_implementation(
        self,
        type_name: str,
        interface_name: str,
        location: TypeLocation,
    ) -> ImplementationCheck:
        """
        Check that a type fully implements an interface.
        """
        iface_def = self._interface_defs.get(interface_name)
        if iface_def is None:
            self.diagnostics.error(
                TypeErrorCode.TYP256_UNDEFINED_TRAIT,
                location,
                interface_name,
            )
            return ImplementationCheck(
                type_name=type_name,
                trait_name=interface_name,
                is_satisfied=False,
                errors=[f"Interface '{interface_name}' not found"],
            )

        check = ImplementationCheck(
            type_name=type_name,
            trait_name=interface_name,
            is_satisfied=True,
        )

        type_methods = self.registry.get_methods(type_name)

        for method_name, required_sig in iface_def.required_methods.items():
            if method_name not in type_methods:
                check.missing_methods.append(method_name)
                check.is_satisfied = False
                self.diagnostics.error(
                    TypeErrorCode.TYP352_NOT_IMPLEMENTED,
                    location,
                    type_name, interface_name,
                )
            else:
                actual_sig = type_methods[method_name]
                if not self._signatures_match(required_sig, actual_sig):
                    check.mismatched_signatures.append(
                        f"Method '{method_name}' signature mismatch"
                    )
                    check.is_satisfied = False

        return check

    # ── Trait Bound Checking ──────────────────────────────────────

    def check_trait_bound(
        self,
        type_name: str,
        trait_name: str,
        location: TypeLocation,
    ) -> bool:
        """
        Check if a type satisfies a trait bound.
        Used for generic constraints.
        """
        # Direct check
        check = self.check_trait_implementation(type_name, trait_name, location)
        if check.is_satisfied:
            return True

        # Check parent types
        parent = self.registry.get_parent(type_name)
        while parent:
            check = self.check_trait_implementation(parent, trait_name, location)
            if check.is_satisfied:
                return True
            parent = self.registry.get_parent(parent)

        return False

    def check_all_implementations(self, location: TypeLocation) -> bool:
        """
        Check all registered trait/interface implementations.
        Returns True if all are satisfied.
        """
        all_satisfied = True
        for type_name, checks in self._impl_cache.items():
            for check in checks:
                if not check.is_satisfied:
                    all_satisfied = False
        return all_satisfied

    # ── Query ─────────────────────────────────────────────────────

    def get_implementors(self, trait_name: str) -> List[str]:
        """Get all types that implement a given trait."""
        result = []
        for type_name, checks in self._impl_cache.items():
            for check in checks:
                if check.trait_name == trait_name and check.is_satisfied:
                    result.append(type_name)
                    break
        return result

    def get_required_methods(self, trait_name: str) -> Dict[str, MethodSignature]:
        """Get all required methods for a trait."""
        defn = self._trait_defs.get(trait_name)
        if defn:
            return dict(defn.required_methods)
        return {}

    def clear(self) -> None:
        """Reset all state."""
        self._trait_defs.clear()
        self._interface_defs.clear()
        self._impl_cache.clear()

    def get_all_trait_names(self) -> List[str]:
        """Get all registered trait names."""
        return list(self._trait_defs.keys())

    def get_all_interface_names(self) -> List[str]:
        """Get all registered interface names."""
        return list(self._interface_defs.keys())

    def is_trait_sealed(self, trait_name: str) -> bool:
        """Check if a trait is sealed (cannot be implemented outside its module)."""
        defn = self._trait_defs.get(trait_name)
        if defn:
            return defn.is_sealed
        return False

    def get_super_traits(self, trait_name: str) -> List[str]:
        """Get all super traits (transitive closure)."""
        result: List[str] = []
        visited: Set[str] = set()
        self._collect_super_traits(trait_name, result, visited)
        return result

    def _collect_super_traits(
        self, trait_name: str, result: List[str], visited: Set[str],
    ) -> None:
        """Recursively collect super traits."""
        if trait_name in visited:
            return
        visited.add(trait_name)
        defn = self._trait_defs.get(trait_name)
        if defn:
            for super_trait in defn.super_traits:
                if super_trait not in visited:
                    result.append(super_trait)
                    self._collect_super_traits(super_trait, result, visited)

    def get_trait_summary(self, trait_name: str) -> Dict[str, Any]:
        """Get a summary of a trait definition."""
        defn = self._trait_defs.get(trait_name)
        if defn is None:
            return {}
        return {
            "name": defn.name,
            "required_methods": list(defn.required_methods.keys()),
            "default_methods": list(defn.default_methods.keys()),
            "super_traits": list(defn.super_traits),
            "generic_params": [p.name for p in defn.generic_params],
            "is_sealed": defn.is_sealed,
            "implementors": self.get_implementors(trait_name),
        }

    def get_interface_summary(self, interface_name: str) -> Dict[str, Any]:
        """Get a summary of an interface definition."""
        defn = self._interface_defs.get(interface_name)
        if defn is None:
            return {}
        return {
            "name": defn.name,
            "required_methods": list(defn.required_methods.keys()),
            "super_interfaces": list(defn.super_interfaces),
        }
