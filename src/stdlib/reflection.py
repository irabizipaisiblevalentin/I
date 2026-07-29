"""reflection — Runtime reflection for the I language.

Provides type inspection, function introspection, and dynamic dispatch.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Dict, List, Optional, Type


def type_name(obj: Any) -> str:
    """Get type name of object."""
    return type(obj).__name__


def type_of(obj: Any) -> Type:
    """Get type of object."""
    return type(obj)


def is_type(obj: Any, expected: Type) -> bool:
    """Check if object is instance of type."""
    return isinstance(obj, expected)


def has_attr(obj: Any, name: str) -> bool:
    return hasattr(obj, name)


def get_attr(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default)


def set_attr(obj: Any, name: str, value: Any) -> None:
    setattr(obj, name, value)


def call_method(obj: Any, method_name: str, *args: Any, **kwargs: Any) -> Any:
    return getattr(obj, method_name)(*args, **kwargs)


def methods(obj: Any) -> List[str]:
    """List public methods of an object."""
    return [m for m in dir(obj) if not m.startswith("_") and callable(getattr(obj, m, None))]


def properties(obj: Any) -> Dict[str, Any]:
    """List properties and their values."""
    result: Dict[str, Any] = {}
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            val = getattr(obj, name)
            if not callable(val):
                result[name] = val
        except Exception:
            pass
    return result


def inspect_function(fn: Callable) -> Dict[str, Any]:
    """Inspect a function's signature."""
    sig = inspect.signature(fn)
    return {
        "name": getattr(fn, "__name__", str(fn)),
        "doc": getattr(fn, "__doc__", None),
        "parameters": list(sig.parameters.keys()),
        "annotations": {
            k: str(v.annotation) for k, v in sig.parameters.items()
            if v.annotation != inspect.Parameter.empty
        },
        "return_type": str(sig.return_annotation) if sig.return_annotation != inspect.Parameter.empty else None,
    }


def is_callable(obj: Any) -> bool:
    return callable(obj)


def is_function(obj: Any) -> bool:
    return inspect.isfunction(obj) or inspect.ismethod(obj)


def is_class(obj: Any) -> bool:
    return inspect.isclass(obj)


def is_module(obj: Any) -> bool:
    return inspect.ismodule(obj)


def subclasses(cls: Type) -> List[Type]:
    """Get all subclasses of a class."""
    return cls.__subclasses__()


def superclass(cls: Type) -> Optional[Type]:
    """Get the first parent class."""
    bases = cls.__bases__
    return bases[0] if bases else None
