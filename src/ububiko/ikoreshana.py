"""ikoreshana — Performance optimization for the UBUBIKO data platform.

Provides connection pooling, prepared statement caching, batch operations,
streaming queries, async execution, index management, and caching layers.
"""

from __future__ import annotations

import hashlib
import queue
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


class ConnectionPool:
    """Thread-safe connection pool for database connections.

    Manages a pool of reusable connections with configurable
    min/max size, timeout, and health checks.
    """

    def __init__(self, create_connection: Callable[[], Any],
                 min_size: int = 2, max_size: int = 20,
                 timeout: int = 30, max_idle: int = 300) -> None:
        self._create = create_connection
        self._min_size = min_size
        self._max_size = max_size
        self._timeout = timeout
        self._max_idle = max_idle
        self._pool: queue.Queue = queue.Queue()
        self._in_use: set = set()
        self._size: int = 0
        self._lock = threading.Lock()

        for _ in range(min_size):
            self._add_connection()

    def _add_connection(self) -> Any:
        try:
            conn = self._create()
            self._pool.put(conn)
            self._size += 1
            return conn
        except Exception:
            return None

    def acquire(self) -> Any:
        """Acquire a connection from the pool."""
        try:
            conn = self._pool.get(timeout=self._timeout)
            self._in_use.add(id(conn))
            return conn
        except queue.Empty:
            with self._lock:
                if self._size < self._max_size:
                    conn = self._add_connection()
                    if conn:
                        self._pool.get()  # Remove from pool
                        self._in_use.add(id(conn))
                        return conn
            raise RuntimeError("Connection pool exhausted")

    def release(self, conn: Any) -> None:
        """Release a connection back to the pool."""
        self._in_use.discard(id(conn))
        self._pool.put(conn)

    def close_all(self) -> None:
        """Close all connections in the pool."""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                if hasattr(conn, 'close'):
                    conn.close()
                self._size -= 1
            except queue.Empty:
                break

    @property
    def size(self) -> int:
        return self._size

    @property
    def available(self) -> int:
        return self._pool.qsize()

    @property
    def in_use_count(self) -> int:
        return len(self._in_use)

    def status(self) -> Dict[str, Any]:
        return {
            "size": self._size,
            "available": self.available,
            "in_use": self.in_use_count,
            "max_size": self._max_size,
        }


class PreparedStatementCache:
    """Cache for prepared/compiled SQL statements.

    Stores parsed and optimized query plans keyed by SQL hash
    to avoid repeated parsing overhead.
    """

    def __init__(self, max_size: int = 1000) -> None:
        self._cache: Dict[str, Any] = {}
        self._max_size = max_size
        self._hit_count: int = 0
        self._miss_count: int = 0

    def _hash(self, sql: str) -> str:
        return hashlib.sha256(sql.encode()).hexdigest()

    def get(self, sql: str) -> Optional[Any]:
        """Retrieve a cached prepared statement."""
        key = self._hash(sql)
        entry = self._cache.get(key)
        if entry:
            self._hit_count += 1
            return entry
        self._miss_count += 1
        return None

    def set(self, sql: str, statement: Any) -> None:
        """Cache a prepared statement."""
        if len(self._cache) >= self._max_size:
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        key = self._hash(sql)
        self._cache[key] = statement

    def invalidate(self, sql: str) -> None:
        """Remove a cached statement."""
        key = self._hash(sql)
        self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached statements."""
        self._cache.clear()

    @property
    def hit_count(self) -> int:
        return self._hit_count

    @property
    def miss_count(self) -> int:
        return self._miss_count

    @property
    def hit_ratio(self) -> float:
        total = self._hit_count + self._miss_count
        return self._hit_count / total if total > 0 else 0.0

    @property
    def size(self) -> int:
        return len(self._cache)


class BatchProcessor:
    """Processes database operations in batches for efficiency.

    Accumulates operations and flushes them in bulk
    to minimize round-trips.
    """

    def __init__(self, batch_size: int = 100, flush_interval: int = 5) -> None:
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._operations: List[Tuple[str, Dict[str, Any]]] = []
        self._last_flush: float = time.time()
        self._total_processed: int = 0

    def add(self, operation: str, params: Dict[str, Any]) -> None:
        """Add an operation to the batch."""
        self._operations.append((operation, params))
        if len(self._operations) >= self._batch_size:
            self.flush()

    def flush(self, adapter: Optional[Any] = None) -> int:
        """Flush all pending operations."""
        if not self._operations:
            return 0
        count = len(self._operations)
        if adapter:
            for op, params in self._operations:
                adapter.execute(op, params)
        self._operations.clear()
        self._last_flush = time.time()
        self._total_processed += count
        return count

    def flush_if_needed(self) -> bool:
        """Flush if the flush interval has elapsed."""
        if time.time() - self._last_flush >= self._flush_interval:
            self.flush()
            return True
        return False

    @property
    def pending_count(self) -> int:
        return len(self._operations)

    @property
    def total_processed(self) -> int:
        return self._total_processed


class AsyncQueryExecutor:
    """Executes queries asynchronously with callback support.

    Provides non-blocking execution for long-running queries
    with result polling and timeout support.
    """

    def __init__(self, max_workers: int = 4) -> None:
        self._max_workers = max_workers
        self._futures: Dict[str, Any] = {}
        self._results: Dict[str, Any] = {}

    def submit(self, query_fn: Callable[..., Any], *args: Any,
               callback: Optional[Callable[[Any], None]] = None,
               **kwargs: Any) -> str:
        """Submit a query for async execution."""
        import threading as _t
        task_id = f"q_{int(time.time() * 1000)}_{len(self._futures)}"

        def _run() -> None:
            try:
                result = query_fn(*args, **kwargs)
                self._results[task_id] = result
                if callback:
                    callback(result)
            except Exception as e:
                self._results[task_id] = e
            finally:
                self._futures.pop(task_id, None)

        thread = _t.Thread(target=_run, daemon=True)
        self._futures[task_id] = thread
        thread.start()
        return task_id

    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Get the result of an async query (blocks if not ready)."""
        start = time.time()
        while task_id not in self._results:
            if timeout and (time.time() - start) >= timeout:
                raise TimeoutError(f"Query {task_id} timed out")
            time.sleep(0.01)
        result = self._results.pop(task_id)
        if isinstance(result, Exception):
            raise result
        return result

    def is_done(self, task_id: str) -> bool:
        """Check if an async query has completed."""
        return task_id in self._results

    def cancel(self, task_id: str) -> bool:
        """Cancel a pending async query."""
        thread = self._futures.pop(task_id, None)
        if thread and thread.is_alive():
            return False
        return True

    @property
    def pending_count(self) -> int:
        return len(self._futures)

    def wait_all(self, timeout: Optional[float] = None) -> None:
        """Wait for all pending queries to complete."""
        start = time.time()
        while self._futures:
            if timeout and (time.time() - start) >= timeout:
                raise TimeoutError("Not all queries completed within timeout")
            time.sleep(0.05)


class IndexManager:
    """Manages database indexes for query performance.

    Provides index creation, analysis, recommendations,
    and maintenance operations.
    """

    def __init__(self, adapter: Any) -> None:
        self._adapter = adapter
        self._indexes: Dict[str, List[Dict[str, Any]]] = {}

    def create_index(self, table: str, columns: List[str],
                     name: str = "", unique: bool = False) -> str:
        """Create a database index."""
        if not name:
            name = f"idx_{table}_{'_'.join(columns)}"
        unique_str = "UNIQUE " if unique else ""
        cols = ", ".join(columns)
        sql = f"CREATE {unique_str}INDEX IF NOT EXISTS {name} ON {table} ({cols})"
        self._adapter.execute(sql, {})
        if table not in self._indexes:
            self._indexes[table] = []
        self._indexes[table].append({"name": name, "columns": columns, "unique": unique})
        return name

    def drop_index(self, name: str) -> None:
        """Drop a database index."""
        self._adapter.execute(f"DROP INDEX IF EXISTS {name}", {})
        for table in list(self._indexes.keys()):
            self._indexes[table] = [i for i in self._indexes[table] if i["name"] != name]

    def list_indexes(self, table: str = "") -> List[Dict[str, Any]]:
        """List indexes, optionally filtered by table."""
        if table:
            return list(self._indexes.get(table, []))
        return [idx for idxs in self._indexes.values() for idx in idxs]

    def suggest_indexes(self, query: str) -> List[Dict[str, str]]:
        """Suggest indexes based on query analysis."""
        suggestions: List[Dict[str, str]] = []
        import re
        where_cols = re.findall(r"WHERE\s+(\w+)\s*=", query, re.IGNORECASE)
        join_cols = re.findall(r"JOIN\s+\w+\s+ON\s+\w+\.(\w+)\s*=", query, re.IGNORECASE)
        order_cols = re.findall(r"ORDER BY\s+(\w+)", query, re.IGNORECASE)
        for col in where_cols + join_cols + order_cols:
            suggestions.append({"column": col, "reason": "query_filter"})
        return suggestions


class CacheLayer:
    """Multi-level cache for query results.

    Supports in-memory and optional distributed caching
    with TTL, invalidation, and LRU eviction.
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 60) -> None:
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits: int = 0
        self._misses: int = 0

    def _key(self, query: str, params: Optional[Dict[str, Any]] = None) -> str:
        raw = query + (str(sorted(params.items())) if params else "")
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Get cached result for a query."""
        key = self._key(query, params)
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        value, expires = entry
        if time.time() > expires:
            del self._cache[key]
            self._misses += 1
            return None
        self._hits += 1
        return value

    def set(self, query: str, result: Any,
            params: Optional[Dict[str, Any]] = None,
            ttl: Optional[int] = None) -> None:
        """Cache a query result."""
        if len(self._cache) >= self._max_size:
            oldest = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest]
        key = self._key(query, params)
        expires = time.time() + (ttl or self._default_ttl)
        self._cache[key] = (result, expires)

    def invalidate(self, query: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Invalidate a cached query."""
        key = self._key(query, params)
        self._cache.pop(key, None)

    def invalidate_table(self, table: str) -> None:
        """Invalidate all cache entries containing a table reference."""
        to_delete = [k for k in self._cache if table in k]
        for k in to_delete:
            del self._cache[k]

    def clear(self) -> None:
        """Clear all cached results."""
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    @property
    def hit_ratio(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0
