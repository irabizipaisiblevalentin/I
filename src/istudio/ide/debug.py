"""I STUDIO IDE — debug service.

Source-level debugger on top of the legacy VirtualMachine. The file is compiled
to a pickled Chunk in an isolated child process (so a pathological parse cannot
hang the IDE), then executed in-process on a worker thread by a DebugVM that
pauses at breakpoints and honours step/continue/stop commands.

Limitations (v1): the legacy VM has a flat function model, so step-over is
approximated as "next source line"; variables are the top-level globals plus the
top of the operand stack; interactive ``soma`` reads are not supported in debug.
"""

from __future__ import annotations

import os
import pickle
import tempfile
import threading
from typing import Any

from compiler.codegen import OpCode
from vm.virtual_machine import VirtualMachine

from . import util
from .sse import SSEHub


class DebugVM(VirtualMachine):
    """VirtualMachine subclass that yields to the session before each instruction."""

    def __init__(self, session: DebugSession) -> None:
        super().__init__()
        self._session = session
        self.builtins["andika"] = self._publish_print

    def _publish_print(self, *args: Any) -> None:
        parts = [str(a) for a in args]
        self._session.hub.publish(
            self._session._stream, "output", {"line": " ".join(parts) + "\n"}
        )

    def interpret(self, chunk: Any) -> Any:
        self.chunk = chunk
        self.ip = 0
        self.stack = []
        self._collect_functions(chunk)
        session = self._session

        while True:
            instruction = self._read_instruction()
            if instruction.opcode == OpCode.HALT:
                break
            line = getattr(instruction, "line", 0)
            if not session._before_instruction(self, line):
                break
            self._execute_instruction(instruction)

        return self._pop() if self.stack else None


class DebugSession:
    def __init__(self, hub: SSEHub, file_path: str, project_dir: str | None = None):
        self.hub = hub
        self.file_path = file_path
        self.project_dir = project_dir or os.path.dirname(file_path)
        self.session_id = f"debug-{id(self)}"
        self._stream = f"debug:{self.session_id}"

        self._breakpoints: set[int] = set()
        self._resume = threading.Event()
        self._command: str = "continue"  # continue | step
        self._step_line: int | None = None
        self._last_line: int = 0
        self._abort = False
        self._running = False
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None

    # ── lifecycle ──────────────────────────────────────────────────────

    def start(self) -> None:
        fd, chunk_path = tempfile.mkstemp(prefix="istudio-debug-", suffix=".pkl")
        os.close(fd)
        try:
            result = util.debug_compile_chunk(self.file_path, chunk_path)
            if not result["ok"]:
                self.hub.publish(self._stream, "error", {"message": result["error"]})
                self.hub.publish(self._stream, "ended", {"ok": False})
                return
            with open(chunk_path, "rb") as f:
                chunk = pickle.load(f)
        finally:
            try:
                os.unlink(chunk_path)
            except OSError:
                pass

        self._running = True
        self._resume.set()
        self.hub.publish(self._stream, "started", {"file": self.file_path})
        self._thread = threading.Thread(
            target=self._execute,
            args=(chunk,),
            daemon=True,
            name=self.session_id,
        )
        self._thread.start()

    def _execute(self, chunk: Any) -> None:
        vm = DebugVM(self)
        try:
            result = vm.interpret(chunk)
            self.hub.publish(self._stream, "ended", {"ok": True, "result": str(result) if result is not None else None})
        except Exception as exc:  # noqa: BLE001
            self.hub.publish(self._stream, "error", {"message": f"{type(exc).__name__}: {exc}"})
            self.hub.publish(self._stream, "ended", {"ok": False})
        finally:
            self._running = False

    def stop(self) -> None:
        with self._lock:
            self._abort = True
        self._resume.set()

    # ── breakpoints ────────────────────────────────────────────────────

    def set_breakpoints(self, lines: list[int]) -> None:
        with self._lock:
            self._breakpoints = {int(line) for line in lines}
        self.hub.publish(self._stream, "breakpoints", {"lines": sorted(self._breakpoints)})

    # ── control ────────────────────────────────────────────────────────

    def continue_run(self) -> None:
        with self._lock:
            self._command = "continue"
            self._step_line = None
        self._resume.set()

    def step(self) -> None:
        with self._lock:
            self._command = "step"
        self._resume.set()

    # ── VM hook ────────────────────────────────────────────────────────

    def _before_instruction(self, vm: VirtualMachine, line: int) -> bool:
        if self._abort:
            return False

        paused = False
        with self._lock:
            if self._command == "step":
                if self._step_line is None or line != self._step_line:
                    paused = True
            elif line in self._breakpoints and line != self._last_line:
                paused = True

        self._last_line = line

        if not paused:
            return True

        with self._lock:
            self._command = "continue"
            self._step_line = line
        self._resume.clear()
        self._publish_paused(vm, line)
        self._resume.wait()

        if self._abort:
            return False
        return True

    def _publish_paused(self, vm: VirtualMachine, line: int) -> None:
        globals_snapshot: dict[str, Any] = {}
        for name, value in list(vm.globals.items())[:50]:
            try:
                globals_snapshot[name] = repr(value)
            except Exception:  # noqa: BLE001
                globals_snapshot[name] = "<unprintable>"
        stack_top: list[str] = []
        for value in list(vm.stack)[-12:][::-1]:
            try:
                stack_top.append(repr(value))
            except Exception:  # noqa: BLE001
                stack_top.append("<unprintable>")
        chunk_name = getattr(vm.chunk, "name", "")
        self.hub.publish(
            self._stream,
            "stopped",
            {
                "line": line,
                "function": chunk_name,
                "globals": globals_snapshot,
                "stack_top": stack_top,
                "breakpoints": sorted(self._breakpoints),
            },
        )
