"""middleware — Middleware pipeline framework.

Provides ordered middleware chaining with context passing,
short-circuit capability, and async middleware support.
"""

from __future__ import annotations

import enum
from typing import Any, Callable, Dict, List, Optional


class MiddlewarePhase(enum.IntEnum):
    PRE = 0
    ROUTE = 1
    CONTROLLER = 2
    POST = 3
    ERROR = 4


class MiddlewareContext:
    """Mutable context passed through the middleware chain."""
    __slots__ = ("data", "_stopped", "_error")

    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        self.data: Dict[str, Any] = data or {}
        self._stopped = False
        self._error: Optional[Exception] = None

    @property
    def stopped(self) -> bool:
        return self._stopped

    @property
    def error(self) -> Optional[Exception]:
        return self._error

    def stop(self) -> None:
        self._stopped = True

    def set_error(self, error: Exception) -> None:
        self._error = error
        self._stopped = True

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value


class MiddlewareEntry:
    """A registered middleware entry."""
    __slots__ = ("handler", "phase", "priority", "name")

    def __init__(self, handler: Callable, phase: MiddlewarePhase = MiddlewarePhase.PRE,
                 priority: int = 0, name: str = "") -> None:
        self.handler = handler
        self.phase = phase
        self.priority = priority
        self.name = name or getattr(handler, "__name__", "anonymous")


class MiddlewarePipeline:
    """Ordered middleware chain that processes contexts through each layer."""

    def __init__(self) -> None:
        self._middlewares: Dict[MiddlewarePhase, List[MiddlewareEntry]] = {}
        self._error_handlers: List[Callable] = []

    def use(self, handler: Callable, phase: MiddlewarePhase = MiddlewarePhase.PRE,
            priority: int = 0, name: str = "") -> None:
        entry = MiddlewareEntry(handler, phase, priority, name)
        entries = self._middlewares.setdefault(phase, [])
        entries.append(entry)
        entries.sort(key=lambda e: e.priority, reverse=True)

    def use_error_handler(self, handler: Callable) -> None:
        self._error_handlers.append(handler)

    def execute(self, context: MiddlewareContext,
                terminal: Optional[Callable] = None) -> MiddlewareContext:
        phases = [
            MiddlewarePhase.PRE,
            MiddlewarePhase.ROUTE,
            MiddlewarePhase.CONTROLLER,
            MiddlewarePhase.POST,
        ]

        for phase in phases:
            entries = self._middlewares.get(phase, [])
            for entry in entries:
                if context.stopped:
                    break
                try:
                    result = entry.handler(context)
                    if result is not None and isinstance(context.data.get("_result"), type(None)):
                        context.set("_result", result)
                except Exception as e:
                    context.set_error(e)
                    self._handle_error(context, e)
                    break

        if not context.stopped and terminal:
            try:
                result = terminal(context)
                context.set("_result", result)
            except Exception as e:
                context.set_error(e)
                self._handle_error(context, e)

        post_entries = self._middlewares.get(MiddlewarePhase.POST, [])
        for entry in post_entries:
            if context.error:
                break
            try:
                entry.handler(context)
            except Exception:
                pass

        return context

    def execute_chain(self, context: MiddlewareContext,
                      handlers: List[Callable],
                      terminal: Optional[Callable] = None) -> MiddlewareContext:
        for handler in handlers:
            if context.stopped:
                break
            try:
                result = handler(context)
                if result is not None:
                    context.set("_result", result)
            except Exception as e:
                context.set_error(e)
                self._handle_error(context, e)
                break

        if not context.stopped and terminal:
            try:
                result = terminal(context)
                context.set("_result", result)
            except Exception as e:
                context.set_error(e)
                self._handle_error(context, e)

        return context

    def _handle_error(self, context: MiddlewareContext, error: Exception) -> None:
        for handler in self._error_handlers:
            try:
                handler(context, error)
            except Exception:
                pass

    def count(self, phase: Optional[MiddlewarePhase] = None) -> int:
        if phase is not None:
            return len(self._middlewares.get(phase, []))
        return sum(len(entries) for entries in self._middlewares.values())

    def clear(self, phase: Optional[MiddlewarePhase] = None) -> None:
        if phase:
            self._middlewares.pop(phase, None)
        else:
            self._middlewares.clear()
            self._error_handlers.clear()
