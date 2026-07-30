"""
High-level NativeCompiler entry point for the I native compilation pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from compiler.native.backend.manager import BackendManager
from compiler.native.backend.registry import BackendRegistry

if TYPE_CHECKING:
    from compiler.ir.module import IRModule
    from compiler.native.backend.base import BackendKind
    from compiler.native.target.kind import TargetKind


@dataclass
class NativeCompilerResult:
    """Result of a native compilation."""

    success: bool = False
    output_path: Path | None = None
    object_bytes: bytes = b""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class NativeCompiler:
    """High-level API for native code compilation.

    Accepts source text or an already-lowered ``IRModule`` and drives
    the full backend pipeline.
    """

    __slots__ = ("_manager", "_registry", "_verbose")

    def __init__(
        self,
        *,
        verbose: bool = False,
        registry: BackendRegistry | None = None,
    ) -> None:
        self._verbose = verbose
        self._registry = registry if registry is not None else BackendRegistry()
        self._manager = BackendManager(self._registry)

    def compile(
        self,
        source: str | IRModule,
        target: TargetKind,
        backend: BackendKind | None = None,
    ) -> NativeCompilerResult:
        """Compile *source* for *target* using the given *backend*.

        When *source* is a ``str`` it is first lowered to an ``IRModule``
        via the standard front-end pipeline.
        """
        result = NativeCompilerResult()

        try:
            module = self._ensure_ir_module(source)
            target_desc = self._build_target_desc(target)
            compile_result = self._manager.compile(
                module=module,
                target=target_desc,
                backend_kind=backend,
                output_format="executable",
            )
            result.success = compile_result.success
            result.output_path = compile_result.output_path
            result.object_bytes = compile_result.object_bytes

            for e in getattr(compile_result, "errors", []):
                result.errors.append(str(e))
            for w in getattr(compile_result, "warnings", []):
                result.warnings.append(str(w))

        except Exception as exc:
            result.success = False
            result.errors.append(str(exc))

        return result

    def _ensure_ir_module(self, source: str | IRModule) -> IRModule:
        if not isinstance(source, str):
            return source

        from compiler.ir.lower import ASTLowering
        from compiler.lexer.lexer import Lexer
        from compiler.parser.parser import Parser
        from compiler.semantic.analyzer import SemanticAnalyzer

        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        if analyzer.has_errors:
            raise RuntimeError(
                f"semantic analysis failed:\n{analyzer.diagnostics.format_all()}"
            )

        lowerer = ASTLowering()
        module = lowerer.lower(ast)

        from compiler.typesystem.checker import check_types

        diag = check_types(ast)
        if diag.has_errors:
            raise RuntimeError(f"type checking failed:\n{diag.format_all()}")

        return module

    @staticmethod
    def _build_target_desc(target: TargetKind) -> object:
        from compiler.native.target.desc import TargetDescription

        bits = 64
        os_hint = "unknown"
        import platform
        sys_name = platform.system().lower()
        if sys_name == "windows":
            os_hint = "windows-msvc"
        elif sys_name == "darwin":
            os_hint = "macosx"
        elif sys_name == "linux":
            os_hint = "linux-gnu"

        triple = f"{target.value}-unknown-{os_hint}"
        return TargetDescription(
            kind=target,
            bits=bits,
            triple=triple,
            features=frozenset(),
        )
