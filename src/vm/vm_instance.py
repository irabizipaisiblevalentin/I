"""IVM Instance — the main VM entry point."""
from __future__ import annotations

import time
from typing import Any, Callable

from vm.vm_config import VMConfig
from vm.vm_context import VMContext
from vm.vm_executor import VMExecutor, VMRuntimeError
from vm.vm_gc import GarbageCollector
from vm.vm_debug import VMDebugger
from vm.vm_profiler import VMProfiler
from vm.vm_stats import VMStatistics
from vm.vm_loader import VMLoader
from vm.vm_runtime import VMRuntime
from vm.vm_scheduler import VMScheduler
from vm.vm_memory import Stack, CallFrame, Heap, StringPool, ConstantPool


class VMInstance:
    """The I Virtual Machine — complete execution environment.

    Usage:
        vm = VMInstance()
        result = vm.execute(chunk)
        # or
        vm = VMInstance(config=VMConfig(max_stack_depth=2048))
        vm.run_file("program.ch")
    """
    __slots__ = (
        "_config", "_context", "_executor", "_gc",
        "_debugger", "_profiler", "_stats",
        "_loader", "_runtime", "_scheduler",
        "_string_pool", "_constant_pool",
        "_initialized",
    )

    def __init__(self, config: VMConfig | None = None) -> None:
        self._config = config or VMConfig()
        self._context = VMContext(self._config)
        self._executor = VMExecutor(self._config, self._context)
        self._gc = GarbageCollector(
            heap=None,
            threshold=self._config.gc_threshold,
            generational=self._config.gc_generational,
            incremental=self._config.gc_incremental,
            stw_limit_ms=self._config.gc_stw_limit_ms,
        )
        self._debugger = VMDebugger()
        self._profiler = VMProfiler()
        self._stats = VMStatistics()
        self._loader = VMLoader(self._config.enable_bytecode_verification)
        self._runtime = VMRuntime(self._context, self._config)
        self._scheduler = VMScheduler()
        self._string_pool = StringPool()
        self._constant_pool = ConstantPool()
        self._initialized = True

        self._executor.set_gc(self._gc)

        if self._config.enable_profiler:
            self._profiler.start()

        self._setup_hooks()

    def _setup_hooks(self) -> None:
        self._executor.hook("call", self._on_call)
        self._executor.hook("return", self._on_return)
        self._executor.hook("instruction", self._on_instruction)

    def _on_call(self, name: str, bp: int) -> None:
        self._stats.record_call()
        if self._profiler.enabled:
            self._profiler.on_call(name)

    def _on_return(self, name: str) -> None:
        self._stats.record_return()
        if self._profiler.enabled:
            self._profiler.on_return(name)

    def _on_instruction(self, opcode: int, ip: int, chunk_name: str) -> None:
        self._stats.record_instruction(opcode)
        if self._profiler.enabled:
            self._profiler.record_instruction(opcode, chunk_name)
        self._stats.record_stack_depth(self._executor.stack.top)

    @property
    def config(self) -> VMConfig:
        return self._config

    @property
    def context(self) -> VMContext:
        return self._context

    @property
    def executor(self) -> VMExecutor:
        return self._executor

    @property
    def gc(self) -> GarbageCollector:
        return self._gc

    @property
    def debugger(self) -> VMDebugger:
        return self._debugger

    @property
    def profiler(self) -> VMProfiler:
        return self._profiler

    @property
    def stats(self) -> VMStatistics:
        return self._stats

    @property
    def loader(self) -> VMLoader:
        return self._loader

    @property
    def runtime(self) -> VMRuntime:
        return self._runtime

    @property
    def scheduler(self) -> VMScheduler:
        return self._scheduler

    @property
    def string_pool(self) -> StringPool:
        return self._string_pool

    @property
    def constant_pool(self) -> ConstantPool:
        return self._constant_pool

    def execute(self, chunk: Any) -> Any:
        """Execute a bytecode chunk. Returns the result."""
        self._stats.start()
        try:
            self._stats.set_bytecode_size(
                len(chunk.code) * 4 if hasattr(chunk, 'code') else 0
            )
            result = self._executor.run(chunk)
            return result
        except VMRuntimeError:
            raise
        except Exception as e:
            raise VMRuntimeError(str(e)) from e
        finally:
            self._stats.stop()
            self._gc.collect()
            self._stats.set_gc_stats(self._gc.stats.to_dict())

    def run_source(self, source: str) -> Any:
        """Compile source and execute."""
        from compiler.codegen.generator import CodeGenerator
        from compiler.lexer.lexer import Lexer
        from compiler.parser.parser import parse

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        ast, errors = parse(source)
        if errors:
            raise RuntimeError(f"parse errors: {errors}")

        gen = CodeGenerator()
        chunk = gen.generate(ast)
        return self.execute(chunk)

    def run_file(self, path: str) -> Any:
        """Load and execute a bytecode file."""
        chunk = self._loader.load_file(path)
        return self.execute(chunk)

    def register_builtin(self, name: str, func: Callable) -> None:
        self._runtime.register_builtin(name, func)

    def register_module(self, name: str, exports: dict[str, Any]) -> None:
        self._runtime.register_module(name, exports)

    def get_global(self, name: str) -> Any:
        return self._context.globals.get(name)

    def set_global(self, name: str, value: Any) -> None:
        self._context.globals[name] = value

    def get_stats_report(self) -> dict[str, Any]:
        return {
            "vm": self._stats.to_dict(),
            "gc": self._gc.stats.to_dict(),
            "profiler": self._profiler.to_dict() if self._profiler.enabled else None,
            "debugger": {
                "breakpoints": len(self._debugger.get_breakpoints()),
            },
        }

    def format_report(self) -> str:
        lines = [
            "═" * 60,
            "  I Virtual Machine — Execution Report",
            "═" * 60,
            "",
            self._stats.format_summary(),
            "",
            self._gc.format_stats(),
        ]
        if self._profiler.enabled:
            lines.extend(["", self._profiler.format_profile()])
        return "\n".join(lines)

    def reset(self) -> None:
        """Reset the VM state."""
        self._executor.stack.clear()
        self._executor.call_stack.clear()
        self._executor._running = False
        self._context.globals.clear()
        self._stats = VMStatistics()
        self._gc = GarbageCollector(
            threshold=self._config.gc_threshold,
            generational=self._config.gc_generational,
        )
        self._executor.set_gc(self._gc)
