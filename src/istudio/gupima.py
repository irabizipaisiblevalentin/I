"""I STUDIO — Profiling Platform (Gupima)."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Dict, List, Optional

from .ibikoreshingiro import ProfileResult, ProfilerType


class Profiler:
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._active_session: Optional[str] = None
        self._samples: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._listeners: Dict[str, List[callable]] = defaultdict(list)

    def start_session(self, name: str, profile_type: ProfilerType = ProfilerType.CPU) -> str:
        session_id = f"{name}_{int(time.time() * 1000)}"
        self._sessions[session_id] = {
            "name": name,
            "type": profile_type.value,
            "start_time": time.time(),
            "end_time": None,
            "samples": [],
            "results": None,
        }
        self._active_session = session_id
        self._emit("session.started", {"session_id": session_id, "type": profile_type.value})
        return session_id

    def stop_session(self, session_id: Optional[str] = None) -> Optional[ProfileResult]:
        session_id = session_id or self._active_session
        if not session_id or session_id not in self._sessions:
            return None
        session = self._sessions[session_id]
        session["end_time"] = time.time()
        elapsed = session["end_time"] - session["start_time"]
        samples = session.get("samples", [])

        result = ProfileResult(
            type=ProfilerType(session["type"]),
            total_time_ms=elapsed * 1000,
            call_count=len(samples),
            details={
                "session_name": session["name"],
                "sample_count": len(samples),
                "avg_time_ms": (elapsed / max(len(samples), 1)) * 1000,
            },
        )
        session["results"] = result
        self._emit("session.stopped", {"session_id": session_id, "result": result})
        return result

    def add_sample(self, data: Dict[str, Any], session_id: Optional[str] = None) -> None:
        session_id = session_id or self._active_session
        if not session_id or session_id not in self._sessions:
            return
        sample = {
            "timestamp": time.time(),
            "data": data,
        }
        self._sessions[session_id]["samples"].append(sample)
        self._emit("sample.added", {"session_id": session_id, "sample": sample})

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def get_active_session(self) -> Optional[str]:
        return self._active_session

    def list_sessions(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": sid,
                "name": s["name"],
                "type": s["type"],
                "start_time": s["start_time"],
                "end_time": s["end_time"],
                "sample_count": len(s["samples"]),
            }
            for sid, s in self._sessions.items()
        ]

    def get_results(self, session_id: Optional[str] = None) -> Optional[ProfileResult]:
        session_id = session_id or self._active_session
        if not session_id:
            return None
        session = self._sessions.get(session_id)
        if not session:
            return None
        return session.get("results")

    def clear(self) -> None:
        self._sessions.clear()
        self._active_session = None
        self._emit("cleared", {})

    def on(self, event: str, handler: callable) -> None:
        self._listeners[event].append(handler)

    def _emit(self, event: str, data: Dict[str, Any]) -> None:
        for handler in self._listeners.get(event, []):
            try:
                handler(data)
            except Exception:
                pass


class CPUSampler:
    def __init__(self, profiler: Profiler):
        self._profiler = profiler

    def sample(self) -> Dict[str, Any]:
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
            return {
                "cpu_percent": cpu_percent,
                "cpu_count": len(cpu_percent),
                "load_avg": psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0, 0, 0),
            }
        except ImportError:
            return {"cpu_percent": [0], "cpu_count": 1, "load_avg": (0, 0, 0)}


class MemorySampler:
    def __init__(self, profiler: Profiler):
        self._profiler = profiler

    def sample(self) -> Dict[str, Any]:
        try:
            import psutil
            mem = psutil.virtual_memory()
            process = psutil.Process()
            return {
                "total_mb": mem.total / 1024 / 1024,
                "available_mb": mem.available / 1024 / 1024,
                "percent_used": mem.percent,
                "process_rss_mb": process.memory_info().rss / 1024 / 1024,
            }
        except ImportError:
            return {"total_mb": 0, "available_mb": 0, "percent_used": 0, "process_rss_mb": 0}
