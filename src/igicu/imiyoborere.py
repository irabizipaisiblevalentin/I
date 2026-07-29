"""IGICU — Orchestration: cluster management, scheduling, deployments, scaling."""

from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    ClusterInfo, ClusterSpec, DeploymentInfo, DeploymentSpec,
    HealthCheckSpec, HealthStatus, NodeStatus, ScalingPolicy,
    ScalingSpec, UpdateStrategy, WorkloadType,
    ClusterError, DeploymentError, IGICU_VERSION,
)


class Node:
    def __init__(self, node_id: str, host: str = "localhost", port: int = 0):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.status = NodeStatus.READY
        self.labels: Dict[str, str] = {}
        self.capacity: Dict[str, str] = {"cpu": "4", "memory": "8Gi", "pods": "110"}
        self.allocated: Dict[str, str] = {"cpu": "0", "memory": "0Gi", "pods": "0"}
        self.conditions: List[str] = ["Ready"]
        self.joined: str = time.strftime("%Y-%m-%dT%H:%M:%SZ")


class ClusterManager:
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.join(
            os.path.expanduser("~"), ".igicu", "clusters"
        )
        self._clusters: Dict[str, ClusterInfo] = {}
        self._nodes: Dict[str, Dict[str, Node]] = {}
        self._load_state()

    def create(self, spec: ClusterSpec) -> ClusterInfo:
        if spec.name in self._clusters:
            raise ClusterError(f"Cluster '{spec.name}' already exists")

        info = ClusterInfo(
            name=spec.name,
            namespace=spec.namespace,
            node_count=spec.node_count,
            version=spec.version,
            status="created",
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            health="unknown",
        )
        self._clusters[spec.name] = info
        self._nodes[spec.name] = {}
        for i in range(spec.node_count):
            node = Node(f"{spec.name}-node-{i}", f"node{i}.{spec.name}.local", 6443 + i)
            self._nodes[spec.name][node.node_id] = node
        self._save_cluster(info)
        return info

    def get(self, name: str) -> Optional[ClusterInfo]:
        return self._clusters.get(name)

    def list(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": c.name,
                "namespace": c.namespace,
                "nodes": c.node_count,
                "status": c.status,
                "health": c.health,
                "version": c.version,
                "deployments": c.deployments,
                "services": c.services,
                "created": c.created_at,
            }
            for c in self._clusters.values()
        ]

    def delete(self, name: str) -> bool:
        if name in self._clusters:
            del self._clusters[name]
            self._nodes.pop(name, None)
            self._remove_cluster_state(name)
            return True
        return False

    def get_nodes(self, cluster_name: str) -> List[Dict[str, Any]]:
        nodes = self._nodes.get(cluster_name, {})
        return [
            {
                "id": n.node_id,
                "host": n.host,
                "status": n.status.value,
                "capacity": n.capacity,
                "allocated": n.allocated,
                "conditions": n.conditions,
                "joined": n.joined,
            }
            for n in nodes.values()
        ]

    def get_node(self, cluster_name: str, node_id: str) -> Optional[Dict[str, Any]]:
        node = self._nodes.get(cluster_name, {}).get(node_id)
        if not node:
            return None
        return {
            "id": node.node_id,
            "host": node.host,
            "status": node.status.value,
            "capacity": node.capacity,
            "allocated": node.allocated,
        }

    def cordon_node(self, cluster_name: str, node_id: str) -> bool:
        node = self._nodes.get(cluster_name, {}).get(node_id)
        if not node:
            return False
        node.status = NodeStatus.CORDONED
        return True

    def uncordon_node(self, cluster_name: str, node_id: str) -> bool:
        node = self._nodes.get(cluster_name, {}).get(node_id)
        if not node:
            return False
        node.status = NodeStatus.READY
        return True

    def drain_node(self, cluster_name: str, node_id: str) -> bool:
        node = self._nodes.get(cluster_name, {}).get(node_id)
        if not node:
            return False
        node.status = NodeStatus.DRAINING
        return True

    def health(self, name: str) -> Dict[str, Any]:
        cluster = self._clusters.get(name)
        if not cluster:
            raise ClusterError(f"Cluster '{name}' not found")
        nodes = self._nodes.get(name, {})
        healthy = sum(1 for n in nodes.values() if n.status == NodeStatus.READY)
        total = len(nodes)
        return {
            "cluster": name,
            "status": "healthy" if healthy == total else "degraded",
            "nodes": {"total": total, "healthy": healthy, "unhealthy": total - healthy},
            "conditions": ["AllNodesReady"] if healthy == total else ["SomeNodesNotReady"],
        }

    def _save_cluster(self, info: ClusterInfo) -> None:
        path = Path(self.data_dir) / info.name / "cluster.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "name": info.name,
            "namespace": info.namespace,
            "node_count": info.node_count,
            "version": info.version,
            "status": info.status,
            "created_at": info.created_at,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _remove_cluster_state(self, name: str) -> None:
        path = Path(self.data_dir) / name
        if path.exists():
            import shutil
            shutil.rmtree(path)

    def _load_state(self) -> None:
        base = Path(self.data_dir)
        if not base.exists():
            return
        for cluster_dir in base.iterdir():
            if not cluster_dir.is_dir():
                continue
            meta_path = cluster_dir / "cluster.json"
            if not meta_path.exists():
                continue
            try:
                data = json.loads(meta_path.read_text(encoding="utf-8"))
                info = ClusterInfo(
                    name=data["name"],
                    namespace=data.get("namespace", "default"),
                    node_count=data.get("node_count", 1),
                    version=data.get("version", "1.0.0"),
                    status=data.get("status", "created"),
                    created_at=data.get("created_at", ""),
                )
                self._clusters[info.name] = info
                self._nodes[info.name] = {}
                for i in range(info.node_count):
                    node = Node(
                        f"{info.name}-node-{i}",
                        f"node{i}.{info.name}.local",
                        6443 + i,
                    )
                    self._nodes[info.name][node.node_id] = node
            except (json.JSONDecodeError, KeyError):
                continue


class Scheduler:
    def __init__(self, cluster_manager: ClusterManager):
        self.cluster = cluster_manager

    def schedule(self, cluster_name: str, deployment: DeploymentSpec) -> str:
        nodes = self.cluster.get_nodes(cluster_name)
        if not nodes:
            raise ClusterError(f"No nodes available in cluster '{cluster_name}'")

        target_replicas = deployment.replicas
        scheduled = []
        node_list = list(self.cluster._nodes.get(cluster_name, {}).values())
        for i in range(target_replicas):
            node = node_list[i % len(node_list)]
            scheduled.append(node.node_id)
            cpu_str = node.allocated["cpu"]
            if cpu_str.endswith("cpu"):
                cpu_val = float(cpu_str.replace("cpu", ""))
            elif cpu_str.endswith("m"):
                cpu_val = float(cpu_str.rstrip("m")) / 1000
            else:
                cpu_val = float(cpu_str)
            node.allocated["cpu"] = f"{cpu_val + 0.5}cpu"
            mem_str = node.allocated["memory"]
            if mem_str.endswith("Gi"):
                mem_val = int(mem_str.rstrip("Gi")) * 1024
            elif mem_str.endswith("Mi"):
                mem_val = int(mem_str.rstrip("Mi"))
            else:
                mem_val = int(mem_str)
            node.allocated["memory"] = f"{mem_val + 256}Mi"
        return ",".join(scheduled)

    def scale(self, cluster_name: str, deployment_name: str,
              replicas: int) -> int:
        current_nodes = self.cluster.get_nodes(cluster_name)
        if not current_nodes:
            return 0
        return replicas


class DeploymentManager:
    def __init__(self, cluster_manager: ClusterManager):
        self.cluster = cluster_manager
        self._deployments: Dict[str, Dict[str, DeploymentInfo]] = {}
        self.scheduler = Scheduler(cluster_manager)

    def deploy(self, spec: DeploymentSpec, cluster_name: str = "default") -> DeploymentInfo:
        cluster = self.cluster.get(cluster_name)
        if not cluster:
            raise DeploymentError(f"Cluster '{cluster_name}' not found")

        if cluster_name not in self._deployments:
            self._deployments[cluster_name] = {}

        if spec.name in self._deployments.get(cluster_name, {}):
            return self.update(spec, cluster_name)

        scheduled_nodes = self.scheduler.schedule(cluster_name, spec)
        info = DeploymentInfo(
            name=spec.name,
            image=spec.image,
            replicas=spec.replicas,
            available=0,
            status="deploying",
            strategy=spec.update_strategy.value,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            updated_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self._deployments[cluster_name][spec.name] = info

        if spec.health_check:
            self._simulate_health_check(spec, info)

        info.status = "running"
        info.available = spec.replicas
        cluster.deployments += 1
        return info

    def update(self, spec: DeploymentSpec, cluster_name: str = "default") -> DeploymentInfo:
        deps = self._deployments.get(cluster_name, {})
        info = deps.get(spec.name)
        if not info:
            raise DeploymentError(f"Deployment '{spec.name}' not found")

        old_image = info.image
        info.image = spec.image
        info.replicas = spec.replicas
        info.strategy = spec.update_strategy.value
        info.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")

        if spec.update_strategy == UpdateStrategy.ROLLING_UPDATE:
            for i in range(spec.replicas):
                time.sleep(0.1)
                info.available = i + 1
        elif spec.update_strategy == UpdateStrategy.BLUE_GREEN:
            info.status = "blue_green_deploying"
            time.sleep(0.3)
            info.available = spec.replicas
        elif spec.update_strategy == UpdateStrategy.CANARY:
            info.status = "canary_deploying"
            time.sleep(0.2)
            info.available = spec.replicas

        info.status = "running"
        return info

    def scale(self, name: str, replicas: int,
              cluster_name: str = "default") -> DeploymentInfo:
        deps = self._deployments.get(cluster_name, {})
        info = deps.get(name)
        if not info:
            raise DeploymentError(f"Deployment '{name}' not found")
        info.replicas = replicas
        info.available = replicas
        info.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        return info

    def rollback(self, name: str, cluster_name: str = "default") -> DeploymentInfo:
        deps = self._deployments.get(cluster_name, {})
        info = deps.get(name)
        if not info:
            raise DeploymentError(f"Deployment '{name}' not found")
        info.status = "rollback"
        info.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        time.sleep(0.1)
        info.status = "running"
        return info

    def get(self, name: str, cluster_name: str = "default") -> Optional[DeploymentInfo]:
        return self._deployments.get(cluster_name, {}).get(name)

    def list(self, cluster_name: str = "default") -> List[Dict[str, Any]]:
        deps = self._deployments.get(cluster_name, {})
        return [
            {
                "name": d.name,
                "image": d.image,
                "replicas": d.replicas,
                "available": d.available,
                "status": d.status,
                "strategy": d.strategy,
                "created_at": d.created_at,
            }
            for d in deps.values()
        ]

    def delete(self, name: str, cluster_name: str = "default") -> bool:
        deps = self._deployments.get(cluster_name, {})
        if name in deps:
            cluster = self.cluster.get(cluster_name)
            if cluster:
                cluster.deployments = max(0, cluster.deployments - 1)
            del deps[name]
            return True
        return False

    def auto_heal(self, cluster_name: str = "default") -> List[Dict[str, Any]]:
        healed = []
        deps = self._deployments.get(cluster_name, {})
        for name, info in deps.items():
            if info.available < info.replicas:
                info.available = info.replicas
                info.status = "healed"
                healed.append({"name": name, "action": "restarted_unhealthy_pods"})
        return healed

    def _simulate_health_check(self, spec: DeploymentSpec, info: DeploymentInfo) -> None:
        check = spec.health_check or HealthCheckSpec()
        time.sleep(0.05)
        info.status = "healthy"

    def get_deployment_count(self, cluster_name: str) -> int:
        return len(self._deployments.get(cluster_name, {}))


class ResourceQuotaManager:
    def __init__(self):
        self._quotas: Dict[str, Dict[str, str]] = {}

    def set(self, namespace: str, quotas: Dict[str, str]) -> None:
        self._quotas[namespace] = quotas

    def get(self, namespace: str) -> Dict[str, str]:
        return self._quotas.get(namespace, {})

    def check(self, namespace: str, requested: Dict[str, str]) -> bool:
        quotas = self._quotas.get(namespace, {})
        if not quotas:
            return True
        for key, value in requested.items():
            if key in quotas:
                req_val = self._parse_quantity(value)
                quota_val = self._parse_quantity(quotas[key])
                if req_val > quota_val:
                    return False
        return True

    def _parse_quantity(self, q: str) -> float:
        if q.endswith("Gi"):
            return float(q[:-2]) * 1024
        if q.endswith("Mi"):
            return float(q[:-2])
        if q.endswith("m"):
            return float(q[:-1]) / 1000
        return float(q)


class HorizontalPodAutoscaler:
    def __init__(self):
        self._scaling_rules: Dict[str, ScalingSpec] = {}

    def register(self, deployment: str, spec: ScalingSpec) -> None:
        self._scaling_rules[deployment] = spec

    def evaluate(self, deployment: str, current_replicas: int,
                 current_cpu: float, current_memory: float) -> int:
        spec = self._scaling_rules.get(deployment)
        if not spec:
            return current_replicas

        desired = current_replicas
        if current_cpu > spec.target_cpu or current_memory > spec.target_memory:
            desired = min(int(current_replicas * 1.5), spec.max_replicas)
        elif current_cpu < spec.target_cpu * 0.5 and current_memory < spec.target_memory * 0.5:
            desired = max(int(current_replicas * 0.75), spec.min_replicas)

        return max(spec.min_replicas, min(desired, spec.max_replicas))
