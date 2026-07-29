"""ikwirakwira — Distributed data support for the UBUBIKO data platform.

Provides replication, sharding, partitioning, read replicas,
high availability, failover, distributed transactions,
and consensus integration.
"""

from __future__ import annotations

import enum
import json
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple


class ReplicationRole(enum.Enum):
    """Roles in a replication setup."""

    PRIMARY = "primary"
    REPLICA = "replica"
    STANDBY = "standby"


class ShardStrategy(enum.Enum):
    """Sharding strategies."""

    HASH = "hash"
    RANGE = "range"
    LIST = "list"
    ROUND_ROBIN = "round_robin"


class ConsistencyLevel(enum.Enum):
    """Consistency levels for distributed operations."""

    EVENTUAL = "eventual"
    CAUSAL = "causal"
    LINEARIZABLE = "linearizable"


@dataclass
class ReplicationConfig:
    """Configuration for database replication.

    Attributes:
        role: Role of this node.
        primary_host: Primary node hostname.
        primary_port: Primary node port.
        sync_mode: Synchronous or asynchronous replication.
        sync_interval: Sync interval in seconds (async mode).
        replicas: List of replica endpoints.
        failover_enabled: Whether automatic failover is enabled.
        health_check_interval: Health check interval in seconds.
    """

    role: ReplicationRole = ReplicationRole.PRIMARY
    primary_host: str = ""
    primary_port: int = 0
    sync_mode: str = "async"
    sync_interval: int = 5
    replicas: List[str] = field(default_factory=list)
    failover_enabled: bool = True
    health_check_interval: int = 10


@dataclass
class ReplicationEvent:
    """An event in the replication log."""

    id: str = ""
    timestamp: str = ""
    operation: str = ""
    table: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = ""


class Replicator:
    """Handles data replication across database nodes.

    Maintains a change log, propagates changes to replicas,
    and manages consistency.
    """

    def __init__(self, config: Optional[ReplicationConfig] = None) -> None:
        self._config = config or ReplicationConfig()
        self._change_log: List[ReplicationEvent] = []
        self._lock = threading.Lock()
        self._running = False
        self._last_sync: float = 0.0

    @property
    def config(self) -> ReplicationConfig:
        return self._config

    @property
    def change_log(self) -> List[ReplicationEvent]:
        return list(self._change_log)

    def record_change(self, table: str, operation: str, data: Dict[str, Any]) -> str:
        """Record a data change for replication."""
        event = ReplicationEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            operation=operation,
            table=table,
            data=data,
            source=f"{self._config.role.value}",
        )
        with self._lock:
            self._change_log.append(event)
        return event.id

    def get_pending_changes(self, since: str = "") -> List[ReplicationEvent]:
        """Get pending changes since a given timestamp."""
        if not since:
            return list(self._change_log)
        return [e for e in self._change_log if e.timestamp >= since]

    def propagate(self, adapter: Any) -> int:
        """Propagate pending changes to replicas."""
        pending = self.get_pending_changes()
        count = 0
        with self._lock:
            for event in pending:
                try:
                    if event.operation == "INSERT":
                        adapter.execute(
                            f"INSERT INTO {event.table} ({', '.join(event.data.keys())}) "
                            f"VALUES ({', '.join(f':{k}' for k in event.data)})",
                            event.data,
                        )
                    elif event.operation == "UPDATE":
                        set_clause = ", ".join(f"{k} = :{k}" for k in event.data if k != "id")
                        adapter.execute(
                            f"UPDATE {event.table} SET {set_clause} WHERE id = :id",
                            event.data,
                        )
                    elif event.operation == "DELETE":
                        adapter.execute(
                            f"DELETE FROM {event.table} WHERE id = :id",
                            {"id": event.data.get("id")},
                        )
                    count += 1
                except Exception:
                    pass
        return count

    def health_check(self) -> bool:
        """Check replication health."""
        now = time.time()
        if now - self._last_sync > self._config.health_check_interval:
            return False
        return True

    def status(self) -> Dict[str, Any]:
        """Return replication status."""
        return {
            "role": self._config.role.value,
            "change_log_size": len(self._change_log),
            "replicas": self._config.replicas,
            "sync_mode": self._config.sync_mode,
            "healthy": self.health_check(),
        }


@dataclass
class ShardConfig:
    """Configuration for a shard.

    Attributes:
        id: Shard identifier.
        host: Shard database host.
        port: Shard database port.
        database: Shard database name.
        range_start: Start of range (range strategy).
        range_end: End of range (range strategy).
        weight: Relative weight for hash distribution.
    """

    id: str = ""
    host: str = "localhost"
    port: int = 0
    database: str = ""
    range_start: str = ""
    range_end: str = ""
    weight: int = 1


class ShardManager:
    """Manages horizontal sharding across database nodes.

    Routes queries to the appropriate shard based on
    configurable strategies.
    """

    def __init__(self, strategy: ShardStrategy = ShardStrategy.HASH) -> None:
        self._strategy = strategy
        self._shards: Dict[str, ShardConfig] = {}
        self._shard_keys: List[str] = []

    @property
    def strategy(self) -> ShardStrategy:
        return self._strategy

    @property
    def shards(self) -> Dict[str, ShardConfig]:
        return dict(self._shards)

    def add_shard(self, config: ShardConfig) -> None:
        """Register a shard."""
        self._shards[config.id] = config
        self._shard_keys = list(self._shards.keys())
        self._shard_keys.sort()

    def remove_shard(self, shard_id: str) -> None:
        """Remove a shard."""
        self._shards.pop(shard_id, None)
        self._shard_keys = list(self._shards.keys())

    def get_shard_for(self, key: Any) -> Optional[ShardConfig]:
        """Determine which shard holds data for a given key."""
        if not self._shards:
            return None
        if self._strategy == ShardStrategy.HASH:
            idx = hash(str(key)) % len(self._shard_keys)
            return self._shards.get(self._shard_keys[idx])
        if self._strategy == ShardStrategy.ROUND_ROBIN:
            idx = int(time.time()) % len(self._shard_keys)
            return self._shards.get(self._shard_keys[idx])
        if self._strategy == ShardStrategy.RANGE:
            str_key = str(key)
            for shard_key in self._shard_keys:
                shard = self._shards[shard_key]
                if shard.range_start <= str_key <= shard.range_end:
                    return shard
                if not shard.range_start and not shard.range_end:
                    return shard
        return None

    def distribute(self, data: List[Tuple[Any, Any]]) -> Dict[str, List[Tuple[Any, Any]]]:
        """Distribute key-value pairs across shards."""
        result: Dict[str, List[Tuple[Any, Any]]] = {s: [] for s in self._shard_keys}
        for key, value in data:
            shard = self.get_shard_for(key)
            if shard:
                result[shard.id].append((key, value))
        return result

    def status(self) -> Dict[str, Any]:
        """Return sharding status."""
        return {
            "strategy": self._strategy.value,
            "shard_count": len(self._shards),
            "shards": list(self._shards.keys()),
        }


class DistributedTransaction:
    """Distributed transaction coordinator (XA-like).

    Supports two-phase commit across multiple database nodes
    with prepare, commit, and rollback phases.
    """

    def __init__(self, transaction_id: str = "") -> None:
        self._transaction_id = transaction_id or str(uuid.uuid4())
        self._participants: List[Dict[str, Any]] = []
        self._state: str = "init"
        self._lock = threading.Lock()

    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    @property
    def state(self) -> str:
        return self._state

    def add_participant(self, name: str, adapter: Any) -> None:
        """Register a transaction participant."""
        self._participants.append({"name": name, "adapter": adapter, "prepared": False})

    def begin(self) -> None:
        """Begin the distributed transaction."""
        self._state = "active"

    def prepare(self) -> bool:
        """Phase 1: Prepare all participants."""
        self._state = "preparing"
        all_prepared = True
        for p in self._participants:
            try:
                p["adapter"].begin()
                p["prepared"] = True
            except Exception:
                all_prepared = False
                p["prepared"] = False
        self._state = "prepared" if all_prepared else "failed"
        return all_prepared

    def commit(self) -> bool:
        """Phase 2: Commit all participants."""
        if self._state != "prepared":
            raise RuntimeError(f"Cannot commit in state: {self._state}")
        self._state = "committing"
        all_committed = True
        for p in self._participants:
            if p["prepared"]:
                try:
                    p["adapter"].commit()
                except Exception:
                    all_committed = False
        self._state = "committed" if all_committed else "partial"
        return all_committed

    def rollback(self) -> bool:
        """Rollback all participants."""
        self._state = "rolling_back"
        all_rolled = True
        for p in self._participants:
            if p["prepared"]:
                try:
                    p["adapter"].rollback()
                except Exception:
                    all_rolled = False
        self._state = "rolled_back" if all_rolled else "partial_rollback"
        return all_rolled

    def execute(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute a function within the distributed transaction."""
        try:
            self.begin()
            if self.prepare():
                result = fn(*args, **kwargs)
                self.commit()
                return result
            else:
                self.rollback()
                raise RuntimeError("Distributed transaction prepare failed")
        except Exception:
            self.rollback()
            raise


class ReadReplicaManager:
    """Manages read replicas for load distribution.

    Routes read queries to replicas and write queries to primary.
    """

    def __init__(self, primary: Any, replicas: Optional[List[Any]] = None) -> None:
        self._primary = primary
        self._replicas = replicas or []
        self._current_replica: int = 0

    @property
    def primary(self) -> Any:
        return self._primary

    @property
    def replicas(self) -> List[Any]:
        return list(self._replicas)

    def add_replica(self, adapter: Any) -> None:
        self._replicas.append(adapter)

    def get_reader(self) -> Any:
        """Get a replica for read operations (round-robin)."""
        if not self._replicas:
            return self._primary
        reader = self._replicas[self._current_replica % len(self._replicas)]
        self._current_replica += 1
        return reader

    def get_writer(self) -> Any:
        """Get the primary for write operations."""
        return self._primary

    def execute_read(self, query: str, params: Dict[str, Any]) -> Any:
        """Execute a read query on a replica."""
        reader = self.get_reader()
        return reader.execute(query, params)

    def execute_write(self, query: str, params: Dict[str, Any]) -> Any:
        """Execute a write query on the primary."""
        return self._primary.execute(query, params)
