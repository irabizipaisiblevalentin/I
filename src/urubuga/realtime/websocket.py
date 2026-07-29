"""websocket — WebSocket support for urubuga.

Provides WebSocket connection management, rooms, channels,
pub/sub messaging, and presence tracking.
"""

from __future__ import annotations

import enum
import json
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set


class WebSocketState(enum.IntEnum):
    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3


class WebSocketMessage:
    """A WebSocket message."""
    __slots__ = ("data", "is_binary", "timestamp")

    def __init__(self, data: Any = "", is_binary: bool = False) -> None:
        self.data = data
        self.is_binary = is_binary
        self.timestamp = time.time()

    def json(self) -> Any:
        if isinstance(self.data, str):
            return json.loads(self.data)
        return self.data

    @classmethod
    def from_json(cls, data: Any) -> "WebSocketMessage":
        return cls(json.dumps(data))

    def __str__(self) -> str:
        return str(self.data)


class WebSocketConnection:
    """Represents a WebSocket connection."""
    __slots__ = ("id", "state", "rooms", "user", "metadata",
                 "_send_fn", "_close_fn", "connected_at")

    _counter = 0

    def __init__(self, send_fn: Optional[Callable] = None,
                 close_fn: Optional[Callable] = None,
                 user: Any = None) -> None:
        WebSocketConnection._counter += 1
        self.id = f"ws_{WebSocketConnection._counter}"
        self.state = WebSocketState.CONNECTING
        self.rooms: Set[str] = set()
        self.user = user
        self.metadata: Dict[str, Any] = {}
        self._send_fn = send_fn
        self._close_fn = close_fn
        self.connected_at = time.time()

    async def send(self, data: Any) -> None:
        if self._send_fn:
            msg = WebSocketMessage(data)
            if self._send_fn.__code__.co_flags & 0x100:
                await self._send_fn(msg)
            else:
                self._send_fn(msg)

    async def send_json(self, data: Any) -> None:
        await self.send(json.dumps(data))

    async def close(self, code: int = 1000, reason: str = "") -> None:
        self.state = WebSocketState.CLOSING
        if self._close_fn:
            self._close_fn(code, reason)
        self.state = WebSocketState.CLOSED

    @property
    def is_open(self) -> bool:
        return self.state == WebSocketState.OPEN

    @property
    def uptime(self) -> float:
        return time.time() - self.connected_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "state": self.state.name,
            "rooms": list(self.rooms),
            "uptime": self.uptime,
        }


class Room:
    """A WebSocket room for group messaging."""
    __slots__ = ("name", "_connections", "metadata")

    def __init__(self, name: str) -> None:
        self.name = name
        self._connections: Dict[str, WebSocketConnection] = {}
        self.metadata: Dict[str, Any] = {}

    async def join(self, connection: WebSocketConnection) -> None:
        self._connections[connection.id] = connection
        connection.rooms.add(self.name)

    async def leave(self, connection: WebSocketConnection) -> None:
        self._connections.pop(connection.id, None)
        connection.rooms.discard(self.name)

    async def broadcast(self, data: Any,
                        exclude: Optional[str] = None) -> int:
        count = 0
        for conn_id, conn in list(self._connections.items()):
            if conn_id != exclude and conn.is_open:
                await conn.send(data)
                count += 1
        return count

    async def broadcast_json(self, data: Any,
                             exclude: Optional[str] = None) -> int:
        return await self.broadcast(json.dumps(data), exclude)

    @property
    def connection_count(self) -> int:
        return len(self._connections)

    def connections(self) -> List[WebSocketConnection]:
        return list(self._connections.values())


class Presence:
    """Tracks who is online and their status."""

    def __init__(self) -> None:
        self._users: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def join(self, user_id: str, connection_id: str,
             status: str = "online") -> None:
        with self._lock:
            self._users[user_id] = {
                "connection_id": connection_id,
                "status": status,
                "joined_at": time.time(),
            }

    def leave(self, user_id: str) -> None:
        with self._lock:
            self._users.pop(user_id, None)

    def update_status(self, user_id: str, status: str) -> None:
        with self._lock:
            if user_id in self._users:
                self._users[user_id]["status"] = status

    def is_online(self, user_id: str) -> bool:
        return user_id in self._users

    def online_users(self) -> List[str]:
        return list(self._users.keys())

    def online_count(self) -> int:
        return len(self._users)

    def get_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._users.get(user_id)


class WebSocketManager:
    """Manages WebSocket connections, rooms, and presence."""

    def __init__(self) -> None:
        self._connections: Dict[str, WebSocketConnection] = {}
        self._rooms: Dict[str, Room] = {}
        self._presence = Presence()
        self._handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()

    def add_connection(self, conn: WebSocketConnection) -> None:
        with self._lock:
            self._connections[conn.id] = conn
            conn.state = WebSocketState.OPEN

    def remove_connection(self, conn_id: str) -> Optional[WebSocketConnection]:
        with self._lock:
            conn = self._connections.pop(conn_id, None)
            if conn:
                conn.state = WebSocketState.CLOSED
                for room_name in list(conn.rooms):
                    room = self._rooms.get(room_name)
                    if room:
                        import asyncio
                        if asyncio.iscoroutinefunction(room.leave):
                            pass
                        else:
                            room._connections.pop(conn_id, None)
                            conn.rooms.discard(room_name)
            return conn

    def get_room(self, name: str) -> Room:
        if name not in self._rooms:
            self._rooms[name] = Room(name)
        return self._rooms[name]

    async def join_room(self, conn: WebSocketConnection,
                        room_name: str) -> None:
        room = self.get_room(room_name)
        await room.join(conn)

    async def leave_room(self, conn: WebSocketConnection,
                         room_name: str) -> None:
        room = self._rooms.get(room_name)
        if room:
            await room.leave(conn)

    async def send_to(self, conn_id: str, data: Any) -> bool:
        conn = self._connections.get(conn_id)
        if conn and conn.is_open:
            await conn.send(data)
            return True
        return False

    async def broadcast(self, data: Any,
                        exclude: Optional[str] = None) -> int:
        count = 0
        for conn in list(self._connections.values()):
            if conn.id != exclude and conn.is_open:
                await conn.send(data)
                count += 1
        return count

    @property
    def presence(self) -> Presence:
        return self._presence

    def connection_count(self) -> int:
        return len(self._connections)

    def room_count(self) -> int:
        return len(self._rooms)

    def room_names(self) -> List[str]:
        return list(self._rooms.keys())

    def get_connection(self, conn_id: str) -> Optional[WebSocketConnection]:
        return self._connections.get(conn_id)
