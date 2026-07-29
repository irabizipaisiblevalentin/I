# Performance Guide (Ikoreshana)

## Connection Pooling

```python
from ububiko.ikoreshana import ConnectionPool

pool = ConnectionPool(
    create_connection=lambda: SQLiteAdapter().connect(config),
    min_size=2, max_size=20, timeout=30,
)

conn = pool.acquire()
try:
    result = conn.execute("SELECT * FROM users", {})
finally:
    pool.release(conn)
```

## Prepared Statement Cache

```python
from ububiko.ikoreshana import PreparedStatementCache

cache = PreparedStatementCache(max_size=1000)
stmt = cache.get("SELECT * FROM users WHERE id = :id")
if stmt is None:
    stmt = adapter.prepare("SELECT * FROM users WHERE id = :id")
    cache.set("SELECT * FROM users WHERE id = :id", stmt)
```

## Batch Processing

```python
from ububiko.ikoreshana import BatchProcessor

batch = BatchProcessor(batch_size=100)
for i in range(1000):
    batch.add("INSERT INTO logs (message) VALUES (:msg)", {"msg": f"Log {i}"})
batch.flush(adapter)
```

## Async Queries

```python
from ububiko.ikoreshana import AsyncQueryExecutor

executor = AsyncQueryExecutor()
task_id = executor.submit(adapter.execute, "SELECT * FROM large_table", {})

# Do other work...
result = executor.get_result(task_id, timeout=30.0)
```

## Cache Layer

```python
from ububiko.ikoreshana import CacheLayer

cache = CacheLayer(max_size=1000, default_ttl=60)
result = cache.get("SELECT count(*) FROM users")
if result is None:
    result = adapter.execute("SELECT count(*) FROM users", {})
    cache.set("SELECT count(*) FROM users", result)
```

## Index Management

```python
from ububiko.ikoreshana import IndexManager

im = IndexManager(adapter)
im.create_index("users", ["email"], unique=True)
im.create_index("users", ["name", "status"])
```
