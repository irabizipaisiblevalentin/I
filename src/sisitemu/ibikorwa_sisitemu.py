"""ibikorwa_sisitemu — OS services: processes, threads, scheduling, signals, timers, environment."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple


class ProcessState(Enum):
    CREATED = "created"
    RUNNING = "running"
    READY = "ready"
    BLOCKED = "blocked"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class ThreadPriority(Enum):
    IDLE = "idle"
    LOWEST = "lowest"
    BELOW_NORMAL = "below_normal"
    NORMAL = "normal"
    ABOVE_NORMAL = "above_normal"
    HIGHEST = "highest"
    REAL_TIME = "real_time"


class SchedulerPolicy(Enum):
    ROUND_ROBIN = "round_robin"
    PRIORITY = "priority"
    FAIR = "fair"
    REAL_TIME = "real_time"
    CUSTOM = "custom"


class Signal(Enum):
    SIGINT = 2
    SIGTERM = 15
    SIGKILL = 9
    SIGHUP = 1
    SIGUSR1 = 10
    SIGUSR2 = 12
    SIGCHLD = 17
    SIGSTOP = 19
    SIGCONT = 18


@dataclass
class ProcessInfo:
    pid: int = 0
    name: str = ""
    state: ProcessState = ProcessState.CREATED
    priority: ThreadPriority = ThreadPriority.NORMAL
    cpu_time: float = 0.0
    memory_usage: int = 0
    thread_count: int = 1
    parent_pid: int = 0
    command: str = ""
    environment: Dict[str, str] = field(default_factory=dict)
    start_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "name": self.name,
            "state": self.state.value,
            "priority": self.priority.value,
            "cpu_time": round(self.cpu_time, 3),
            "memory_usage": self.memory_usage,
            "threads": self.thread_count,
        }


@dataclass
class ThreadInfo:
    tid: int = 0
    name: str = ""
    state: ProcessState = ProcessState.CREATED
    priority: ThreadPriority = ThreadPriority.NORMAL
    cpu_affinity: List[int] = field(default_factory=list)
    stack_size: int = 1048576
    exit_code: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tid": self.tid,
            "name": self.name,
            "state": self.state.value,
            "priority": self.priority.value,
            "exit_code": self.exit_code,
        }


class Scheduler:
    def __init__(self, policy: SchedulerPolicy = SchedulerPolicy.ROUND_ROBIN,
                 quantum: float = 0.100):
        self.policy = policy
        self.quantum = quantum
        self.threads: List[ThreadInfo] = []
        self._current_index = 0
        self._total_switches = 0

    def add_thread(self, thread: ThreadInfo) -> None:
        self.threads.append(thread)

    def remove_thread(self, tid: int) -> bool:
        for t in self.threads:
            if t.tid == tid:
                self.threads.remove(t)
                return True
        return False

    def next_thread(self) -> Optional[ThreadInfo]:
        if not self.threads:
            return None
        if self.policy == SchedulerPolicy.ROUND_ROBIN:
            self._current_index = (self._current_index + 1) % len(self.threads)
            self._total_switches += 1
            return self.threads[self._current_index]
        elif self.policy == SchedulerPolicy.PRIORITY:
            priorities = [ThreadPriority.HIGHEST, ThreadPriority.ABOVE_NORMAL,
                          ThreadPriority.NORMAL, ThreadPriority.BELOW_NORMAL,
                          ThreadPriority.LOWEST, ThreadPriority.IDLE]
            for prio in priorities:
                for t in self.threads:
                    if t.priority == prio:
                        self._total_switches += 1
                        return t
            return self.threads[0] if self.threads else None
        else:
            self._current_index = (self._current_index + 1) % len(self.threads)
            self._total_switches += 1
            return self.threads[self._current_index]

    @property
    def context_switches(self) -> int:
        return self._total_switches

    def summary(self) -> Dict[str, Any]:
        return {
            "policy": self.policy.value,
            "quantum": self.quantum,
            "threads": len(self.threads),
            "context_switches": self._total_switches,
        }


class Timer:
    def __init__(self, name: str = ""):
        self.name = name
        self._start: float = 0.0
        self._elapsed: float = 0.0
        self._running: bool = False

    def start(self) -> None:
        self._start = time.perf_counter()
        self._running = True

    def stop(self) -> float:
        if self._running:
            self._elapsed += time.perf_counter() - self._start
            self._running = False
        return self._elapsed

    def reset(self) -> None:
        self._elapsed = 0.0
        self._running = False

    def read(self) -> float:
        if self._running:
            return self._elapsed + (time.perf_counter() - self._start)
        return self._elapsed

    @property
    def running(self) -> bool:
        return self._running

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "elapsed": round(self.read(), 6), "running": self._running}


class IntervalTimer(Timer):
    def __init__(self, name: str = "", interval: float = 1.0,
                 callback: Optional[Callable] = None):
        super().__init__(name)
        self.interval = interval
        self.callback = callback
        self._last_fire: float = 0.0
        self._fired_count: int = 0

    def update(self) -> None:
        if not self._running:
            return
        now = self.read()
        if now - self._last_fire >= self.interval:
            self._last_fire = now
            self._fired_count += 1
            if self.callback:
                self.callback()

    @property
    def fired_count(self) -> int:
        return self._fired_count


class SignalManager:
    def __init__(self):
        self._handlers: Dict[Signal, List[Callable]] = {}
        self._pending: List[Signal] = []
        self._masked: List[Signal] = []

    def register_handler(self, sig: Signal, handler: Callable) -> None:
        if sig not in self._handlers:
            self._handlers[sig] = []
        self._handlers[sig].append(handler)

    def unregister_handler(self, sig: Signal, handler: Callable) -> bool:
        if sig in self._handlers and handler in self._handlers[sig]:
            self._handlers[sig].remove(handler)
            return True
        return False

    def send(self, sig: Signal, target_pid: int = 0) -> None:
        if sig in self._masked:
            self._pending.append(sig)
            return
        handlers = self._handlers.get(sig, [])
        for handler in handlers:
            handler()

    def mask(self, sig: Signal) -> None:
        if sig not in self._masked:
            self._masked.append(sig)

    def unmask(self, sig: Signal) -> None:
        if sig in self._masked:
            self._masked.remove(sig)

    def deliver_pending(self) -> None:
        pending = self._pending.copy()
        self._pending.clear()
        for sig in pending:
            self.send(sig)


class EnvironmentManager:
    def __init__(self):
        self._vars: Dict[str, str] = {}
        self._load_system()

    def _load_system(self) -> None:
        for key, value in os.environ.items():
            self._vars[key] = value

    def get(self, key: str, default: str = "") -> str:
        return self._vars.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._vars[key] = value

    def unset(self, key: str) -> bool:
        if key in self._vars:
            del self._vars[key]
            return True
        return False

    def has(self, key: str) -> bool:
        return key in self._vars

    def list(self) -> Dict[str, str]:
        return dict(self._vars)

    def to_dict(self) -> Dict[str, str]:
        return self.list()


class ProcessManager:
    def __init__(self):
        self.processes: Dict[int, ProcessInfo] = {}
        self.scheduler = Scheduler()
        self.signals = SignalManager()
        self.environment = EnvironmentManager()
        self._timers: Dict[str, Timer] = {}

    def create_process(self, name: str, command: str = "",
                       priority: ThreadPriority = ThreadPriority.NORMAL) -> ProcessInfo:
        pid = len(self.processes) + 1
        info = ProcessInfo(
            pid=pid, name=name, command=command,
            priority=priority, start_time=time.time(),
        )
        self.processes[pid] = info
        return info

    def get_process(self, pid: int) -> Optional[ProcessInfo]:
        return self.processes.get(pid)

    def list_processes(self, state: Optional[ProcessState] = None) -> List[ProcessInfo]:
        if state:
            return [p for p in self.processes.values() if p.state == state]
        return list(self.processes.values())

    def terminate(self, pid: int, force: bool = False) -> bool:
        proc = self.processes.get(pid)
        if proc:
            proc.state = ProcessState.TERMINATED
            return True
        return False

    def create_timer(self, name: str) -> Timer:
        timer = Timer(name)
        self._timers[name] = timer
        return timer

    def get_timer(self, name: str) -> Optional[Timer]:
        return self._timers.get(name)

    def create_interval_timer(self, name: str, interval: float,
                              callback: Optional[Callable] = None) -> IntervalTimer:
        timer = IntervalTimer(name, interval, callback)
        self._timers[name] = timer
        return timer

    def execute(self, command: str, args: Optional[List[str]] = None,
                wait: bool = True) -> Tuple[int, str, str]:
        try:
            result = subprocess.run(
                [command] + (args or []),
                capture_output=True, text=True, timeout=30,
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)

    def spawn(self, target: Callable, args: Tuple = (),
              daemon: bool = False) -> threading.Thread:
        thread = threading.Thread(target=target, args=args, daemon=daemon)
        thread.start()
        return thread

    def summary(self) -> Dict[str, Any]:
        return {
            "processes": len(self.processes),
            "scheduler": self.scheduler.summary(),
            "timers": list(self._timers.keys()),
            "env_vars": len(self.environment.list()),
        }


_os_manager = ProcessManager()


def get_os_manager() -> ProcessManager:
    return _os_manager
