"""I STUDIO — System Tools (SISITEMU Integration)."""

from __future__ import annotations

import os
import platform
from typing import Any, Dict, List, Optional


class SystemExplorer:
    def __init__(self):
        self._processes: List[Dict[str, Any]] = []

    def get_system_info(self) -> Dict[str, Any]:
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
        }

    def get_cpu_info(self) -> Dict[str, Any]:
        try:
            import psutil
            return {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else 0,
                "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                "percent_usage": psutil.cpu_percent(interval=0.1),
            }
        except ImportError:
            return {"error": "psutil not available"}

    def get_memory_info(self) -> Dict[str, Any]:
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "total_gb": round(mem.total / 1024**3, 2),
                "available_gb": round(mem.available / 1024**3, 2),
                "used_gb": round(mem.used / 1024**3, 2),
                "percent": mem.percent,
            }
        except ImportError:
            return {"error": "psutil not available"}

    def get_disk_info(self) -> List[Dict[str, Any]]:
        try:
            import psutil
            disks = []
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disks.append({
                        "device": part.device,
                        "mountpoint": part.mountpoint,
                        "fstype": part.fstype,
                        "total_gb": round(usage.total / 1024**3, 2),
                        "used_gb": round(usage.used / 1024**3, 2),
                        "free_gb": round(usage.free / 1024**3, 2),
                        "percent": usage.percent,
                    })
                except PermissionError:
                    continue
            return disks
        except ImportError:
            return [{"error": "psutil not available"}]

    def get_network_info(self) -> Dict[str, Any]:
        try:
            import psutil
            net = psutil.net_if_addrs()
            io = psutil.net_io_counters()
            interfaces = {}
            for name, addrs in net.items():
                interfaces[name] = [{"address": a.address, "family": str(a.family)} for a in addrs]
            return {
                "interfaces": interfaces,
                "bytes_sent": io.bytes_sent,
                "bytes_received": io.bytes_recv,
                "packets_sent": io.packets_sent,
                "packets_received": io.packets_recv,
            }
        except ImportError:
            return {"error": "psutil not available"}

    def list_processes(self) -> List[Dict[str, Any]]:
        try:
            import psutil
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            processes.sort(key=lambda p: p.get("cpu_percent", 0), reverse=True)
            self._processes = processes
            return processes
        except ImportError:
            return [{"error": "psutil not available"}]

    def get_process_info(self, pid: int) -> Dict[str, Any]:
        try:
            import psutil
            try:
                proc = psutil.Process(pid)
                return {
                    "pid": proc.pid,
                    "name": proc.name(),
                    "status": proc.status(),
                    "cpu_percent": proc.cpu_percent(),
                    "memory_percent": proc.memory_percent(),
                    "memory_rss": proc.memory_info().rss,
                    "create_time": proc.create_time(),
                    "num_threads": proc.num_threads(),
                    "exe": proc.exe(),
                    "cwd": proc.cwd(),
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                return {"error": str(e)}
        except ImportError:
            return {"error": "psutil not available"}

    def get_environment_variables(self) -> Dict[str, str]:
        return dict(os.environ)

    def get_file_system_info(self, path: str = ".") -> Dict[str, Any]:
        try:
            import psutil
            try:
                usage = psutil.disk_usage(path)
                return {
                    "path": os.path.abspath(path),
                    "total_gb": round(usage.total / 1024**3, 2),
                    "used_gb": round(usage.used / 1024**3, 2),
                    "free_gb": round(usage.free / 1024**3, 2),
                    "percent": usage.percent,
                }
            except Exception as e:
                return {"error": str(e)}
        except ImportError:
            return {"error": "psutil not available", "path": os.path.abspath(path)}
