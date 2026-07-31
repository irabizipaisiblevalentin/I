"""Tests for IGICU Edge Computing (impande)."""

from __future__ import annotations

import pytest

from igicu.impande import (
    EdgeNode, EdgeCluster, OfflineSyncEngine,
    GeoDistributionManager, EdgePlatform,
)
from igicu.ibikoreshingiro import EdgeNodeConfig, EdgeNodeTier


class TestEdgeNode:
    def test_create_node(self):
        config = EdgeNodeConfig(node_id="node-1", region="us-east",
                                 tier=EdgeNodeTier.STANDARD)
        node = EdgeNode(config)
        assert node.node_id == "node-1"
        assert node.status == "online"

    def test_deploy_workload(self):
        node = EdgeNode(EdgeNodeConfig(node_id="w1", region="default"))
        wl_id = node.deploy({"type": "inference", "model": "v1"})
        assert wl_id is not None
        workloads = node.get_workloads()
        assert len(workloads) == 1

    def test_remove_workload(self):
        node = EdgeNode(EdgeNodeConfig(node_id="w2", region="default"))
        wl_id = node.deploy({"type": "web"})
        assert node.remove_workload(wl_id) is True

    def test_local_storage(self):
        node = EdgeNode(EdgeNodeConfig(node_id="s1", region="default"))
        node.store_local("key1", "value1")
        assert node.get_local("key1") == "value1"

    def test_pending_sync(self):
        node = EdgeNode(EdgeNodeConfig(node_id="sync1", region="default"))
        node.store_local("k", "v")
        pending = node.get_pending_sync()
        assert len(pending) == 1

    def test_health(self):
        node = EdgeNode(EdgeNodeConfig(node_id="h1", region="us"))
        health = node.health()
        assert health["node_id"] == "h1"
        assert health["status"] == "online"

    def test_load_ai_model(self):
        config = EdgeNodeConfig(node_id="ai-node", region="default", local_ai=True)
        node = EdgeNode(config)
        assert node.load_ai_model("llama-v2") is True
        assert "llama-v2" in node.get_ai_models()

    def test_ai_model_not_available(self):
        config = EdgeNodeConfig(node_id="no-ai", region="default", local_ai=False)
        node = EdgeNode(config)
        assert node.load_ai_model("model") is False


class TestEdgeCluster:
    def test_add_node(self):
        cluster = EdgeCluster("test")
        config = EdgeNodeConfig(node_id="n1", region="us-east")
        node = cluster.add_node(config)
        assert node.node_id == "n1"
        assert len(cluster.list_nodes()) == 1

    def test_remove_node(self):
        cluster = EdgeCluster()
        cluster.add_node(EdgeNodeConfig(node_id="n1", region="r1"))
        assert cluster.remove_node("n1") is True
        assert len(cluster.list_nodes()) == 0

    def test_get_node(self):
        cluster = EdgeCluster()
        cluster.add_node(EdgeNodeConfig(node_id="get-me", region="r1"))
        node = cluster.get_node("get-me")
        assert node is not None

    def test_list_nodes_by_region(self):
        cluster = EdgeCluster()
        cluster.add_node(EdgeNodeConfig(node_id="a", region="us"))
        cluster.add_node(EdgeNodeConfig(node_id="b", region="eu"))
        us_nodes = cluster.list_nodes(region="us")
        assert len(us_nodes) == 1

    def test_sync_all(self):
        cluster = EdgeCluster()
        node = cluster.add_node(EdgeNodeConfig(node_id="sync", region="r1"))
        node.store_local("k", "v")
        result = cluster.sync_all()
        assert result["synced_items"] == 1

    def test_regional_failover(self):
        cluster = EdgeCluster()
        cluster.add_node(EdgeNodeConfig(node_id="n1", region="primary"))
        cluster.add_node(EdgeNodeConfig(node_id="n2", region="backup"))
        result = cluster.regional_failover("primary", "backup")
        assert result["status"] == "completed"


class TestGeoDistributionManager:
    def test_register_region(self):
        geo = GeoDistributionManager()
        geo.register_region("us-east", "us-east.api.igicu.io", 10)
        regions = geo.list_regions()
        assert len(regions) == 1

    def test_route_request(self):
        geo = GeoDistributionManager()
        geo.register_region("us", "us.api", 5)
        geo.register_region("eu", "eu.api", 20)
        target = geo.route_request("us")
        assert target is not None

    def test_mark_unhealthy(self):
        geo = GeoDistributionManager()
        geo.register_region("us", "us.api", 10)
        geo.mark_region_unhealthy("us")
        target = geo.route_request("us")
        assert target is None or target["name"] != "us"

    def test_preferred_region(self):
        geo = GeoDistributionManager()
        geo.register_region("us", "us.api", 10)
        geo.register_region("eu", "eu.api", 5)
        target = geo.route_request("us", preferred_region="eu")
        assert target["name"] == "eu"


class TestEdgePlatform:
    def test_deploy_to_edge(self):
        platform = EdgePlatform()
        ids = platform.deploy_to_edge({"type": "video-processor"}, region="us")
        assert len(ids) >= 1

    def test_add_node(self):
        platform = EdgePlatform()
        config = EdgeNodeConfig(node_id="edge-1", region="global")
        node = platform.add_node(config)
        assert node.node_id == "edge-1"

    def test_get_network_status(self):
        platform = EdgePlatform()
        status = platform.get_network_status()
        assert "edge_cluster" in status
        assert "nodes" in status
