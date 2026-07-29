"""umuyobora — Kernel framework: scheduler, memory manager, system calls, IPC, driver framework, power management."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ibikoresho_sisitemu import (
    Allocator, MemoryBlock, MemoryRegion, SystemsCore, get_systems_core,
)


class KernelState(Enum):
    BOOTING = "booting"
    RUNNING = "running"
    SLEEPING = "sleeping"
    HALTED = "halted"
    PANIC = "panic"


class PrivilegeLevel(Enum):
    USER = "user"
    KERNEL = "kernel"
    HYPERVISOR = "hypervisor"


class SyscallNumber(Enum):
    EXIT = 0
    READ = 1
    WRITE = 2
    OPEN = 3
    CLOSE = 4
    MMAP = 5
    MUNMAP = 6
    SLEEP = 7
    YIELD = 8
    GETPID = 9
    SPAWN = 10
    IPC_SEND = 11
    IPC_RECV = 12
    SHARED_MEM = 13
    CREATE_THREAD = 14
    EXIT_THREAD = 15


@dataclass
class SyscallContext:
    number: SyscallNumber = SyscallNumber.EXIT
    args: List[int] = field(default_factory=list)
    result: int = 0
    caller_pid: int = 0
    privilege: PrivilegeLevel = PrivilegeLevel.USER
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "syscall": self.number.name,
            "args": self.args,
            "result": self.result,
            "caller": self.caller_pid,
            "privilege": self.privilege.value,
        }


@dataclass
class KernelThread:
    tid: int = 0
    name: str = ""
    state: str = "ready"
    priority: int = 0
    stack_pointer: int = 0
    program_counter: int = 0
    cpu_time: float = 0.0
    privilege: PrivilegeLevel = PrivilegeLevel.USER
    registers: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tid": self.tid,
            "name": self.name,
            "state": self.state,
            "priority": self.priority,
            "cpu_time": round(self.cpu_time, 3),
        }


class Scheduler:
    def __init__(self):
        self.threads: List[KernelThread] = []
        self._current: Optional[KernelThread] = None
        self._quantum: float = 0.010
        self._total_switches: int = 0

    def add_thread(self, thread: KernelThread) -> None:
        self.threads.append(thread)

    def remove_thread(self, tid: int) -> bool:
        for t in self.threads:
            if t.tid == tid:
                self.threads.remove(t)
                return True
        return False

    def schedule(self) -> Optional[KernelThread]:
        if not self.threads:
            return None
        ready = [t for t in self.threads if t.state == "ready"]
        if not ready:
            return self._current if self._current else self.threads[0]
        ready.sort(key=lambda t: (-t.priority, t.cpu_time))
        self._current = ready[0]
        self._current.state = "running"
        self._total_switches += 1
        return self._current

    def yield_cpu(self) -> None:
        if self._current:
            self._current.state = "ready"

    def summary(self) -> Dict[str, Any]:
        return {
            "threads": len(self.threads),
            "current_tid": self._current.tid if self._current else None,
            "context_switches": self._total_switches,
        }


class VirtualMemoryManager:
    def __init__(self, total_pages: int = 65536, page_size: int = 4096):
        self.total_pages = total_pages
        self.page_size = page_size
        self.pages: List[bool] = [False] * total_pages
        self.page_tables: Dict[int, Dict[str, Any]] = {}

    def allocate_page(self, process_id: int = 0) -> Optional[int]:
        for i in range(len(self.pages)):
            if not self.pages[i]:
                self.pages[i] = True
                self.page_tables[i] = {
                    "process_id": process_id,
                    "virtual_addr": i * self.page_size,
                    "physical_addr": i * self.page_size,
                    "readable": True,
                    "writable": True,
                    "executable": False,
                }
                return i
        return None

    def free_page(self, page_index: int) -> bool:
        if 0 <= page_index < len(self.pages) and self.pages[page_index]:
            self.pages[page_index] = False
            self.page_tables.pop(page_index, None)
            return True
        return False

    def translate(self, virtual_addr: int) -> Optional[int]:
        page_index = virtual_addr // self.page_size
        entry = self.page_tables.get(page_index)
        if entry:
            offset = virtual_addr % self.page_size
            return entry["physical_addr"] + offset
        return None

    def map_page(self, virtual_addr: int, physical_addr: int,
                 process_id: int = 0) -> bool:
        page_index = virtual_addr // self.page_size
        if page_index < len(self.pages):
            self.pages[page_index] = True
            self.page_tables[page_index] = {
                "process_id": process_id,
                "virtual_addr": virtual_addr,
                "physical_addr": physical_addr,
                "readable": True,
                "writable": True,
                "executable": False,
            }
            return True
        return False

    def protect(self, virtual_addr: int, readable: bool = True,
                writable: bool = True, executable: bool = False) -> bool:
        page_index = virtual_addr // self.page_size
        entry = self.page_tables.get(page_index)
        if entry:
            entry["readable"] = readable
            entry["writable"] = writable
            entry["executable"] = executable
            return True
        return False

    @property
    def used_pages(self) -> int:
        return sum(1 for p in self.pages if p)

    @property
    def free_pages(self) -> int:
        return sum(1 for p in self.pages if not p)

    def summary(self) -> Dict[str, Any]:
        return {
            "total": self.total_pages,
            "used": self.used_pages,
            "free": self.free_pages,
            "utilization": round(self.used_pages / self.total_pages, 4) if self.total_pages > 0 else 0,
        }


class IPCChannel:
    def __init__(self, name: str = "ipc"):
        self.name = name
        self._messages: List[Dict[str, Any]] = []
        self._subscribers: Dict[int, List[Callable]] = {}

    def send(self, sender_pid: int, receiver_pid: int,
             data: Dict[str, Any]) -> bool:
        msg = {
            "sender": sender_pid,
            "receiver": receiver_pid,
            "data": data,
            "timestamp": time.time(),
        }
        self._messages.append(msg)
        if receiver_pid in self._subscribers:
            for handler in self._subscribers[receiver_pid]:
                handler(msg)
        return True

    def recv(self, pid: int) -> Optional[Dict[str, Any]]:
        for msg in self._messages:
            if msg["receiver"] == pid:
                self._messages.remove(msg)
                return msg
        return None

    def subscribe(self, pid: int, handler: Callable) -> None:
        if pid not in self._subscribers:
            self._subscribers[pid] = []
        self._subscribers[pid].append(handler)

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "pending": len(self._messages),
            "subscribers": len(self._subscribers),
        }


class SharedMemoryRegion:
    def __init__(self, name: str = "", size: int = 4096):
        self.name = name
        self.size = size
        self.data: bytearray = bytearray(size)
        self._access: Dict[int, bool] = {}

    def grant_access(self, pid: int, writable: bool = False) -> None:
        self._access[pid] = writable

    def revoke_access(self, pid: int) -> None:
        self._access.pop(pid, None)

    def read(self, pid: int, offset: int, size: int) -> Optional[bytes]:
        if pid not in self._access:
            return None
        return bytes(self.data[offset:offset + size])

    def write(self, pid: int, offset: int, data: bytes) -> bool:
        if pid not in self._access or not self._access[pid]:
            return False
        self.data[offset:offset + len(data)] = data
        return True


class Driver:
    def __init__(self, name: str = "", driver_type: str = ""):
        self.name = name
        self.driver_type = driver_type
        self._initialized = False

    def init(self) -> bool:
        self._initialized = True
        return True

    def deinit(self) -> None:
        self._initialized = False

    def read(self, buf: bytearray, size: int) -> int:
        return 0

    def write(self, buf: bytes, size: int) -> int:
        return 0

    def ioctl(self, request: int, arg: Any) -> int:
        return 0

    def summary(self) -> Dict[str, Any]:
        return {"name": self.name, "type": self.driver_type, "initialized": self._initialized}


class DriverManager:
    def __init__(self):
        self.drivers: Dict[str, Driver] = {}

    def register(self, driver: Driver) -> bool:
        self.drivers[driver.name] = driver
        return True

    def unregister(self, name: str) -> bool:
        if name in self.drivers:
            self.drivers[name].deinit()
            del self.drivers[name]
            return True
        return False

    def get(self, name: str) -> Optional[Driver]:
        return self.drivers.get(name)

    def init_all(self) -> None:
        for driver in self.drivers.values():
            driver.init()

    def summary(self) -> Dict[str, Any]:
        return {"drivers": len(self.drivers), "names": list(self.drivers.keys())}


class PowerManager:
    def __init__(self):
        self.state: str = "active"
        self.frequency: int = 100
        self.voltage: float = 1.2
        self._sleep_count: int = 0

    def sleep(self) -> None:
        self.state = "sleep"
        self._sleep_count += 1

    def wake(self) -> None:
        self.state = "active"

    def set_frequency(self, mhz: int) -> None:
        self.frequency = mhz

    def set_voltage(self, volts: float) -> None:
        self.voltage = volts

    def summary(self) -> Dict[str, Any]:
        return {
            "state": self.state,
            "frequency_mhz": self.frequency,
            "voltage": self.voltage,
        }


class Kernel:
    def __init__(self, name: str = "I-Kernel"):
        self.name = name
        self.state = KernelState.BOOTING
        self.scheduler = Scheduler()
        self.vmm = VirtualMemoryManager()
        self.ipc = IPCChannel()
        self.shared_memory: Dict[str, SharedMemoryRegion] = {}
        self.drivers = DriverManager()
        self.power = PowerManager()
        self._core = get_systems_core()
        self._syscall_count: int = 0
        self._boot_time: float = 0.0

    def boot(self) -> bool:
        self._boot_time = time.time()
        self.state = KernelState.BOOTING
        self.drivers.init_all()
        kernel_thread = KernelThread(
            tid=0, name="kernel_main", state="running",
            priority=255, privilege=PrivilegeLevel.KERNEL,
        )
        self.scheduler.add_thread(kernel_thread)
        self.state = KernelState.RUNNING
        return True

    def halt(self) -> None:
        self.state = KernelState.HALTED

    def panic(self, message: str) -> None:
        self.state = KernelState.PANIC

    def syscall(self, ctx: SyscallContext) -> int:
        self._syscall_count += 1
        ctx.timestamp = time.time()

        if ctx.number == SyscallNumber.EXIT:
            self.scheduler.remove_thread(ctx.caller_pid)
            ctx.result = 0
        elif ctx.number == SyscallNumber.YIELD:
            self.scheduler.yield_cpu()
            self.scheduler.schedule()
            ctx.result = 0
        elif ctx.number == SyscallNumber.GETPID:
            ctx.result = ctx.caller_pid
        elif ctx.number == SyscallNumber.SLEEP:
            time.sleep(ctx.args[0] / 1000.0)
            ctx.result = 0
        elif ctx.number == SyscallNumber.IPC_SEND:
            if len(ctx.args) >= 3:
                ctx.result = 1 if self.ipc.send(ctx.caller_pid, ctx.args[0], {}) else 0
        elif ctx.number == SyscallNumber.SHARED_MEM:
            name = f"shm_{ctx.caller_pid}_{ctx.args[0]}"
            region = SharedMemoryRegion(name=name, size=ctx.args[0])
            self.shared_memory[name] = region
            ctx.result = 0
        else:
            ctx.result = -1

        return ctx.result

    def handle_interrupt(self, irq: int) -> None:
        pass

    @property
    def uptime(self) -> float:
        return time.time() - self._boot_time if self._boot_time > 0 else 0.0

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "uptime": round(self.uptime, 2),
            "scheduler": self.scheduler.summary(),
            "memory": self.vmm.summary(),
            "drivers": self.drivers.summary(),
            "ipc_pending": len(self.ipc._messages),
            "power": self.power.summary(),
        }


# ─── Container Isolation (cgroups, namespaces) ──────────────────────────────

@dataclass
class CGroupStats:
    cpu_usage_us: int = 0
    memory_usage_bytes: int = 0
    pids_current: int = 0
    io_read_bytes: int = 0
    io_write_bytes: int = 0


class CGroupManager:
    def __init__(self, mount_point: str = "/sys/fs/cgroup"):
        self.mount_point = mount_point
        self._controllers: Dict[str, bool] = {
            "cpu": True, "memory": True, "pids": True, "io": True, "cpuset": True,
        }
        self._groups: Dict[str, CGroupStats] = {}

    def create_group(self, name: str) -> bool:
        if name not in self._groups:
            self._groups[name] = CGroupStats()
            return True
        return False

    def set_cpu_limit(self, group: str, quota: int, period: int = 100000) -> bool:
        if group in self._groups:
            return True
        return False

    def set_memory_limit(self, group: str, limit_bytes: int) -> bool:
        if group in self._groups:
            return True
        return False

    def set_pids_limit(self, group: str, max_pids: int) -> bool:
        if group in self._groups:
            return True
        return False

    def get_stats(self, group: str) -> Optional[CGroupStats]:
        return self._groups.get(group)

    def remove_group(self, name: str) -> bool:
        return self._groups.pop(name, None) is not None

    def summary(self) -> Dict[str, Any]:
        return {"groups": len(self._groups), "controllers": list(self._controllers.keys())}


@dataclass
class Namespace:
    ns_type: str = "pid"
    ns_id: int = 0
    processes: List[int] = field(default_factory=list)


class NamespaceManager:
    def __init__(self):
        self._namespaces: Dict[str, Namespace] = {}

    def create(self, ns_type: str) -> Namespace:
        ns = Namespace(ns_type=ns_type, ns_id=len(self._namespaces) + 1)
        self._namespaces[f"{ns_type}:{ns.ns_id}"] = ns
        return ns

    def attach_process(self, ns_key: str, pid: int) -> bool:
        ns = self._namespaces.get(ns_key)
        if not ns:
            return False
        ns.processes.append(pid)
        return True

    def list_by_type(self, ns_type: str) -> List[Namespace]:
        return [ns for k, ns in self._namespaces.items() if k.startswith(f"{ns_type}:")]

    def summary(self) -> Dict[str, Any]:
        return {"total": len(self._namespaces),
                "types": list(set(ns.ns_type for ns in self._namespaces.values()))}


class ContainerIsolation:
    def __init__(self):
        self.cgroups = CGroupManager()
        self.namespaces = NamespaceManager()

    def create_container_namespace(self, name: str) -> Dict[str, str]:
        ns_keys: Dict[str, str] = {}
        for ns_type in ["pid", "net", "mnt", "uts", "ipc"]:
            ns = self.namespaces.create(ns_type)
            ns_keys[ns_type] = f"{ns_type}:{ns.ns_id}"
        return ns_keys

    def summary(self) -> Dict[str, Any]:
        return {"cgroups": self.cgroups.summary(), "namespaces": self.namespaces.summary()}


class Unikernel:
    def __init__(self, name: str = "unikernel"):
        self.name = name
        self._booted: bool = False
        self._memory_mb: int = 128

    def build(self, source: str, target: str = "x86_64") -> bool:
        return True

    def boot(self) -> bool:
        self._booted = True
        return True

    def halt(self) -> None:
        self._booted = False

    @property
    def is_running(self) -> bool:
        return self._booted


_kernel = Kernel()


def get_kernel() -> Kernel:
    return _kernel
