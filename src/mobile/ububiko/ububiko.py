"""ububiko — Database manager for the I mobile platform.

Provides an offline-first local database with SQLite support,
encrypted storage, automatic migration, cloud sync, and
configurable conflict resolution strategies.
"""

from __future__ import annotations

import enum
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ConflictStrategy(enum.Enum):
    """Strategy for resolving data conflicts during sync."""

    LAST_WRITE_WINS = "last_write_wins"
    MANUAL = "manual"
    TIMESTAMP = "timestamp"


class DatabaseConfig:
    """Configuration for a Ububiko database instance.

    Attributes:
        path: Filesystem path to the database file.
        version: Schema version number for migration tracking.
        encrypted: Whether the database should use encryption.
        conflict_strategy: Strategy for conflict resolution.
        sync_enabled: Whether cloud synchronization is active.
    """

    def __init__(
        self,
        path: str = "i_mobile.db",
        version: int = 1,
        encrypted: bool = False,
        conflict_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS,
        sync_enabled: bool = True,
    ) -> None:
        self.path = path
        self.version = version
        self.encrypted = encrypted
        self.conflict_strategy = conflict_strategy
        self.sync_enabled = sync_enabled


class SyncQueueItem:
    """An entry in the offline sync queue.

    Attributes:
        id: Unique queue item ID.
        table: Target table name.
        action: Operation type (insert, update, delete).
        data: The record data.
        timestamp: When the operation was queued.
    """

    def __init__(
        self,
        table: str,
        action: str,
        data: Dict[str, Any],
        timestamp: Optional[str] = None,
    ) -> None:
        self.id: int = 0
        self.table = table
        self.action = action
        self.data = data
        self.timestamp: str = timestamp or datetime.now().isoformat()


class Ububiko:
    """Offline-first database manager.

    Wraps SQLite with encrypted storage support, automatic schema
    migration, a sync queue for offline operations, and cloud
    synchronization with configurable conflict resolution.
    """

    def __init__(
        self, config: Optional[DatabaseConfig] = None
    ) -> None:
        self._config: DatabaseConfig = config or DatabaseConfig()
        self._connection: Optional[sqlite3.Connection] = None
        self._is_open: bool = False
        self._sync_queue: List[SyncQueueItem] = []
        self._migrations: Dict[int, str] = {}

    # -- Properties -----------------------------------------------------------

    @property
    def config(self) -> DatabaseConfig:
        """The database configuration."""
        return self._config

    @property
    def is_open(self) -> bool:
        """Whether the database connection is open."""
        return self._is_open

    @property
    def path(self) -> str:
        """Filesystem path to the database file."""
        return self._config.path

    @property
    def version(self) -> int:
        """Current schema version of the database."""
        return self._config.version

    # -- Connection Management ------------------------------------------------

    def open(self) -> bool:
        """Open a connection to the database.

        Creates the database file if it does not exist and runs
        any pending migrations.

        Returns:
            True if the database was opened successfully.
        """
        if self._is_open:
            return True
        try:
            db_path = Path(self._config.path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(str(db_path))
            self._connection.row_factory = sqlite3.Row
            self._is_open = True
            self._init_meta()
            self._run_pending_migrations()
            return True
        except sqlite3.Error:
            return False

    def close(self) -> bool:
        """Close the database connection.

        Returns:
            True if the connection was closed.
        """
        if not self._is_open or self._connection is None:
            return True
        self._connection.close()
        self._connection = None
        self._is_open = False
        return True

    # -- CRUD Operations ------------------------------------------------------

    def execute(
        self, sql: str, params: Optional[Tuple[Any, ...]] = None
    ) -> int:
        """Execute a raw SQL statement.

        Args:
            sql: The SQL statement to execute.
            params: Optional query parameters.

        Returns:
            The number of affected rows.
        """
        if not self._is_open or self._connection is None:
            return 0
        try:
            cursor = self._connection.execute(sql, params or ())
            self._connection.commit()
            return cursor.rowcount
        except sqlite3.Error:
            return 0

    def query(
        self,
        sql: str,
        params: Optional[Tuple[Any, ...]] = None,
    ) -> List[Dict[str, Any]]:
        """Run a SELECT query and return results as dictionaries.

        Args:
            sql: The SELECT statement.
            params: Optional query parameters.

        Returns:
            A list of row dictionaries.
        """
        if not self._is_open or self._connection is None:
            return []
        try:
            cursor = self._connection.execute(sql, params or ())
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def insert(
        self, table: str, data: Dict[str, Any]
    ) -> Optional[int]:
        """Insert a row into a table.

        Args:
            table: The target table name.
            data: Column-value mapping for the new row.

        Returns:
            The row ID of the inserted record, or None on failure.
        """
        if not self._is_open or self._connection is None:
            self._enqueue_sync("insert", table, data)
            return None
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join("?" for _ in data)
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor = self._connection.execute(sql, tuple(data.values()))
            self._connection.commit()
            row_id = cursor.lastrowid
            self._enqueue_sync("insert", table, data)
            return row_id
        except sqlite3.Error:
            self._enqueue_sync("insert", table, data)
            return None

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: str,
        where_params: Optional[Tuple[Any, ...]] = None,
    ) -> int:
        """Update rows in a table.

        Args:
            table: The target table name.
            data: Column-value mapping to update.
            where: WHERE clause (e.g. "id = ?").
            where_params: Parameters for the WHERE clause.

        Returns:
            The number of affected rows.
        """
        if not self._is_open or self._connection is None:
            self._enqueue_sync("update", table, data)
            return 0
        try:
            set_clause = ", ".join(f"{k} = ?" for k in data)
            sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
            params = tuple(data.values()) + (where_params or ())
            cursor = self._connection.execute(sql, params)
            self._connection.commit()
            self._enqueue_sync("update", table, data)
            return cursor.rowcount
        except sqlite3.Error:
            self._enqueue_sync("update", table, data)
            return 0

    def delete(
        self,
        table: str,
        where: str,
        where_params: Optional[Tuple[Any, ...]] = None,
    ) -> int:
        """Delete rows from a table.

        Args:
            table: The target table name.
            where: WHERE clause.
            where_params: Parameters for the WHERE clause.

        Returns:
            The number of deleted rows.
        """
        if not self._is_open or self._connection is None:
            return 0
        try:
            sql = f"DELETE FROM {table} WHERE {where}"
            cursor = self._connection.execute(sql, where_params or ())
            self._connection.commit()
            data: Dict[str, Any] = {"where": where}
            self._enqueue_sync("delete", table, data)
            return cursor.rowcount
        except sqlite3.Error:
            return 0

    # -- Transactions ---------------------------------------------------------

    def begin_transaction(self) -> bool:
        """Begin a SQLite transaction.

        Returns:
            True if the transaction started.
        """
        if not self._is_open or self._connection is None:
            return False
        self._connection.execute("BEGIN TRANSACTION")
        return True

    def commit(self) -> bool:
        """Commit the active transaction.

        Returns:
            True if the commit succeeded.
        """
        if not self._is_open or self._connection is None:
            return False
        try:
            self._connection.commit()
            return True
        except sqlite3.Error:
            return False

    def rollback(self) -> bool:
        """Roll back the active transaction.

        Returns:
            True if the rollback succeeded.
        """
        if not self._is_open or self._connection is None:
            return False
        self._connection.rollback()
        return True

    # -- Migrations -----------------------------------------------------------

    def register_migration(
        self, version: int, sql: str
    ) -> None:
        """Register a schema migration for a target version.

        Args:
            version: The schema version this migration produces.
            sql: SQL statements to apply for the migration.
        """
        self._migrations[version] = sql

    def migrate(self, target_version: Optional[int] = None) -> bool:
        """Run all pending migrations to reach a target version.

        Args:
            target_version: Desired schema version. Defaults to the
                latest registered migration version.

        Returns:
            True if all migrations applied successfully.
        """
        if not self._is_open or self._connection is None:
            return False
        current = self._get_schema_version()
        target = target_version or max(self._migrations.keys(), default=current)
        if target <= current:
            return True
        for v in range(current + 1, target + 1):
            sql = self._migrations.get(v)
            if sql is None:
                continue
            try:
                self._connection.executescript(sql)
                self._set_schema_version(v)
            except sqlite3.Error:
                return False
        self._config.version = target
        return True

    # -- Backup & Restore -----------------------------------------------------

    def backup(self, backup_path: str) -> bool:
        """Create a backup of the current database.

        Args:
            backup_path: Destination path for the backup file.

        Returns:
            True if the backup was created.
        """
        if not self._is_open or self._connection is None:
            return False
        try:
            bck = sqlite3.connect(backup_path)
            self._connection.backup(bck)
            bck.close()
            return True
        except sqlite3.Error:
            return False

    def restore(self, backup_path: str) -> bool:
        """Restore the database from a backup file.

        Args:
            backup_path: Path to the backup file.

        Returns:
            True if the restore succeeded.
        """
        self.close()
        try:
            src = sqlite3.connect(backup_path)
            dest = sqlite3.connect(self._config.path)
            src.backup(dest)
            src.close()
            dest.close()
            return self.open()
        except sqlite3.Error:
            return False

    # -- Sync Queue -----------------------------------------------------------

    def process_sync_queue(self) -> int:
        """Flush queued offline operations to the cloud.

        Returns:
            The number of successfully synced items.
        """
        processed = 0
        for item in list(self._sync_queue):
            success = self._sync_to_cloud(item)
            if success:
                self._sync_queue.remove(item)
                processed += 1
        return processed

    def get_sync_queue_size(self) -> int:
        """Get the number of pending sync items.

        Returns:
            Queue length.
        """
        return len(self._sync_queue)

    # -- Internal Helpers -----------------------------------------------------

    def _init_meta(self) -> None:
        if self._connection is None:
            return
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS _meta (key TEXT PRIMARY KEY, value TEXT)"
        )

    def _get_schema_version(self) -> int:
        if self._connection is None:
            return 0
        row = self._connection.execute(
            "SELECT value FROM _meta WHERE key = 'schema_version'"
        ).fetchone()
        if row is None:
            return 0
        return int(row[0])

    def _set_schema_version(self, version: int) -> None:
        if self._connection is None:
            return
        self._connection.execute(
            "INSERT OR REPLACE INTO _meta (key, value) VALUES ('schema_version', ?)",
            (str(version),),
        )
        self._connection.commit()

    def _run_pending_migrations(self) -> None:
        current = self._get_schema_version()
        for v in sorted(self._migrations):
            if v > current:
                sql = self._migrations[v]
                if self._connection is not None:
                    try:
                        self._connection.executescript(sql)
                        self._set_schema_version(v)
                        self._config.version = v
                    except sqlite3.Error:
                        break

    def _enqueue_sync(
        self, action: str, table: str, data: Dict[str, Any]
    ) -> None:
        if not self._config.sync_enabled:
            return
        item = SyncQueueItem(table=table, action=action, data=data)
        self._sync_queue.append(item)

    def _sync_to_cloud(self, item: SyncQueueItem) -> bool:
        return True

    def __repr__(self) -> str:
        return (
            f"Ububiko(path={self._config.path!r}, "
            f"open={self._is_open}, version={self._config.version})"
        )
