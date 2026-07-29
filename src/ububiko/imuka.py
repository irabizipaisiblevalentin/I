"""imuka — Migration system for the UBUBIKO data platform.

Provides schema creation, updates, rollback, seed data,
migration history tracking, and transformation pipelines.
"""

from __future__ import annotations

import json
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type


class ColumnType:
    """Standard column type constants."""

    INTEGER = "INTEGER"
    BIGINT = "BIGINT"
    SMALLINT = "SMALLINT"
    REAL = "REAL"
    DOUBLE = "DOUBLE PRECISION"
    DECIMAL = "DECIMAL"
    VARCHAR = "VARCHAR"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    TIME = "TIME"
    TIMESTAMP = "TIMESTAMP"
    BLOB = "BLOB"
    UUID = "UUID"
    JSON = "JSON"
    ARRAY = "ARRAY"
    VECTOR = "VECTOR"


@dataclass
class ColumnDef:
    """Definition of a table column for migrations."""

    name: str = ""
    col_type: str = ColumnType.TEXT
    primary_key: bool = False
    unique: bool = False
    nullable: bool = True
    default: Any = None
    foreign_key: Optional[Dict[str, str]] = None
    index: bool = False
    auto_increment: bool = False

    def to_sql(self) -> str:
        parts = [self.name, self.col_type]
        if self.primary_key:
            parts.append("PRIMARY KEY")
        if self.auto_increment:
            parts.append("AUTOINCREMENT" if "SQLite" in str(type(self)) else "AUTO_INCREMENT")
        if self.unique:
            parts.append("UNIQUE")
        if not self.nullable:
            parts.append("NOT NULL")
        if self.default is not None:
            if isinstance(self.default, str):
                parts.append(f"DEFAULT '{self.default}'")
            else:
                parts.append(f"DEFAULT {self.default}")
        if self.foreign_key:
            ref_table = self.foreign_key.get("table", "")
            ref_col = self.foreign_key.get("column", "id")
            parts.append(f"REFERENCES {ref_table}({ref_col})")
        return " ".join(parts)


@dataclass
class TableDef:
    """Definition of a table for migration."""

    name: str = ""
    columns: List[ColumnDef] = field(default_factory=list)
    if_not_exists: bool = True

    def to_create_sql(self) -> str:
        col_sql = ",\n  ".join(c.to_sql() for c in self.columns)
        return f"CREATE TABLE {'IF NOT EXISTS ' if self.if_not_exists else ''}{self.name} (\n  {col_sql}\n)"

    def to_drop_sql(self) -> str:
        return f"DROP TABLE IF EXISTS {self.name}"


@dataclass
class IndexDef:
    """Definition of a database index."""

    name: str = ""
    table: str = ""
    columns: List[str] = field(default_factory=list)
    unique: bool = False

    def to_sql(self) -> str:
        unique = "UNIQUE " if self.unique else ""
        cols = ", ".join(self.columns)
        return f"CREATE {unique}INDEX {self.name} ON {self.table} ({cols})"

    def to_drop_sql(self) -> str:
        return f"DROP INDEX IF EXISTS {self.name}"


MigrationFn = Callable[["MigrationEngine"], None]
SeedFn = Callable[["MigrationEngine"], None]


class Migration:
    """Base class for database migrations.

    Subclasses define up() and down() methods for
    forward and rollback operations.
    """

    version: str = ""
    description: str = ""

    def __init__(self) -> None:
        self._engine: Optional[MigrationEngine] = None

    @property
    def engine(self) -> Optional[MigrationEngine]:
        return self._engine

    @engine.setter
    def engine(self, value: MigrationEngine) -> None:
        self._engine = value

    def up(self, engine: MigrationEngine) -> None:
        """Apply the migration forward."""

    def down(self, engine: MigrationEngine) -> None:
        """Roll back the migration."""

    def create_table(self, table: TableDef) -> None:
        if self._engine:
            self._engine.execute(table.to_create_sql(), {})

    def drop_table(self, name: str) -> None:
        if self._engine:
            self._engine.execute(f"DROP TABLE IF EXISTS {name}", {})

    def add_column(self, table: str, column: ColumnDef) -> None:
        if self._engine:
            self._engine.execute(f"ALTER TABLE {table} ADD COLUMN {column.to_sql()}", {})

    def drop_column(self, table: str, column: str) -> None:
        if self._engine:
            self._engine.execute(f"ALTER TABLE {table} DROP COLUMN {column}", {})

    def rename_table(self, old: str, new: str) -> None:
        if self._engine:
            self._engine.execute(f"ALTER TABLE {old} RENAME TO {new}", {})

    def create_index(self, index: IndexDef) -> None:
        if self._engine:
            self._engine.execute(index.to_sql(), {})

    def drop_index(self, name: str) -> None:
        if self._engine:
            self._engine.execute(f"DROP INDEX IF EXISTS {name}", {})

    def execute_raw(self, sql: str, params: Optional[Dict[str, Any]] = None) -> None:
        if self._engine:
            self._engine.execute(sql, params or {})

    def seed(self, engine: MigrationEngine) -> None:
        """Insert seed data after migration."""


@dataclass
class MigrationRecord:
    """Record of an applied migration."""

    version: str = ""
    description: str = ""
    applied_at: str = ""
    checksum: str = ""


class MigrationEngine:
    """Engine that discovers, orders, and applies migrations.

    Tracks applied migrations, manages the migration history table,
    and supports forward/rollback operations.
    """

    def __init__(self, adapter: Any, migrations_dir: str = "migrations") -> None:
        self._adapter = adapter
        self._migrations_dir = migrations_dir
        self._migrations: List[Migration] = []
        self._history_table = "_ububiko_migrations"

    @property
    def adapter(self) -> Any:
        return self._adapter

    @property
    def history_table(self) -> str:
        return self._history_table

    def _ensure_history_table(self) -> None:
        self._adapter.execute(
            f"CREATE TABLE IF NOT EXISTS {self._history_table} (\n"
            "  version TEXT PRIMARY KEY,\n"
            "  description TEXT NOT NULL,\n"
            "  applied_at TEXT NOT NULL,\n"
            "  checksum TEXT NOT NULL\n"
            ")",
            {},
        )

    def _get_applied(self) -> Dict[str, MigrationRecord]:
        self._ensure_history_table()
        try:
            result_set = self._adapter.execute(
                f"SELECT version, description, applied_at, checksum FROM {self._history_table} ORDER BY version",
                {},
            )
            result: Dict[str, MigrationRecord] = {}
            for row in result_set.rows:
                record = MigrationRecord(
                    version=row[0],
                    description=row[1],
                    applied_at=row[2],
                    checksum=row[3],
                )
                result[record.version] = record
            return result
        except Exception:
            return {}

    def _mark_applied(self, migration: Migration) -> None:
        now = datetime.utcnow().isoformat()
        self._adapter.execute(
            f"INSERT INTO {self._history_table} (version, description, applied_at, checksum) "
            "VALUES (:v, :d, :a, :c)",
            {"v": migration.version, "d": migration.description, "a": now, "c": migration.version},
        )

    def _mark_rolled_back(self, version: str) -> None:
        self._adapter.execute(
            f"DELETE FROM {self._history_table} WHERE version = :v",
            {"v": version},
        )

    def register(self, migration: Migration) -> None:
        """Register a migration class or instance."""
        if isinstance(migration, type):
            migration = migration()
        migration.engine = self
        self._migrations.append(migration)
        self._migrations.sort(key=lambda m: m.version)

    def register_class(self, migration_class: Type[Migration]) -> None:
        self.register(migration_class())

    def load_from_directory(self, directory: str = "") -> None:
        """Auto-discover and register migrations from a directory."""
        path = directory or self._migrations_dir
        if not os.path.isdir(path):
            return
        import importlib.util
        import sys
        for filename in sorted(os.listdir(path)):
            if filename.endswith((".py", ".i")):
                filepath = os.path.join(path, filename)
                mod_name = f"_ububiko_mig_{filename[:-3]}"
                spec = importlib.util.spec_from_file_location(mod_name, filepath)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = mod
                    spec.loader.exec_module(mod)
                    for attr in dir(mod):
                        obj = getattr(mod, attr)
                        if isinstance(obj, type) and issubclass(obj, Migration) and obj is not Migration:
                            self.register(obj())

    def execute(self, sql: str, params: Dict[str, Any]) -> Any:
        """Execute SQL through the adapter."""
        return self._adapter.execute(sql, params)

    def migrate(self, target_version: str = "") -> List[str]:
        """Apply all pending migrations up to target_version."""
        applied = self._get_applied()
        applied_versions = set(applied.keys())
        results: List[str] = []

        for migration in self._migrations:
            if migration.version in applied_versions:
                continue
            if target_version and migration.version > target_version:
                break
            migration.up(self)
            self._mark_applied(migration)
            results.append(f"Applied {migration.version}: {migration.description}")

        return results

    def rollback(self, target_version: str = "") -> List[str]:
        """Roll back migrations down to (but not including) target_version.

        If no target_version is given, rolls back only the most recent migration.
        """
        applied = self._get_applied()
        applied_versions = sorted(applied.keys(), reverse=True)
        results: List[str] = []

        for version in applied_versions:
            if target_version and version <= target_version:
                break
            for migration in reversed(self._migrations):
                if migration.version == version:
                    migration.down(self)
                    self._mark_rolled_back(version)
                    results.append(f"Rolled back {version}: {migration.description}")
                    break
            if not target_version:
                break

        return results

    def history(self) -> List[MigrationRecord]:
        """Return the migration history."""
        return list(self._get_applied().values())

    def status(self) -> Dict[str, Any]:
        """Return migration status summary."""
        applied = self._get_applied()
        pending = [m for m in self._migrations if m.version not in applied]
        return {
            "total": len(self._migrations),
            "applied": len(applied),
            "pending": len(pending),
            "pending_versions": [m.version for m in pending],
        }

    def seed(self) -> None:
        """Run seed data for all applied migrations."""
        for migration in self._migrations:
            try:
                migration.seed(self)
            except Exception:
                pass

    def generate_migration(self, name: str, version: Optional[str] = None) -> str:
        """Generate a migration file skeleton."""
        if version is None:
            version = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{version}_{name}.py"
        content = f'''"""Migration: {name}"""

from ububiko.imuka import Migration, MigrationEngine, TableDef, ColumnDef, ColumnType


class Migration_{version}(Migration):
    """_{name.replace("_", " ").title()}."""

    version = "{version}"
    description = "{name}"

    def up(self, engine: MigrationEngine) -> None:
        pass

    def down(self, engine: MigrationEngine) -> None:
        pass

    def seed(self, engine: MigrationEngine) -> None:
        pass
'''
        os.makedirs(self._migrations_dir, exist_ok=True)
        filepath = os.path.join(self._migrations_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath
