"""Integration tests for IGICU — cross-module workflows."""

from __future__ import annotations

import pytest

from igicu.imiyoborere import ClusterManager, DeploymentManager, ClusterSpec, DeploymentSpec
from igicu.ikorwa import ContainerRuntime, ContainerConfig
from igicu.ibikoresho import ServerlessPlatform, FunctionSpec
from igicu.ubushakashatsi import ServiceMesh, ServiceSpec, ServicePort
from igicu.ubutumwa import MessagingPlatform, TopicSpec
from igicu.umutekano import IdentityManager
from igicu.ibirebana import ObservabilityPlatform


class TestClusterToDeploymentWorkflow:
    def test_full_workflow(self):
        cm = ClusterManager()
        spec = ClusterSpec(name="integration-cluster", node_count=3)
        cluster = cm.create(spec)
        assert cluster.status == "created"

        dm = DeploymentManager(cm)
        dep_spec = DeploymentSpec(name="web-app", image="nginx:latest", replicas=3)
        deploy = dm.deploy(dep_spec, "integration-cluster")
        assert deploy.status == "running"
        assert deploy.available == 3

        scaled = dm.scale("web-app", 5, "integration-cluster")
        assert scaled.replicas == 5

        info = dm.get("web-app", "integration-cluster")
        assert info is not None
        assert info.name == "web-app"

        cm.delete("integration-cluster")


class TestServerlessWithMessaging:
    def test_function_event_flow(self):
        platform = ServerlessPlatform()
        spec = FunctionSpec(name="order-processor", memory_mb=256)
        platform.create_function(spec)

        msg = MessagingPlatform()
        msg.create_topic(TopicSpec(name="orders", partitions=2))

        result = platform.invoke("order-processor", {"order_id": "123"})
        assert result["status"] == "success"


class TestSecurityWithServiceMesh:
    def test_secure_service_workflow(self):
        identity = IdentityManager()
        user_id = identity.create_user("deployer", "secret", ["admin"])
        assert user_id is not None

        token = identity.authenticate("deployer", "secret")
        assert token is not None

        validated = identity.validate_token(token)
        assert validated is not None
        assert "admin" in validated["roles"]

        mesh = ServiceMesh()
        port = ServicePort(name="grpc", port=50051, target_port=50051)
        spec = ServiceSpec(name="secure-svc", ports=[port])
        mesh.create_service(spec)

        endpoint = mesh.resolve("secure-svc")
        assert endpoint is not None


class TestObservabilityWorkflow:
    def test_logging_metrics_tracing(self):
        obs = ObservabilityPlatform()

        obs.logger.info("app started", {"version": "1.0"})
        obs.metrics.increment("requests", 10)
        obs.metrics.set_gauge("connections", 42)

        span_id = obs.tracer.start_span("request-handler")
        obs.tracer.end_span(span_id)

        health = obs.health_dashboard()
        assert health["status"] == "healthy"

        trace_stats = obs.tracer.get_statistics()
        assert trace_stats["completed_spans"] >= 1


class TestContainerWithServiceDiscovery:
    def test_container_service_workflow(self):
        runtime = ContainerRuntime()

        config = ContainerConfig(
            image="my-app:latest",
            name="web-server",
            ports={8080: 8080},
            environment={"MODE": "production"},
        )
        cid = runtime.create(config)
        runtime.start(cid)

        container = runtime.get(cid)
        assert container["status"] == "running"

        mesh = ServiceMesh()
        port = ServicePort(name="http", port=80, target_port=8080)
        spec = ServiceSpec(name="web", ports=[port])
        mesh.create_service(spec)

        runtime.stop(cid)
        runtime.remove(cid)
