"""sse — Server-Sent Events support.

Provides SSE stream creation, event broadcasting, and client management.
"""

from __future__ import annotations

import json
import threading
import time
from typing import Any, Callable, Dict, List, Optional


class SSEEvent:
    """A Server-Sent Event."""
    __slots__ = ("event", "data", "id", "retry", "comment")

    def __init__(self, data: Any = "", event: str = "message",
                 id: Optional[str] = None, retry: Optional[int] = None,
                 comment: str = "") -> None:
        self.event = event
        self.data = data
        self.id = id
        self.retry = retry
        self.comment = comment

    def to_string(self) -> str:
        parts = []
        if self.comment:
            parts.append(f": {self.comment}")
        if self.event:
            parts.append(f"event: {self.event}")
        if self.id:
            parts.append(f"id: {self.id}")
        if self.retry is not None:
            parts.append(f"retry: {self.retry}")
        data = self.data if isinstance(self.data, str) else json.dumps(self.data)
        for line in data.split("\n"):
            parts.append(f"data: {line}")
        return "\n".join(parts) + "\n\n"

    @classmethod
    def json(cls, data: Any, event: str = "message",
             id: Optional[str] = None) -> "SSEEvent":
        return cls(json.dumps(data, default=str), event, id)

    @classmethod
    def heartbeat(cls) -> "SSEEvent":
        return cls(comment="heartbeat")


class SSEClient:
    """Represents an SSE client connection."""
    __slots__ = ("id", "stream_fn", "connected_at", "last_event_id",
                 "topics", "_closed")

    _counter = 0

    def __init__(self, stream_fn: Optional[Callable] = None) -> None:
        SSEClient._counter += 1
        self.id = f"sse_{SSEClient._counter}"
        self.stream_fn = stream_fn
        self.connected_at = time.time()
        self.last_event_id: Optional[str] = None
        self.topics: set = set()
        self._closed = False

    async def send(self, event: SSEEvent) -> None:
        if self._closed or not self.stream_fn:
            return
        data = event.to_string()
        if self.stream_fn.__code__.co_flags & 0x100:
            await self.stream_fn(data)
        else:
            self.stream_fn(data)

    async def send_json(self, data: Any, event: str = "message") -> None:
        await self.send(SSEEvent.json(data, event))

    def close(self) -> None:
        self._closed = True

    @property
    def is_open(self) -> bool:
        return not self._closed

    @property
    def uptime(self) -> float:
        return time.time() - self.connected_at


class SSEManager:
    """Manages SSE client connections and event broadcasting."""

    def __init__(self) -> None:
        self._clients: Dict[str, SSEClient] = {}
        self._topics: Dict[str, Set[str]] = {}
        self._lock = threading.Lock()
        self._event_count = 0

    def add_client(self, client: SSEClient) -> None:
        with self._lock:
            self._clients[client.id] = client

    def remove_client(self, client_id: str) -> Optional[SSEClient]:
        with self._lock:
            client = self._clients.pop(client_id, None)
            if client:
                for topic in client.topics:
                    subs = self._topics.get(topic, set())
                    subs.discard(client_id)
            return client

    def subscribe(self, client_id: str, topic: str) -> None:
        with self._lock:
            client = self._clients.get(client_id)
            if client:
                client.topics.add(topic)
                self._topics.setdefault(topic, set()).add(client_id)

    def unsubscribe(self, client_id: str, topic: str) -> None:
        with self._lock:
            client = self._clients.get(client_id)
            if client:
                client.topics.discard(topic)
            subs = self._topics.get(topic, set())
            subs.discard(client_id)

    async def send(self, client_id: str, event: SSEEvent) -> bool:
        client = self._clients.get(client_id)
        if client and client.is_open:
            self._event_count += 1
            await client.send(event)
            return True
        return False

    async def broadcast(self, event: SSEEvent,
                        topic: Optional[str] = None) -> int:
        self._event_count += 1
        count = 0
        if topic:
            client_ids = self._topics.get(topic, set())
            for cid in client_ids:
                client = self._clients.get(cid)
                if client and client.is_open:
                    await client.send(event)
                    count += 1
        else:
            for client in list(self._clients.values()):
                if client.is_open:
                    await client.send(event)
                    count += 1
        return count

    async def broadcast_json(self, data: Any,
                             topic: Optional[str] = None,
                             event: str = "message") -> int:
        return await self.broadcast(SSEEvent.json(data, event), topic)

    def client_count(self) -> int:
        return len(self._clients)

    def topic_count(self) -> int:
        return len(self._topics)

    @property
    def event_count(self) -> int:
        return self._event_count

    def clients(self) -> List[SSEClient]:
        return list(self._clients.values())

    def topic_clients(self, topic: str) -> List[SSEClient]:
        client_ids = self._topics.get(topic, set())
        return [self._clients[cid] for cid in client_ids
                if cid in self._clients]
