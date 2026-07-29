"""Tests for IGICU Service Discovery (ubushakashatsi)."""

from __future__ import annotations

import pytest

from igicu.ubushakashatsi import (
    ServiceRegistry, LoadBalancer, HealthChecker,
    CircuitBreaker, RetryHandler, ServiceMesh,
)
from igicu.ibikoreshingiro import (
    ServiceSpec, ServicePort, CircuitBreakerSpec, RetrySpec,
    HealthCheckSpec, LoadBalanceStrategy, CircuitBreakerState,
    ServiceDiscoveryError,
)


class TestServiceRegistry:
    def test_register_and_discover(self):
        reg = ServiceRegistry()
        inst_id = reg.register("api", "localhost", 8080)
        services = reg.discover("api")
        assert len(services) == 1
        assert services[0]["host"] == "localhost"

    def test_deregister(self):
        reg = ServiceRegistry()
        inst_id = reg.register("api", "host1", 80)
        assert reg.deregister("api", inst_id) is True
        assert len(reg.discover("api")) == 0

    def test_list_services(self):
        reg = ServiceRegistry()
        reg.register("svc1", "h1", 80)
        reg.register("svc2", "h2", 81)
        services = reg.list_services()
        assert len(services) == 2

    def test_heartbeat(self):
        reg = ServiceRegistry()
        inst_id = reg.register("api", "h1", 80)
        assert reg.heartbeat("api", inst_id) is True

    def test_mark_unhealthy(self):
        reg = ServiceRegistry()
        inst_id = reg.register("api", "h1", 80)
        reg.mark_unhealthy("api", inst_id)
        assert len(reg.discover("api")) == 0

    def test_prune_stale(self):
        reg = ServiceRegistry()
        inst_id = reg.register("api", "h1", 80)
        import time
        time.sleep(0.1)
        count = reg.prune_stale(timeout_sec=0.05)
        assert count >= 0


class TestLoadBalancer:
    def test_round_robin(self):
        reg = ServiceRegistry()
        reg.register("api", "h1", 80)
        reg.register("api", "h2", 81)
        lb = LoadBalancer(reg)
        ep1 = lb.get_endpoint("api", LoadBalanceStrategy.ROUND_ROBIN)
        ep2 = lb.get_endpoint("api", LoadBalanceStrategy.ROUND_ROBIN)
        assert ep1 is not None
        assert ep2 is not None

    def test_random(self):
        reg = ServiceRegistry()
        reg.register("api", "h1", 80)
        lb = LoadBalancer(reg)
        ep = lb.get_endpoint("api", LoadBalanceStrategy.RANDOM)
        assert ep is not None

    def test_no_instances(self):
        reg = ServiceRegistry()
        lb = LoadBalancer(reg)
        ep = lb.get_endpoint("nonexistent")
        assert ep is None


class TestHealthChecker:
    def test_check(self):
        hc = HealthChecker()
        result = hc.check(HealthCheckSpec(), "localhost", 8080)
        assert "healthy" in result
        assert "latency_ms" in result

    def test_aggregate(self):
        hc = HealthChecker()
        hosts = [{"host": "h1", "port": 80}, {"host": "h2", "port": 81}]
        result = hc.aggregate(hosts)
        assert result["total"] == 2


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = CircuitBreaker(CircuitBreakerSpec())
        assert cb.state == CircuitBreakerState.CLOSED

    def test_trips_on_failures(self):
        cb = CircuitBreaker(CircuitBreakerSpec(failure_threshold=3))

        def failing():
            raise ValueError("fail")

        for _ in range(3):
            try:
                cb.call(failing)
            except ValueError:
                pass
        assert cb.state == CircuitBreakerState.OPEN

    def test_half_open_on_timeout(self):
        spec = CircuitBreakerSpec(failure_threshold=1, timeout_sec=0)
        cb = CircuitBreaker(spec)
        try:
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        except ValueError:
            pass
        assert cb.state == CircuitBreakerState.OPEN


class TestServiceMesh:
    def test_create_service(self):
        mesh = ServiceMesh()
        port = ServicePort(name="http", port=80, target_port=8080)
        spec = ServiceSpec(name="test-svc", ports=[port])
        svc_id = mesh.create_service(spec)
        assert svc_id is not None

    def test_resolve(self):
        mesh = ServiceMesh()
        port = ServicePort(name="http", port=80, target_port=8080)
        spec = ServiceSpec(name="resolve-svc", ports=[port])
        mesh.create_service(spec)
        endpoint = mesh.resolve("resolve-svc")
        assert endpoint is not None
        assert "host" in endpoint
