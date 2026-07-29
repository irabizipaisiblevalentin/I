"""IGICU — Observability: logging, metrics, tracing, dashboards, alerting."""

from __future__ import annotations

import json
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .ibikoreshingiro import (
    AlertSeverity, LogLevel, MetricType, ObservabilityConfig,
    IGICU_VERSION,
)


class Logger:
    def __init__(self, name: str = "igicu",
                 level: LogLevel = LogLevel.INFO,
                 output_dir: Optional[str] = None):
        self.name = name
        self.level = level
        self.output_dir = output_dir or os.path.join(
            os.path.expanduser("~"), ".igicu", "logs"
        )
        self._entries: List[Dict[str, Any]] = []

    def _log(self, level: LogLevel, message: str,
             context: Optional[Dict[str, Any]] = None) -> None:
        if level.value < LogLevel[self.level.name].value:
            return

        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": level.value,
            "logger": self.name,
            "message": message,
            "context": context or {},
        }
        self._entries.append(entry)
        self._write(entry)

    def trace(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._log(LogLevel.TRACE, message, context)

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._log(LogLevel.DEBUG, message, context)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._log(LogLevel.INFO, message, context)

    def warn(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._log(LogLevel.WARN, message, context)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._log(LogLevel.ERROR, message, context)

    def fatal(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self._log(LogLevel.FATAL, message, context)

    def get_entries(self, level: Optional[LogLevel] = None) -> List[Dict[str, Any]]:
        if level:
            return [e for e in self._entries if e["level"] == level.value]
        return self._entries

    def _write(self, entry: Dict[str, Any]) -> None:
        path = Path(self.output_dir) / f"{self.name}.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


class MetricsCollector:
    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, List[float]] = defaultdict(list)

    def increment(self, name: str, value: int = 1) -> None:
        self._counters[name] += value

    def decrement(self, name: str, value: int = 1) -> None:
        if name in self._counters:
            self._counters[name] = max(0, self._counters[name] - value)
        else:
            self._counters[name] = 0

    def set_gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value

    def observe(self, name: str, value: float) -> None:
        self._histograms[name].append(value)
        if len(self._histograms[name]) > 1000:
            self._histograms[name] = self._histograms[name][-1000:]

    def time(self, name: str) -> "_TimerContext":
        return _TimerContext(self, name)

    def get_metrics(self) -> Dict[str, Any]:
        result = {}
        for name, value in self._counters.items():
            result[f"counter_{name}"] = value
        for name, value in self._gauges.items():
            result[f"gauge_{name}"] = value
        for name, values in self._histograms.items():
            if values:
                sorted_vals = sorted(values)
                result[f"histogram_{name}_count"] = len(values)
                result[f"histogram_{name}_avg"] = sum(values) / len(values)
                result[f"histogram_{name}_min"] = min(values)
                result[f"histogram_{name}_max"] = max(values)
                result[f"histogram_{name}_p50"] = sorted_vals[len(sorted_vals) // 2]
                result[f"histogram_{name}_p95"] = sorted_vals[int(len(sorted_vals) * 0.95)]
                result[f"histogram_{name}_p99"] = sorted_vals[int(len(sorted_vals) * 0.99)]
        for name, values in self._timers.items():
            if values:
                sorted_vals = sorted(values)
                result[f"timer_{name}_count"] = len(values)
                result[f"timer_{name}_avg_ms"] = sum(values) / len(values)
                result[f"timer_{name}_p50"] = sorted_vals[len(sorted_vals) // 2]
                result[f"timer_{name}_p95"] = sorted_vals[int(len(sorted_vals) * 0.95)]
        return result

    def reset(self) -> None:
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._timers.clear()


class _TimerContext:
    def __init__(self, collector: MetricsCollector, name: str):
        self.collector = collector
        self.name = name
        self.start: float = 0.0

    def __enter__(self) -> "_TimerContext":
        self.start = time.time()
        return self

    def __exit__(self, *args: Any) -> None:
        elapsed = (time.time() - self.start) * 1000
        self.collector._timers[self.name].append(elapsed)
        if len(self.collector._timers[self.name]) > 1000:
            self.collector._timers[self.name] = self.collector._timers[self.name][-1000:]


class Tracer:
    def __init__(self, service_name: str = "igicu", sampling_rate: float = 0.1):
        self.service_name = service_name
        self.sampling_rate = sampling_rate
        self._spans: List[Dict[str, Any]] = []
        self._max_spans = 10000

    def start_span(self, name: str, parent_id: Optional[str] = None,
                   tags: Optional[Dict[str, str]] = None) -> str:
        import random
        span_id = str(uuid.uuid4())
        if parent_id:
            parent_span = next((s for s in self._spans if s["span_id"] == parent_id), None)
            trace_id = parent_span["trace_id"] if parent_span else str(uuid.uuid4())
        else:
            trace_id = str(uuid.uuid4())

        span = {
            "span_id": span_id,
            "trace_id": trace_id,
            "parent_id": parent_id,
            "name": name,
            "service": self.service_name,
            "tags": tags or {},
            "start_time": time.time_ns(),
            "end_time": None,
            "duration_ns": None,
        }
        self._spans.append(span)
        if len(self._spans) > self._max_spans:
            self._spans = self._spans[-self._max_spans:]
        return span_id

    def end_span(self, span_id: str, tags: Optional[Dict[str, str]] = None) -> None:
        for span in self._spans:
            if span["span_id"] == span_id:
                span["end_time"] = time.time_ns()
                span["duration_ns"] = span["end_time"] - span["start_time"]
                if tags:
                    span["tags"].update(tags)
                break

    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        return [s for s in self._spans if s["trace_id"] == trace_id]

    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._spans[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        completed = [s for s in self._spans if s["duration_ns"] is not None]
        if not completed:
            return {"total_spans": 0}
        durations = [s["duration_ns"] / 1_000_000 for s in completed]
        sorted_d = sorted(durations)
        return {
            "total_spans": len(self._spans),
            "completed_spans": len(completed),
            "avg_duration_ms": sum(durations) / len(durations),
            "p50_ms": sorted_d[len(sorted_d) // 2],
            "p95_ms": sorted_d[int(len(sorted_d) * 0.95)],
            "p99_ms": sorted_d[int(len(sorted_d) * 0.99)],
        }


class AlertManager:
    def __init__(self):
        self._alerts: List[Dict[str, Any]] = []
        self._rules: List[Dict[str, Any]] = []
        self._channels: Dict[str, Callable] = {}

    def add_rule(self, name: str, condition: str,
                 severity: AlertSeverity = AlertSeverity.WARNING,
                 message: str = "") -> str:
        rule_id = f"rule-{uuid.uuid4().hex[:8]}"
        self._rules.append({
            "id": rule_id,
            "name": name,
            "condition": condition,
            "severity": severity.value,
            "message": message,
            "enabled": True,
        })
        return rule_id

    def register_channel(self, name: str, notifier: Callable) -> None:
        self._channels[name] = notifier

    def trigger(self, rule_id: str, value: Any = None) -> Dict[str, Any]:
        rule = next((r for r in self._rules if r["id"] == rule_id), None)
        if not rule or not rule["enabled"]:
            return {}

        alert = {
            "id": f"alert-{uuid.uuid4().hex[:8]}",
            "rule_id": rule_id,
            "rule_name": rule["name"],
            "severity": rule["severity"],
            "message": rule["message"],
            "value": value,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "acknowledged": False,
            "resolved": False,
        }
        self._alerts.append(alert)

        for channel_name, notifier in self._channels.items():
            try:
                notifier(alert)
            except Exception:
                pass

        return alert

    def acknowledge(self, alert_id: str) -> bool:
        for alert in self._alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                return True
        return False

    def resolve(self, alert_id: str) -> bool:
        for alert in self._alerts:
            if alert["id"] == alert_id:
                alert["resolved"] = True
                return True
        return False

    def list_alerts(self, unresolved: bool = False) -> List[Dict[str, Any]]:
        if unresolved:
            return [a for a in self._alerts if not a["resolved"]]
        return self._alerts

    def list_rules(self) -> List[Dict[str, Any]]:
        return self._rules


class Dashboard:
    def __init__(self, name: str = "igicu-dashboard"):
        self.name = name
        self._panels: List[Dict[str, Any]] = []
        self._refresh_interval = 30

    def add_panel(self, title: str, metric: str,
                  panel_type: str = "graph",
                  position: Optional[Dict[str, int]] = None) -> str:
        panel_id = f"panel-{uuid.uuid4().hex[:8]}"
        self._panels.append({
            "id": panel_id,
            "title": title,
            "metric": metric,
            "type": panel_type,
            "position": position or {"x": 0, "y": 0, "w": 6, "h": 4},
        })
        return panel_id

    def render(self, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "name": self.name,
            "refresh_interval": self._refresh_interval,
            "panels": [
                {
                    "id": p["id"],
                    "title": p["title"],
                    "type": p["type"],
                    "value": (metrics or {}).get(p["metric"], 0),
                    "position": p["position"],
                }
                for p in self._panels
            ],
        }


class AuditLogger:
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or os.path.join(
            os.path.expanduser("~"), ".igicu", "audit"
        )
        self._entries: List[Dict[str, Any]] = []

    def log(self, action: str, actor: str, resource: str,
            result: str = "success",
            details: Optional[Dict[str, Any]] = None) -> None:
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "actor": actor,
            "action": action,
            "resource": resource,
            "result": result,
            "details": details or {},
        }
        self._entries.append(entry)
        self._write(entry)

    def query(self, actor: Optional[str] = None,
              action: Optional[str] = None,
              resource: Optional[str] = None,
              limit: int = 100) -> List[Dict[str, Any]]:
        results = self._entries
        if actor:
            results = [e for e in results if e["actor"] == actor]
        if action:
            results = [e for e in results if e["action"] == action]
        if resource:
            results = [e for e in results if e["resource"] == resource]
        return results[-limit:]

    def _write(self, entry: Dict[str, Any]) -> None:
        path = Path(self.output_dir) / "audit.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


class ObservabilityPlatform:
    def __init__(self, config: Optional[ObservabilityConfig] = None):
        self.config = config or ObservabilityConfig()
        self.logger = Logger()
        self.metrics = MetricsCollector()
        self.tracer = Tracer()
        self.alerts = AlertManager()
        self.dashboard = Dashboard()
        self.audit = AuditLogger()

    def health_dashboard(self) -> Dict[str, Any]:
        return {
            "service": "igicu",
            "version": IGICU_VERSION,
            "uptime": time.time(),
            "status": "healthy",
            "metrics": self.metrics.get_metrics(),
        }

    def performance_dashboard(self) -> Dict[str, Any]:
        return self.dashboard.render(self.metrics.get_metrics())
