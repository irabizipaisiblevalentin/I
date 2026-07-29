"""debug — Debug utilities for the I language.

Provides assertion helpers, variable inspection, and stack trace utilities.
"""

from __future__ import annotations

import inspect
import sys
import traceback
from typing import Any, Dict, List, Optional


def debug_var(name: str, value: Any) -> None:
    """Print variable name and value."""
    print(f"[DEBUG] {name} = {value!r} (type={type(value).__name__})")


def debug_vars(**kwargs: Any) -> None:
    """Print multiple variables."""
    for name, value in kwargs.items():
        debug_var(name, value)


def stack_trace(skip: int = 0) -> List[str]:
    """Get formatted stack trace."""
    frames = traceback.extract_stack()
    result = []
    for frame in frames[:-skip]:
        result.append(f"  {frame.filename}:{frame.lineno} in {frame.name}: {frame.line}")
    return result


def print_stack(skip: int = 1) -> None:
    """Print current call stack."""
    for line in stack_trace(skip):
        print(line)


def caller_info(skip: int = 1) -> Dict[str, Any]:
    """Get information about the caller."""
    frame = inspect.currentframe()
    if frame is None:
        return {}
    for _ in range(skip):
        if frame.f_back:
            frame = frame.f_back
    return {
        "function": frame.f_code.co_name,
        "filename": frame.f_code.co_filename,
        "lineno": frame.f_lineno,
        "locals": dict(frame.f_locals),
    }


def breakpoint_here() -> None:
    """Trigger debugger breakpoint."""
    import pdb
    pdb.set_trace()


def assert_debug(condition: Any, msg: str = "") -> None:
    """Assertion with debug info on failure."""
    if not condition:
        info = caller_info(skip=2)
        loc = f"{info.get('filename', '?')}:{info.get('lineno', '?')}"
        func = info.get('function', '?')
        raise AssertionError(
            f"Assertion failed at {loc} in {func()}: {msg}" if msg
            else f"Assertion failed at {loc} in {func}"
        )


def trace_calls(fn):
    """Decorator that traces function calls."""
    def wrapper(*args, **kwargs):
        args_repr = ", ".join(repr(a) for a in args)
        kwargs_repr = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        all_args = ", ".join(filter(None, [args_repr, kwargs_repr]))
        print(f"[TRACE] {fn.__name__}({all_args})")
        result = fn(*args, **kwargs)
        print(f"[TRACE] {fn.__name__} -> {result!r}")
        return result
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


def memory_dump(obj: Any) -> Dict[str, Any]:
    """Get basic memory info about an object."""
    return {
        "type": type(obj).__name__,
        "size_bytes": sys.getsizeof(obj),
        "repr": repr(obj)[:200],
    }
