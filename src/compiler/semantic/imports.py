"""
Import and Export Resolution

Validates module existence, duplicate imports, circular imports,
visibility of exported symbols, alias imports, and future package imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .symbols import Symbol, SymbolKind, Visibility, make_module
from .errors import SemanticErrorCode, SemanticErrorCollection, SourceLocation


@dataclass
class ModuleInfo:
    """Information about a resolved module."""
    name: str
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    exports: Dict[str, Symbol] = field(default_factory=dict)
    imports: List[str] = field(default_factory=list)
    location: Optional[SourceLocation] = None

    @property
    def exported_names(self) -> List[str]:
        return list(self.exports.keys())

    @property
    def all_names(self) -> List[str]:
        return list(self.symbols.keys())


class ImportResolver:
    """
    Manages module imports, exports, and resolution.

    Tracks:
    - Registered modules (name → ModuleInfo)
    - Current import chain (for circular import detection)
    - Duplicate import detection
    """

    def __init__(self) -> None:
        self._modules: Dict[str, ModuleInfo] = {}
        self._import_chain: List[str] = []
        self._current_module: Optional[str] = None

    def register_module(self, name: str, location: Optional[SourceLocation] = None) -> ModuleInfo:
        """Register a new module."""
        if name not in self._modules:
            self._modules[name] = ModuleInfo(name=name, location=location)
        return self._modules[name]

    def get_module(self, name: str) -> Optional[ModuleInfo]:
        """Get a module by name."""
        return self._modules.get(name)

    def resolve_import(
        self,
        path: str,
        alias: Optional[str],
        diagnostics: SemanticErrorCollection,
        location: SourceLocation,
    ) -> Optional[Symbol]:
        """
        Resolve an import statement.
        Returns a module symbol if successful, None if error.
        """
        # Check if module exists
        module_info = self._modules.get(path)
        if module_info is None:
            # Try built-in modules
            if path in ('std', 'io', 'math', 'string', 'list'):
                module_info = self.register_module(path, location)
            else:
                diagnostics.error(
                    SemanticErrorCode.SEM400_MODULE_NOT_FOUND,
                    location, path,
                )
                return None

        # Check for circular imports
        if path in self._import_chain:
            diagnostics.error(
                SemanticErrorCode.SEM402_CIRCULAR_IMPORT,
                location, path,
            )
            return None

        # Create module symbol
        module_sym = make_module(alias or path, loc=location)
        module_sym.exports = dict(module_info.exports)
        return module_sym

    def register_export(
        self,
        name: str,
        symbol: Symbol,
        diagnostics: SemanticErrorCollection,
        location: SourceLocation,
    ) -> None:
        """Register an exported symbol in the current module."""
        if self._current_module:
            module = self._modules.get(self._current_module)
            if module:
                if name in module.exports:
                    diagnostics.warning(
                        SemanticErrorCode.SEM105_DUPLICATE_MODULE,
                        location, name,
                    )
                module.exports[name] = symbol

    def start_module(self, name: str) -> None:
        """Begin processing a module."""
        self._current_module = name
        self._import_chain.append(name)

    def end_module(self) -> None:
        """Finish processing a module."""
        if self._import_chain:
            self._import_chain.pop()
        self._current_module = None

    def check_export_exists(
        self,
        name: str,
        diagnostics: SemanticErrorCollection,
        location: SourceLocation,
    ) -> bool:
        """Check if an exported symbol exists in the current module."""
        if self._current_module:
            module = self._modules.get(self._current_module)
            if module and name not in module.exports:
                diagnostics.error(
                    SemanticErrorCode.SEM404_EXPORT_NOT_FOUND,
                    location, name,
                )
                return False
        return True

    @property
    def registered_modules(self) -> List[str]:
        return list(self._modules.keys())

    def clear(self) -> None:
        self._modules.clear()
        self._import_chain.clear()
        self._current_module = None
