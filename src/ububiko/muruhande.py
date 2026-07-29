"""muruhande — Offline data support for the UBUBIKO data platform.

Provides offline database, conflict resolution, automatic synchronization,
delta sync, change tracking, and version history.
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class ConflictStrategy(Enum):
    """Strategies for resolving sync conflicts."""

    CLIENT_WINS = "client_wins"
    SERVER_WINS = "server_wins"
    LAST_WRITE_WINS = "last_write_wins"
    MERGE = "merge"
    MANUAL = "manual"


class SyncDirection(Enum):
    """Directions for data synchronization."""

    BIDIRECTIONAL = "bidirectional"
    PUSH_ONLY = "push_only"
    PULL_ONLY = "pull_only"


@dataclass
class ChangeLogEntry:
    """An entry in the change log for sync tracking.

    Attributes:
        id: Unique entry identifier.
        entity_type: Type of entity changed.
        entity_id: ID of the changed entity.
        operation: Operation performed (INSERT, UPDATE, DELETE).
        data: Snapshot of the entity data.
        timestamp: When the change occurred.
        version: Version number of the change.
        synced: Whether the change has been synced.
    """

    id: str = ""
    entity_type: str = ""
    entity_id: str = ""
    operation: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    version: int = 1
    synced: bool = False


@dataclass
class SyncResult:
    """Result of a synchronization operation."""

    pushed: int = 0
    pulled: int = 0
    conflicts: int = 0
    errors: List[str] = field(default_factory=list)
    timestamp: str = ""


class OfflineDatabase:
    """Local database for offline operation.

    Stores data locally and tracks changes for synchronization
    when connectivity is restored.
    """

    def __init__(self, adapter: Any, name: str = "default") -> None:
        self._adapter = adapter
        self._name = name
        self._change_log: List[ChangeLogEntry] = []
        self._lock = threading.Lock()
        self._online: bool = True
        self._version: int = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def adapter(self) -> Any:
        return self._adapter

    @property
    def is_online(self) -> bool:
        return self._online

    @is_online.setter
    def is_online(self, value: bool) -> None:
        self._online = value

    def _next_version(self) -> int:
        self._version += 1
        return self._version

    def execute(self, query: str, params: Dict[str, Any]) -> Any:
        """Execute a query with change tracking."""
        result = self._adapter.execute(query, params)
        operation = query.strip().split()[0].upper()
        if operation in ("INSERT", "UPDATE", "DELETE"):
            self._log_change(operation, query, params)
        return result

    def _log_change(self, operation: str, query: str, params: Dict[str, Any]) -> str:
        entry = ChangeLogEntry(
            id=str(uuid.uuid4()),
            entity_type="",
            entity_id=str(params.get("id", "")),
            operation=operation,
            data={"query": query, "params": params},
            timestamp=datetime.utcnow().isoformat(),
            version=self._next_version(),
            synced=self._online,
        )
        with self._lock:
            self._change_log.append(entry)
        return entry.id

    def get_pending_changes(self) -> List[ChangeLogEntry]:
        """Get unsynced changes."""
        return [e for e in self._change_log if not e.synced]

    def mark_synced(self, change_ids: List[str]) -> None:
        """Mark changes as synced."""
        with self._lock:
            for entry in self._change_log:
                if entry.id in change_ids:
                    entry.synced = True

    def get_change_log(self, since_version: int = 0) -> List[ChangeLogEntry]:
        """Get changes since a version number."""
        return [e for e in self._change_log if e.version > since_version]

    def status(self) -> Dict[str, Any]:
        """Return offline database status."""
        return {
            "name": self._name,
            "online": self._online,
            "pending_changes": len(self.get_pending_changes()),
            "total_changes": len(self._change_log),
            "current_version": self._version,
        }


class ConflictResolver:
    """Resolves conflicts that arise during data synchronization.

    Supports multiple resolution strategies and custom
    merge functions.
    """

    def __init__(self, strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS) -> None:
        self._strategy = strategy
        self._merge_fn: Optional[Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]] = None

    @property
    def strategy(self) -> ConflictStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, value: ConflictStrategy) -> None:
        self._strategy = value

    def set_merge_fn(self, fn: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]) -> None:
        """Set a custom merge function for MERGE strategy."""
        self._merge_fn = fn

    def resolve(self, local_data: Dict[str, Any], remote_data: Dict[str, Any],
                local_version: int = 0, remote_version: int = 0) -> Dict[str, Any]:
        """Resolve a conflict between local and remote data."""
        if self._strategy == ConflictStrategy.CLIENT_WINS:
            return dict(local_data)
        if self._strategy == ConflictStrategy.SERVER_WINS:
            return dict(remote_data)
        if self._strategy == ConflictStrategy.LAST_WRITE_WINS:
            return dict(remote_data if remote_version >= local_version else local_data)
        if self._strategy == ConflictStrategy.MERGE:
            if self._merge_fn:
                return self._merge_fn(local_data, remote_data)
            merged = dict(local_data)
            for k, v in remote_data.items():
                if k not in merged or merged[k] != v:
                    merged[k] = v
            return merged
        raise ValueError(f"Unresolved conflict: {self._strategy.value}")


class DeltaSyncEngine:
    """Delta synchronization engine for efficient data sync.

    Transfers only changed data between local and remote
    stores using version tracking and change logs.
    """

    def __init__(self, local_adapter: Any, remote_adapter: Any,
                 conflict_resolver: Optional[ConflictResolver] = None) -> None:
        self._local = local_adapter
        self._remote = remote_adapter
        self._resolver = conflict_resolver or ConflictResolver()
        self._sync_version: int = 0

    @property
    def local(self) -> Any:
        return self._local

    @property
    def remote(self) -> Any:
        return self._remote

    @property
    def sync_version(self) -> int:
        return self._sync_version

    def sync(self, tables: List[str], direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
             on_conflict: Optional[Callable[[Dict[str, Any]], None]] = None) -> SyncResult:
        """Synchronize data between local and remote stores."""
        result = SyncResult(timestamp=datetime.utcnow().isoformat())

        for table in tables:
            try:
                local_versions = self._get_versions(self._local, table)
                remote_versions = self._get_versions(self._remote, table)

                if direction in (SyncDirection.BIDIRECTIONAL, SyncDirection.PUSH_ONLY):
                    for row_id, version in local_versions.items():
                        remote_ver = remote_versions.get(row_id, 0)
                        if version > remote_ver:
                            local_data = self._get_row(self._local, table, row_id)
                            if local_data:
                                self._upsert(self._remote, table, row_id, local_data)
                                result.pushed += 1
                        elif remote_ver > version:
                            remote_data = self._get_row(self._remote, table, row_id)
                            if remote_data:
                                resolved = self._resolver.resolve(
                                    self._get_row(self._local, table, row_id) or {},
                                    remote_data,
                                    version,
                                    remote_ver,
                                )
                                if on_conflict:
                                    on_conflict(resolved)
                                self._upsert(self._local, table, row_id, resolved)
                                result.conflicts += 1
                                result.pulled += 1

                if direction in (SyncDirection.BIDIRECTIONAL, SyncDirection.PULL_ONLY):
                    for row_id, version in remote_versions.items():
                        if row_id not in local_versions:
                            remote_data = self._get_row(self._remote, table, row_id)
                            if remote_data:
                                self._upsert(self._local, table, row_id, remote_data)
                                result.pulled += 1

            except Exception as e:
                result.errors.append(f"Sync error on {table}: {e}")

        self._sync_version += 1
        return result

    def _get_versions(self, adapter: Any, table: str) -> Dict[str, int]:
        try:
            rows = adapter.execute(f"SELECT id, version FROM {table}", {})
            return {str(r[0]): int(r[1]) for r in rows}
        except Exception:
            return {}

    def _get_row(self, adapter: Any, table: str, row_id: str) -> Optional[Dict[str, Any]]:
        try:
            rows = adapter.execute(f"SELECT * FROM {table} WHERE id = :id", {"id": row_id})
            if rows:
                return dict(rows[0])
        except Exception:
            pass
        return None

    def _upsert(self, adapter: Any, table: str, row_id: str, data: Dict[str, Any]) -> None:
        try:
            existing = adapter.execute(f"SELECT id FROM {table} WHERE id = :id", {"id": row_id})
            if existing:
                set_clause = ", ".join(f"{k} = :{k}" for k in data if k != "id")
                adapter.execute(
                    f"UPDATE {table} SET {set_clause} WHERE id = :id",
                    {**data, "id": row_id},
                )
            else:
                cols = ", ".join(data.keys())
                vals = ", ".join(f":{k}" for k in data)
                adapter.execute(f"INSERT INTO {table} ({cols}) VALUES ({vals})", data)
        except Exception:
            pass


class VersionTracker:
    """Tracks data versioning for audit and rollback.

    Maintains a history of data changes with the ability
    to view and restore previous versions.
    """

    def __init__(self, adapter: Any) -> None:
        self._adapter = adapter
        self._history_table = "_ububiko_version_history"

    def record_version(self, table: str, row_id: str, data: Dict[str, Any],
                       version: int = 1) -> None:
        """Record a version of a data row."""
        self._adapter.execute(
            f"CREATE TABLE IF NOT EXISTS {self._history_table} (\n"
            "  id TEXT,\n"
            "  table_name TEXT,\n"
            "  row_id TEXT,\n"
            "  version INTEGER,\n"
            "  data TEXT,\n"
            "  created_at TEXT\n"
            ")",
            {},
        )
        self._adapter.execute(
            f"INSERT INTO {self._history_table} (id, table_name, row_id, version, data, created_at) "
            "VALUES (:id, :tbl, :rid, :ver, :data, :ts)",
            {
                "id": str(uuid.uuid4()),
                "tbl": table,
                "rid": row_id,
                "ver": version,
                "data": json.dumps(data),
                "ts": datetime.utcnow().isoformat(),
            },
        )

    def get_versions(self, table: str, row_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a data row."""
        try:
            rows = self._adapter.execute(
                f"SELECT version, data, created_at FROM {self._history_table} "
                "WHERE table_name = :tbl AND row_id = :rid ORDER BY version DESC",
                {"tbl": table, "rid": row_id},
            )
            return [{"version": r[0], "data": json.loads(r[1]), "created_at": r[2]} for r in rows]
        except Exception:
            return []

    def restore_version(self, table: str, row_id: str, version: int) -> bool:
        """Restore a specific version of a data row."""
        versions = self.get_versions(table, row_id)
        for v in versions:
            if v["version"] == version:
                data = v["data"]
                set_clause = ", ".join(f"{k} = :{k}" for k in data if k != "id")
                self._adapter.execute(
                    f"UPDATE {table} SET {set_clause} WHERE id = :id",
                    {**data, "id": row_id},
                )
                return True
        return False
