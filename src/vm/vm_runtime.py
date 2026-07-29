"""IVM Runtime — exception handling, module loading, builtins."""
from __future__ import annotations

import math
import time
import random
from typing import Any, Callable

from vm.vm_config import VMConfig
from vm.vm_context import VMContext
from vm.vm_objects import (
    VMClosure, VMException, VMIterator, VMList, VMMap,
    VMSet, VMString, VMStruct, VMTuple,
)


def _builtin_andika(*args: Any) -> None:
    """Print function (Kinyarwanda: andika = write)."""
    print(*args)


def _builtin_ishobora(*args: Any) -> int:
    """Length function."""
    if args:
        return len(args[0])
    return 0


def _builtin_tangura(*args: Any) -> int:
    """Type-of function."""
    if not args:
        return 0
    val = args[0]
    if val is None:
        return 0
    if isinstance(val, bool):
        return 1
    if isinstance(val, int):
        return 2
    if isinstance(val, float):
        return 3
    if isinstance(val, str):
        return 4
    if isinstance(val, VMList):
        return 5
    if isinstance(val, VMMap):
        return 6
    if isinstance(val, VMTuple):
        return 7
    if isinstance(val, VMStruct):
        return 8
    if isinstance(val, VMClosure):
        return 9
    return -1


def _builtin_int(*args: Any) -> int:
    """Convert to integer."""
    if not args:
        return 0
    val = args[0]
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        return int(val)
    if isinstance(val, bool):
        return int(val)
    return 0


def _builtin_float(*args: Any) -> float:
    """Convert to float."""
    if not args:
        return 0.0
    val = args[0]
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        return float(val)
    return 0.0


def _builtin_str(*args: Any) -> str:
    """Convert to string."""
    if not args:
        return ""
    return str(args[0])


def _builtin_bool(*args: Any) -> bool:
    """Convert to boolean."""
    if not args:
        return False
    return bool(args[0])


def _builtin_abs(*args: Any) -> Any:
    """Absolute value."""
    if not args:
        raise VMException("abs() takes exactly 1 argument")
    return abs(args[0])


def _builtin_min(*args: Any) -> Any:
    """Minimum value."""
    if not args:
        raise VMException("min() takes at least 1 argument")
    if len(args) == 1 and isinstance(args[0], (VMList, list)):
        return min(args[0].elements if isinstance(args[0], VMList) else args[0])
    return min(args)


def _builtin_max(*args: Any) -> Any:
    """Maximum value."""
    if not args:
        raise VMException("max() takes at least 1 argument")
    if len(args) == 1 and isinstance(args[0], (VMList, list)):
        return max(args[0].elements if isinstance(args[0], VMList) else args[0])
    return max(args)


def _builtin_soma(*args: Any) -> Any:
    """Sum function."""
    if not args:
        return 0
    if len(args) == 1 and isinstance(args[0], (VMList, list)):
        items = args[0].elements if isinstance(args[0], VMList) else args[0]
        return sum(items)
    return sum(args)


def _builtin_uburyo(*args: Any) -> str:
    """String representation."""
    if not args:
        return "None"
    return repr(args[0])


def _builtin_igenzura(*args: Any) -> bool:
    """Range check."""
    if len(args) < 2:
        return False
    val = args[0]
    low, high = args[0], args[1] if len(args) > 1 else args[0]
    if len(args) == 2:
        low, high = args[0], args[1]
    return low <= val <= high


def _builtin_igihe(*args: Any) -> float:
    """Current time."""
    return time.time()


def _builtin_izuburamwaka(*args: Any) -> int:
    """Random integer."""
    if len(args) >= 2:
        return random.randint(args[0], args[1])
    return random.randint(0, 100)


def _builtin_kubura(*args: Any) -> Any:
    """Raise an exception."""
    msg = args[0] if args else "error"
    raise VMException(str(msg))


def _builtin_gukora(*args: Any) -> Any:
    """Assert function."""
    if not args or not args[0]:
        msg = args[1] if len(args) > 1 else "assertion failed"
        raise VMException(str(msg))
    return None


def _builtin_math_abs(*args: Any) -> float:
    return abs(args[0]) if args else 0.0


def _builtin_math_sqrt(*args: Any) -> float:
    return math.sqrt(args[0]) if args else 0.0


def _builtin_math_sin(*args: Any) -> float:
    return math.sin(args[0]) if args else 0.0


def _builtin_math_cos(*args: Any) -> float:
    return math.cos(args[0]) if args else 0.0


def _builtin_math_tan(*args: Any) -> float:
    return math.tan(args[0]) if args else 0.0


def _builtin_math_log(*args: Any) -> float:
    return math.log(args[0]) if args else 0.0


def _builtin_math_exp(*args: Any) -> float:
    return math.exp(args[0]) if args else 0.0


def _builtin_math_pow(*args: Any) -> float:
    if len(args) >= 2:
        return math.pow(args[0], args[1])
    return 0.0


class VMRuntime:
    """Runtime services — builtins, modules, exception handling."""

    __slots__ = ("_context", "_config", "_builtins", "_modules")

    def __init__(self, context: VMContext, config: VMConfig) -> None:
        self._context = context
        self._config = config
        self._builtins: dict[str, Callable] = {}
        self._modules: dict[str, dict[str, Any]] = {}
        self._register_default_builtins()

    @property
    def builtins(self) -> dict[str, Callable]:
        return self._builtins

    @property
    def modules(self) -> dict[str, dict[str, Any]]:
        return self._modules

    def _register_default_builtins(self) -> None:
        builtins = {
            "andika": _builtin_andika,
            "ishobora": _builtin_ishobora,
            "tangura": _builtin_tangura,
            "int": _builtin_int,
            "float": _builtin_float,
            "str": _builtin_str,
            "bool": _builtin_bool,
            "abs": _builtin_abs,
            "min": _builtin_min,
            "max": _builtin_max,
            "soma": _builtin_soma,
            "uburyo": _builtin_uburyo,
            "igenzura": _builtin_igenzura,
            "igihe": _builtin_igihe,
            "izuburamwaka": _builtin_izuburamwaka,
            "kubura": _builtin_kubura,
            "gukora": _builtin_gukora,
        }

        math_builtins = {
            "math_abs": _builtin_math_abs,
            "math_sqrt": _builtin_math_sqrt,
            "math_sin": _builtin_math_sin,
            "math_cos": _builtin_math_cos,
            "math_tan": _builtin_math_tan,
            "math_log": _builtin_math_log,
            "math_exp": _builtin_math_exp,
            "math_pow": _builtin_math_pow,
        }

        all_builtins = {**builtins, **math_builtins}
        for name, func in all_builtins.items():
            self._builtins[name] = func
            self._context.register_builtin(name, func)

    def register_builtin(self, name: str, func: Callable) -> None:
        self._builtins[name] = func
        self._context.register_builtin(name, func)

    def register_module(self, name: str, exports: dict[str, Any]) -> None:
        self._modules[name] = exports
        self._context.register_module(name, exports)

    def get_module(self, name: str) -> dict[str, Any] | None:
        return self._modules.get(name)

    def has_module(self, name: str) -> bool:
        return name in self._modules

    def create_exception(self, message: str, type_name: str = "RuntimeError") -> VMException:
        return VMException(message, type_name)

    def get_traceback(self, call_stack: list[Any]) -> str:
        lines = ["Traceback (most recent call last):"]
        for frame in reversed(call_stack):
            lines.append(f'  File "{frame.function_name}", line {frame.line}')
        return "\n".join(lines)

    def format_exception(self, exc: VMException) -> str:
        lines = [f"{exc.type_name}: {exc.message}"]
        for frame in exc.stack_trace:
            lines.append(f'  File "{frame.get("function", "<unknown>")}", line {frame.get("line", 0)}')
        return "\n".join(lines)
