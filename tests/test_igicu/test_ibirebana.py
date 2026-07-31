"""Tests for IGICU Observability (ibirebana)."""

from __future__ import annotations

import pytest

from igicu.ibirebana import (
    Logger, MetricsCollector, Tracer, AlertManager,
    Dashboard, AuditLogger, ObservabilityPlatform,
)
from igicu.ibikoreshingiro import LogLevel, AlertSeverity


class TestLogger:
    def test_info_log(self):
        logger = Logger("test", LogLevel.INFO)
        logger.info("test message", {"key": "value"})
        entries = logger.get_entries()
        assert len(entries) >= 1
        assert entries[-1]["level"] == "info"
        assert entries[-1]["message"] == "test message"

    def test_error_log(self):
        logger = Logger("test", LogLevel.ERROR)
        logger.error("error occurred")
        entries = logger.get_entries()
        assert len(entries) >= 1
        assert entries[-1]["level"] == "error"

    def test_level_filtering(self):
        logger = Logger("filter", LogLevel.WARN)
        logger.trace("should not appear")
        logger.warn("warning message")
        entries = logger.get_entries()
        assert all(e["level"] in ("warn", "error", "fatal") for e in entries)

    def test_multiple_levels(self):
        logger = Logger("multi", LogLevel.DEBUG)
        logger.debug("debug")
        logger.info("info")
        logger.warn("warn")
        entries = logger.get_entries()
        levels = [e["level"] for e in entries]
        assert "debug" in levels
        assert "info" in levels
        assert "warn" in levels


class TestMetricsCollector:
    def test_increment(self):
        mc = MetricsCollector()
        mc.increment("requests")
        mc.increment("requests")
        metrics = mc.get_metrics()
        assert metrics["counter_requests"] == 2

    def test_decrement(self):
        mc = MetricsCollector()
        mc.increment("active")
        mc.decrement("active")
        metrics = mc.get_metrics()
        assert metrics["counter_active"] == 0

    def test_gauge(self):
        mc = MetricsCollector()
        mc.set_gauge("temperature", 36.5)
        metrics = mc.get_metrics()
        assert metrics["gauge_temperature"] == 36.5

    def test_histogram(self):
        mc = MetricsCollector()
        mc.observe("latency", 10)
        mc.observe("latency", 20)
        mc.observe("latency", 30)
        metrics = mc.get_metrics()
        assert metrics["histogram_latency_count"] == 3
        assert metrics["histogram_latency_avg"] == 20.0

    def test_timer(self):
        mc = MetricsCollector()
        with mc.time("operation"):
            pass
        metrics = mc.get_metrics()
        assert metrics["timer_operation_count"] >= 1

    def test_reset(self):
        mc = MetricsCollector()
        mc.increment("test", 5)
        mc.reset()
        metrics = mc.get_metrics()
        assert len(metrics) == 0


class TestTracer:
    def test_start_and_end_span(self):
        tracer = Tracer("test-svc")
        span_id = tracer.start_span("operation")
        assert span_id is not None
        tracer.end_span(span_id)
        stats = tracer.get_statistics()
        assert stats["completed_spans"] >= 1

    def test_trace_correlation(self):
        tracer = Tracer("svc")
        span1 = tracer.start_span("parent")
        span2 = tracer.start_span("child", parent_id=span1)
        tracer.end_span(span2)
        tracer.end_span(span1)
        trace = tracer.get_trace(tracer.get_recent()[0]["trace_id"])
        assert len(trace) == 2


class TestAlertManager:
    def test_add_rule(self):
        am = AlertManager()
        rule_id = am.add_rule("high-cpu", "cpu > 90%", AlertSeverity.CRITICAL)
        assert rule_id is not None
        assert len(am.list_rules()) == 1

    def test_trigger_alert(self):
        am = AlertManager()
        rule_id = am.add_rule("test", "x > 5", AlertSeverity.WARNING)
        alert = am.trigger(rule_id, 10)
        assert alert["severity"] == "warning"

    def test_acknowledge(self):
        am = AlertManager()
        rule_id = am.add_rule("r", "x > 0", AlertSeverity.INFO)
        alert = am.trigger(rule_id)
        assert am.acknowledge(alert["id"]) is True

    def test_resolve(self):
        am = AlertManager()
        rule_id = am.add_rule("r", "x > 0", AlertSeverity.INFO)
        alert = am.trigger(rule_id)
        assert am.resolve(alert["id"]) is True


class TestDashboard:
    def test_add_panel(self):
        d = Dashboard("test")
        panel_id = d.add_panel("CPU", "cpu_usage", "gauge")
        assert panel_id is not None

    def test_render(self):
        d = Dashboard("test")
        d.add_panel("CPU", "cpu_usage")
        rendered = d.render({"cpu_usage": 75.5})
        assert rendered["name"] == "test"
        assert len(rendered["panels"]) == 1


class TestObservabilityPlatform:
    def test_health_dashboard(self):
        op = ObservabilityPlatform()
        health = op.health_dashboard()
        assert health["status"] == "healthy"
        assert health["service"] == "igicu"

    def test_performance_dashboard(self):
        op = ObservabilityPlatform()
        perf = op.performance_dashboard()
        assert "panels" in perf
