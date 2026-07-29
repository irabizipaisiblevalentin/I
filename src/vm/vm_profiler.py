"""IVM Profiler — execution profiling and hot-spot detection."""
from __future__ import annotations

import time
from typing import Any


class ProfileEntry:
    """Profile data for a single function/chunk."""
    __slots__ = ("name", "calls", "total_time_ms", "self_time_ms",
                 "max_time_ms", "min_time_ms", "instruction_count")

    def __init__(self, name: str) -> None:
        self.name = name
        self.calls = 0
        self.total_time_ms = 0.0
        self.self_time_ms = 0.0
        self.max_time_ms = 0.0
        self.min_time_ms = float("inf")
        self.instruction_count = 0

    @property
    def avg_time_ms(self) -> float:
        return self.total_time_ms / self.calls if self.calls > 0 else 0.0


class VMProfiler:
    """Execution profiler for the IVM."""
    __slots__ = (
        "_entries", "_enabled", "_start_time",
        "_current_entry", "_call_stack",
        "_instruction_counts",
    )

    def __init__(self) -> None:
        self._entries: dict[str, ProfileEntry] = {}
        self._enabled = False
        self._start_time = 0.0
        self._current_entry: ProfileEntry | None = None
        self._call_stack: list[ProfileEntry] = []
        self._instruction_counts: dict[str, int] = {}

    @property
    def enabled(self) -> bool:
        return self._enabled

    def start(self) -> None:
        self._enabled = True
        self._start_time = time.monotonic()

    def stop(self) -> None:
        self._enabled = False
        if self._current_entry is not None:
            elapsed = (time.monotonic() - self._start_time) * 1000.0
            self._current_entry.self_time_ms += elapsed

    def reset(self) -> None:
        self._entries.clear()
        self._instruction_counts.clear()
        self._call_stack.clear()
        self._current_entry = None

    def _get_or_create(self, name: str) -> ProfileEntry:
        if name not in self._entries:
            self._entries[name] = ProfileEntry(name=name)
        return self._entries[name]

    def on_call(self, name: str) -> None:
        if not self._enabled:
            return
        entry = self._get_or_create(name)
        entry.calls += 1
        self._call_stack.append(entry)

    def on_return(self, name: str) -> None:
        if not self._enabled:
            return
        if self._call_stack:
            self._call_stack.pop()

    def record_instruction(self, opcode: int, chunk_name: str = "") -> None:
        if not self._enabled:
            return
        key = f"{chunk_name}:op{opcode}"
        self._instruction_counts[key] = self._instruction_counts.get(key, 0) + 1

    def record_time(self, name: str, elapsed_ms: float) -> None:
        entry = self._get_or_create(name)
        entry.total_time_ms += elapsed_ms
        entry.self_time_ms += elapsed_ms
        entry.max_time_ms = max(entry.max_time_ms, elapsed_ms)
        if elapsed_ms > 0:
            entry.min_time_ms = min(entry.min_time_ms, elapsed_ms)

    def get_entries(self) -> list[ProfileEntry]:
        return sorted(self._entries.values(), key=lambda e: e.total_time_ms, reverse=True)

    def top_functions(self, n: int = 10) -> list[ProfileEntry]:
        return self.get_entries()[:n]

    def format_profile(self) -> str:
        entries = self.get_entries()
        if not entries:
            return "No profile data."

        lines = [
            f"{'Function':<30} {'Calls':>8} {'Total (ms)':>12} {'Self (ms)':>12} {'Avg (ms)':>12}",
            "-" * 76,
        ]
        for e in entries:
            lines.append(
                f"{e.name:<30} {e.calls:>8} {e.total_time_ms:>12.3f} "
                f"{e.self_time_ms:>12.3f} {e.avg_time_ms:>12.3f}"
            )
        return "\n".join(lines)

    def get_hot_spots(self, threshold: float = 10.0) -> list[ProfileEntry]:
        return [e for e in self.get_entries() if e.self_time_ms > threshold]

    def to_dict(self) -> dict[str, Any]:
        return {
            "entries": [
                {
                    "name": e.name,
                    "calls": e.calls,
                    "total_time_ms": round(e.total_time_ms, 3),
                    "self_time_ms": round(e.self_time_ms, 3),
                    "avg_time_ms": round(e.avg_time_ms, 3),
                }
                for e in self.get_entries()
            ],
            "instruction_counts": dict(self._instruction_counts),
        }
