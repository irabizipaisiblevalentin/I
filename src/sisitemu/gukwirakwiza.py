"""gukwirakwiza — Distributed systems: Raft consensus, RPC, service discovery, distributed locks, message queues."""

from __future__ import annotations

import enum
import hashlib
import json
import logging
import os
import random
import socket
import struct
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


logger = logging.getLogger(__name__)


class RaftRole(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


@dataclass
class LogEntry:
    index: int = 0
    term: int = 0
    command: str = ""
    data: bytes = b""

    def to_dict(self) -> Dict[str, Any]:
        return {"index": self.index, "term": self.term,
                "command": self.command, "data": self.data.hex()}

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> LogEntry:
        return LogEntry(index=d["index"], term=d["term"],
                        command=d["command"], data=bytes.fromhex(d.get("data", "")))


@dataclass
class RaftConfig:
    node_id: str = ""
    peers: List[str] = field(default_factory=list)
    election_timeout_min: int = 150
    election_timeout_max: int = 300
    heartbeat_interval: int = 50
    data_dir: str = "raft_data"


class RaftConsensus:
    def __init__(self, config: RaftConfig):
        self.config = config
        self._current_term: int = 0
        self._voted_for: Optional[str] = None
        self._role: RaftRole = RaftRole.FOLLOWER
        self._leader_id: Optional[str] = None
        self._log: List[LogEntry] = []
        self._commit_index: int = 0
        self._last_applied: int = 0
        self._next_index: Dict[str, int] = {}
        self._match_index: Dict[str, int] = {}
        self._election_timer: float = 0.0
        self._election_timeout: int = config.election_timeout_min
        self._last_heartbeat: float = 0.0
        self._lock = threading.Lock()
        self._running = False
        self._state_machine: Dict[str, Callable] = {}
        self._leader_lease_duration: float = 1.0
        self._lease_expiry: float = 0.0
        self._snapshot: Dict[str, Any] = {}
        self._snapshot_index: int = 0

    def start(self) -> None:
        self._running = True
        self._reset_election_timeout()
        logger.info(f"Raft node {self.config.node_id} started")

    def stop(self) -> None:
        self._running = False
        logger.info(f"Raft node {self.config.node_id} stopped")

    def _reset_election_timeout(self) -> None:
        self._election_timeout = random.randint(
            self.config.election_timeout_min,
            self.config.election_timeout_max,
        )
        self._last_heartbeat = time.time()

    def tick(self) -> Optional[str]:
        if not self._running:
            return None
        with self._lock:
            now = time.time()
            if self._role != RaftRole.LEADER:
                if now - self._last_heartbeat > self._election_timeout / 1000.0:
                    return self._start_election()
            else:
                if now - self._last_heartbeat > self.config.heartbeat_interval / 1000.0:
                    self._last_heartbeat = now
                    return "heartbeat"
            return None

    def _start_election(self) -> str:
        self._role = RaftRole.CANDIDATE
        self._current_term += 1
        self._voted_for = self.config.node_id
        self._reset_election_timeout()
        votes = 1
        quorum = len(self.config.peers) // 2 + 1
        for peer in self.config.peers:
            if self._request_vote(peer):
                votes += 1
        if votes >= quorum:
            self._become_leader()
            return "elected"
        self._role = RaftRole.FOLLOWER
        return "not_elected"

    def _request_vote(self, peer: str) -> bool:
        last_log_index = len(self._log)
        last_log_term = self._log[-1].term if self._log else 0
        resp = self._send_rpc(peer, "request_vote", {
            "term": self._current_term,
            "candidate_id": self.config.node_id,
            "last_log_index": last_log_index,
            "last_log_term": last_log_term,
        })
        if resp and resp.get("vote_granted"):
            return True
        return False

    def handle_request_vote(self, term: int, candidate_id: str,
                            last_log_index: int, last_log_term: int) -> Dict[str, Any]:
        with self._lock:
            if term < self._current_term:
                return {"term": self._current_term, "vote_granted": False}
            if term > self._current_term:
                self._current_term = term
                self._role = RaftRole.FOLLOWER
                self._voted_for = None
            if (self._voted_for is None or self._voted_for == candidate_id):
                my_last_term = self._log[-1].term if self._log else 0
                my_last_index = len(self._log)
                if last_log_term > my_last_term or (
                    last_log_term == my_last_term and last_log_index >= my_last_index
                ):
                    self._voted_for = candidate_id
                    self._reset_election_timeout()
                    return {"term": self._current_term, "vote_granted": True}
            return {"term": self._current_term, "vote_granted": False}

    def _become_leader(self) -> None:
        self._role = RaftRole.LEADER
        self._leader_id = self.config.node_id
        for peer in self.config.peers:
            self._next_index[peer] = len(self._log) + 1
            self._match_index[peer] = 0
        self._lease_expiry = time.time() + self._leader_lease_duration
        logger.info(f"Node {self.config.node_id} became leader for term {self._current_term}")

    def append_entries(self, entries: List[LogEntry]) -> Optional[int]:
        if self._role != RaftRole.LEADER:
            return None
        with self._lock:
            for entry in entries:
                entry.term = self._current_term
                entry.index = len(self._log) + 1
                self._log.append(entry)
            self._replicate_log()
            return len(self._log)

    def _replicate_log(self) -> None:
        for peer in self.config.peers:
            prev_index = self._next_index[peer] - 1
            prev_term = self._log[prev_index - 1].term if prev_index > 0 and prev_index <= len(self._log) else 0
            entries = self._log[self._next_index[peer] - 1:]
            resp = self._send_rpc(peer, "append_entries", {
                "term": self._current_term,
                "leader_id": self.config.node_id,
                "prev_log_index": prev_index,
                "prev_log_term": prev_term,
                "entries": [e.to_dict() for e in entries],
                "leader_commit": self._commit_index,
            })
            if resp:
                if resp.get("success"):
                    self._match_index[peer] = resp.get("match_index", 0)
                    self._next_index[peer] = self._match_index[peer] + 1
                else:
                    self._next_index[peer] = max(1, self._next_index[peer] - 1)
        self._advance_commit_index()

    def handle_append_entries(self, term: int, leader_id: str,
                              prev_log_index: int, prev_log_term: int,
                              entries: List[Dict[str, Any]],
                              leader_commit: int) -> Dict[str, Any]:
        with self._lock:
            if term < self._current_term:
                return {"term": self._current_term, "success": False}
            if term >= self._current_term:
                self._current_term = term
                self._role = RaftRole.FOLLOWER
                self._leader_id = leader_id
                self._reset_election_timeout()
            if prev_log_index > len(self._log):
                return {"term": self._current_term, "success": False}
            if prev_log_index > 0:
                if prev_log_index > len(self._log):
                    return {"term": self._current_term, "success": False}
            for e_dict in entries:
                entry = LogEntry.from_dict(e_dict)
                if entry.index <= len(self._log):
                    if self._log[entry.index - 1].term != entry.term:
                        self._log = self._log[:entry.index - 1]
                        self._log.append(entry)
                else:
                    self._log.append(entry)
            if leader_commit > self._commit_index:
                self._commit_index = min(leader_commit, len(self._log))
            return {"term": self._current_term, "success": True,
                    "match_index": len(self._log)}

    def _advance_commit_index(self) -> None:
        for n in range(self._commit_index + 1, len(self._log) + 1):
            if self._log[n - 1].term == self._current_term:
                replicas = 1
                for peer in self.config.peers:
                    if self._match_index.get(peer, 0) >= n:
                        replicas += 1
                if replicas > len(self.config.peers) // 2:
                    self._commit_index = n
                    self._apply_log_entries()

    def _apply_log_entries(self) -> None:
        while self._last_applied < self._commit_index:
            self._last_applied += 1
            entry = self._log[self._last_applied - 1]
            handler = self._state_machine.get(entry.command)
            if handler:
                try:
                    handler(entry.data)
                except Exception as e:
                    logger.error(f"Apply failed: {e}")

    def register_command(self, name: str, handler: Callable) -> None:
        self._state_machine[name] = handler

    def propose(self, command: str, data: bytes) -> Optional[int]:
        if self._role != RaftRole.LEADER:
            return None
        entry = LogEntry(command=command, data=data)
        return self.append_entries([entry])

    def _send_rpc(self, peer: str, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            host, port_str = peer.split(":")
            port = int(port_str)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            sock.connect((host, port))
            msg = json.dumps({"method": method, "params": params}).encode()
            sock.send(struct.pack(">I", len(msg)) + msg)
            resp_len = struct.unpack(">I", sock.recv(4))[0]
            resp = json.loads(sock.recv(resp_len).decode())
            sock.close()
            return resp
        except Exception as e:
            logger.debug(f"RPC to {peer} failed: {e}")
            return None

    @property
    def leader(self) -> Optional[str]:
        return self._leader_id

    @property
    def role(self) -> RaftRole:
        return self._role

    @property
    def current_term(self) -> int:
        return self._current_term

    def summary(self) -> Dict[str, Any]:
        return {
            "node": self.config.node_id,
            "role": self._role.value,
            "term": self._current_term,
            "leader": self._leader_id,
            "log_size": len(self._log),
            "commit_index": self._commit_index,
            "peers": self.config.peers,
        }


class RPCHandler:
    def handle(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class RPCServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 9000):
        self.host = host
        self.port = port
        self._handlers: Dict[str, RPCHandler] = {}
        self._running = False
        self._server_sock: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None

    def register(self, name: str, handler: RPCHandler) -> None:
        self._handlers[name] = handler

    def start(self) -> None:
        self._running = True
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind((self.host, self.port))
        self._server_sock.listen(10)
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._server_sock:
            self._server_sock.close()

    def _serve(self) -> None:
        while self._running:
            try:
                conn, addr = self._server_sock.accept()
                threading.Thread(target=self._handle_conn, args=(conn,), daemon=True).start()
            except Exception:
                break

    def _handle_conn(self, conn: socket.socket) -> None:
        try:
            data = conn.recv(4)
            if not data:
                return
            msg_len = struct.unpack(">I", data)[0]
            msg = conn.recv(msg_len)
            req = json.loads(msg.decode())
            method = req.get("method", "")
            params = req.get("params", {})
            result: Optional[Dict[str, Any]] = None
            for handler in self._handlers.values():
                result = handler.handle(method, params)
                if result is not None:
                    break
            if result is None:
                result = {"error": "unknown method"}
            resp = json.dumps(result).encode()
            conn.send(struct.pack(">I", len(resp)) + resp)
        except Exception as e:
            logger.debug(f"RPC handler error: {e}")
        finally:
            conn.close()


@dataclass
class ServiceInstance:
    id: str = ""
    name: str = ""
    host: str = ""
    port: int = 0
    health_endpoint: str = "/health"
    metadata: Dict[str, str] = field(default_factory=dict)
    registered_at: float = 0.0
    ttl: int = 30


class ServiceDiscovery:
    def __init__(self):
        self._services: Dict[str, List[ServiceInstance]] = {}
        self._lock = threading.Lock()

    def register(self, instance: ServiceInstance) -> None:
        with self._lock:
            instance.registered_at = time.time()
            if instance.name not in self._services:
                self._services[instance.name] = []
            for existing in self._services[instance.name]:
                if existing.id == instance.id:
                    existing.host = instance.host
                    existing.port = instance.port
                    existing.registered_at = time.time()
                    return
            self._services[instance.name].append(instance)

    def unregister(self, service_name: str, instance_id: str) -> bool:
        with self._lock:
            if service_name not in self._services:
                return False
            before = len(self._services[service_name])
            self._services[service_name] = [
                s for s in self._services[service_name] if s.id != instance_id
            ]
            return len(self._services[service_name]) < before

    def discover(self, service_name: str) -> List[ServiceInstance]:
        with self._lock:
            instances = self._services.get(service_name, [])
            now = time.time()
            healthy = [
                s for s in instances
                if now - s.registered_at < s.ttl
            ]
            self._services[service_name] = healthy
            return list(healthy)

    def list_services(self) -> List[str]:
        with self._lock:
            return list(self._services.keys())

    def health_check(self, service_name: str) -> bool:
        instances = self.discover(service_name)
        return len(instances) > 0


@dataclass
class LockRequest:
    lock_id: str = ""
    holder_id: str = ""
    ttl: int = 30
    acquired_at: float = 0.0
    fence_token: int = 0


class DistributedLock:
    def __init__(self):
        self._locks: Dict[str, LockRequest] = {}
        self._lock = threading.Lock()

    def acquire(self, lock_id: str, holder_id: str, ttl: int = 30) -> Optional[int]:
        with self._lock:
            existing = self._locks.get(lock_id)
            now = time.time()
            if existing:
                if now - existing.acquired_at < existing.ttl:
                    if existing.holder_id != holder_id:
                        return None
                    existing.ttl = ttl
                    return existing.fence_token
            req = LockRequest(
                lock_id=lock_id,
                holder_id=holder_id,
                ttl=ttl,
                acquired_at=now,
                fence_token=int(time.time() * 1000),
            )
            self._locks[lock_id] = req
            return req.fence_token

    def release(self, lock_id: str, holder_id: str, fence_token: int) -> bool:
        with self._lock:
            existing = self._locks.get(lock_id)
            if not existing:
                return False
            if existing.holder_id != holder_id or existing.fence_token != fence_token:
                return False
            del self._locks[lock_id]
            return True

    def is_locked(self, lock_id: str) -> bool:
        with self._lock:
            existing = self._locks.get(lock_id)
            if not existing:
                return False
            if time.time() - existing.acquired_at > existing.ttl:
                del self._locks[lock_id]
                return False
            return True

    def refresh(self, lock_id: str, holder_id: str) -> Optional[int]:
        with self._lock:
            existing = self._locks.get(lock_id)
            if not existing or existing.holder_id != holder_id:
                return None
            existing.acquired_at = time.time()
            return existing.fence_token

    def active_locks(self) -> List[str]:
        now = time.time()
        return [
            lid for lid, lock in self._locks.items()
            if now - lock.acquired_at < lock.ttl
        ]


@dataclass
class Message:
    message_id: str = ""
    topic: str = ""
    partition: int = 0
    key: bytes = b""
    value: bytes = b""
    timestamp: float = 0.0
    offset: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.message_id,
            "topic": self.topic,
            "partition": self.partition,
            "key": self.key.hex(),
            "value": self.value.hex(),
            "ts": self.timestamp,
            "offset": self.offset,
        }


class MessageQueue:
    def __init__(self):
        self._topics: Dict[str, List[Message]] = {}
        self._partitions: Dict[str, int] = {}
        self._offsets: Dict[str, int] = {}
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()

    def create_topic(self, topic: str, partitions: int = 1) -> None:
        with self._lock:
            if topic not in self._topics:
                self._topics[topic] = []
                self._partitions[topic] = partitions
                self._offsets[topic] = 0
                self._subscriptions[topic] = []

    def publish(self, topic: str, key: bytes, value: bytes) -> int:
        with self._lock:
            if topic not in self._topics:
                self.create_topic(topic)
            self._offsets[topic] += 1
            msg = Message(
                message_id=str(uuid.uuid4()),
                topic=topic,
                partition=hash(key) % self._partitions[topic],
                key=key,
                value=value,
                timestamp=time.time(),
                offset=self._offsets[topic],
            )
            self._topics[topic].append(msg)
            for handler in self._subscriptions[topic]:
                try:
                    handler(msg)
                except Exception as e:
                    logger.error(f"Subscription handler error: {e}")
            return msg.offset

    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> None:
        with self._lock:
            if topic not in self._subscriptions:
                self._subscriptions[topic] = []
            self._subscriptions[topic].append(handler)

    def unsubscribe(self, topic: str, handler: Callable) -> bool:
        with self._lock:
            if topic in self._subscriptions:
                before = len(self._subscriptions[topic])
                self._subscriptions[topic] = [
                    h for h in self._subscriptions[topic] if h != handler
                ]
                return len(self._subscriptions[topic]) < before
            return False

    def consume(self, topic: str, offset: int = 0, limit: int = 10) -> List[Message]:
        with self._lock:
            if topic not in self._topics:
                return []
            messages = [
                m for m in self._topics[topic] if m.offset > offset
            ]
            return messages[:limit]

    def latest_offset(self, topic: str) -> int:
        with self._lock:
            return self._offsets.get(topic, 0)

    def list_topics(self) -> List[str]:
        with self._lock:
            return list(self._topics.keys())

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "topics": len(self._topics),
                "total_messages": sum(len(msgs) for msgs in self._topics.values()),
                "topic_details": {
                    t: {
                        "partitions": self._partitions.get(t, 1),
                        "messages": len(self._topics[t]),
                        "latest_offset": self._offsets.get(t, 0),
                        "subscribers": len(self._subscriptions.get(t, [])),
                    }
                    for t in self._topics
                },
            }


@dataclass
class DistributedCounter:
    counter_id: str = ""
    value: int = 0
    version: int = 0
    last_updated: float = 0.0


class CRDTCounter:
    def __init__(self):
        self._counters: Dict[str, DistributedCounter] = {}
        self._lock = threading.Lock()

    def increment(self, counter_id: str, delta: int = 1) -> int:
        with self._lock:
            now = time.time()
            if counter_id not in self._counters:
                self._counters[counter_id] = DistributedCounter(
                    counter_id=counter_id, last_updated=now,
                )
            counter = self._counters[counter_id]
            counter.value += delta
            counter.version += 1
            counter.last_updated = now
            return counter.value

    def get(self, counter_id: str) -> int:
        with self._lock:
            counter = self._counters.get(counter_id)
            return counter.value if counter else 0

    def merge(self, counter_id: str, value: int, version: int) -> None:
        with self._lock:
            now = time.time()
            if counter_id not in self._counters:
                self._counters[counter_id] = DistributedCounter(
                    counter_id=counter_id, last_updated=now,
                )
            counter = self._counters[counter_id]
            if version > counter.version:
                counter.value = value
                counter.version = version
                counter.last_updated = now

    def list(self) -> List[str]:
        with self._lock:
            return list(self._counters.keys())


def get_raft_node(config: RaftConfig) -> RaftConsensus:
    return RaftConsensus(config)


def get_service_discovery() -> ServiceDiscovery:
    return ServiceDiscovery()


def get_distributed_lock() -> DistributedLock:
    return DistributedLock()


def get_message_queue() -> MessageQueue:
    return MessageQueue()
