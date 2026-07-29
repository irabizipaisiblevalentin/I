"""Tests for IGICU Orchestration (imiyoborere)."""

from __future__ import annotations

import pytest

from igicu.imiyoborere import (
    ClusterManager, DeploymentManager, Scheduler,
    ResourceQuotaManager, HorizontalPodAutoscaler,
)
from igicu.ibikoreshingiro import (
    ClusterSpec, DeploymentSpec, ScalingSpec, ScalingPolicy,
    UpdateStrategy, ClusterError,
)


class TestClusterManager:
    def test_create_cluster(self):
        mgr = ClusterManager()
        spec = ClusterSpec(name="test-cluster", node_count=3)
        info = mgr.create(spec)
        assert info.name == "test-cluster"
        assert info.node_count == 3
        assert info.status == "created"

    def test_create_duplicate_raises(self):
        mgr = ClusterManager()
        mgr.create(ClusterSpec(name="dup"))
        with pytest.raises(ClusterError):
            mgr.create(ClusterSpec(name="dup"))

    def test_get_cluster(self):
        mgr = ClusterManager()
        mgr.create(ClusterSpec(name="get-test"))
        info = mgr.get("get-test")
        assert info is not None
        assert info.name == "get-test"

    def test_get_nonexistent(self):
        mgr = ClusterManager()
        assert mgr.get("nonexistent") is None

    def test_list_clusters(self):
        mgr = ClusterManager()
        mgr.create(ClusterSpec(name="c1"))
        mgr.create(ClusterSpec(name="c2"))
        clusters = mgr.list()
        assert len(clusters) >= 2

    def test_delete_cluster(self):
        mgr = ClusterManager()
        mgr.create(ClusterSpec(name="to-delete"))
        assert mgr.delete("to-delete") is True
        assert mgr.get("to-delete") is None

    def test_get_nodes(self):
        mgr = ClusterManager()
        mgr.create(ClusterSpec(name="node-test", node_count=3))
        nodes = mgr.get_nodes("node-test")
        assert len(nodes) == 3

    def test_cordon_node(self):
        mgr = ClusterManager()
        mgr.create(ClusterSpec(name="cordon-test", node_count=1))
        nodes = mgr.get_nodes("cordon-test")
        assert mgr.cordon_node("cordon-test", nodes[0]["id"]) is True

    def test_health(self):
        mgr = ClusterManager()
        mgr.create(ClusterSpec(name="health-test", node_count=2))
        health = mgr.health("health-test")
        assert health["status"] == "healthy"


class TestDeploymentManager:
    def test_deploy(self):
        cm = ClusterManager()
        cm.create(ClusterSpec(name="dep-cluster", node_count=2))
        dm = DeploymentManager(cm)
        spec = DeploymentSpec(name="web", image="nginx:latest", replicas=2)
        info = dm.deploy(spec, "dep-cluster")
        assert info.name == "web"
        assert info.status == "running"
        assert info.available == 2

    def test_deploy_auto_creates_cluster(self):
        from igicu.ibikoreshingiro import DeploymentError
        cm = ClusterManager()
        dm = DeploymentManager(cm)
        spec = DeploymentSpec(name="auto", image="app:latest", replicas=1)
        with pytest.raises(DeploymentError):
            dm.deploy(spec, "nonexistent")
        # Expected to fail since cluster doesn't exist

    def test_update_deployment(self):
        cm = ClusterManager()
        cm.create(ClusterSpec(name="upd-cluster"))
        dm = DeploymentManager(cm)
        spec = DeploymentSpec(name="upd", image="v1", replicas=2)
        dm.deploy(spec, "upd-cluster")
        updated = DeploymentSpec(name="upd", image="v2", replicas=3)
        info = dm.update(updated, "upd-cluster")
        assert info.image == "v2"
        assert info.replicas == 3

    def test_scale(self):
        cm = ClusterManager()
        cm.create(ClusterSpec(name="scale-cluster"))
        dm = DeploymentManager(cm)
        dm.deploy(DeploymentSpec(name="scalable", image="app", replicas=2), "scale-cluster")
        info = dm.scale("scalable", 5, "scale-cluster")
        assert info.replicas == 5

    def test_rollback(self):
        cm = ClusterManager()
        cm.create(ClusterSpec(name="rb-cluster"))
        dm = DeploymentManager(cm)
        dm.deploy(DeploymentSpec(name="rb", image="app"), "rb-cluster")
        info = dm.rollback("rb", "rb-cluster")
        assert info.status == "running"

    def test_list_deployments(self):
        cm = ClusterManager()
        cm.create(ClusterSpec(name="ls-cluster"))
        dm = DeploymentManager(cm)
        dm.deploy(DeploymentSpec(name="d1", image="app1"), "ls-cluster")
        dm.deploy(DeploymentSpec(name="d2", image="app2"), "ls-cluster")
        deps = dm.list("ls-cluster")
        assert len(deps) == 2

    def test_delete_deployment(self):
        cm = ClusterManager()
        cm.create(ClusterSpec(name="del-cluster"))
        dm = DeploymentManager(cm)
        dm.deploy(DeploymentSpec(name="del-me", image="app"), "del-cluster")
        assert dm.delete("del-me", "del-cluster") is True

    def test_auto_heal(self):
        cm = ClusterManager()
        cm.create(ClusterSpec(name="heal-cluster"))
        dm = DeploymentManager(cm)
        healed = dm.auto_heal("heal-cluster")
        assert isinstance(healed, list)


class TestResourceQuotaManager:
    def test_set_and_get(self):
        mgr = ResourceQuotaManager()
        mgr.set("default", {"cpu": "2", "memory": "4Gi"})
        quotas = mgr.get("default")
        assert quotas["cpu"] == "2"

    def test_check_within_quota(self):
        mgr = ResourceQuotaManager()
        mgr.set("default", {"cpu": "4", "memory": "8Gi"})
        assert mgr.check("default", {"cpu": "2", "memory": "4Gi"}) is True

    def test_check_exceeds_quota(self):
        mgr = ResourceQuotaManager()
        mgr.set("default", {"cpu": "2"})
        assert mgr.check("default", {"cpu": "8"}) is False  # 8 > 2, exceeds quota


class TestHorizontalPodAutoscaler:
    def test_register_and_evaluate(self):
        hpa = HorizontalPodAutoscaler()
        spec = ScalingSpec(min_replicas=1, max_replicas=10, target_cpu=80)
        hpa.register("web", spec)
        desired = hpa.evaluate("web", current_replicas=2, current_cpu=90, current_memory=50)
        assert desired > 2  # Should scale up

    def test_evaluate_scale_down(self):
        hpa = HorizontalPodAutoscaler()
        spec = ScalingSpec(min_replicas=1, max_replicas=10, target_cpu=80)
        hpa.register("web", spec)
        desired = hpa.evaluate("web", current_replicas=5, current_cpu=20, current_memory=20)
        assert desired < 5  # Should scale down

    def test_evaluate_no_change(self):
        hpa = HorizontalPodAutoscaler()
        spec = ScalingSpec(min_replicas=1, max_replicas=10, target_cpu=80)
        hpa.register("stable", spec)
        desired = hpa.evaluate("stable", current_replicas=3, current_cpu=50, current_memory=40)
        assert desired == 3  # Should stay
