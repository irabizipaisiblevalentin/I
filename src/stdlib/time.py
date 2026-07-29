"""time — Time utilities for the I language.

Provides time measurement, formatting, parsing, and manipulation.
"""

from __future__ import annotations

import time as _time
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Optional


# ---------------------------------------------------------------------------
# Current time
# ---------------------------------------------------------------------------

def now() -> float:
    """Current time as Unix timestamp (float seconds)."""
    return _time.time()


def now_monotonic() -> float:
    """Monotonic clock (immune to system clock changes)."""
    return _time.monotonic()


def now_perf_counter() -> float:
    """High-resolution performance counter."""
    return _time.perf_counter()


def now_ns() -> int:
    """Current time in nanoseconds since epoch."""
    return _time.time_ns()


# ---------------------------------------------------------------------------
# Sleep
# ---------------------------------------------------------------------------

def sleep(seconds: float) -> None:
    """Sleep for given seconds."""
    _time.sleep(seconds)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_time(timestamp: float, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format Unix timestamp to string."""
    return datetime.fromtimestamp(timestamp).strftime(fmt)


def format_duration(seconds: float) -> str:
    """Format seconds as human-readable duration."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f} us"
    if seconds < 1:
        return f"{seconds * 1000:.1f} ms"
    if seconds < 60:
        return f"{seconds:.2f} s"
    mins = int(seconds // 60)
    secs = seconds % 60
    if mins < 60:
        return f"{mins}m {secs:.0f}s"
    hours = mins // 60
    mins = mins % 60
    return f"{hours}h {mins}m"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse(s: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> float:
    """Parse time string to Unix timestamp."""
    dt = datetime.strptime(s, fmt)
    return dt.timestamp()


# ---------------------------------------------------------------------------
# Timer utility
# ---------------------------------------------------------------------------

class Timer:
    """Context-manager timer for measuring elapsed time."""

    def __init__(self) -> None:
        self._start: float = 0.0
        self._end: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> Timer:
        self._start = _time.perf_counter()
        return self

    def __exit__(self, *args: object) -> None:
        self._end = _time.perf_counter()
        self.elapsed = self._end - self._start

    def start(self) -> None:
        self._start = _time.perf_counter()

    def stop(self) -> float:
        self._end = _time.perf_counter()
        self.elapsed = self._end - self._start
        return self.elapsed

    def reset(self) -> None:
        self.elapsed = 0.0
