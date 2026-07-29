"""health — Health monitoring and readiness checks.

Provides health check registration, liveness/readiness probes,
dependency health tracking, and aggregated status reporting.
"""

from __future__ import annotations

import enum
import time
from typing import Any, Callable, Dict, List, Optional


class HealthStatus(enum.IntEnum):
    HEALTHY = 0
    DEGRADED = 1
    UNHEALTHY = 2
    UNKNOWN = 3


class CheckResult:
    """Result of a single health check."""
    __slots__ = ("name", "status", "message", "details", "latency_ms",
                 "timestamp", "critical")

    def __init__(self, name: str, status: HealthStatus = HealthStatus.UNKNOWN,
                 message: str = "", details: Optional[Dict[str, Any]] = None,
                 latency_ms: float = 0.0, critical: bool = False) -> None:
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.latency_ms = latency_ms
        self.timestamp = time.time()
        self.critical = critical

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.name,
            "message": self.message,
            "latency_ms": round(self.latency_ms, 2),
            "critical": self.critical,
        }


class HealthCheck:
    """A registered health check."""
    __slots__ = ("name", "check_fn", "critical", "tags", "timeout_sec")

    def __init__(self, name: str, check_fn: Callable,
                 critical: bool = False, tags: Optional[List[str]] = None,
                 timeout_sec: float = 5.0) -> None:
        self.name = name
        self.check_fn = check_fn
        self.critical = critical
        self.tags = tags or []
        self.timeout_sec = timeout_sec


class HealthReport:
    """Aggregated health report."""
    __slots__ = ("status", "checks", "timestamp", "uptime_sec")

    def __init__(self, status: HealthStatus = HealthStatus.UNKNOWN,
                 checks: Optional[List[CheckResult]] = None,
                 uptime_sec: float = 0.0) -> None:
        self.status = status
        self.checks = checks or []
        self.timestamp = time.time()
        self.uptime_sec = uptime_sec

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.name,
            "timestamp": self.timestamp,
            "uptime_sec": round(self.uptime_sec, 2),
            "checks": [c.to_dict() for c in self.checks],
            "summary": {
                "total": len(self.checks),
                "healthy": sum(1 for c in self.checks if c.status == HealthStatus.HEALTHY),
                "degraded": sum(1 for c in self.checks if c.status == HealthStatus.DEGRADED),
                "unhealthy": sum(1 for c in self.checks if c.status == HealthStatus.UNHEALTHY),
            },
        }


class HealthMonitor:
    """Health monitoring system with checks and reporting."""

    def __init__(self) -> None:
        self._checks: Dict[str, HealthCheck] = {}
        self._results: Dict[str, CheckResult] = {}
        self._history: List[HealthReport] = []
        self._started_at = time.time()

    def register(self, name: str, check_fn: Callable,
                 critical: bool = False, tags: Optional[List[str]] = None) -> None:
        self._checks[name] = HealthCheck(name, check_fn, critical, tags)

    def unregister(self, name: str) -> bool:
        if name in self._checks:
            del self._checks[name]
            self._results.pop(name, None)
            return True
        return False

    def check(self, name: str) -> Optional[CheckResult]:
        hc = self._checks.get(name)
        if not hc:
            return None

        start = time.time()
        try:
            result = hc.check_fn()
            latency = (time.time() - start) * 1000

            if isinstance(result, CheckResult):
                result.latency_ms = latency
                result.critical = hc.critical
            elif isinstance(result, dict):
                status = HealthStatus(result.get("status", HealthStatus.HEALTHY))
                result = CheckResult(name, status, result.get("message", ""),
                                     result.get("details", {}), latency, hc.critical)
            elif isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                result = CheckResult(name, status, critical=hc.critical,
                                     latency_ms=latency)
            else:
                result = CheckResult(name, HealthStatus.HEALTHY,
                                     latency_ms=latency, critical=hc.critical)

            self._results[name] = result
            return result

        except Exception as e:
            latency = (time.time() - start) * 1000
            result = CheckResult(name, HealthStatus.UNHEALTHY, str(e),
                                 latency_ms=latency, critical=hc.critical)
            self._results[name] = result
            return result

    def check_all(self) -> List[CheckResult]:
        results = []
        for name in self._checks:
            result = self.check(name)
            if result:
                results.append(result)
        return results

    def report(self) -> HealthReport:
        results = self.check_all()

        statuses = [r.status for r in results]
        if HealthStatus.UNHEALTHY in statuses:
            status = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            status = HealthStatus.DEGRADED
        elif HealthStatus.HEALTHY in statuses:
            status = HealthStatus.HEALTHY
        else:
            status = HealthStatus.UNKNOWN

        report = HealthReport(status, results, time.time() - self._started_at)
        self._history.append(report)
        return report

    def is_healthy(self) -> bool:
        report = self.report()
        return report.status in (HealthStatus.HEALTHY, HealthStatus.UNKNOWN)

    def get_result(self, name: str) -> Optional[CheckResult]:
        return self._results.get(name)

    def history(self, limit: int = 10) -> List[HealthReport]:
        return self._history[-limit:]

    def check_count(self) -> int:
        return len(self._checks)
