"""IVM Statistics Engine — execution metrics and reporting."""
from __future__ import annotations

import time
from typing import Any


class VMStatistics:
    """Tracks execution statistics for a VM instance."""
    __slots__ = (
        "_instructions_executed", "_function_calls", "_max_call_depth",
        "_current_call_depth", "_stack_max_depth", "_current_stack_depth",
        "_exceptions_raised", "_exceptions_caught",
        "_start_time", "_end_time", "_gc_stats",
        "_opcodes", "_bytecode_size",
    )

    def __init__(self) -> None:
        self._instructions_executed: int = 0
        self._function_calls: int = 0
        self._max_call_depth: int = 0
        self._current_call_depth: int = 0
        self._stack_max_depth: int = 0
        self._current_stack_depth: int = 0
        self._exceptions_raised: int = 0
        self._exceptions_caught: int = 0
        self._start_time: float = 0.0
        self._end_time: float = 0.0
        self._gc_stats: dict[str, Any] = {}
        self._opcodes: dict[int, int] = {}
        self._bytecode_size: int = 0

    @property
    def instructions_executed(self) -> int:
        return self._instructions_executed

    @property
    def function_calls(self) -> int:
        return self._function_calls

    @property
    def max_call_depth(self) -> int:
        return self._max_call_depth

    @property
    def max_stack_depth(self) -> int:
        return self._stack_max_depth

    @property
    def execution_time_ms(self) -> float:
        if self._start_time == 0:
            return 0.0
        end = self._end_time if self._end_time > 0 else time.monotonic()
        return (end - self._start_time) * 1000.0

    @property
    def instructions_per_second(self) -> float:
        t = self.execution_time_ms
        if t <= 0:
            return 0.0
        return self._instructions_executed / (t / 1000.0)

    def start(self) -> None:
        self._start_time = time.monotonic()

    def stop(self) -> None:
        self._end_time = time.monotonic()

    def record_instruction(self, opcode: int) -> None:
        self._instructions_executed += 1
        self._opcodes[opcode] = self._opcodes.get(opcode, 0) + 1

    def record_call(self) -> None:
        self._function_calls += 1
        self._current_call_depth += 1
        self._max_call_depth = max(self._max_call_depth, self._current_call_depth)

    def record_return(self) -> None:
        self._current_call_depth = max(0, self._current_call_depth - 1)

    def record_stack_depth(self, depth: int) -> None:
        self._current_stack_depth = depth
        self._stack_max_depth = max(self._stack_max_depth, depth)

    @property
    def exceptions_raised(self) -> int:
        return self._exceptions_raised

    @property
    def exceptions_caught(self) -> int:
        return self._exceptions_caught

    def record_exception(self) -> None:
        self._exceptions_raised += 1

    def record_exception_caught(self) -> None:
        self._exceptions_caught += 1

    def set_gc_stats(self, stats: dict[str, Any]) -> None:
        self._gc_stats = dict(stats)

    def set_bytecode_size(self, size: int) -> None:
        self._bytecode_size = size

    def get_top_opcodes(self, n: int = 10) -> list[tuple[int, int]]:
        return sorted(self._opcodes.items(), key=lambda x: x[1], reverse=True)[:n]

    def to_dict(self) -> dict[str, Any]:
        return {
            "instructions_executed": self._instructions_executed,
            "function_calls": self._function_calls,
            "max_call_depth": self._max_call_depth,
            "max_stack_depth": self._stack_max_depth,
            "exceptions_raised": self._exceptions_raised,
            "exceptions_caught": self._exceptions_caught,
            "execution_time_ms": round(self.execution_time_ms, 3),
            "instructions_per_second": round(self.instructions_per_second, 0),
            "bytecode_size": self._bytecode_size,
            "gc": self._gc_stats,
            "top_opcodes": [
                {"opcode": op, "count": cnt}
                for op, cnt in self.get_top_opcodes()
            ],
        }

    def format_summary(self) -> str:
        lines = [
            "IVM Execution Statistics",
            f"  Instructions executed: {self._instructions_executed:,}",
            f"  Function calls:        {self._function_calls:,}",
            f"  Max call depth:        {self._max_call_depth}",
            f"  Max stack depth:       {self._stack_max_depth}",
            f"  Exceptions raised:     {self._exceptions_raised}",
            f"  Execution time:        {self.execution_time_ms:.2f} ms",
            f"  Instructions/sec:      {self.instructions_per_second:,.0f}",
        ]
        return "\n".join(lines)
