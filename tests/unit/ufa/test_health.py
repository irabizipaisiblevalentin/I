"""Tests for UFA health monitoring."""

import pytest
from ufa.health import HealthMonitor, HealthStatus, CheckResult


class TestHealthMonitor:
    def test_register_and_check(self):
        hm = HealthMonitor()
        hm.register("db", lambda: True)
        result = hm.check("db")
        assert result.status == HealthStatus.HEALTHY

    def test_check_failing(self):
        hm = HealthMonitor()
        hm.register("db", lambda: False)
        result = hm.check("db")
        assert result.status == HealthStatus.UNHEALTHY

    def test_check_exception(self):
        hm = HealthMonitor()
        hm.register("db", lambda: 1 / 0)
        result = hm.check("db")
        assert result.status == HealthStatus.UNHEALTHY

    def test_report(self):
        hm = HealthMonitor()
        hm.register("a", lambda: True)
        hm.register("b", lambda: True)
        report = hm.report()
        assert report.status == HealthStatus.HEALTHY
        assert len(report.checks) == 2

    def test_report_degraded(self):
        hm = HealthMonitor()
        hm.register("a", lambda: True)
        hm.register("b", lambda: {"status": HealthStatus.DEGRADED, "message": "slow"})
        report = hm.report()
        assert report.status == HealthStatus.DEGRADED

    def test_report_unhealthy(self):
        hm = HealthMonitor()
        hm.register("a", lambda: True)
        hm.register("b", lambda: False)
        report = hm.report()
        assert report.status == HealthStatus.UNHEALTHY

    def test_is_healthy(self):
        hm = HealthMonitor()
        hm.register("a", lambda: True)
        assert hm.is_healthy()

    def test_unregister(self):
        hm = HealthMonitor()
        hm.register("db", lambda: True)
        assert hm.unregister("db")
        assert hm.check_count() == 0

    def test_check_result_dict(self):
        result = CheckResult("test", HealthStatus.HEALTHY, "ok")
        d = result.to_dict()
        assert d["name"] == "test"
        assert d["status"] == "HEALTHY"

    def test_report_to_dict(self):
        hm = HealthMonitor()
        hm.register("x", lambda: True)
        report = hm.report()
        d = report.to_dict()
        assert "status" in d
        assert "checks" in d
        assert "summary" in d

    def test_history(self):
        hm = HealthMonitor()
        hm.register("x", lambda: True)
        hm.report()
        hm.report()
        assert len(hm.history(10)) == 2

    def test_check_latency(self):
        hm = HealthMonitor()
        hm.register("fast", lambda: True)
        result = hm.check("fast")
        assert result.latency_ms >= 0

    def test_check_count(self):
        hm = HealthMonitor()
        hm.register("a", lambda: True)
        hm.register("b", lambda: True)
        assert hm.check_count() == 2
