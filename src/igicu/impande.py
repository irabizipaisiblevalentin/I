"""IGICU — Edge Computing: edge nodes, offline sync, geo distribution, edge AI."""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    EdgeNodeConfig, EdgeNodeTier, EdgeError, IGICU_VERSION,
)


class EdgeNode:
    def __init__(self, config: EdgeNodeConfig):
        self.config = config
        self.node_id = config.node_id
        self.status = "online"
        self._storage: Dict[str, Any] = {}
        self._pending_sync: List[Dict[str, Any]] = []
        self._local_models: List[str] = []
        self.started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.last_heartbeat = time.time()
        self._metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "storage_used_mb": 0.0,
            "requests_served": 0,
        }

    def deploy(self, workload: Dict[str, Any]) -> str:
        workload_id = f"wl-{uuid.uuid4().hex[:8]}"
        self._storage[workload_id] = {
            "id": workload_id,
            **workload,
            "deployed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        self._metrics["storage_used_mb"] += 10
        return workload_id

    def remove_workload(self, workload_id: str) -> bool:
        return self._storage.pop(workload_id, None) is not None

    def get_workloads(self) -> List[Dict[str, Any]]:
        return list(self._storage.values())

    def store_local(self, key: str, value: Any) -> None:
        self._storage[key] = value
        self._pending_sync.append({
            "key": key,
            "action": "store",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

    def get_local(self, key: str) -> Optional[Any]:
        return self._storage.get(key)

    def get_pending_sync(self) -> List[Dict[str, Any]]:
        items = list(self._pending_sync)
        self._pending_sync.clear()
        return items

    def sync_complete(self, sync_id: str) -> None:
        pass

    def health(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "tier": self.config.tier.value,
            "status": self.status,
            "uptime_sec": round(time.time() - self.last_heartbeat),
            "workloads": len(self._storage),
            "pending_sync": len(self._pending_sync),
            "metrics": self._metrics,
            "region": self.config.region,
        }

    def load_ai_model(self, model_name: str) -> bool:
        if not self.config.local_ai:
            return False
        self._local_models.append(model_name)
        return True

    def get_ai_models(self) -> List[str]:
        return self._local_models


class EdgeCluster:
    def __init__(self, name: str = "default-edge"):
        self.name = name
        self._nodes: Dict[str, EdgeNode] = {}
        self._regions: Dict[str, List[str]] = {}
        self._sync_queue: List[Dict[str, Any]] = []

    def add_node(self, config: EdgeNodeConfig) -> EdgeNode:
        node = EdgeNode(config)
        self._nodes[node.node_id] = node
        if config.region not in self._regions:
            self._regions[config.region] = []
        self._regions[config.region].append(node.node_id)
        return node

    def remove_node(self, node_id: str) -> bool:
        if node_id in self._nodes:
            node = self._nodes[node_id]
            region = node.config.region
            if region in self._regions and node_id in self._regions[region]:
                self._regions[region].remove(node_id)
            del self._nodes[node_id]
            return True
        return False

    def get_node(self, node_id: str) -> Optional[EdgeNode]:
        return self._nodes.get(node_id)

    def list_nodes(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        if region:
            return [
                self._nodes[nid].health()
                for nid in self._regions.get(region, [])
                if nid in self._nodes
            ]
        return [n.health() for n in self._nodes.values()]

    def get_region(self, region: str) -> Optional[List[EdgeNode]]:
        node_ids = self._regions.get(region)
        if not node_ids:
            return None
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]

    def sync_all(self) -> Dict[str, Any]:
        synced = 0
        for node in self._nodes.values():
            pending = node.get_pending_sync()
            synced += len(pending)
            self._sync_queue.extend(pending)
        return {"nodes": len(self._nodes), "synced_items": synced}

    def regional_failover(self, failed_region: str,
                          target_region: str) -> Dict[str, Any]:
        failed_nodes = self._regions.get(failed_region, [])
        target_nodes = self._regions.get(target_region, [])
        if not target_nodes:
            return {"status": "failed", "reason": "no_target_region"}

        migrated = 0
        for node_id in list(failed_nodes):
            self._nodes[node_id].config.region = target_region
            self._regions[target_region].append(node_id)
            migrated += 1
        self._regions[failed_region] = []

        return {
            "status": "completed",
            "migrated": migrated,
            "from": failed_region,
            "to": target_region,
        }

    def get_edge_metrics(self) -> Dict[str, Any]:
        total_workloads = 0
        total_requests = 0
        for node in self._nodes.values():
            total_workloads += len(node.get_workloads())
            total_requests += node._metrics["requests_served"]
        return {
            "total_nodes": len(self._nodes),
            "regions": list(self._regions.keys()),
            "total_workloads": total_workloads,
            "total_requests": total_requests,
            "pending_sync": len(self._sync_queue),
        }


class OfflineSyncEngine:
    def __init__(self):
        self._sync_log: List[Dict[str, Any]] = []

    def sync(self, node: EdgeNode, target_url: str) -> Dict[str, Any]:
        pending = node.get_pending_sync()
        result = {
            "node_id": node.node_id,
            "synced_items": len(pending),
            "success": True,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        self._sync_log.append(result)
        return result

    def get_sync_history(self, node_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if node_id:
            return [s for s in self._sync_log if s.get("node_id") == node_id]
        return self._sync_log

    def resolve_conflict(self, local_value: Any,
                         remote_value: Any,
                         strategy: str = "last_write_wins") -> Any:
        if strategy == "last_write_wins":
            return remote_value
        elif strategy == "local_wins":
            return local_value
        elif strategy == "merge":
            if isinstance(local_value, dict) and isinstance(remote_value, dict):
                merged = dict(local_value)
                merged.update(remote_value)
                return merged
            return remote_value
        return remote_value


class GeoDistributionManager:
    def __init__(self):
        self._regions: Dict[str, Dict[str, Any]] = {}
        self._routing_table: Dict[str, str] = {}

    def register_region(self, name: str, endpoint: str,
                         latency_ms: float = 0.0) -> None:
        self._regions[name] = {
            "name": name,
            "endpoint": endpoint,
            "latency_ms": latency_ms,
            "healthy": True,
            "registered": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def route_request(self, client_region: str,
                      preferred_region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if preferred_region and preferred_region in self._regions:
            region = self._regions[preferred_region]
            if region["healthy"]:
                return region

        healthy_regions = [
            r for r in self._regions.values()
            if r["healthy"]
        ]
        if not healthy_regions:
            return None
        healthy_regions.sort(key=lambda r: r["latency_ms"])
        return healthy_regions[0]

    def mark_region_unhealthy(self, region_name: str) -> bool:
        region = self._regions.get(region_name)
        if not region:
            return False
        region["healthy"] = False
        return True

    def mark_region_healthy(self, region_name: str) -> bool:
        region = self._regions.get(region_name)
        if not region:
            return False
        region["healthy"] = True
        return True

    def list_regions(self) -> List[Dict[str, Any]]:
        return list(self._regions.values())


class EdgePlatform:
    def __init__(self):
        self.cluster = EdgeCluster()
        self.sync_engine = OfflineSyncEngine()
        self.geo = GeoDistributionManager()
        self._deployed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    def deploy_to_edge(self, workload: Dict[str, Any],
                        region: str = "default") -> List[str]:
        nodes = self.cluster.list_nodes(region=region)
        if not nodes:
            node = self.add_node(EdgeNodeConfig(
                node_id=f"edge-{region}-{uuid.uuid4().hex[:4]}",
                region=region,
            ))
            return [node.deploy(workload)]

        deployed_ids = []
        for node_info in nodes:
            node = self.cluster.get_node(node_info["node_id"])
            if node:
                deployed_ids.append(node.deploy(workload))
        return deployed_ids

    def add_node(self, config: EdgeNodeConfig) -> EdgeNode:
        return self.cluster.add_node(config)

    def get_network_status(self) -> Dict[str, Any]:
        return {
            "edge_cluster": self.cluster.name,
            "nodes": self.cluster.get_edge_metrics(),
            "regions": self.geo.list_regions(),
            "deployed_at": self._deployed_at,
        }
