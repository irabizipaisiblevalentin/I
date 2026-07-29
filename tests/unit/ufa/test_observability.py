"""Tests for UFA observability (logging, metrics, tracing)."""

import pytest
from ufa.observability import (
    Logger, MetricsCollector, Tracer,
    LogLevel, SpanState
)


class TestLogger:
    def test_log_levels(self):
        log = Logger("test")
        log.debug("d")
        log.info("i")
        log.warning("w")
        log.error("e")
        log.critical("c")
        assert len(log.records()) == 5

    def test_level_filter(self):
        log = Logger("test", LogLevel.WARNING)
        log.debug("d")
        log.info("i")
        log.warning("w")
        log.error("e")
        assert len(log.records()) == 2

    def test_handler(self):
        log = Logger("test")
        received = []
        log.add_handler(lambda r: received.append(r.message))
        log.info("hello")
        assert received == ["hello"]

    def test_records_filtered(self):
        log = Logger("test")
        log.info("a")
        log.error("b")
        assert len(log.records(level=LogLevel.ERROR)) == 1

    def test_correlation_id(self):
        log = Logger("test")
        r = log.info("msg", correlation_id="abc123")
        assert r.correlation_id == "abc123"


class TestMetricsCollector:
    def test_counter(self):
        m = MetricsCollector()
        m.counter("requests")
        m.counter("requests")
        assert m.get_counter("requests") == 2.0

    def test_gauge(self):
        m = MetricsCollector()
        m.gauge("temperature", 25.5)
        assert m.get_gauge("temperature") == 25.5

    def test_histogram(self):
        m = MetricsCollector()
        m.histogram("latency", 100.0)
        recent = m.recent("latency")
        assert len(recent) == 1

    def test_clear(self):
        m = MetricsCollector()
        m.counter("x")
        m.gauge("y", 1)
        m.clear()
        assert m.get_counter("x") == 0.0


class TestTracer:
    def test_start_finish_span(self):
        t = Tracer()
        span = t.start_span("op1")
        assert span.state == SpanState.STARTED
        t.finish_span(span)
        assert span.state == SpanState.FINISHED
        assert span.duration_ms >= 0

    def test_parent_child(self):
        t = Tracer()
        s1 = t.start_span("parent")
        s2 = t.start_span("child")
        assert s2.parent_id == s1.id
        t.finish_span(s2)
        t.finish_span(s1)

    def test_error_span(self):
        t = Tracer()
        span = t.start_span("fail")
        t.finish_span(span, error="boom")
        assert span.state == SpanState.ERROR
        assert span.error == "boom"

    def test_active_span(self):
        t = Tracer()
        span = t.start_span("active")
        assert t.active_span() is span
        t.finish_span(span)
        assert t.active_span() is None

    def test_completed_spans(self):
        t = Tracer()
        s1 = t.start_span("a")
        t.finish_span(s1)
        s2 = t.start_span("b")
        assert len(t.completed_spans()) == 1

    def test_span_log(self):
        t = Tracer()
        span = t.start_span("log_test")
        span.log("step1")
        assert len(span.logs) == 1

    def test_span_to_dict(self):
        t = Tracer()
        span = t.start_span("dict_test")
        d = span.to_dict()
        assert d["name"] == "dict_test"
        assert "id" in d

    def test_clear(self):
        t = Tracer()
        t.start_span("x")
        t.clear()
        assert len(t.all_spans()) == 0
