"""Tests for istudio.ugutunganya — Debugger."""

from __future__ import annotations

from src.istudio.ugutunganya import Debugger
from src.istudio.ibikoreshingiro import BreakpointType, DebuggerState, StackFrame, VariableInfo


def test_debugger_initial_state():
    d = Debugger()
    assert d.state == DebuggerState.STOPPED


def test_debugger_start_stop():
    d = Debugger()
    d.start()
    assert d.state == DebuggerState.RUNNING
    d.stop()
    assert d.state == DebuggerState.STOPPED


def test_debugger_pause_continue():
    d = Debugger()
    d.start()
    d.pause()
    assert d.state == DebuggerState.PAUSED
    d.continue_execution()
    assert d.state == DebuggerState.RUNNING


def test_debugger_step_over():
    d = Debugger()
    d.start()
    d.step_over()
    assert d.state == DebuggerState.STEPPING


def test_debugger_step_into():
    d = Debugger()
    d.start()
    d.step_into()
    assert d.state == DebuggerState.STEPPING


def test_debugger_step_out():
    d = Debugger()
    d.start()
    d.step_out()
    assert d.state == DebuggerState.STEPPING


def test_add_breakpoint():
    d = Debugger()
    bp = d.add_breakpoint("main.i", 10)
    assert bp.file == "main.i"
    assert bp.line == 10
    assert bp.enabled is True


def test_add_conditional_breakpoint():
    d = Debugger()
    bp = d.add_breakpoint("main.i", 20, bp_type=BreakpointType.CONDITIONAL, condition="x > 5")
    assert bp.type == BreakpointType.CONDITIONAL
    assert bp.condition == "x > 5"


def test_add_logpoint():
    d = Debugger()
    bp = d.add_breakpoint("main.i", 30, bp_type=BreakpointType.LOG_POINT, log_message="x={x}")
    assert bp.type == BreakpointType.LOG_POINT
    assert bp.log_message == "x={x}"


def test_remove_breakpoint():
    d = Debugger()
    d.add_breakpoint("main.i", 10)
    assert d.remove_breakpoint("main.i", 10) is True
    assert d.remove_breakpoint("main.i", 10) is False


def test_toggle_breakpoint():
    d = Debugger()
    bp = d.add_breakpoint("main.i", 10)
    assert bp.enabled is True
    d.toggle_breakpoint("main.i", 10)
    assert bp.enabled is False
    d.toggle_breakpoint("main.i", 10)
    assert bp.enabled is True


def test_toggle_creates_breakpoint():
    d = Debugger()
    bp = d.toggle_breakpoint("main.i", 99)
    assert bp is not None
    assert bp.line == 99


def test_get_breakpoints():
    d = Debugger()
    d.add_breakpoint("a.i", 1)
    d.add_breakpoint("a.i", 2)
    d.add_breakpoint("b.i", 3)
    assert len(d.get_breakpoints()) == 3
    assert len(d.get_breakpoints("a.i")) == 2
    assert len(d.get_breakpoints("b.i")) == 1


def test_clear_breakpoints():
    d = Debugger()
    d.add_breakpoint("a.i", 1)
    d.add_breakpoint("b.i", 2)
    d.clear_breakpoints("a.i")
    assert len(d.get_breakpoints("a.i")) == 0
    assert len(d.get_breakpoints()) == 1
    d.clear_breakpoints()
    assert len(d.get_breakpoints()) == 0


def test_stack_frames():
    d = Debugger()
    frames = [
        StackFrame(id=0, name="main", file="main.i", line=10),
        StackFrame(id=1, name="foo", file="main.i", line=20),
    ]
    d.set_stack_frames(frames)
    assert len(d.get_stack_frames()) == 2
    assert d.get_stack_frames()[0].name == "main"


def test_variables():
    d = Debugger()
    d.set_variables("local", [
        VariableInfo(name="x", value="1", type="int"),
        VariableInfo(name="y", value="hello", type="str"),
    ])
    vars_dict = d.get_variables()
    assert "local" in vars_dict
    assert len(vars_dict["local"].children) == 2


def test_evaluate():
    d = Debugger()
    result = d.evaluate("2 + 2")
    assert result == "4"


def test_evaluate_error():
    d = Debugger()
    result = d.evaluate("undefined_symbol")
    assert "error" in result


def test_debugger_events():
    d = Debugger()
    events = []
    d.on("started", lambda e: events.append("started"))
    d.on("stopped", lambda e: events.append("stopped"))
    d.start()
    d.stop()
    assert "started" in events
    assert "stopped" in events
