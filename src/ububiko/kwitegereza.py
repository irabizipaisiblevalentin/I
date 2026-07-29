"""kwitegereza — Observability for the UBUBIKO data platform.

Provides slow query detection, performance metrics, connection monitoring,
replication monitoring, storage metrics, health checks, and audit dashboards.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


@dataclass
class QueryMetric:
    """Metrics for a single query execution.

    Attributes:
        query: The SQL query text.
        duration_ms: Execution time in milliseconds.
        rows_affected: Number of rows affected/returned.
        timestamp: When the query executed.
        source: Source component (ORM, raw, migration, etc.).
        params_hash: Hash of query parameters.
    """

    query: str = ""
    duration_ms: float = 0.0
    rows_affected: int = 0
    timestamp: str = ""
    source: str = ""
    params_hash: str = ""


class SlowQueryDetector:
    """Detects and logs slow database queries.

    Monitors query execution times and logs queries that exceed
    configurable thresholds.
    """

    def __init__(self, slow_threshold_ms: float = 100.0) -> None:
        self._threshold = slow_threshold_ms
        self._slow_queries: List[QueryMetric] = []
        self._max_logged: int = 1000
        self._callback: Optional[Callable[[QueryMetric], None]] = None

    @property
    def threshold_ms(self) -> float:
        return self._threshold

    @threshold_ms.setter
    def threshold_ms(self, value: float) -> None:
        self._threshold = value

    def on_slow_query(self, callback: Callable[[QueryMetric], None]) -> None:
        """Register a callback for slow query notifications."""
        self._callback = callback

    def record(self, query: str, duration_ms: float, rows: int = 0,
               source: str = "") -> Optional[QueryMetric]:
        """Record a query execution and detect if it's slow."""
        metric = QueryMetric(
            query=query,
            duration_ms=duration_ms,
            rows_affected=rows,
            timestamp=datetime.utcnow().isoformat(),
            source=source,
        )
        if duration_ms >= self._threshold:
            self._slow_queries.append(metric)
            if len(self._slow_queries) > self._max_logged:
                self._slow_queries.pop(0)
            if self._callback:
                try:
                    self._callback(metric)
                except Exception:
                    pass
            return metric
        return None

    def get_slow_queries(self, min_duration: float = 0.0,
                         limit: int = 100) -> List[QueryMetric]:
        """Get recorded slow queries, optionally filtered."""
        results = [q for q in self._slow_queries if q.duration_ms >= min_duration]
        results.sort(key=lambda q: q.duration_ms, reverse=True)
        return results[:limit]

    def get_average_duration(self) -> float:
        """Get average duration of recorded slow queries."""
        if not self._slow_queries:
            return 0.0
        return sum(q.duration_ms for q in self._slow_queries) / len(self._slow_queries)

    def get_max_duration(self) -> float:
        """Get the maximum duration recorded."""
        if not self._slow_queries:
            return 0.0
        return max(q.duration_ms for q in self._slow_queries)

    def clear(self) -> None:
        """Clear all recorded slow queries."""
        self._slow_queries.clear()

    def report(self) -> Dict[str, Any]:
        """Generate a slow query report."""
        return {
            "threshold_ms": self._threshold,
            "total_slow": len(self._slow_queries),
            "avg_duration_ms": self.get_average_duration(),
            "max_duration_ms": self.get_max_duration(),
            "top_queries": [
                {"query": q.query[:100], "duration_ms": q.duration_ms, "source": q.source}
                for q in self.get_slow_queries(limit=10)
            ],
        }


class MetricsCollector:
    """Collects and exposes database performance metrics.

    Tracks query counts, durations, errors, connection usage,
    and cache statistics.
    """

    def __init__(self) -> None:
        self._query_count: int = 0
        self._error_count: int = 0
        self._total_duration_ms: float = 0.0
        self._queries_per_second: List[float] = []
        self._lock = threading.Lock()
        self._start_time: float = time.time()
        self._last_reset: float = time.time()
        self._metrics: Dict[str, Any] = {}

    def record_query(self, duration_ms: float, success: bool = True) -> None:
        """Record a query execution."""
        with self._lock:
            self._query_count += 1
            self._total_duration_ms += duration_ms
            if not success:
                self._error_count += 1

    def set_metric(self, name: str, value: Any) -> None:
        """Set a custom metric."""
        with self._lock:
            self._metrics[name] = value

    def get_metric(self, name: str) -> Optional[Any]:
        """Get a custom metric."""
        return self._metrics.get(name)

    @property
    def query_count(self) -> int:
        return self._query_count

    @property
    def error_count(self) -> int:
        return self._error_count

    @property
    def error_rate(self) -> float:
        if self._query_count == 0:
            return 0.0
        return self._error_count / self._query_count

    @property
    def avg_duration_ms(self) -> float:
        if self._query_count == 0:
            return 0.0
        return self._total_duration_ms / self._query_count

    @property
    def uptime_seconds(self) -> float:
        return time.time() - self._start_time

    def queries_per_second(self, window_seconds: int = 60) -> float:
        """Calculate queries per second over a window."""
        elapsed = time.time() - self._last_reset
        if elapsed == 0:
            return 0.0
        return self._query_count / elapsed

    def snapshot(self) -> Dict[str, Any]:
        """Return a snapshot of current metrics."""
        return {
            "query_count": self._query_count,
            "error_count": self._error_count,
            "error_rate": round(self.error_rate, 4),
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "total_duration_ms": round(self._total_duration_ms, 2),
            "uptime_seconds": round(self.uptime_seconds, 1),
            "queries_per_second": round(self.queries_per_second(), 2),
            "custom_metrics": dict(self._metrics),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._query_count = 0
            self._error_count = 0
            self._total_duration_ms = 0.0
            self._last_reset = time.time()
            self._metrics.clear()


@dataclass
class HealthStatus:
    """Status of a health check."""

    component: str = ""
    status: str = "healthy"
    message: str = ""
    latency_ms: float = 0.0
    timestamp: str = ""


class HealthChecker:
    """Performs health checks on database components.

    Checks connection status, replication lag, storage capacity,
    and component availability.
    """

    def __init__(self) -> None:
        self._checks: Dict[str, Callable[[], HealthStatus]] = {}

    def register_check(self, name: str, check_fn: Callable[[], HealthStatus]) -> None:
        """Register a health check function."""
        self._checks[name] = check_fn

    def run_all(self) -> List[HealthStatus]:
        """Run all registered health checks."""
        results = []
        for name, check_fn in self._checks.items():
            try:
                start = time.time()
                status = check_fn()
                status.latency_ms = (time.time() - start) * 1000
                results.append(status)
            except Exception as e:
                results.append(HealthStatus(
                    component=name,
                    status="error",
                    message=str(e),
                    timestamp=datetime.utcnow().isoformat(),
                ))
        return results

    def is_healthy(self) -> bool:
        """Check if all components are healthy."""
        return all(s.status == "healthy" for s in self.run_all())

    def summary(self) -> Dict[str, Any]:
        """Return a health check summary."""
        results = self.run_all()
        healthy = sum(1 for r in results if r.status == "healthy")
        return {
            "overall": "healthy" if healthy == len(results) else "degraded",
            "healthy": healthy,
            "total": len(results),
            "checks": [{"component": r.component, "status": r.status,
                        "message": r.message, "latency_ms": round(r.latency_ms, 2)}
                       for r in results],
        }


class StorageMetrics:
    """Tracks storage utilization and performance metrics."""

    def __init__(self, adapter: Any) -> None:
        self._adapter = adapter

    def table_sizes(self) -> Dict[str, int]:
        """Get row counts for all tables."""
        sizes: Dict[str, int] = {}
        try:
            tables = self._adapter.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", {}
            )
            for (table_name,) in tables:
                count = self._adapter.execute(f"SELECT COUNT(*) FROM {table_name}", {})
                sizes[table_name] = count[0][0] if count else 0
        except Exception:
            pass
        return sizes

    def database_size(self) -> int:
        """Estimate database size in bytes."""
        total = 0
        try:
            tables = self._adapter.execute(
                "SELECT name FROM sqlite_master WHERE type='table'", {}
            )
            for (table_name,) in tables:
                try:
                    page_count = self._adapter.execute(f"PRAGMA page_count", {})
                    page_size = self._adapter.execute(f"PRAGMA page_size", {})
                    if page_count and page_size:
                        total += page_count[0][0] * page_size[0][0]
                except Exception:
                    pass
        except Exception:
            pass
        return total

    def index_info(self) -> List[Dict[str, Any]]:
        """Get information about database indexes."""
        indexes = []
        try:
            rows = self._adapter.execute(
                "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL",
                {},
            )
            for name, table, sql in rows:
                indexes.append({"name": name, "table": table, "definition": sql})
        except Exception:
            pass
        return indexes

    def report(self) -> Dict[str, Any]:
        """Generate a storage report."""
        return {
            "database_size_bytes": self.database_size(),
            "table_sizes": self.table_sizes(),
            "index_count": len(self.index_info()),
            "indexes": self.index_info(),
        }


class AuditDashboard:
    """Dashboard for viewing audit and monitoring data.

    Aggregates data from audit logs, metrics, and health checks
    into a unified view.
    """

    def __init__(self, audit_logger: Any, metrics_collector: Any,
                 health_checker: Any) -> None:
        self._audit = audit_logger
        self._metrics = metrics_collector
        self._health = health_checker

    def overview(self) -> Dict[str, Any]:
        """Return a dashboard overview."""
        return {
            "metrics": self._metrics.snapshot(),
            "health": self._health.summary(),
            "recent_audit": [
                {"user": e.user, "action": e.action, "resource": e.resource, "timestamp": e.timestamp}
                for e in self._audit.get_recent(limit=20)
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def audit_report(self, user: str = "", action: str = "",
                     limit: int = 100) -> Dict[str, Any]:
        """Generate an audit report."""
        entries = self._audit.query(user=user, action=action, limit=limit)
        return {
            "total": len(entries),
            "entries": [vars(e) for e in entries],
            "generated_at": datetime.utcnow().isoformat(),
        }

    def performance_report(self) -> Dict[str, Any]:
        """Generate a performance report."""
        return {
            "metrics": self._metrics.snapshot(),
            "recommendations": self._generate_recommendations(),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _generate_recommendations(self) -> List[str]:
        recommendations = []
        metrics = self._metrics.snapshot()
        if metrics.get("error_rate", 0) > 0.05:
            recommendations.append("Error rate is above 5%. Review query errors.")
        if metrics.get("avg_duration_ms", 0) > 100:
            recommendations.append("Average query duration exceeds 100ms. Consider optimization.")
        return recommendations
