"""
Backend registry — discovers, registers and resolves native backends.
"""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compiler.native.backend.base import Backend, BackendKind


class BackendRegistry:
    """Singleton-like registry that maps BackendKind to Backend classes."""

    _instance: BackendRegistry | None = None
    __slots__ = ("_entries",)

    def __new__(cls) -> BackendRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_entries"):
            object.__setattr__(self, "_entries", {})

    def register(self, kind: BackendKind, backend_class: type[Backend]) -> None:
        """Register a backend class for the given kind."""
        self._entries[kind] = backend_class

    def get(self, kind: BackendKind) -> Backend:
        """Return an instantiated backend for *kind*.

        Raises ``BackendError`` if the kind is not registered.
        """
        cls = self._entries.get(kind)
        if cls is None:
            from compiler.native.backend.base import BackendError

            raise BackendError(f"no backend registered for {kind.value!r}")
        return cls()

    def list_available(self) -> list[BackendKind]:
        """Return all registered backend kinds."""
        return list(self._entries.keys())

    def detect_best_backend(self) -> BackendKind:
        """Auto-detect the best available backend.

        Priority:
          1. LLVM (if ``llc`` or ``opt`` is on ``PATH``)
          2. Cranelift (if module import succeeds)
          3. Custom x86-64 on x86_64 hosts
          4. Custom ARM64 on ARM64 hosts
        """
        if shutil.which("llc") is not None or shutil.which("opt") is not None:
            return self._try_kind(self._entries, "LLVM")

        try:
            importlib.import_module("cranelift")
            return self._try_kind(self._entries, "CRANELIFT")
        except ImportError:
            pass

        machine = self._host_machine()
        if machine == "AMD64":
            return self._try_kind(self._entries, "CUSTOM_X86_64")
        if machine in ("ARM64", "ARM"):
            return self._try_kind(self._entries, "CUSTOM_ARM64")

        available = self.list_available()
        if available:
            return available[0]

        from compiler.native.backend.base import BackendError

        raise BackendError("no backend registered and no backend could be auto-detected")

    @staticmethod
    def _try_kind(
        entries: dict, name: str
    ) -> BackendKind:
        from compiler.native.backend.base import BackendKind

        kind = BackendKind[name]
        if kind in entries:
            return kind
        available = list(entries.keys())
        if available:
            return available[0]
        from compiler.native.backend.base import BackendError

        raise BackendError(f"backend {name} is the best match but is not registered")

    @staticmethod
    def _host_machine() -> str:
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import platform; print(platform.machine())"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        import platform

        return platform.machine()
