"""Tests for istudio.ibikoresho_igicu — Cloud Tools."""

from __future__ import annotations

from src.istudio.ibikoresho_igicu import CloudExplorer


def test_cloud_explorer_init():
    ce = CloudExplorer()
    assert ce.list_providers() == []
    assert ce.list_deployments() == []


def test_register_provider():
    ce = CloudExplorer()
    name = ce.register_provider("my-cloud", "igicu", {"region": "us-east"})
    assert name == "my-cloud"
    providers = ce.list_providers()
    assert len(providers) == 1
    assert providers[0]["type"] == "igicu"
    assert providers[0]["connected"] is True


def test_list_resources():
    ce = CloudExplorer()
    ce.register_provider("my-cloud")
    providers = ce.list_providers()
    assert any(p["name"] == "my-cloud" for p in providers)
    resources = ce.list_resources()
    assert "my-cloud" in resources
    assert resources["my-cloud"] == []


def test_add_resource():
    ce = CloudExplorer()
    ce.register_provider("my-cloud")
    ce.add_resource("my-cloud", {"type": "vm", "name": "web-1"})
    resources = ce.list_resources("my-cloud")
    assert len(resources) == 1


def test_deploy():
    ce = CloudExplorer()
    ce.register_provider("my-cloud")
    dep = ce.deploy("my-app", "my-cloud", {"image": "nginx"})
    assert dep["name"] == "my-app"
    assert dep["status"] == "deployed"
    assert "endpoint" in dep


def test_get_deployment():
    ce = CloudExplorer()
    ce.register_provider("my-cloud")
    ce.deploy("my-app", "my-cloud", {})
    dep = ce.get_deployment("my-app")
    assert dep is not None
    assert dep["name"] == "my-app"
    assert ce.get_deployment("nonexistent") is None


def test_list_deployments():
    ce = CloudExplorer()
    ce.register_provider("c1")
    ce.register_provider("c2")
    ce.deploy("app1", "c1", {})
    ce.deploy("app2", "c2", {})
    assert len(ce.list_deployments()) == 2


def test_undeploy():
    ce = CloudExplorer()
    ce.register_provider("c1")
    ce.deploy("my-app", "c1", {})
    assert ce.undeploy("my-app") is True
    assert ce.undeploy("my-app") is False


def test_get_logs():
    ce = CloudExplorer()
    ce.register_provider("c1")
    ce.deploy("my-app", "c1", {})
    logs = ce.get_logs("my-app", lines=5)
    assert len(logs) <= 5


def test_get_metrics():
    ce = CloudExplorer()
    ce.register_provider("c1")
    ce.deploy("my-app", "c1", {})
    metrics = ce.get_metrics("my-app")
    assert "cpu_usage" in metrics
    assert "memory_usage" in metrics
    assert "requests_per_second" in metrics


def test_run_command():
    ce = CloudExplorer()
    ce.register_provider("c1")
    result = ce.run_command("c1", "ls -la")
    assert "exit_code" in result
    assert result["exit_code"] == 0


def test_resource_isolation():
    ce = CloudExplorer()
    ce.register_provider("p1")
    ce.register_provider("p2")
    ce.add_resource("p1", {"name": "r1"})
    p1_resources = ce.list_resources("p1")
    p2_resources = ce.list_resources("p2")
    assert len(p1_resources["p1"]) == 1
    assert len(p2_resources["p2"]) == 0
