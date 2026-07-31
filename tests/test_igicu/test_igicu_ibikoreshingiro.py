"""Tests for IGICU core types (ibikoreshingiro)."""

from __future__ import annotations

import pytest

from igicu.ibikoreshingiro import (
    ContainerStatus, ScalingPolicy, UpdateStrategy, NodeStatus,
    HealthStatus, LoadBalanceStrategy, DeliveryGuarantee,
    LogLevel, AuthMethod, ContainerConfig, ClusterSpec,
    DeploymentSpec, HealthCheckSpec, ScalingSpec,
    FunctionSpec, TriggerSpec, ServiceSpec, ServicePort,
    CircuitBreakerSpec, RetrySpec, MessageQueueSpec,
    TopicSpec, ObservabilityConfig, SecurityConfig,
    EdgeNodeConfig, ClusterInfo, DeploymentInfo,
    IgicuError, ContainerError, ClusterError,
    IGICU_VERSION,
)


class TestEnums:
    def test_container_status_values(self):
        assert ContainerStatus.RUNNING.value == "running"
        assert ContainerStatus.CREATED.value == "created"
        assert ContainerStatus.FAILED.value == "failed"

    def test_scaling_policy_values(self):
        assert ScalingPolicy.HORIZONTAL.value == "horizontal"
        assert ScalingPolicy.PREDICTIVE.value == "predictive"

    def test_update_strategy_values(self):
        assert UpdateStrategy.BLUE_GREEN.value == "blue_green"
        assert UpdateStrategy.CANARY.value == "canary"

    def test_load_balance_strategy_values(self):
        assert LoadBalanceStrategy.ROUND_ROBIN.value == "round_robin"
        assert LoadBalanceStrategy.CONSISTENT_HASH.value == "consistent_hash"

    def test_delivery_guarantee_values(self):
        assert DeliveryGuarantee.EXACTLY_ONCE.value == "exactly_once"

    def test_log_level_values(self):
        assert LogLevel.ERROR.value == "error"
        assert LogLevel.TRACE.value == "trace"

    def test_auth_method_values(self):
        assert AuthMethod.MTLS.value == "mtls"
        assert AuthMethod.OIDC.value == "oidc"


class TestDataclasses:
    def test_container_config_defaults(self):
        config = ContainerConfig(image="nginx:latest", name="web")
        assert config.image == "nginx:latest"
        assert config.memory_limit == "256m"
        assert config.cpu_limit == "0.5"
        assert config.restart_policy == "always"
        assert config.network == "bridge"

    def test_cluster_spec_defaults(self):
        spec = ClusterSpec(name="prod")
        assert spec.name == "prod"
        assert spec.namespace == "default"
        assert spec.node_count == 1
        assert spec.version == "1.0.0"

    def test_deployment_spec_with_ports(self):
        spec = DeploymentSpec(
            name="api", image="api:v1", replicas=3,
            ports={"http": 8080},
        )
        assert spec.name == "api"
        assert spec.replicas == 3
        assert spec.ports["http"] == 8080

    def test_health_check_spec_defaults(self):
        hc = HealthCheckSpec()
        assert hc.path == "/health"
        assert hc.port == 8080
        assert hc.interval_sec == 10
        assert hc.healthy_threshold == 2

    def test_scaling_spec_defaults(self):
        sc = ScalingSpec()
        assert sc.min_replicas == 1
        assert sc.max_replicas == 10
        assert sc.target_cpu == 80.0

    def test_function_spec(self):
        spec = FunctionSpec(name="my-func", memory_mb=256, timeout_sec=60)
        assert spec.name == "my-func"
        assert spec.memory_mb == 256
        assert spec.timeout_sec == 60

    def test_service_spec_with_ports(self):
        port = ServicePort(name="http", port=80, target_port=3000)
        spec = ServiceSpec(name="web", ports=[port])
        assert spec.name == "web"
        assert spec.ports[0].target_port == 3000

    def test_circuit_breaker_spec_defaults(self):
        cb = CircuitBreakerSpec()
        assert cb.failure_threshold == 5
        assert cb.timeout_sec == 30

    def test_retry_spec_defaults(self):
        r = RetrySpec()
        assert r.max_retries == 3
        assert r.backoff_sec == 1.0

    def test_topic_spec_defaults(self):
        t = TopicSpec(name="events")
        assert t.partitions == 1
        assert t.replication_factor == 2
        assert t.retention_hours == 168

    def test_observability_config_defaults(self):
        o = ObservabilityConfig()
        assert o.log_level == LogLevel.INFO
        assert o.metrics_enabled is True
        assert o.tracing_enabled is True

    def test_security_config_defaults(self):
        s = SecurityConfig()
        assert s.auth_method == AuthMethod.JWT
        assert s.tls_enabled is True
        assert s.encryption_enabled is True

    def test_edge_node_config_defaults(self):
        e = EdgeNodeConfig(node_id="edge-1", region="us-east")
        assert e.storage_gb == 100
        assert e.memory_gb == 4
        assert e.offline_sync is True


class TestConstants:
    def test_version(self):
        assert IGICU_VERSION == "0.1.0"


class TestErrors:
    def test_igicu_error(self):
        with pytest.raises(IgicuError):
            raise IgicuError("base error")

    def test_container_error(self):
        with pytest.raises(ContainerError):
            raise ContainerError("container error")

    def test_cluster_error(self):
        with pytest.raises(ClusterError):
            raise ClusterError("cluster error")
