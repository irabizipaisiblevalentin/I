"""igenzura_sisitemu — Debugging: kernel debugger, memory inspector, profiler, tracing, crash dumps, live diagnostics."""

from __future__ import annotations

import time
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple


class DebugLevel(Enum):
    NONE = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5


class TraceEvent(Enum):
    SYSCALL = "syscall"
    CONTEXT_SWITCH = "context_switch"
    INTERRUPT = "interrupt"
    ALLOC = "alloc"
    FREE = "free"
    IPC = "ipc"
    DRIVER = "driver"
    SCHEDULER = "scheduler"
    POWER = "power"
    CUSTOM = "custom"


@dataclass
class TracePoint:
    timestamp: float = 0.0
    event: TraceEvent = TraceEvent.CUSTOM
    cpu: int = 0
    pid: int = 0
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": round(self.timestamp, 6),
            "event": self.event.value,
            "pid": self.pid,
            "message": self.message,
        }


@dataclass
class ProfileSample:
    timestamp: float = 0.0
    function: str = ""
    module: str = ""
    cpu_percent: float = 0.0
    memory_bytes: int = 0
    thread_id: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": round(self.timestamp, 3),
            "function": self.function,
            "cpu": round(self.cpu_percent, 1),
            "memory": self.memory_bytes,
        }


@dataclass
class MemoryRegion:
    address: int = 0
    size: int = 0
    used: bool = False
    owner: str = ""
    tag: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "address": hex(self.address),
            "size": self.size,
            "used": self.used,
            "owner": self.owner,
        }


class Tracer:
    def __init__(self):
        self.traces: List[TracePoint] = []
        self._enabled = False
        self._max_entries = 10000
        self._filters: List[TraceEvent] = []

    def enable(self) -> None:
        self._enabled = True

    def disable(self) -> None:
        self._enabled = False

    def trace(self, event: TraceEvent, message: str = "",
              pid: int = 0, data: Optional[Dict[str, Any]] = None) -> None:
        if not self._enabled:
            return
        if self._filters and event not in self._filters:
            return
        point = TracePoint(
            timestamp=time.time(),
            event=event,
            pid=pid,
            message=message,
            data=data or {},
        )
        self.traces.append(point)
        if len(self.traces) > self._max_entries:
            self.traces = self.traces[-self._max_entries:]

    def set_filter(self, events: List[TraceEvent]) -> None:
        self._filters = events

    def clear(self) -> None:
        self.traces.clear()

    def query(self, event_type: Optional[TraceEvent] = None,
              pid: Optional[int] = None,
              limit: int = 100) -> List[TracePoint]:
        results = self.traces
        if event_type:
            results = [t for t in results if t.event == event_type]
        if pid is not None:
            results = [t for t in results if t.pid == pid]
        return results[-limit:]

    def summary(self) -> Dict[str, Any]:
        return {"enabled": self._enabled, "entries": len(self.traces)}


class Profiler:
    def __init__(self):
        self.samples: List[ProfileSample] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._interval: float = 0.01
        self._function_times: Dict[str, float] = defaultdict(float)
        self._call_counts: Dict[str, int] = defaultdict(int)

    def start(self, interval: float = 0.01) -> None:
        self._interval = interval
        self._running = True

    def stop(self) -> None:
        self._running = False

    def record_sample(self, function: str = "", module: str = "",
                      cpu: float = 0.0, memory: int = 0) -> None:
        sample = ProfileSample(
            timestamp=time.time(),
            function=function,
            module=module,
            cpu_percent=cpu,
            memory_bytes=memory,
            thread_id=threading.get_ident(),
        )
        self.samples.append(sample)

    def record_call(self, function: str, duration: float) -> None:
        self._function_times[function] += duration
        self._call_counts[function] += 1

    def get_hotspots(self, top_n: int = 10) -> List[Dict[str, Any]]:
        sorted_funcs = sorted(
            self._function_times.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_n]
        return [
            {
                "function": func,
                "total_time": round(total, 4),
                "calls": self._call_counts.get(func, 0),
                "avg_time": round(total / self._call_counts.get(func, 1), 6),
            }
            for func, total in sorted_funcs
        ]

    def summary(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "samples": len(self.samples),
            "functions_tracked": len(self._function_times),
            "hotspots": self.get_hotspots(5),
        }


class MemoryInspector:
    def __init__(self):
        self.regions: List[MemoryRegion] = []

    def add_region(self, region: MemoryRegion) -> None:
        self.regions.append(region)

    def find_leaks(self) -> List[MemoryRegion]:
        leaked = [r for r in self.regions if r.used and r.owner != "kernel"]
        return leaked

    def get_stats(self) -> Dict[str, Any]:
        total = sum(r.size for r in self.regions)
        used = sum(r.size for r in self.regions if r.used)
        free = total - used
        return {
            "total": total,
            "used": used,
            "free": free,
            "utilization": round(used / total, 4) if total > 0 else 0,
            "blocks": len(self.regions),
        }

    def dump(self, address: int, size: int) -> bytes:
        return b'\x00' * size

    def summary(self) -> Dict[str, Any]:
        return self.get_stats()


class CrashDump:
    def __init__(self):
        self.dumps: List[Dict[str, Any]] = []
        self._enabled = True

    def capture(self, message: str, registers: Optional[Dict[str, int]] = None,
                stack_trace: Optional[List[str]] = None) -> Dict[str, Any]:
        dump = {
            "timestamp": time.time(),
            "message": message,
            "registers": registers or {},
            "stack_trace": stack_trace or [],
            "thread": threading.current_thread().name,
        }
        self.dumps.append(dump)
        return dump

    def last(self) -> Optional[Dict[str, Any]]:
        return self.dumps[-1] if self.dumps else None

    def clear(self) -> None:
        self.dumps.clear()

    def summary(self) -> Dict[str, Any]:
        return {"total_dumps": len(self.dumps), "last": self.dumps[-1] if self.dumps else None}


class LiveDiagnostics:
    def __init__(self):
        self._checks: Dict[str, Callable[[], bool]] = {}
        self._results: Dict[str, Tuple[bool, str, float]] = {}

    def register_check(self, name: str, check_fn: Callable[[], bool]) -> None:
        self._checks[name] = check_fn

    def run_check(self, name: str) -> Tuple[bool, str, float]:
        start = time.time()
        try:
            result = self._checks[name]()
            elapsed = time.time() - start
            status = "PASS" if result else "FAIL"
            self._results[name] = (result, status, elapsed)
            return result, status, elapsed
        except Exception as e:
            elapsed = time.time() - start
            self._results[name] = (False, str(e), elapsed)
            return False, str(e), elapsed

    def run_all(self) -> List[Dict[str, Any]]:
        results = []
        for name in self._checks:
            result, status, elapsed = self.run_check(name)
            results.append({"name": name, "status": status, "elapsed": round(elapsed, 3)})
        return results

    def summary(self) -> Dict[str, Any]:
        return {"checks": len(self._checks), "results": len(self._results)}


class Debugger:
    def __init__(self):
        self.tracer = Tracer()
        self.profiler = Profiler()
        self.memory_inspector = MemoryInspector()
        self.crash_dump = CrashDump()
        self.diagnostics = LiveDiagnostics()
        self.level = DebugLevel.INFO
        self._breakpoints: Dict[str, Callable] = {}
        self._stepping = False

    def set_level(self, level: DebugLevel) -> None:
        self.level = level
        if level >= DebugLevel.TRACE:
            self.tracer.enable()
        else:
            self.tracer.disable()

    def set_breakpoint(self, name: str, handler: Callable) -> None:
        self._breakpoints[name] = handler

    def remove_breakpoint(self, name: str) -> bool:
        if name in self._breakpoints:
            del self._breakpoints[name]
            return True
        return False

    def log(self, level: DebugLevel, message: str, **kwargs: Any) -> None:
        if level.value <= self.level.value:
            prefix = {
                DebugLevel.ERROR: "ERROR", DebugLevel.WARNING: "WARN",
                DebugLevel.INFO: "INFO", DebugLevel.DEBUG: "DEBUG",
                DebugLevel.TRACE: "TRACE",
            }.get(level, "INFO")
            extra = f" {kwargs}" if kwargs else ""
            print(f"[{prefix}] {message}{extra}")

    def step_into(self) -> None:
        self._stepping = True

    def step_over(self) -> None:
        self._stepping = True

    def continue_execution(self) -> None:
        self._stepping = False

    def summary(self) -> Dict[str, Any]:
        return {
            "level": self.level.name,
            "tracer": self.tracer.summary(),
            "profiler": self.profiler.summary(),
            "memory": self.memory_inspector.summary(),
            "crash_dumps": len(self.crash_dump.dumps),
            "checks": len(self.diagnostics._checks),
            "breakpoints": list(self._breakpoints.keys()),
        }


_debugger = Debugger()


def get_debugger() -> Debugger:
    return _debugger
