"""ububiko_db — Database engine primitives: B+trees, LSM trees, WAL, buffer pool, transactions, indexing."""

from __future__ import annotations

import hashlib
import json
import os
import struct
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple


class IsolationLevel(Enum):
    READ_UNCOMMITTED = "read_uncommitted"
    READ_COMMITTED = "read_committed"
    REPEATABLE_READ = "repeatable_read"
    SERIALIZABLE = "serializable"


class LogAction(Enum):
    BEGIN = "begin"
    COMMIT = "commit"
    ROLLBACK = "rollback"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CHECKPOINT = "checkpoint"


class IndexType(Enum):
    BTREE = "btree"
    HASH = "hash"
    LSM = "lsm"
    BITMAP = "bitmap"
    INVERTED = "inverted"


@dataclass
class WALEntry:
    lsn: int = 0
    action: LogAction = LogAction.BEGIN
    transaction_id: str = ""
    table: str = ""
    key: bytes = b""
    old_value: bytes = b""
    new_value: bytes = b""
    timestamp: float = 0.0

    def to_bytes(self) -> bytes:
        data = {
            "lsn": self.lsn,
            "action": self.action.value,
            "txn": self.transaction_id,
            "table": self.table,
            "key": self.key.hex(),
            "old": self.old_value.hex(),
            "new": self.new_value.hex(),
            "ts": self.timestamp,
        }
        return json.dumps(data).encode() + b"\n"

    @staticmethod
    def from_bytes(data: bytes) -> WALEntry:
        d = json.loads(data.decode().strip())
        return WALEntry(
            lsn=d["lsn"],
            action=LogAction(d["action"]),
            transaction_id=d["txn"],
            table=d["table"],
            key=bytes.fromhex(d["key"]),
            old_value=bytes.fromhex(d["old"]),
            new_value=bytes.fromhex(d["new"]),
            timestamp=d["ts"],
        )


class WriteAheadLog:
    def __init__(self, path: str = "wal.log"):
        self.path = path
        self._lsn: int = 0
        self._lock = threading.Lock()
        self._entries: List[WALEntry] = []
        self._file: Optional[Any] = None

    def open(self) -> None:
        if os.path.exists(self.path):
            self._file = open(self.path, "ab+")
        else:
            self._file = open(self.path, "wb")
        self._recover()

    def close(self) -> None:
        if self._file:
            self._file.close()

    def append(self, entry: WALEntry) -> int:
        with self._lock:
            self._lsn += 1
            entry.lsn = self._lsn
            self._entries.append(entry)
            if self._file:
                self._file.write(entry.to_bytes())
                self._file.flush()
            return self._lsn

    def truncate(self, up_to_lsn: int) -> None:
        with self._lock:
            self._entries = [e for e in self._entries if e.lsn > up_to_lsn]
            if self._file:
                self._file.seek(0)
                self._file.truncate()
                for e in self._entries:
                    self._file.write(e.to_bytes())
                self._file.flush()

    def checkpoint(self) -> int:
        entry = WALEntry(
            action=LogAction.CHECKPOINT,
            transaction_id="",
            timestamp=time.time(),
        )
        return self.append(entry)

    def _recover(self) -> None:
        if not self._file:
            return
        self._file.seek(0)
        for line in self._file:
            if line.strip():
                entry = WALEntry.from_bytes(line)
                self._entries.append(entry)
                if entry.lsn > self._lsn:
                    self._lsn = entry.lsn

    def pending_transactions(self) -> List[str]:
        active = set()
        committed = set()
        for e in self._entries:
            if e.action == LogAction.BEGIN:
                active.add(e.transaction_id)
            elif e.action == LogAction.COMMIT:
                committed.add(e.transaction_id)
            elif e.action == LogAction.ROLLBACK:
                active.discard(e.transaction_id)
        return list(active - committed)

    @property
    def last_lsn(self) -> int:
        return self._lsn


@dataclass
class BTreeNode:
    is_leaf: bool = True
    keys: List[Any] = field(default_factory=list)
    values: List[Any] = field(default_factory=list)
    children: List[int] = field(default_factory=list)
    next_leaf: Optional[int] = None


class BTreeIndex:
    def __init__(self, order: int = 4):
        self.order = order
        self._nodes: Dict[int, BTreeNode] = {0: BTreeNode()}
        self._root_id: int = 0
        self._next_id: int = 1

    def _new_node(self) -> int:
        nid = self._next_id
        self._next_id += 1
        self._nodes[nid] = BTreeNode()
        return nid

    def search(self, key: Any) -> Optional[Any]:
        return self._search(self._root_id, key)

    def _search(self, nid: int, key: Any) -> Optional[Any]:
        node = self._nodes[nid]
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if node.is_leaf:
            if i < len(node.keys) and node.keys[i] == key:
                return node.values[i]
            return None
        if i < len(node.keys) and node.keys[i] == key:
            return node.values[i]
        return self._search(node.children[i], key)

    def insert(self, key: Any, value: Any) -> None:
        root = self._nodes[self._root_id]
        if len(root.keys) == 2 * self.order - 1:
            new_root_id = self._new_node()
            new_root = self._nodes[new_root_id]
            new_root.is_leaf = False
            new_root.children.append(self._root_id)
            self._root_id = new_root_id
            self._split_child(new_root_id, 0)
        self._insert_non_full(self._root_id, key, value)

    def _insert_non_full(self, nid: int, key: Any, value: Any) -> None:
        node = self._nodes[nid]
        i = len(node.keys) - 1
        if node.is_leaf:
            node.keys.append(None)
            node.values.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(self._nodes[node.children[i]].keys) == 2 * self.order - 1:
                self._split_child(nid, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent_id: int, child_index: int) -> None:
        parent = self._nodes[parent_id]
        child = self._nodes[parent.children[child_index]]
        new_child_id = self._new_node()
        new_child = self._nodes[new_child_id]
        new_child.is_leaf = child.is_leaf
        mid = self.order - 1
        new_child.keys = child.keys[mid + 1:]
        new_child.values = child.values[mid + 1:]
        if not child.is_leaf:
            new_child.children = child.children[mid + 1:]
            child.children = child.children[:mid + 1]
        elif child.next_leaf:
            new_child.next_leaf = child.next_leaf
            child.next_leaf = new_child_id
        parent.keys.insert(child_index, child.keys[mid])
        parent.values.insert(child_index, child.values[mid])
        parent.children.insert(child_index + 1, new_child_id)
        child.keys = child.keys[:mid]
        child.values = child.values[:mid]

    def range_scan(self, start: Any, end: Any) -> List[Tuple[Any, Any]]:
        results: List[Tuple[Any, Any]] = []
        leaf_id = self._find_leaf(self._root_id, start)
        while leaf_id is not None:
            node = self._nodes[leaf_id]
            for k, v in zip(node.keys, node.values):
                if k > end:
                    return results
                if k >= start:
                    results.append((k, v))
            leaf_id = node.next_leaf
        return results

    def _find_leaf(self, nid: int, key: Any) -> int:
        node = self._nodes[nid]
        if node.is_leaf:
            return nid
        i = 0
        while i < len(node.keys) and key >= node.keys[i]:
            i += 1
        return self._find_leaf(node.children[i], key)


@dataclass
class MemTableEntry:
    key: bytes = b""
    value: bytes = b""
    deleted: bool = False
    sequence: int = 0


class MemTable:
    def __init__(self, max_size: int = 4096):
        self._entries: Dict[bytes, MemTableEntry] = {}
        self._max_size = max_size
        self._size = 0
        self._sequence = 0

    def put(self, key: bytes, value: bytes) -> None:
        self._sequence += 1
        entry = MemTableEntry(key=key, value=value, sequence=self._sequence)
        self._entries[key] = entry
        self._size = len(self._entries)

    def get(self, key: bytes) -> Optional[bytes]:
        entry = self._entries.get(key)
        if entry is None or entry.deleted:
            return None
        return entry.value

    def delete(self, key: bytes) -> None:
        self._sequence += 1
        self._entries[key] = MemTableEntry(key=key, deleted=True, sequence=self._sequence)
        self._size = len(self._entries)

    @property
    def is_full(self) -> bool:
        return self._size >= self._max_size

    @property
    def entries(self) -> List[MemTableEntry]:
        return sorted(self._entries.values(), key=lambda e: e.sequence)

    def clear(self) -> None:
        self._entries.clear()
        self._size = 0


@dataclass
class SSTableBlock:
    data: bytes = b""
    offset: int = 0
    first_key: bytes = b""


class SSTable:
    def __init__(self, path: str, block_size: int = 4096):
        self.path = path
        self.block_size = block_size
        self._blocks: List[SSTableBlock] = []
        self._bloom: bytearray = bytearray(256)

    def build(self, entries: List[MemTableEntry]) -> None:
        data = b""
        block = SSTableBlock()
        for e in sorted(entries, key=lambda x: x.key):
            key_len = len(e.key).to_bytes(2, "big")
            val_len = len(e.value).to_bytes(4, "big") if not e.deleted else b"\x00" * 4
            deleted_byte = b"\x01" if e.deleted else b"\x00"
            row = key_len + e.key + val_len + e.value + deleted_byte
            if len(block.data) + len(row) > self.block_size and block.data:
                block.offset = len(data)
                self._blocks.append(block)
                block = SSTableBlock()
            block.data += row
            self._add_to_bloom(e.key)
        if block.data:
            block.offset = len(data)
            self._blocks.append(block)
        data += self._write_index()
        with open(self.path, "wb") as f:
            f.write(data)

    def _add_to_bloom(self, key: bytes) -> None:
        h = hashlib.sha256(key).digest()
        for i in range(4):
            idx = (h[i * 2] << 8 | h[i * 2 + 1]) % len(self._bloom)
            self._bloom[idx] = 1

    def _write_index(self) -> bytes:
        index: Dict[str, Any] = {
            "blocks": [
                {"offset": b.offset, "size": len(b.data), "first_key": b.first_key.hex()}
                for b in self._blocks
            ],
            "bloom": self._bloom.hex(),
        }
        data = json.dumps(index).encode()
        return struct.pack(">I", len(data)) + data

    def query(self, key: bytes) -> Optional[bytes]:
        if not self._check_bloom(key):
            return None
        try:
            with open(self.path, "rb") as f:
                meta_size = struct.unpack(">I", f.read(4))[0]
                f.seek(-(meta_size + 4), os.SEEK_END)
                meta = json.loads(f.read(meta_size))
                blocks = meta.get("blocks", [])
                for b in reversed(blocks):
                    f.seek(b["offset"])
                    block = f.read(b["size"])
                    pos = 0
                    while pos < len(block):
                        kl = int.from_bytes(block[pos:pos + 2], "big")
                        pos += 2
                        k = block[pos:pos + kl]
                        pos += kl
                        vl = int.from_bytes(block[pos:pos + 4], "big")
                        pos += 4
                        v = block[pos:pos + vl]
                        pos += vl
                        deleted = block[pos] == 1
                        pos += 1
                        if k == key and not deleted:
                            return v
        except (FileNotFoundError, OSError, ValueError):
            pass
        return None

    def _check_bloom(self, key: bytes) -> bool:
        h = hashlib.sha256(key).digest()
        for i in range(4):
            idx = (h[i * 2] << 8 | h[i * 2 + 1]) % len(self._bloom)
            if self._bloom[idx] == 0:
                return False
        return True


class LSMTree:
    def __init__(self, path: str = "lsm_data"):
        self.path = path
        self._memtable = MemTable(max_size=1024)
        self._immutable: Optional[MemTable] = None
        self._levels: List[List[SSTable]] = [[] for _ in range(4)]
        self._level_max: List[int] = [4, 8, 16, 32]
        self._lock = threading.Lock()

    def put(self, key: bytes, value: bytes) -> None:
        with self._lock:
            self._memtable.put(key, value)
            if self._memtable.is_full:
                self._flush()

    def get(self, key: bytes) -> Optional[bytes]:
        with self._lock:
            val = self._memtable.get(key)
            if val is not None:
                return val
            if self._immutable:
                val = self._immutable.get(key)
                if val is not None:
                    return val
        for level in self._levels:
            for table in reversed(level):
                val = table.query(key)
                if val is not None:
                    return val
        return None

    def delete(self, key: bytes) -> None:
        self.put(key, b"")

    def _flush(self) -> None:
        if not self._memtable or self._memtable._size == 0:
            return
        self._immutable = self._memtable
        self._memtable = MemTable(max_size=1024)
        seq = int(time.time() * 1000000)
        sst = SSTable(os.path.join(self.path, f"L0_{seq}.sst"))
        sst.build(self._immutable.entries)
        self._levels[0].append(sst)
        self._immutable = None
        self._maybe_compact(0)

    def _maybe_compact(self, level: int) -> None:
        if len(self._levels[level]) <= self._level_max[level]:
            return
        if level + 1 >= len(self._levels):
            return
        to_compact = self._levels[level][:self._level_max[level]]
        self._levels[level] = self._levels[level][self._level_max[level]:]
        seq = int(time.time() * 1000000)
        compacted = SSTable(os.path.join(self.path, f"L{level + 1}_{seq}.sst"))
        all_entries: List[MemTableEntry] = []
        for table in to_compact:
            all_entries.extend(table._blocks)
        compacted.build([])
        self._levels[level + 1].append(compacted)
        if len(self._levels[level + 1]) > self._level_max[level + 1]:
            self._maybe_compact(level + 1)

    def flush(self) -> None:
        with self._lock:
            self._flush()


@dataclass
class Page:
    page_id: int = 0
    data: bytearray = field(default_factory=lambda: bytearray(4096))
    dirty: bool = False
    pin_count: int = 0
    last_access: float = 0.0


class BufferPool:
    def __init__(self, capacity: int = 100, page_size: int = 4096):
        self.capacity = capacity
        self.page_size = page_size
        self._pages: Dict[int, Page] = {}
        self._access_order: List[int] = []
        self._lock = threading.Lock()
        self._disk_path: str = ""

    def set_disk(self, path: str) -> None:
        self._disk_path = path

    def get_page(self, page_id: int) -> Optional[Page]:
        with self._lock:
            if page_id in self._pages:
                page = self._pages[page_id]
                page.last_access = time.time()
                page.pin_count += 1
                self._update_access(page_id)
                return page
            if len(self._pages) >= self.capacity:
                self._evict()
            data = self._read_from_disk(page_id)
            page = Page(page_id=page_id, data=bytearray(data), last_access=time.time())
            page.pin_count = 1
            self._pages[page_id] = page
            self._access_order.append(page_id)
            return page

    def unpin_page(self, page_id: int, dirty: bool = False) -> None:
        with self._lock:
            if page_id in self._pages:
                self._pages[page_id].pin_count -= 1
                if dirty:
                    self._pages[page_id].dirty = True

    def flush_page(self, page_id: int) -> None:
        with self._lock:
            if page_id in self._pages and self._pages[page_id].dirty:
                self._write_to_disk(page_id)
                self._pages[page_id].dirty = False

    def flush_all(self) -> None:
        with self._lock:
            for page_id in list(self._pages.keys()):
                self.flush_page(page_id)

    def _evict(self) -> None:
        for page_id in self._access_order:
            page = self._pages.get(page_id)
            if page and page.pin_count == 0:
                if page.dirty:
                    self._write_to_disk(page_id)
                del self._pages[page_id]
                self._access_order.remove(page_id)
                return

    def _update_access(self, page_id: int) -> None:
        if page_id in self._access_order:
            self._access_order.remove(page_id)
        self._access_order.append(page_id)

    def _read_from_disk(self, page_id: int) -> bytes:
        if not self._disk_path or not os.path.exists(self._disk_path):
            return b"\x00" * self.page_size
        try:
            with open(self._disk_path, "rb") as f:
                f.seek(page_id * self.page_size)
                return f.read(self.page_size)
        except (OSError, IOError):
            return b"\x00" * self.page_size

    def _write_to_disk(self, page_id: int) -> None:
        if not self._disk_path:
            return
        try:
            with open(self._disk_path, "r+b") as f:
                f.seek(page_id * self.page_size)
                f.write(self._pages[page_id].data)
        except (OSError, IOError):
            pass

    def allocate_page(self) -> int:
        with self._lock:
            page_id = len(self._pages) + 1
            page = Page(page_id=page_id)
            self._pages[page_id] = page
            self._access_order.append(page_id)
            return page_id

    @property
    def usage(self) -> float:
        return len(self._pages) / self.capacity


@dataclass
class Transaction:
    transaction_id: str = ""
    isolation: IsolationLevel = IsolationLevel.SERIALIZABLE
    started_at: float = 0.0
    read_set: set = field(default_factory=set)
    write_set: set = field(default_factory=set)
    changes: List[WALEntry] = field(default_factory=list)
    active: bool = True


class TransactionManager:
    def __init__(self, wal: Optional[WriteAheadLog] = None):
        self._wal = wal
        self._transactions: Dict[str, Transaction] = {}
        self._lock = threading.Lock()
        self._next_txn_id: int = 1

    def begin(self, isolation: IsolationLevel = IsolationLevel.SERIALIZABLE) -> Transaction:
        with self._lock:
            txn_id = f"T{self._next_txn_id:06d}"
            self._next_txn_id += 1
            txn = Transaction(
                transaction_id=txn_id,
                isolation=isolation,
                started_at=time.time(),
            )
            self._transactions[txn_id] = txn
            if self._wal:
                self._wal.append(WALEntry(
                    action=LogAction.BEGIN,
                    transaction_id=txn_id,
                    timestamp=txn.started_at,
                ))
            return txn

    def commit(self, txn: Transaction) -> bool:
        with self._lock:
            if not txn.active:
                return False
            txn.active = False
            if self._wal:
                for change in txn.changes:
                    self._wal.append(change)
                self._wal.append(WALEntry(
                    action=LogAction.COMMIT,
                    transaction_id=txn.transaction_id,
                    timestamp=time.time(),
                ))
            self._transactions.pop(txn.transaction_id, None)
            return True

    def rollback(self, txn: Transaction) -> bool:
        with self._lock:
            if not txn.active:
                return False
            txn.active = False
            if self._wal:
                for change in reversed(txn.changes):
                    rollback_entry = WALEntry(
                        action=LogAction.ROLLBACK,
                        transaction_id=txn.transaction_id,
                        table=change.table,
                        key=change.key,
                        old_value=change.old_value,
                        new_value=change.new_value,
                        timestamp=time.time(),
                    )
                    self._wal.append(rollback_entry)
            self._transactions.pop(txn.transaction_id, None)
            return True

    def active_transactions(self) -> List[str]:
        return [t.transaction_id for t in self._transactions.values() if t.active]


@dataclass
class Record:
    key: bytes = b""
    value: bytes = b""
    timestamp: float = 0.0
    tombstone: bool = False

    def encode(self) -> bytes:
        klen = len(self.key).to_bytes(2, "big")
        vlen = len(self.value).to_bytes(4, "big")
        ts = struct.pack(">d", self.timestamp)
        tomb = b"\x01" if self.tombstone else b"\x00"
        return klen + self.key + vlen + self.value + ts + tomb

    @staticmethod
    def decode(data: bytes) -> Record:
        klen = int.from_bytes(data[0:2], "big")
        key = data[2:2 + klen]
        vlen = int.from_bytes(data[2 + klen:6 + klen], "big")
        val_start = 6 + klen
        value = data[val_start:val_start + vlen]
        ts = struct.unpack(">d", data[val_start + vlen:val_start + vlen + 8])[0]
        tomb = data[val_start + vlen + 8] == 1
        return Record(key=key, value=value, timestamp=ts, tombstone=tomb)


class HashIndex:
    def __init__(self, bucket_count: int = 256):
        self._buckets: List[List[Tuple[bytes, bytes]]] = [[] for _ in range(bucket_count)]
        self._count = bucket_count

    def _hash(self, key: bytes) -> int:
        return int(hashlib.sha256(key).hexdigest()[:8], 16) % self._count

    def put(self, key: bytes, value: bytes) -> None:
        bucket = self._buckets[self._hash(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))

    def get(self, key: bytes) -> Optional[bytes]:
        for k, v in self._buckets[self._hash(key)]:
            if k == key:
                return v
        return None

    def delete(self, key: bytes) -> bool:
        bucket = self._buckets[self._hash(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                return True
        return False


class StorageEngine:
    def __init__(self, name: str = "default"):
        self.name = name
        self._btree = BTreeIndex()
        self._lsm = LSMTree(path=f"lsm_{name}")
        self._hash = HashIndex()
        self._txn_mgr = TransactionManager()
        self._wal = WriteAheadLog(path=f"{name}.wal")
        self._buffer = BufferPool()

    def open(self) -> None:
        self._wal.open()
        self._buffer.set_disk(f"{self.name}.data")

    def close(self) -> None:
        self._buffer.flush_all()
        self._wal.checkpoint()
        self._wal.close()

    def put(self, key: bytes, value: bytes, index: IndexType = IndexType.BTREE) -> None:
        if index == IndexType.BTREE:
            self._btree.insert(key, value)
        elif index == IndexType.LSM:
            self._lsm.put(key, value)
        elif index == IndexType.HASH:
            self._hash.put(key, value)

    def get(self, key: bytes, index: IndexType = IndexType.BTREE) -> Optional[bytes]:
        if index == IndexType.BTREE:
            return self._btree.search(key)
        elif index == IndexType.LSM:
            return self._lsm.get(key)
        elif index == IndexType.HASH:
            return self._hash.get(key)
        return None

    def delete(self, key: bytes, index: IndexType = IndexType.BTREE) -> None:
        if index == IndexType.BTREE:
            pass
        elif index == IndexType.LSM:
            self._lsm.delete(key)
        elif index == IndexType.HASH:
            self._hash.delete(key)

    def begin_txn(self, isolation: IsolationLevel = IsolationLevel.SERIALIZABLE) -> Transaction:
        return self._txn_mgr.begin(isolation)

    def commit_txn(self, txn: Transaction) -> bool:
        for change in txn.changes:
            self.put(change.key, change.new_value)
        return self._txn_mgr.commit(txn)

    def rollback_txn(self, txn: Transaction) -> bool:
        return self._txn_mgr.rollback(txn)

    def range_scan(self, start: Any, end: Any) -> List[Tuple[Any, Any]]:
        return self._btree.range_scan(start, end)

    def summary(self) -> Dict[str, Any]:
        return {
            "engine": self.name,
            "buffer_usage": self._buffer.usage,
            "wal_lsn": self._wal.last_lsn,
            "active_txns": self._txn_mgr.active_transactions(),
        }


def get_storage_engine(name: str = "default") -> StorageEngine:
    return StorageEngine(name)
