"""
Backend manager — orchestrates compilation from IR to native code.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from compiler.native.backend.registry import BackendRegistry
from compiler.native.link.result import CompileResult, OutputFormat
from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind

if TYPE_CHECKING:
    from compiler.ir.module import IRModule
    from compiler.native.backend.base import BackendKind


class BackendManager:
    """Orchestrates compilation by selecting a backend and driving the pipeline."""

    __slots__ = ("_registry",)

    def __init__(self, registry: BackendRegistry | None = None) -> None:
        self._registry = registry if registry is not None else BackendRegistry()

    def compile(
        self,
        module: IRModule,
        target: TargetDescription,
        backend_kind: BackendKind | None = None,
        output_format: OutputFormat = "object",
    ) -> CompileResult:
        """Compile an IR module to the requested output format.

        If *backend_kind* is ``None`` the best available backend is
        auto-detected via the registry.
        """
        if backend_kind is None:
            backend_kind = self._registry.detect_best_backend()

        backend = self._registry.get(backend_kind)
        target_kind = target.kind

        if output_format == "executable":
            tmp = Path.cwd() / f".i_cache_{module.name or 'out'}"
            tmp.parent.mkdir(parents=True, exist_ok=True)
            out = backend.compile_to_executable(module, target_kind, tmp)
            result = CompileResult(
                success=True,
                output_path=out,
                object_bytes=out.read_bytes() if out.exists() else b"",
            )
            if tmp.exists():
                tmp.unlink(missing_ok=True)
            return result

        if output_format == "object":
            data = backend.compile_to_object(module, target_kind)
            return CompileResult(
                success=True,
                output_path=None,
                object_bytes=data,
            )

        return backend.compile(module)

    def detect_target(self) -> TargetDescription:
        """Detect the host target and return a ``TargetDescription``."""
        machine = platform.machine().lower()
        if machine in ("amd64", "x86_64", "x64"):
            kind = TargetKind.X86_64
        elif machine in ("arm64", "aarch64"):
            kind = TargetKind.ARM64
        elif machine in ("arm", "armv7l"):
            kind = TargetKind.ARM32
        elif machine in ("riscv64",):
            kind = TargetKind.RISCV64
        else:
            kind = TargetKind.X86_64

        bits = 64 if sys.maxsize > 2**32 else 32
        return TargetDescription(
            kind=kind,
            bits=bits,
            triple=f"{kind.value}-unknown-{self._host_os()}",
            features=frozenset(),
        )

    @staticmethod
    def _host_os() -> str:
        sys_name = platform.system().lower()
        if sys_name == "windows":
            return "windows-msvc"
        if sys_name == "darwin":
            return "macosx"
        if sys_name == "linux":
            return "linux-gnu"
        return sys_name
