"""IVM context — shared state for a VM execution session."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vm.vm_config import VMConfig


class VMContext:
    """Shared execution context for a VM instance."""
    __slots__ = (
        "_config", "_globals", "_builtins", "_modules",
        "_string_pool", "_interned_strings", "_modules_loaded",
        "_ffi_registry", "_metadata",
    )

    def __init__(self, config: VMConfig) -> None:
        self._config = config
        self._globals: dict[str, Any] = {}
        self._builtins: dict[str, Any] = {}
        self._modules: dict[str, Any] = {}
        self._modules_loaded: set[str] = set()
        self._string_pool: dict[str, str] = {}
        self._interned_strings: dict[str, int] = {}
        self._ffi_registry: dict[str, Any] = {}
        self._metadata: dict[str, Any] = {}

    @property
    def config(self) -> VMConfig:
        return self._config

    @property
    def globals(self) -> dict[str, Any]:
        return self._globals

    @property
    def builtins(self) -> dict[str, Any]:
        return self._builtins

    @property
    def modules(self) -> dict[str, Any]:
        return self._modules

    def register_builtin(self, name: str, func: Any) -> None:
        self._builtins[name] = func

    def get_builtin(self, name: str) -> Any | None:
        return self._builtins.get(name)

    def has_module(self, name: str) -> bool:
        return name in self._modules_loaded

    def register_module(self, name: str, module: Any) -> None:
        self._modules[name] = module
        self._modules_loaded.add(name)

    def intern_string(self, s: str) -> int:
        if s in self._interned_strings:
            return self._interned_strings[s]
        idx = len(self._string_pool)
        self._string_pool[s] = s
        self._interned_strings[s] = idx
        return idx

    def get_interned(self, idx: int) -> str:
        return self._string_pool.get(idx, "")

    def register_ffi(self, name: str, func: Any) -> None:
        self._ffi_registry[name] = func

    def get_ffi(self, name: str) -> Any | None:
        return self._ffi_registry.get(name)

    def set_metadata(self, key: str, value: Any) -> None:
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self._metadata.get(key, default)
