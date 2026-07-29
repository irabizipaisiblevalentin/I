"""I STUDIO — Debugging Platform (Ugutunganya)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    Breakpoint,
    BreakpointType,
    DebuggerError,
    DebuggerState,
    StackFrame,
    VariableInfo,
)


class Debugger:
    def __init__(self):
        self._state = DebuggerState.STOPPED
        self._breakpoints: Dict[str, List[Breakpoint]] = {}
        self._stack_frames: List[StackFrame] = []
        self._variables: Dict[str, VariableInfo] = {}
        self._listeners: Dict[str, List[callable]] = {}

    @property
    def state(self) -> DebuggerState:
        return self._state

    def start(self) -> None:
        self._state = DebuggerState.RUNNING
        self._stack_frames = []
        self._variables = {}
        self._emit("started")

    def stop(self) -> None:
        self._state = DebuggerState.STOPPED
        self._emit("stopped")

    def pause(self) -> None:
        self._state = DebuggerState.PAUSED
        self._emit("paused")

    def continue_execution(self) -> None:
        self._state = DebuggerState.RUNNING
        self._emit("continued")

    def step_over(self) -> None:
        self._state = DebuggerState.STEPPING
        self._emit("step_over")

    def step_into(self) -> None:
        self._state = DebuggerState.STEPPING
        self._emit("step_into")

    def step_out(self) -> None:
        self._state = DebuggerState.STEPPING
        self._emit("step_out")

    def add_breakpoint(self, file_path: str, line: int, bp_type: BreakpointType = BreakpointType.LINE,
                       condition: str = "", log_message: str = "") -> Breakpoint:
        bp = Breakpoint(
            file=file_path,
            line=line,
            type=bp_type,
            condition=condition,
            log_message=log_message,
        )
        self._breakpoints.setdefault(file_path, []).append(bp)
        self._emit("breakpoint.added", {"breakpoint": bp})
        return bp

    def remove_breakpoint(self, file_path: str, line: int) -> bool:
        bps = self._breakpoints.get(file_path, [])
        for bp in bps:
            if bp.line == line:
                bps.remove(bp)
                self._emit("breakpoint.removed", {"breakpoint": bp})
                return True
        return False

    def toggle_breakpoint(self, file_path: str, line: int) -> Optional[Breakpoint]:
        bps = self._breakpoints.get(file_path, [])
        for bp in bps:
            if bp.line == line:
                if bp.enabled:
                    bp.enabled = False
                    self._emit("breakpoint.disabled", {"breakpoint": bp})
                else:
                    bp.enabled = True
                    self._emit("breakpoint.enabled", {"breakpoint": bp})
                return bp
        return self.add_breakpoint(file_path, line)

    def get_breakpoints(self, file_path: Optional[str] = None) -> List[Breakpoint]:
        if file_path:
            return self._breakpoints.get(file_path, [])
        result: List[Breakpoint] = []
        for bps in self._breakpoints.values():
            result.extend(bps)
        return result

    def clear_breakpoints(self, file_path: Optional[str] = None) -> None:
        if file_path:
            self._breakpoints.pop(file_path, None)
        else:
            self._breakpoints.clear()
        self._emit("breakpoints.cleared")

    def set_stack_frames(self, frames: List[StackFrame]) -> None:
        self._stack_frames = frames
        self._emit("stack.updated", {"frames": frames})

    def get_stack_frames(self) -> List[StackFrame]:
        return list(self._stack_frames)

    def set_variables(self, scope: str, variables: List[VariableInfo]) -> None:
        self._variables[scope] = VariableInfo(
            name=scope,
            value="",
            type="scope",
            children=variables,
        )
        self._emit("variables.updated", {"scope": scope, "variables": variables})

    def get_variables(self, scope: Optional[str] = None) -> Dict[str, VariableInfo]:
        if scope:
            return {scope: self._variables.get(scope)} if scope in self._variables else {}
        return dict(self._variables)

    def evaluate(self, expression: str) -> str:
        self._emit("evaluate", {"expression": expression})
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"<error: {e}>"

    def on(self, event: str, handler: callable) -> None:
        self._listeners.setdefault(event, []).append(handler)

    def _emit(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        for handler in self._listeners.get(event, []):
            try:
                handler(data or {})
            except Exception:
                pass
