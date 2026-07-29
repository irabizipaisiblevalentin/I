"""events — Event bus with pub/sub and async support.

Provides event emission, subscription, wildcard patterns,
priority ordering, and async handler execution.
"""

from __future__ import annotations

import enum
import threading
import time
from typing import Any, Callable, Dict, List, Optional


class EventPriority(enum.IntEnum):
    LOWEST = -100
    LOW = -50
    NORMAL = 0
    HIGH = 50
    HIGHEST = 100


class Event:
    """An event dispatched through the bus."""
    __slots__ = ("name", "data", "source", "_stopped", "_timestamp")

    def __init__(self, name: str, data: Any = None, source: str = "") -> None:
        self.name = name
        self.data = data
        self.source = source
        self._stopped = False
        self._timestamp = time.time()

    @property
    def stopped(self) -> bool:
        return self._stopped

    def stop_propagation(self) -> None:
        self._stopped = True

    @property
    def timestamp(self) -> float:
        return self._timestamp


class Subscription:
    """A registered event subscription."""
    __slots__ = ("handler", "priority", "once", "filter_fn", "id")

    _counter = 0

    def __init__(self, handler: Callable, priority: int = 0,
                 once: bool = False, filter_fn: Optional[Callable] = None) -> None:
        Subscription._counter += 1
        self.id = Subscription._counter
        self.handler = handler
        self.priority = priority
        self.once = once
        self.filter_fn = filter_fn

    def matches_filter(self, event: Event) -> bool:
        if self.filter_fn is None:
            return True
        return bool(self.filter_fn(event))


class EventBus:
    """Central event bus supporting pub/sub with wildcards."""

    def __init__(self) -> None:
        self._subscriptions: Dict[str, List[Subscription]] = {}
        self._global: List[Subscription] = []
        self._lock = threading.Lock()
        self._history: List[Event] = []
        self._max_history = 1000
        self._emit_count = 0

    def subscribe(self, event_name: str, handler: Callable,
                  priority: int = 0, once: bool = False,
                  filter_fn: Optional[Callable] = None) -> Subscription:
        sub = Subscription(handler, priority, once, filter_fn)
        with self._lock:
            subs = self._subscriptions.setdefault(event_name, [])
            subs.append(sub)
            subs.sort(key=lambda s: s.priority, reverse=True)
        return sub

    def on(self, event_name: str, handler: Callable,
           priority: int = 0) -> Subscription:
        return self.subscribe(event_name, handler, priority)

    def once(self, event_name: str, handler: Callable,
             priority: int = 0) -> Subscription:
        return self.subscribe(event_name, handler, priority, once=True)

    def subscribe_all(self, handler: Callable,
                      priority: int = 0) -> Subscription:
        sub = Subscription(handler, priority)
        with self._lock:
            self._global.append(sub)
            self._global.sort(key=lambda s: s.priority, reverse=True)
        return sub

    def unsubscribe(self, subscription: Subscription) -> bool:
        with self._lock:
            for event_name, subs in self._subscriptions.items():
                for i, s in enumerate(subs):
                    if s.id == subscription.id:
                        subs.pop(i)
                        return True
            for i, s in enumerate(self._global):
                if s.id == subscription.id:
                    self._global.pop(i)
                    return True
        return False

    def emit(self, event_name: str, data: Any = None,
             source: str = "") -> Event:
        event = Event(event_name, data, source)
        self._emit_count += 1

        with self._lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

        all_subs = []

        exact_subs = list(self._subscriptions.get(event_name, []))
        all_subs.extend(exact_subs)

        if "*" in self._subscriptions:
            all_subs.extend(self._subscriptions["*"])

        all_subs.extend(self._global)

        all_subs.sort(key=lambda s: s.priority, reverse=True)

        to_remove = []
        for sub in all_subs:
            if event.stopped:
                break
            if not sub.matches_filter(event):
                continue
            try:
                sub.handler(event)
            except Exception as e:
                self._handle_error(event, sub, e)
            if sub.once:
                to_remove.append(sub)

        if to_remove:
            self._remove_subscriptions(to_remove)

        return event

    def emit_async(self, event_name: str, data: Any = None,
                   source: str = "") -> Event:
        event = Event(event_name, data, source)
        self._emit_count += 1

        with self._lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

        all_subs = []
        all_subs.extend(self._subscriptions.get(event_name, []))
        if "*" in self._subscriptions:
            all_subs.extend(self._subscriptions["*"])
        all_subs.extend(self._global)
        all_subs.sort(key=lambda s: s.priority, reverse=True)

        for sub in all_subs:
            try:
                sub.handler(event)
            except Exception:
                pass

        return event

    def _remove_subscriptions(self, subs: List[Subscription]) -> None:
        ids = {s.id for s in subs}
        for event_name in list(self._subscriptions.keys()):
            self._subscriptions[event_name] = [
                s for s in self._subscriptions[event_name] if s.id not in ids
            ]
        self._global = [s for s in self._global if s.id not in ids]

    def _handle_error(self, event: Event, sub: Subscription, error: Exception) -> None:
        pass

    def history(self, event_name: Optional[str] = None,
                limit: int = 50) -> List[Event]:
        events = self._history
        if event_name:
            events = [e for e in events if e.name == event_name]
        return events[-limit:]

    def subscription_count(self, event_name: Optional[str] = None) -> int:
        if event_name:
            return len(self._subscriptions.get(event_name, []))
        return sum(len(s) for s in self._subscriptions.values()) + len(self._global)

    def event_names(self) -> List[str]:
        return list(self._subscriptions.keys())

    def clear(self) -> None:
        with self._lock:
            self._subscriptions.clear()
            self._global.clear()
            self._history.clear()

    @property
    def emit_count(self) -> int:
        return self._emit_count
