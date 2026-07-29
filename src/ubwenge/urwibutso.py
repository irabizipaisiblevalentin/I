"""Memory system — short-term, long-term, vector, knowledge graph, conversation, persistent."""

from __future__ import annotations

import json
import math
import sqlite3
import threading
import time
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime


@dataclass
class MemoryEntry:
    key: str = ""
    content: str = ""
    content_type: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    importance: float = 0.5
    embedding: Optional[List[float]] = field(default=None)
    ttl_seconds: float = 0.0
    source: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()

    @property
    def is_expired(self) -> bool:
        if self.ttl_seconds <= 0:
            return False
        return time.time() - self.timestamp > self.ttl_seconds


class MemoryStore:
    def __init__(self, max_size: int = 10000):
        self._entries: Dict[str, MemoryEntry] = OrderedDict()
        self._max_size = max_size
        self._lock = threading.RLock()

    def store(self, entry: MemoryEntry) -> str:
        with self._lock:
            key = entry.key or f"mem_{int(time.time() * 1000)}_{len(self._entries)}"
            entry.key = key
            self._entries[key] = entry
            self._enforce_limit()
            return key

    def get(self, key: str) -> Optional[MemoryEntry]:
        with self._lock:
            entry = self._entries.get(key)
            if entry and entry.is_expired:
                del self._entries[key]
                return None
            return entry

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._entries:
                del self._entries[key]
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()

    def search(self, query: str, top_k: int = 10,
               content_type: Optional[str] = None) -> List[MemoryEntry]:
        with self._lock:
            results = []
            query_lower = query.lower()
            for entry in self._entries.values():
                if entry.is_expired:
                    continue
                if content_type and entry.content_type != content_type:
                    continue
                if query_lower in entry.content.lower():
                    results.append(entry)
            results.sort(key=lambda e: e.importance, reverse=True)
            return results[:top_k]

    def recent(self, limit: int = 20) -> List[MemoryEntry]:
        with self._lock:
            entries = [e for e in self._entries.values() if not e.is_expired]
            entries.sort(key=lambda e: e.timestamp, reverse=True)
            return entries[:limit]

    def count(self) -> int:
        with self._lock:
            return len(self._entries)

    def _enforce_limit(self) -> None:
        while len(self._entries) > self._max_size:
            oldest = next(iter(self._entries))
            del self._entries[oldest]


class ShortTermMemory:
    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.messages: List[Dict[str, Any]] = []

    def add(self, role: str, content: str, **kwargs: Any) -> None:
        self.messages.append({"role": role, "content": content, **kwargs})
        if len(self.messages) > self.capacity:
            self.messages = self.messages[-self.capacity:]

    def get_context(self, max_tokens: int = 4000) -> List[Dict[str, Any]]:
        total = 0
        context = []
        for msg in reversed(self.messages):
            approx = len(msg["content"]) // 4 + 10
            if total + approx > max_tokens:
                break
            context.insert(0, msg)
            total += approx
        return context

    def clear(self) -> None:
        self.messages.clear()


class LongTermMemory:
    def __init__(self, storage_path: str = "./memory/ltm"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._db_path = self.storage_path / "ltm.db"
        self._init_db()
        self._cache: Dict[str, MemoryEntry] = {}

    def _init_db(self) -> None:
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                key TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'text',
                metadata TEXT DEFAULT '{}',
                timestamp REAL NOT NULL,
                importance REAL DEFAULT 0.5,
                source TEXT DEFAULT ''
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)
        """)
        self._conn.commit()

    def store(self, entry: MemoryEntry) -> str:
        key = entry.key or f"ltm_{int(time.time() * 1000)}"
        entry.key = key
        self._conn.execute(
            "INSERT OR REPLACE INTO memories VALUES (?, ?, ?, ?, ?, ?, ?)",
            (key, entry.content, entry.content_type, json.dumps(entry.metadata),
             entry.timestamp, entry.importance, entry.source),
        )
        self._conn.commit()
        self._cache[key] = entry
        return key

    def get(self, key: str) -> Optional[MemoryEntry]:
        if key in self._cache:
            return self._cache[key]
        row = self._conn.execute("SELECT * FROM memories WHERE key=?", (key,)).fetchone()
        if not row:
            return None
        entry = MemoryEntry(
            key=row[0], content=row[1], content_type=row[2],
            metadata=json.loads(row[3]), timestamp=row[4],
            importance=row[5], source=row[6],
        )
        self._cache[key] = entry
        return entry

    def search(self, query: str, top_k: int = 10,
               content_type: Optional[str] = None) -> List[MemoryEntry]:
        sql = "SELECT * FROM memories WHERE content LIKE ?"
        params = [f"%{query}%"]
        if content_type:
            sql += " AND content_type=?"
            params.append(content_type)
        sql += " ORDER BY importance DESC LIMIT ?"
        params.append(top_k)
        rows = self._conn.execute(sql, params).fetchall()
        return [MemoryEntry(key=r[0], content=r[1], content_type=r[2],
                            metadata=json.loads(r[3]), timestamp=r[4],
                            importance=r[5], source=r[6]) for r in rows]

    def delete(self, key: str) -> bool:
        self._conn.execute("DELETE FROM memories WHERE key=?", (key,))
        self._conn.commit()
        self._cache.pop(key, None)
        return True

    def clear(self) -> None:
        self._conn.execute("DELETE FROM memories")
        self._conn.commit()
        self._cache.clear()

    def count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) FROM memories").fetchone()
        return row[0] if row else 0


class VectorMemory:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._entries: Dict[str, Tuple[MemoryEntry, List[float]]] = {}
        self._lock = threading.RLock()

    def store(self, entry: MemoryEntry) -> str:
        with self._lock:
            key = entry.key or f"vec_{int(time.time() * 1000)}"
            entry.key = key
            emb = entry.embedding or [0.0] * self.dimension
            if len(emb) != self.dimension:
                emb = emb[:self.dimension] + [0.0] * (self.dimension - len(emb[:self.dimension]))
            self._entries[key] = (entry, emb)
            return key

    def search(self, query_embedding: List[float], top_k: int = 10) -> List[Tuple[MemoryEntry, float]]:
        with self._lock:
            if not self._entries:
                return []
            q = query_embedding[:self.dimension]
            if len(q) < self.dimension:
                q = q + [0.0] * (self.dimension - len(q))
            scored = []
            for entry, emb in self._entries.values():
                sim = self._cosine_similarity(q, emb)
                scored.append((entry, sim))
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[:top_k]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def count(self) -> int:
        return len(self._entries)

    def clear(self) -> None:
        self._entries.clear()


class KnowledgeGraph:
    def __init__(self):
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[Tuple[str, str, str, Dict[str, Any]]] = []
        self._lock = threading.RLock()

    def add_node(self, node_id: str, label: str = "",
                 properties: Optional[Dict[str, Any]] = None) -> None:
        with self._lock:
            self._nodes[node_id] = {
                "label": label, "properties": properties or {},
            }

    def add_edge(self, source: str, target: str, relation: str,
                 properties: Optional[Dict[str, Any]] = None) -> None:
        with self._lock:
            self._edges.append((source, target, relation, properties or {}))
            if source not in self._nodes:
                self.add_node(source)
            if target not in self._nodes:
                self.add_node(target)

    def get_neighbors(self, node_id: str,
                      max_depth: int = 1) -> List[Dict[str, Any]]:
        with self._lock:
            visited = {node_id}
            results = []
            queue = [(node_id, 0)]
            while queue:
                current, depth = queue.pop(0)
                if depth >= max_depth:
                    continue
                for s, t, r, p in self._edges:
                    if s == current and t not in visited:
                        visited.add(t)
                        results.append({
                            "node_id": t,
                            "node": self._nodes.get(t, {}),
                            "relation": r,
                            "depth": depth + 1,
                        })
                        queue.append((t, depth + 1))
                    elif t == current and s not in visited:
                        visited.add(s)
                        results.append({
                            "node_id": s,
                            "node": self._nodes.get(s, {}),
                            "relation": r,
                            "depth": depth + 1,
                        })
                        queue.append((s, depth + 1))
            return results

    def query(self, label: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            if label:
                return [{"id": nid, **props}
                        for nid, props in self._nodes.items()
                        if props.get("label") == label]
            return [{"id": nid, **props} for nid, props in self._nodes.items()]


class ConversationMemory:
    def __init__(self, max_turns: int = 100):
        self.turns: List[Dict[str, Any]] = []
        self.max_turns = max_turns

    def add_turn(self, user: str, assistant: str,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        self.turns.append({
            "user": user, "assistant": assistant,
            "timestamp": time.time(),
            "metadata": metadata or {},
        })
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit:
            return self.turns[-limit:]
        return self.turns

    def summarize(self, max_turns: int = 5) -> str:
        recent = self.turns[-max_turns:]
        lines = []
        for t in recent:
            lines.append(f"User: {t['user'][:100]}")
            lines.append(f"Assistant: {t['assistant'][:100]}")
        return "\n".join(lines)

    def clear(self) -> None:
        self.turns.clear()
