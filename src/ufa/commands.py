"""commands — Command/Message bus for request handling.

Supports command dispatch, query dispatch, pipeline behaviors,
validation, and result streaming.
"""

from __future__ import annotations

import enum
import threading
import time
from typing import Any, Callable, Dict, List, Optional


class MessageType(enum.IntEnum):
    COMMAND = 0
    QUERY = 1
    EVENT = 2


class Message:
    """A message dispatched through the bus."""
    __slots__ = ("type", "payload", "id", "timestamp", "metadata")

    _counter = 0

    def __init__(self, msg_type: MessageType, payload: Any = None,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        Message._counter += 1
        self.type = msg_type
        self.payload = payload
        self.id = Message._counter
        self.timestamp = time.time()
        self.metadata = metadata or {}


class Command(Message):
    def __init__(self, payload: Any = None,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(MessageType.COMMAND, payload, metadata)


class Query(Message):
    def __init__(self, payload: Any = None,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(MessageType.QUERY, payload, metadata)


class CommandResult:
    """Result of a command execution."""
    __slots__ = ("success", "data", "errors", "elapsed_ms")

    def __init__(self, success: bool = True, data: Any = None,
                 errors: Optional[List[str]] = None,
                 elapsed_ms: float = 0.0) -> None:
        self.success = success
        self.data = data
        self.errors = errors or []
        self.elapsed_ms = elapsed_ms

    @property
    def error(self) -> Optional[str]:
        return self.errors[0] if self.errors else None


class HandlerRegistration:
    """A registered command/query handler."""
    __slots__ = ("message_type", "handler", "message_class", "name")

    def __init__(self, message_type: MessageType, handler: Callable,
                 message_class: Optional[type] = None, name: str = "") -> None:
        self.message_type = message_type
        self.handler = handler
        self.message_class = message_class
        self.name = name or getattr(handler, "__name__", "handler")


class PipelineBehavior:
    """A behavior that wraps all command/query handlers."""
    __slots__ = ("handler", "order")

    def __init__(self, handler: Callable, order: int = 0) -> None:
        self.handler = handler
        self.order = order


class MessageBus:
    """Command/query message bus with pipeline behaviors."""

    def __init__(self) -> None:
        self._handlers: Dict[str, HandlerRegistration] = {}
        self._behaviors: List[PipelineBehavior] = []
        self._lock = threading.Lock()
        self._dispatch_count = 0
        self._error_count = 0

    def register_command(self, message_class: type, handler: Callable,
                         name: str = "") -> None:
        key = f"command:{message_class.__name__}"
        reg = HandlerRegistration(MessageType.COMMAND, handler, message_class, name)
        with self._lock:
            self._handlers[key] = reg

    def register_query(self, message_class: type, handler: Callable,
                       name: str = "") -> None:
        key = f"query:{message_class.__name__}"
        reg = HandlerRegistration(MessageType.QUERY, handler, message_class, name)
        with self._lock:
            self._handlers[key] = reg

    def register_behavior(self, handler: Callable, order: int = 0) -> None:
        behavior = PipelineBehavior(handler, order)
        self._behaviors.append(behavior)
        self._behaviors.sort(key=lambda b: b.order)

    def dispatch(self, message: Message) -> CommandResult:
        start = time.time()
        self._dispatch_count += 1

        prefix = "command" if message.type == MessageType.COMMAND else "query"
        msg_class_name = type(message).__name__
        key = f"{prefix}:{msg_class_name}"

        handler_reg = self._handlers.get(key)
        if not handler_reg:
            self._error_count += 1
            return CommandResult(
                success=False,
                errors=[f"no handler for {msg_class_name}"],
                elapsed_ms=(time.time() - start) * 1000,
            )

        try:
            for behavior in self._behaviors:
                result = behavior.handler(message, lambda: handler_reg.handler(message))
                if isinstance(result, CommandResult):
                    return result

            result = handler_reg.handler(message)
            elapsed = (time.time() - start) * 1000

            if isinstance(result, CommandResult):
                result.elapsed_ms = elapsed
                return result

            return CommandResult(success=True, data=result, elapsed_ms=elapsed)

        except Exception as e:
            self._error_count += 1
            return CommandResult(
                success=False,
                errors=[str(e)],
                elapsed_ms=(time.time() - start) * 1000,
            )

    def dispatch_many(self, messages: List[Message]) -> List[CommandResult]:
        return [self.dispatch(msg) for msg in messages]

    def has_handler(self, message_class: type,
                    msg_type: MessageType = MessageType.COMMAND) -> bool:
        prefix = "command" if msg_type == MessageType.COMMAND else "query"
        key = f"{prefix}:{message_class.__name__}"
        return key in self._handlers

    def clear(self) -> None:
        with self._lock:
            self._handlers.clear()
            self._behaviors.clear()

    @property
    def dispatch_count(self) -> int:
        return self._dispatch_count

    @property
    def error_count(self) -> int:
        return self._error_count

    def handler_count(self) -> int:
        return len(self._handlers)
