"""observability — Logging, metrics, and tracing.

Provides structured logging, metric collection, span tracing,
and correlation across distributed operations.
"""

from __future__ import annotations

import enum
import threading
import time
from typing import Any, Callable, Dict, List, Optional


class LogLevel(enum.IntEnum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class SpanState(enum.IntEnum):
    CREATED = 0
    STARTED = 1
    FINISHED = 2
    ERROR = 3


class LogRecord:
    """A structured log entry."""
    __slots__ = ("level", "message", "logger", "timestamp", "data",
                 "correlation_id", "exception")

    def __init__(self, level: LogLevel, message: str, logger: str = "",
                 data: Optional[Dict[str, Any]] = None,
                 correlation_id: str = "",
                 exception: Optional[str] = None) -> None:
        self.level = level
        self.message = message
        self.logger = logger
        self.timestamp = time.time()
        self.data = data or {}
        self.correlation_id = correlation_id
        self.exception = exception


class MetricPoint:
    """A single metric data point."""
    __slots__ = ("name", "value", "metric_type", "tags", "timestamp")

    def __init__(self, name: str, value: float, metric_type: str = "gauge",
                 tags: Optional[Dict[str, str]] = None) -> None:
        self.name = name
        self.value = value
        self.metric_type = metric_type
        self.tags = tags or {}
        self.timestamp = time.time()


class Span:
    """A tracing span representing a unit of work."""
    __slots__ = ("id", "name", "parent_id", "state", "start_time",
                 "end_time", "tags", "logs", "error")

    _counter = 0

    def __init__(self, name: str, parent_id: Optional[str] = None,
                 tags: Optional[Dict[str, str]] = None) -> None:
        Span._counter += 1
        self.id = f"span_{Span._counter}"
        self.name = name
        self.parent_id = parent_id
        self.state = SpanState.CREATED
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.tags = tags or {}
        self.logs: List[LogRecord] = []
        self.error: Optional[str] = None

    @property
    def duration_ms(self) -> float:
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return (end - self.start_time) * 1000

    def start(self) -> None:
        self.start_time = time.time()
        self.state = SpanState.STARTED

    def finish(self, error: Optional[str] = None) -> None:
        self.end_time = time.time()
        if error:
            self.state = SpanState.ERROR
            self.error = error
        else:
            self.state = SpanState.FINISHED

    def log(self, message: str, level: LogLevel = LogLevel.INFO,
            data: Optional[Dict[str, Any]] = None) -> None:
        record = LogRecord(level, message, data=data)
        self.logs.append(record)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "state": self.state.name,
            "duration_ms": self.duration_ms,
            "tags": self.tags,
            "error": self.error,
        }


class Logger:
    """Structured logger with level filtering and handlers."""

    def __init__(self, name: str = "", level: LogLevel = LogLevel.DEBUG) -> None:
        self.name = name
        self.level = level
        self._handlers: List[Callable] = []
        self._records: List[LogRecord] = []
        self._lock = threading.Lock()

    def add_handler(self, handler: Callable) -> None:
        self._handlers.append(handler)

    def log(self, level: LogLevel, message: str,
            data: Optional[Dict[str, Any]] = None,
            correlation_id: str = "",
            exception: Optional[str] = None) -> LogRecord:
        if level < self.level:
            record = LogRecord(level, message, self.name, data,
                               correlation_id, exception)
            return record

        record = LogRecord(level, message, self.name, data,
                           correlation_id, exception)

        with self._lock:
            self._records.append(record)

        for handler in self._handlers:
            try:
                handler(record)
            except Exception:
                pass

        return record

    def debug(self, message: str, **kw: Any) -> LogRecord:
        return self.log(LogLevel.DEBUG, message, kw.get("data"), kw.get("correlation_id", ""))

    def info(self, message: str, **kw: Any) -> LogRecord:
        return self.log(LogLevel.INFO, message, kw.get("data"), kw.get("correlation_id", ""))

    def warning(self, message: str, **kw: Any) -> LogRecord:
        return self.log(LogLevel.WARNING, message, kw.get("data"), kw.get("correlation_id", ""))

    def error(self, message: str, **kw: Any) -> LogRecord:
        return self.log(LogLevel.ERROR, message, kw.get("data"),
                        kw.get("correlation_id", ""), kw.get("exception"))

    def critical(self, message: str, **kw: Any) -> LogRecord:
        return self.log(LogLevel.CRITICAL, message, kw.get("data"),
                        kw.get("correlation_id", ""), kw.get("exception"))

    def records(self, level: Optional[LogLevel] = None,
                limit: int = 100) -> List[LogRecord]:
        recs = self._records
        if level:
            recs = [r for r in recs if r.level >= level]
        return recs[-limit:]


class MetricsCollector:
    """Collects and aggregates metrics."""

    def __init__(self) -> None:
        self._metrics: List[MetricPoint] = []
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        self._lock = threading.Lock()

    def counter(self, name: str, value: float = 1.0,
                tags: Optional[Dict[str, str]] = None) -> None:
        key = f"{name}:{tags}"
        with self._lock:
            self._counters[key] = self._counters.get(key, 0) + value
            self._metrics.append(MetricPoint(name, self._counters[key], "counter", tags))

    def gauge(self, name: str, value: float,
              tags: Optional[Dict[str, str]] = None) -> None:
        with self._lock:
            self._gauges[name] = value
            self._metrics.append(MetricPoint(name, value, "gauge", tags))

    def histogram(self, name: str, value: float,
                  tags: Optional[Dict[str, str]] = None) -> None:
        self._metrics.append(MetricPoint(name, value, "histogram", tags))

    def get_counter(self, name: str,
                    tags: Optional[Dict[str, str]] = None) -> float:
        key = f"{name}:{tags}"
        return self._counters.get(key, 0.0)

    def get_gauge(self, name: str) -> float:
        return self._gauges.get(name, 0.0)

    def recent(self, name: Optional[str] = None,
               limit: int = 100) -> List[MetricPoint]:
        metrics = self._metrics
        if name:
            metrics = [m for m in metrics if m.name == name]
        return metrics[-limit:]

    def clear(self) -> None:
        with self._lock:
            self._metrics.clear()
            self._counters.clear()
            self._gauges.clear()


class Tracer:
    """Distributed tracing with span management."""

    def __init__(self) -> None:
        self._spans: Dict[str, Span] = {}
        self._active_span_id: Optional[str] = None
        self._lock = threading.Lock()

    def start_span(self, name: str, tags: Optional[Dict[str, str]] = None) -> Span:
        parent_id = self._active_span_id
        span = Span(name, parent_id, tags)
        span.start()

        with self._lock:
            self._spans[span.id] = span
            self._active_span_id = span.id

        return span

    def finish_span(self, span: Span, error: Optional[str] = None) -> None:
        span.finish(error)
        with self._lock:
            if self._active_span_id == span.id:
                self._active_span_id = span.parent_id

    def get_span(self, span_id: str) -> Optional[Span]:
        return self._spans.get(span_id)

    def active_span(self) -> Optional[Span]:
        if self._active_span_id:
            return self._spans.get(self._active_span_id)
        return None

    def completed_spans(self) -> List[Span]:
        return [s for s in self._spans.values() if s.state in (SpanState.FINISHED, SpanState.ERROR)]

    def all_spans(self) -> List[Span]:
        return list(self._spans.values())

    def clear(self) -> None:
        with self._lock:
            self._spans.clear()
            self._active_span_id = None
