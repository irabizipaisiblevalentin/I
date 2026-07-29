"""IVM Debug Interface — breakpoints, stepping, variable inspection."""
from __future__ import annotations

from typing import Any, Callable


class Breakpoint:
    """A breakpoint in bytecode."""
    __slots__ = ("chunk_name", "line", "enabled", "hit_count", "condition")

    def __init__(self, chunk_name: str, line: int, condition: str | None = None) -> None:
        self.chunk_name = chunk_name
        self.line = line
        self.enabled = True
        self.hit_count = 0
        self.condition = condition


class StepMode:
    NONE = 0
    INTO = 1
    OVER = 2
    OUT = 3


class VMDebugger:
    """Debug interface for the IVM."""
    __slots__ = (
        "_breakpoints", "_step_mode", "_step_depth",
        "_paused", "_pause_reason", "_on_pause", "_on_resume",
        "_watch_expressions", "_inspect_requests",
    )

    def __init__(self) -> None:
        self._breakpoints: list[Breakpoint] = []
        self._step_mode: int = StepMode.NONE
        self._step_depth: int = 0
        self._paused: bool = False
        self._pause_reason: str = ""
        self._on_pause: list[Callable] = []
        self._on_resume: list[Callable] = []
        self._watch_expressions: dict[str, Any] = {}
        self._inspect_requests: list[Callable] = []

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def step_mode(self) -> int:
        return self._step_mode

    def add_breakpoint(self, chunk_name: str, line: int, condition: str | None = None) -> Breakpoint:
        bp = Breakpoint(chunk_name=chunk_name, line=line, condition=condition)
        self._breakpoints.append(bp)
        return bp

    def remove_breakpoint(self, chunk_name: str, line: int) -> bool:
        before = len(self._breakpoints)
        self._breakpoints = [
            bp for bp in self._breakpoints
            if not (bp.chunk_name == chunk_name and bp.line == line)
        ]
        return len(self._breakpoints) < before

    def clear_breakpoints(self) -> None:
        self._breakpoints.clear()

    def get_breakpoints(self) -> list[Breakpoint]:
        return list(self._breakpoints)

    def hit_breakpoint(self, chunk_name: str, line: int) -> bool:
        for bp in self._breakpoints:
            if bp.chunk_name == chunk_name and bp.line == line and bp.enabled:
                bp.hit_count += 1
                return True
        return False

    def step_into(self) -> None:
        self._step_mode = StepMode.INTO
        self._step_depth = 0
        self._paused = False

    def step_over(self) -> None:
        self._step_mode = StepMode.OVER
        self._step_depth = 0
        self._paused = False

    def step_out(self) -> None:
        self._step_mode = StepMode.OUT
        self._step_depth = 0
        self._paused = False

    def continue_execution(self) -> None:
        self._step_mode = StepMode.NONE
        self._paused = False
        self._fire("resume")

    def should_break(self, chunk_name: str, line: int, call_depth: int) -> bool:
        if self._step_mode == StepMode.INTO:
            return True
        if self._step_mode == StepMode.OVER:
            if call_depth <= self._step_depth:
                return True
        if self._step_mode == StepMode.OUT:
            if call_depth < self._step_depth:
                return True
        return self.hit_breakpoint(chunk_name, line)

    def on_call(self) -> None:
        if self._step_mode in (StepMode.INTO, StepMode.OVER):
            self._step_depth += 1

    def on_return(self) -> None:
        if self._step_mode in (StepMode.INTO, StepMode.OVER, StepMode.OUT):
            self._step_depth = max(0, self._step_depth - 1)

    def pause(self, reason: str = "") -> None:
        self._paused = True
        self._pause_reason = reason
        self._fire("pause", reason)

    def resume(self) -> None:
        self._paused = False
        self._fire("resume")

    def add_watch(self, name: str, value: Any) -> None:
        self._watch_expressions[name] = value

    def remove_watch(self, name: str) -> None:
        self._watch_expressions.pop(name, None)

    def get_watches(self) -> dict[str, Any]:
        return dict(self._watch_expressions)

    def _fire(self, event: str, *args: Any) -> None:
        if event == "pause":
            for cb in self._on_pause:
                cb(*args)
        elif event == "resume":
            for cb in self._on_resume:
                cb(*args)

    def on_pause(self, callback: Callable) -> None:
        self._on_pause.append(callback)

    def on_resume(self, callback: Callable) -> None:
        self._on_resume.append(callback)

    def get_stack_trace(self, call_stack: list[Any]) -> list[dict[str, Any]]:
        trace = []
        for frame in reversed(call_stack):
            trace.append({
                "function": frame.function_name,
                "line": frame.line,
                "ip": frame.ip,
            })
        return trace

    def inspect_variable(self, name: str, value: Any) -> dict[str, Any]:
        result = {
            "name": name,
            "type": type(value).__name__,
            "repr": repr(value),
        }
        if isinstance(value, (int, float, str, bool, type(None))):
            result["value"] = value
        return result
