"""database — Database abstraction for the I language.

Provides a lightweight SQLite wrapper for local data storage.
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union


class Database:
    """SQLite database wrapper."""

    def __init__(self, path: str = ":memory:") -> None:
        self._path = path
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row

    def execute(self, sql: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        return self._conn.execute(sql, params)

    def executemany(self, sql: str, params_seq: Sequence[Sequence[Any]]) -> sqlite3.Cursor:
        return self._conn.executemany(sql, params_seq)

    def execute_script(self, script: str) -> None:
        self._conn.executescript(script)

    def fetch_one(self, sql: str, params: Sequence[Any] = ()) -> Optional[Dict[str, Any]]:
        cursor = self._conn.execute(sql, params)
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetch_all(self, sql: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
        cursor = self._conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a row. Returns rowid."""
        cols = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        cursor = self._conn.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
            list(data.values()),
        )
        self._conn.commit()
        return cursor.lastrowid

    def update(self, table: str, data: Dict[str, Any], where: str,
               where_params: Sequence[Any] = ()) -> int:
        """Update rows. Returns number of affected rows."""
        sets = ", ".join(f"{k} = ?" for k in data.keys())
        sql = f"UPDATE {table} SET {sets} WHERE {where}"
        cursor = self._conn.execute(sql, list(data.values()) + list(where_params))
        self._conn.commit()
        return cursor.rowcount

    def delete(self, table: str, where: str, where_params: Sequence[Any] = ()) -> int:
        cursor = self._conn.execute(f"DELETE FROM {table} WHERE {where}", where_params)
        self._conn.commit()
        return cursor.rowcount

    def table_exists(self, name: str) -> bool:
        result = self.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (name,),
        )
        return result is not None

    def tables(self) -> List[str]:
        rows = self.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
        return [r["name"] for r in rows]

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> Database:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
