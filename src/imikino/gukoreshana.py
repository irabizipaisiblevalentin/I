"""gukoreshana — Networking/multiplayer: client-server, P2P, replication, matchmaking."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class NetworkRole(str, Enum):
    CLIENT = "client"
    SERVER = "server"
    HOST = "host"
    DEDICATED_SERVER = "dedicated_server"


class ConnectionState(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    DISCONNECTING = "disconnecting"


@dataclass
class NetworkMessage:
    msg_type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    sender_id: str = ""
    timestamp: float = 0.0
    reliable: bool = True
    sequence: int = 0
    message_id: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()
        if not self.message_id:
            import uuid
            self.message_id = uuid.uuid4().hex[:12]

    def to_bytes(self) -> bytes:
        return json.dumps({
            "type": self.msg_type,
            "data": self.data,
            "sender": self.sender_id,
            "ts": self.timestamp,
            "seq": self.sequence,
            "mid": self.message_id,
        }).encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> NetworkMessage:
        d = json.loads(data.decode("utf-8"))
        return cls(
            msg_type=d["type"], data=d.get("data", {}),
            sender_id=d.get("sender", ""), timestamp=d.get("ts", 0),
            sequence=d.get("seq", 0), message_id=d.get("mid", ""),
        )


@dataclass
class NetworkPeer:
    peer_id: str = ""
    address: str = ""
    port: int = 0
    state: ConnectionState = ConnectionState.DISCONNECTED
    latency_ms: float = 0.0
    connected_at: float = 0.0
    player_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplicatedProperty:
    name: str = ""
    value: Any = None
    owner: str = ""
    sync_mode: str = "always"


@dataclass
class ReplicatedObject:
    object_id: str = ""
    prefab: str = ""
    owner_id: str = ""
    properties: Dict[str, ReplicatedProperty] = field(default_factory=dict)


class NetworkManager:
    def __init__(self):
        self.role: NetworkRole = NetworkRole.CLIENT
        self.peer_id: str = ""
        self.peers: Dict[str, NetworkPeer] = {}
        self.replicated_objects: Dict[str, ReplicatedObject] = {}
        self._message_handlers: Dict[str, List[Callable]] = {}
        self._sequence: int = 0
        self._local_objects: Dict[str, ReplicatedObject] = {}
        self._latency_samples: List[float] = []

    def start_server(self, port: int = 7777, max_players: int = 16) -> None:
        self.role = NetworkRole.SERVER
        import uuid
        self.peer_id = f"server_{uuid.uuid4().hex[:8]}"

    def start_client(self, host: str = "localhost", port: int = 7777) -> None:
        self.role = NetworkRole.CLIENT
        import uuid
        self.peer_id = f"client_{uuid.uuid4().hex[:8]}"

    def start_host(self, port: int = 7777) -> None:
        self.role = NetworkRole.HOST
        import uuid
        self.peer_id = f"host_{uuid.uuid4().hex[:8]}"

    def send(self, target_id: str, message: NetworkMessage) -> None:
        message.sender_id = self.peer_id
        message.sequence = self._sequence
        self._sequence += 1

    def broadcast(self, message: NetworkMessage) -> None:
        message.sender_id = self.peer_id
        message.sequence = self._sequence
        self._sequence += 1

    def register_handler(self, msg_type: str, handler: Callable) -> None:
        if msg_type not in self._message_handlers:
            self._message_handlers[msg_type] = []
        self._message_handlers[msg_type].append(handler)

    def on_message(self, message: NetworkMessage) -> None:
        for handler in self._message_handlers.get(message.msg_type, []):
            try:
                handler(message)
            except Exception:
                pass

    def create_replicated_object(self, prefab: str,
                                  properties: Optional[Dict[str, Any]] = None) -> str:
        import uuid
        obj_id = f"obj_{uuid.uuid4().hex[:12]}"
        obj = ReplicatedObject(
            object_id=obj_id, prefab=prefab,
            owner_id=self.peer_id,
        )
        if properties:
            for k, v in properties.items():
                obj.properties[k] = ReplicatedProperty(name=k, value=v, owner=self.peer_id)
        self.replicated_objects[obj_id] = obj
        return obj_id

    def destroy_replicated_object(self, object_id: str) -> bool:
        if object_id in self.replicated_objects:
            del self.replicated_objects[object_id]
            return True
        return False

    def measure_latency(self, peer_id: str) -> float:
        peer = self.peers.get(peer_id)
        return peer.latency_ms if peer else 0.0

    def disconnect(self) -> None:
        self.peers.clear()
        self.state = ConnectionState.DISCONNECTED

    @property
    def state(self) -> ConnectionState:
        if self.peer_id and self.role in (NetworkRole.SERVER, NetworkRole.HOST):
            return ConnectionState.CONNECTED
        return ConnectionState.DISCONNECTED

    @state.setter
    def state(self, value: ConnectionState) -> None:
        pass

    def summary(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "peer_id": self.peer_id,
            "peers": len(self.peers),
            "replicated_objects": len(self.replicated_objects),
            "message_handlers": len(self._message_handlers),
        }


class Matchmaker:
    def __init__(self):
        self.rooms: Dict[str, Dict[str, Any]] = {}

    def create_room(self, name: str, max_players: int = 16,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        import uuid
        room_id = f"room_{uuid.uuid4().hex[:8]}"
        self.rooms[room_id] = {
            "name": name,
            "room_id": room_id,
            "max_players": max_players,
            "players": [],
            "metadata": metadata or {},
            "created": time.time(),
        }
        return room_id

    def join_room(self, room_id: str, player_id: str) -> bool:
        room = self.rooms.get(room_id)
        if room and len(room["players"]) < room["max_players"]:
            room["players"].append(player_id)
            return True
        return False

    def leave_room(self, room_id: str, player_id: str) -> bool:
        room = self.rooms.get(room_id)
        if room and player_id in room["players"]:
            room["players"].remove(player_id)
            return True
        return False

    def list_rooms(self) -> List[Dict[str, Any]]:
        return [
            {"id": rid, "name": r["name"],
             "players": len(r["players"]), "max": r["max_players"]}
            for rid, r in self.rooms.items()
        ]


_network = NetworkManager()


def get_network() -> NetworkManager:
    return _network
