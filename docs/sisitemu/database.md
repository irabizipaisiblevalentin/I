# Database Engine Primitives — `ububiko_db`

Build embedded database engines with B+trees, LSM trees, WAL, buffer pools, and
transactions — all running directly on SISITEMU with no external dependencies.

## Quick Start

```python
from sisitemu.ububiko_db import StorageEngine, BTreeIndex, WriteAheadLog

engine = StorageEngine(path="data/")
txn = engine.begin()
engine.set(txn, b"key1", b"value1")
engine.set(txn, b"key2", b"value2")
engine.commit(txn)

result = engine.get(b"key1")
assert result == b"value1"

for key, value in engine.scan(b"key", b"keyz"):
    print(key, value)
```

## Components

### BTreeIndex
```python
tree = BTreeIndex(order=4)
tree.insert(42, b"data")
result = tree.search(42)
for k, v in tree.range_scan(10, 50):
    print(k, v)
```

### LSMTree
```python
lsm = LSMTree(path="data/lsm", memtable_size=4096)
lsm.put(b"key", b"value")
result = lsm.get(b"key")
lsm.compact()
```

### WriteAheadLog
```python
wal = WriteAheadLog(path="data/wal.log")
seq = wal.append(b"user:42", b"data")
wal.checkpoint()
records = wal.recover()
```

### BufferPool
```python
pool = BufferPool(capacity=64, page_size=4096)
page = pool.acquire(page_id=1)
pool.release(page_id=1)
pool.flush()
```

### TransactionManager
```python
tm = TransactionManager(isolation=IsolationLevel.SERIALIZABLE)
txn = tm.begin()
tm.write(txn, b"key", b"value")
assert tm.read(txn, b"key") == b"value"
tm.commit(txn)
```

### HashIndex
```python
idx = HashIndex(buckets=16)
idx.insert(b"user:1", b"alice")
result = idx.search(b"user:1")
```

## Architecture

```
StorageEngine
├── BTreeIndex       — ordered index with range scans
├── LSMTree          — write-optimized log-structured merge tree
│   ├── MemTable     — in-memory sorted buffer
│   └── SSTable      — on-disk sorted run with bloom filter
├── HashIndex        — O(1) point lookups
├── WriteAheadLog    — crash recovery
├── BufferPool       — page cache with LRU eviction
└── TransactionManager — ACID transactions (begin/commit/rollback)
```

## Isolation Levels

- `READ_UNCOMMITTED`
- `READ_COMMITTED`
- `REPEATABLE_READ`
- `SERIALIZABLE`
