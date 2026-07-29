"""lifecycle — Application lifecycle management.

Defines the universal lifecycle stages that every framework must follow:
  CREATE → CONFIGURE → INITIALIZE → START → RUN → STOP → DESTROY

Provides lifecycle hooks, phase management, and graceful shutdown.
"""

from __future__ import annotations

import enum
import time
from typing import Any, Callable, Dict, List, Optional


class Phase(enum.IntEnum):
    """Lifecycle phases in execution order."""
    CREATED = 0
    CONFIGURED = 1
    INITIALIZED = 2
    STARTING = 3
    RUNNING = 4
    STOPPING = 5
    STOPPED = 6
    DESTROYING = 7
    DESTROYED = 8
    ERROR = -1


class LifecycleHook:
    """A registered lifecycle hook."""
    __slots__ = ("phase", "callback", "priority", "name", "once")

    def __init__(self, phase: Phase, callback: Callable,
                 priority: int = 0, name: str = "", once: bool = False) -> None:
        self.phase = phase
        self.callback = callback
        self.priority = priority
        self.name = name or getattr(callback, "__name__", "anonymous")
        self.once = once

    def __repr__(self) -> str:
        return f"LifecycleHook({self.phase.name}, {self.name}, p={self.priority})"


class LifecycleManager:
    """Manages application lifecycle phases and hooks."""

    def __init__(self) -> None:
        self._phase = Phase.CREATED
        self._hooks: Dict[Phase, List[LifecycleHook]] = {}
        self._history: List[tuple] = []
        self._started_at: float = 0.0
        self._stopped_at: float = 0.0

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def uptime(self) -> float:
        if self._started_at == 0:
            return 0.0
        if self._stopped_at > 0:
            return self._stopped_at - self._started_at
        return time.time() - self._started_at

    @property
    def is_running(self) -> bool:
        return self._phase == Phase.RUNNING

    @property
    def history(self) -> List[tuple]:
        return list(self._history)

    def on(self, phase: Phase, callback: Callable,
           priority: int = 0, name: str = "", once: bool = False) -> None:
        """Register a hook for a lifecycle phase."""
        hook = LifecycleHook(phase, callback, priority, name, once)
        hooks = self._hooks.setdefault(phase, [])
        hooks.append(hook)
        hooks.sort(key=lambda h: h.priority, reverse=True)

    def on_create(self, callback: Callable, **kw: Any) -> None:
        self.on(Phase.CREATED, callback, **kw)

    def on_configure(self, callback: Callable, **kw: Any) -> None:
        self.on(Phase.CONFIGURED, callback, **kw)

    def on_init(self, callback: Callable, **kw: Any) -> None:
        self.on(Phase.INITIALIZED, callback, **kw)

    def on_start(self, callback: Callable, **kw: Any) -> None:
        self.on(Phase.STARTING, callback, **kw)

    def on_run(self, callback: Callable, **kw: Any) -> None:
        self.on(Phase.RUNNING, callback, **kw)

    def on_stop(self, callback: Callable, **kw: Any) -> None:
        self.on(Phase.STOPPING, callback, **kw)

    def on_destroy(self, callback: Callable, **kw: Any) -> None:
        self.on(Phase.DESTROYING, callback, **kw)

    def on_error(self, callback: Callable, **kw: Any) -> None:
        self.on(Phase.ERROR, callback, **kw)

    def advance(self, target: Phase, context: Any = None) -> None:
        """Advance to the target phase, firing all hooks in between."""
        order = list(Phase)
        current_idx = order.index(self._phase) if self._phase in order else -1
        target_idx = order.index(target) if target in order else -1

        if target_idx < 0:
            self._set_phase(Phase.ERROR, context)
            return

        start = max(current_idx + 1, 0)
        for i in range(start, target_idx + 1):
            phase = order[i]
            self._set_phase(phase, context)

    def _set_phase(self, phase: Phase, context: Any = None) -> None:
        old = self._phase
        self._phase = phase
        self._history.append((phase.name, time.time()))

        if phase == Phase.STARTING and self._started_at == 0:
            self._started_at = time.time()
        elif phase == Phase.STOPPED:
            self._stopped_at = time.time()

        hooks = list(self._hooks.get(phase, []))
        to_remove = []
        for hook in hooks:
            try:
                if context is not None:
                    hook.callback(context)
                else:
                    hook.callback()
            except Exception as e:
                self._fire_error(hook, e)
            if hook.once:
                to_remove.append(hook)

        for hook in to_remove:
            self._hooks[phase].remove(hook)

    def _fire_error(self, hook: LifecycleHook, error: Exception) -> None:
        error_hooks = self._hooks.get(Phase.ERROR, [])
        for eh in error_hooks:
            try:
                eh.callback(error, hook)
            except Exception:
                pass

    def reset(self) -> None:
        self._phase = Phase.CREATED
        self._hooks.clear()
        self._history.clear()
        self._started_at = 0.0
        self._stopped_at = 0.0

    def remove_hooks(self, phase: Optional[Phase] = None) -> int:
        if phase is None:
            count = sum(len(h) for h in self._hooks.values())
            self._hooks.clear()
            return count
        hooks = self._hooks.pop(phase, [])
        return len(hooks)
