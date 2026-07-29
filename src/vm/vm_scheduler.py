"""IVM Scheduler — fiber/coroutine scheduler (future-ready)."""
from __future__ import annotations

import time
from typing import Any, Callable
from enum import IntEnum


class FiberState(IntEnum):
    CREATED = 0
    READY = 1
    RUNNING = 2
    SUSPENDED = 3
    FINISHED = 4


class Fiber:
    """A lightweight cooperative execution unit."""
    __slots__ = ("_id", "_state", "_entry", "_result", "_error")

    def __init__(self, fiber_id: int, entry: Callable) -> None:
        self._id = fiber_id
        self._state = FiberState.CREATED
        self._entry = entry
        self._result: Any = None
        self._error: BaseException | None = None

    @property
    def id(self) -> int:
        return self._id

    @property
    def state(self) -> FiberState:
        return self._state

    @state.setter
    def state(self, value: FiberState) -> None:
        self._state = value

    @property
    def result(self) -> Any:
        return self._result

    @property
    def error(self) -> BaseException | None:
        return self._error

    def run(self) -> Any:
        self._state = FiberState.RUNNING
        try:
            self._result = self._entry()
            self._state = FiberState.FINISHED
        except Exception as e:
            self._error = e
            self._state = FiberState.FINISHED
        return self._result

    def __repr__(self) -> str:
        return f"Fiber(id={self._id}, state={self._state.name})"


class VMScheduler:
    """Cooperative fiber scheduler."""
    __slots__ = ("_fibers", "_next_id", "_current", "_time_slice_ms", "_total_time_ms")

    def __init__(self, time_slice_ms: float = 10.0) -> None:
        self._fibers: list[Fiber] = []
        self._next_id: int = 0
        self._current: Fiber | None = None
        self._time_slice_ms = time_slice_ms
        self._total_time_ms: float = 0.0

    @property
    def current(self) -> Fiber | None:
        return self._current

    def spawn(self, entry: Callable) -> Fiber:
        fiber = Fiber(self._next_id, entry)
        self._next_id += 1
        fiber.state = FiberState.READY
        self._fibers.append(fiber)
        return fiber

    def run_all(self) -> None:
        ready = [f for f in self._fibers if f.state == FiberState.READY]
        for fiber in ready:
            self._current = fiber
            fiber.run()
            self._current = None
        self._fibers = [f for f in self._fibers if f.state != FiberState.FINISHED]

    def step(self) -> bool:
        ready = [f for f in self._fibers if f.state == FiberState.READY]
        if not ready:
            return False
        fiber = ready[0]
        self._current = fiber
        start = time.monotonic()
        fiber.run()
        elapsed = (time.monotonic() - start) * 1000.0
        self._total_time_ms += elapsed
        self._current = None
        return True

    def get_fibers(self) -> list[Fiber]:
        return list(self._fibers)

    def finished_count(self) -> int:
        return sum(1 for f in self._fibers if f.state == FiberState.FINISHED)

    def active_count(self) -> int:
        return sum(1 for f in self._fibers if f.state in (FiberState.READY, FiberState.RUNNING))

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_fibers": len(self._fibers) + self.finished_count(),
            "active": self.active_count(),
            "finished": self.finished_count(),
            "total_time_ms": round(self._total_time_ms, 3),
        }
