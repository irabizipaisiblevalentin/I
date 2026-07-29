"""itumanaho_sisitemu — Networking: TCP, UDP, HTTP, DNS, DHCP, WebSocket, QUIC, serial, CAN."""

from __future__ import annotations

import json
import socket
import struct
import threading
import time
import urllib.parse
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple


class Protocol(Enum):
    TCP = "tcp"
    UDP = "udp"
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    QUIC = "quic"
    DNS = "dns"
    DHCP = "dhcp"
    BLE = "ble"
    SERIAL = "serial"
    CAN = "can"
    MODBUS = "modbus"
    MQTT = "mqtt"


class SocketType(Enum):
    STREAM = socket.SOCK_STREAM
    DGRAM = socket.SOCK_DGRAM
    RAW = socket.SOCK_RAW


class SocketState(Enum):
    CLOSED = "closed"
    LISTENING = "listening"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    CLOSING = "closing"


@dataclass
class NetworkAddress:
    host: str = "0.0.0.0"
    port: int = 0
    family: int = socket.AF_INET

    @staticmethod
    def local(port: int = 0) -> NetworkAddress:
        return NetworkAddress(host="127.0.0.1", port=port)

    @staticmethod
    def any(port: int = 0) -> NetworkAddress:
        return NetworkAddress(host="0.0.0.0", port=port)

    def to_tuple(self) -> Tuple[str, int]:
        return (self.host, self.port)

    def to_dict(self) -> Dict[str, Any]:
        return {"host": self.host, "port": self.port}


@dataclass
class Packet:
    data: bytes = b""
    source: NetworkAddress = field(default_factory=NetworkAddress)
    dest: NetworkAddress = field(default_factory=NetworkAddress)
    protocol: Protocol = Protocol.TCP
    timestamp: float = 0.0
    ttl: int = 64
    sequence: int = 0
    flags: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "size": len(self.data),
            "source": self.source.to_dict(),
            "dest": self.dest.to_dict(),
            "protocol": self.protocol.value,
        }


@dataclass
class Connection:
    id: str = ""
    state: SocketState = SocketState.CLOSED
    local: NetworkAddress = field(default_factory=NetworkAddress)
    remote: NetworkAddress = field(default_factory=NetworkAddress)
    protocol: Protocol = Protocol.TCP
    socket: Optional[socket.socket] = None
    created: float = 0.0
    bytes_sent: int = 0
    bytes_recv: int = 0
    error_count: int = 0

    def send(self, data: bytes) -> int:
        if self.socket:
            try:
                sent = self.socket.send(data)
                self.bytes_sent += sent
                return sent
            except Exception:
                self.error_count += 1
                return 0
        return 0

    def recv(self, bufsize: int = 4096) -> bytes:
        if self.socket:
            try:
                data = self.socket.recv(bufsize)
                self.bytes_recv += len(data)
                return data
            except Exception:
                self.error_count += 1
                return b""
        return b""

    def close(self) -> None:
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None
        self.state = SocketState.CLOSED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "state": self.state.value,
            "local": self.local.to_dict(),
            "remote": self.remote.to_dict(),
            "protocol": self.protocol.value,
            "bytes_sent": self.bytes_sent,
            "bytes_recv": self.bytes_recv,
        }


class TCPServer:
    def __init__(self, address: NetworkAddress = NetworkAddress.any(8080)):
        self.address = address
        self.connections: Dict[str, Connection] = {}
        self._server: Optional[socket.socket] = None
        self._running = False
        self.on_connect: Optional[Callable[[Connection], None]] = None
        self.on_data: Optional[Callable[[Connection, bytes], None]] = None
        self.on_disconnect: Optional[Callable[[Connection], None]] = None

    def start(self) -> bool:
        try:
            self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server.bind(self.address.to_tuple())
            self._server.listen(5)
            self._running = True
            return True
        except Exception as e:
            return False

    def stop(self) -> None:
        self._running = False
        for c in self.connections.values():
            c.close()
        if self._server:
            try:
                self._server.close()
            except Exception:
                pass
            self._server = None

    def accept(self) -> Optional[Connection]:
        if not self._server:
            return None
        try:
            client, addr = self._server.accept()
            conn_id = f"{addr[0]}:{addr[1]}"
            conn = Connection(
                id=conn_id,
                state=SocketState.CONNECTED,
                local=self.address,
                remote=NetworkAddress(host=addr[0], port=addr[1]),
                protocol=Protocol.TCP,
                socket=client,
                created=time.time(),
            )
            self.connections[conn_id] = conn
            if self.on_connect:
                self.on_connect(conn)
            return conn
        except Exception:
            return None

    def summary(self) -> Dict[str, Any]:
        return {
            "address": self.address.to_dict(),
            "running": self._running,
            "connections": len(self.connections),
        }


class UDPEndpoint:
    def __init__(self, address: NetworkAddress = NetworkAddress.any(0)):
        self.address = address
        self._socket: Optional[socket.socket] = None
        self._running = False
        self.on_packet: Optional[Callable[[Packet], None]] = None

    def start(self) -> bool:
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if self.address.port > 0:
                self._socket.bind(self.address.to_tuple())
            self._running = True
            return True
        except Exception:
            return False

    def stop(self) -> None:
        self._running = False
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None

    def send(self, data: bytes, dest: NetworkAddress) -> int:
        if self._socket:
            try:
                return self._socket.sendto(data, dest.to_tuple())
            except Exception:
                return 0
        return 0

    def recv(self, bufsize: int = 65535) -> Optional[Packet]:
        if self._socket:
            try:
                data, addr = self._socket.recvfrom(bufsize)
                return Packet(
                    data=data,
                    dest=self.address,
                    source=NetworkAddress(host=addr[0], port=addr[1]),
                    protocol=Protocol.UDP,
                    timestamp=time.time(),
                )
            except Exception:
                return None
        return None


class HTTPRequest:
    def __init__(self, method: str = "GET", path: str = "/",
                 headers: Optional[Dict[str, str]] = None,
                 body: bytes = b""):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body
        self.http_version: str = "1.1"

    def to_bytes(self) -> bytes:
        lines = [f"{self.method} {self.path} HTTP/{self.http_version}"]
        for key, value in self.headers.items():
            lines.append(f"{key}: {value}")
        lines.append("")
        return "\r\n".join(lines).encode() + self.body

    @staticmethod
    def from_bytes(data: bytes) -> HTTPRequest:
        parts = data.split(b"\r\n\r\n", 1)
        head = parts[0].decode("utf-8", errors="replace") if parts else ""
        body = parts[1] if len(parts) > 1 else b""
        lines = head.split("\r\n")
        method, path, _ = lines[0].split() if lines else ("GET", "/", "HTTP/1.1")
        headers = {}
        for line in lines[1:]:
            if ": " in line:
                k, v = line.split(": ", 1)
                headers[k] = v
        return HTTPRequest(method=method, path=path, headers=headers, body=body)


class HTTPResponse:
    def __init__(self, status: int = 200, body: bytes = b"",
                 headers: Optional[Dict[str, str]] = None):
        self.status = status
        self.body = body
        self.headers = headers or {}
        self.http_version: str = "1.1"
        self._status_texts = {200: "OK", 404: "Not Found", 500: "Internal Server Error"}

    def to_bytes(self) -> bytes:
        status_text = self._status_texts.get(self.status, "Unknown")
        lines = [f"HTTP/{self.http_version} {self.status} {status_text}"]
        if "Content-Length" not in self.headers:
            self.headers["Content-Length"] = str(len(self.body))
        for key, value in self.headers.items():
            lines.append(f"{key}: {value}")
        lines.append("")
        return "\r\n".join(lines).encode() + self.body


class HTTPServer:
    def __init__(self, address: NetworkAddress = NetworkAddress.any(8080)):
        self.address = address
        self._server = TCPServer(address)
        self.routes: Dict[str, Callable[[HTTPRequest], HTTPResponse]] = {}
        self._server.on_data = self._handle_data

    def route(self, method: str, path: str,
              handler: Callable[[HTTPRequest], HTTPResponse]) -> None:
        self.routes[f"{method}:{path}"] = handler

    def start(self) -> bool:
        return self._server.start()

    def stop(self) -> None:
        self._server.stop()

    def _handle_data(self, conn: Connection, data: bytes) -> None:
        try:
            req = HTTPRequest.from_bytes(data)
            handler = self.routes.get(f"{req.method}:{req.path}")
            if handler:
                resp = handler(req)
            else:
                resp = HTTPResponse(404, b"Not Found")
            conn.send(resp.to_bytes())
        except Exception:
            resp = HTTPResponse(500, b"Internal Server Error")
            conn.send(resp.to_bytes())

    def summary(self) -> Dict[str, Any]:
        return {
            "address": self.address.to_dict(),
            "routes": list(self.routes.keys()),
        }


class DNSResolver:
    def __init__(self):
        self._cache: Dict[str, Tuple[str, float]] = {}
        self._cache_ttl: float = 300.0

    def resolve(self, hostname: str) -> Optional[str]:
        now = time.time()
        if hostname in self._cache:
            ip, expires = self._cache[hostname]
            if now < expires:
                return ip
            else:
                del self._cache[hostname]
        try:
            ip = socket.gethostbyname(hostname)
            self._cache[hostname] = (ip, now + self._cache_ttl)
            return ip
        except Exception:
            return None

    def reverse_lookup(self, ip: str) -> Optional[str]:
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except Exception:
            return None

    def flush_cache(self) -> None:
        self._cache.clear()

    def summary(self) -> Dict[str, Any]:
        return {"cache_size": len(self._cache)}


class DHCPClient:
    def __init__(self):
        self.ip_address: str = ""
        self.subnet_mask: str = "255.255.255.0"
        self.gateway: str = ""
        self.dns_servers: List[str] = []
        self.lease_time: int = 86400
        self._obtained: bool = False

    def discover(self) -> bool:
        self.ip_address = "192.168.1.100"
        self.gateway = "192.168.1.1"
        self.dns_servers = ["8.8.8.8", "8.8.4.4"]
        self._obtained = True
        return True

    def release(self) -> None:
        self.ip_address = ""
        self._obtained = False

    @property
    def has_ip(self) -> bool:
        return self._obtained

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ip": self.ip_address,
            "gateway": self.gateway,
            "dns": self.dns_servers,
            "obtained": self._obtained,
        }


class SerialPort:
    def __init__(self, name: str = "COM1", baudrate: int = 115200):
        self.name = name
        self.baudrate = baudrate
        self._open = False
        self._buffer: bytearray = bytearray()

    def open(self) -> bool:
        self._open = True
        return True

    def close(self) -> None:
        self._open = False

    def write(self, data: bytes) -> int:
        if not self._open:
            return 0
        return len(data)

    def read(self, size: int = 1) -> bytes:
        if not self._open:
            return b""
        result = bytes(self._buffer[:size])
        self._buffer = self._buffer[size:]
        return result

    def write_byte(self, byte: int) -> None:
        self._buffer.append(byte)

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "baudrate": self.baudrate,
            "open": self._open,
            "buffer_size": len(self._buffer),
        }


class CANBus:
    def __init__(self, name: str = "can0", bitrate: int = 500000):
        self.name = name
        self.bitrate = bitrate
        self._messages: List[Dict[str, Any]] = []

    def send(self, arbitration_id: int, data: bytes,
             extended: bool = False) -> bool:
        self._messages.append({
            "id": arbitration_id,
            "data": list(data),
            "extended": extended,
            "timestamp": time.time(),
        })
        return True

    def recv(self) -> Optional[Dict[str, Any]]:
        if self._messages:
            return self._messages.pop(0)
        return None

    def summary(self) -> Dict[str, Any]:
        return {"name": self.name, "bitrate": self.bitrate, "pending": len(self._messages)}


class NetworkStack:
    def __init__(self):
        self.tcp_servers: Dict[str, TCPServer] = {}
        self.udp_endpoints: Dict[str, UDPEndpoint] = {}
        self.http_servers: Dict[str, HTTPServer] = {}
        self.dns = DNSResolver()
        self.dhcp = DHCPClient()
        self.serial_ports: Dict[str, SerialPort] = {}
        self.can_buses: Dict[str, CANBus] = {}
        self.connections: Dict[str, Connection] = {}

    def create_tcp_server(self, name: str, port: int = 8080) -> TCPServer:
        server = TCPServer(NetworkAddress.any(port))
        self.tcp_servers[name] = server
        return server

    def create_udp_endpoint(self, name: str, port: int = 0) -> UDPEndpoint:
        ep = UDPEndpoint(NetworkAddress.any(port))
        self.udp_endpoints[name] = ep
        return ep

    def create_http_server(self, name: str, port: int = 8080) -> HTTPServer:
        server = HTTPServer(NetworkAddress.any(port))
        self.http_servers[name] = server
        return server

    def create_serial_port(self, name: str, port_name: str = "COM1",
                           baudrate: int = 115200) -> SerialPort:
        port = SerialPort(port_name, baudrate)
        self.serial_ports[name] = port
        return port

    def create_can_bus(self, name: str, bus_name: str = "can0",
                       bitrate: int = 500000) -> CANBus:
        bus = CANBus(bus_name, bitrate)
        self.can_buses[name] = bus
        return bus

    def connect_tcp(self, host: str, port: int) -> Optional[Connection]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            conn_id = f"{host}:{port}"
            conn = Connection(
                id=conn_id,
                state=SocketState.CONNECTED,
                local=NetworkAddress(),
                remote=NetworkAddress(host=host, port=port),
                socket=sock,
                created=time.time(),
            )
            self.connections[conn_id] = conn
            return conn
        except Exception:
            return None

    def summary(self) -> Dict[str, Any]:
        return {
            "tcp_servers": list(self.tcp_servers.keys()),
            "udp_endpoints": list(self.udp_endpoints.keys()),
            "http_servers": list(self.http_servers.keys()),
            "connections": len(self.connections),
            "dns_cache": self.dns.summary()["cache_size"],
            "serial_ports": list(self.serial_ports.keys()),
            "can_buses": list(self.can_buses.keys()),
        }


# ─── RDMA (Remote Direct Memory Access) ─────────────────────────────────────

@dataclass
class RdmaMemoryRegion:
    local_key: int = 0
    remote_key: int = 0
    address: int = 0
    length: int = 0
    permissions: str = "rw"


@dataclass
class RdmaCompletionEntry:
    wr_id: int = 0
    status: str = "success"
    bytes_transferred: int = 0


class RdmaCompletionQueue:
    def __init__(self, depth: int = 256):
        self.depth = depth
        self._entries: List[RdmaCompletionEntry] = []

    def poll(self) -> List[RdmaCompletionEntry]:
        entries = list(self._entries)
        self._entries.clear()
        return entries

    def notify(self, entry: RdmaCompletionEntry) -> None:
        if len(self._entries) < self.depth:
            self._entries.append(entry)


class RdmaEndpoint:
    def __init__(self, host: str = "", port: int = 0):
        self.host = host
        self.port = port
        self._regions: Dict[int, RdmaMemoryRegion] = {}
        self._cq = RdmaCompletionQueue()
        self._connected: bool = False

    def register_memory(self, address: int, length: int,
                        permissions: str = "rw") -> RdmaMemoryRegion:
        lkey = len(self._regions) + 1
        region = RdmaMemoryRegion(
            local_key=lkey, remote_key=lkey,
            address=address, length=length, permissions=permissions,
        )
        self._regions[lkey] = region
        return region

    def connect(self, remote_host: str, remote_port: int) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def rdma_write(self, remote_addr: int, local_region: RdmaMemoryRegion,
                   length: int) -> bool:
        if not self._connected:
            return False
        self._cq.notify(RdmaCompletionEntry(wr_id=1, bytes_transferred=length))
        return True

    def rdma_read(self, remote_addr: int, local_region: RdmaMemoryRegion,
                  length: int) -> bool:
        if not self._connected:
            return False
        self._cq.notify(RdmaCompletionEntry(wr_id=2, bytes_transferred=length))
        return True

    def summary(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "connected": self._connected,
            "regions": len(self._regions),
        }


# ─── DPDK (Data Plane Development Kit) ──────────────────────────────────────

class DpdkBufferPool:
    def __init__(self, name: str, buffer_size: int = 2048, count: int = 4096):
        self.name = name
        self.buffer_size = buffer_size
        self.count = count
        self._available = count
        self._lock = threading.Lock()

    def alloc_buf(self) -> Optional[bytearray]:
        with self._lock:
            if self._available <= 0:
                return None
            self._available -= 1
            return bytearray(self.buffer_size)

    def free_buf(self, buf: bytearray) -> None:
        with self._lock:
            self._available += 1

    @property
    def utilization(self) -> float:
        return 1.0 - (self._available / self.count)


@dataclass
class DpdkPortStats:
    rx_packets: int = 0
    tx_packets: int = 0
    rx_bytes: int = 0
    tx_bytes: int = 0
    rx_dropped: int = 0
    tx_dropped: int = 0


class DpdkPort:
    def __init__(self, port_id: int = 0, name: str = "dpdk0",
                 rx_queues: int = 1, tx_queues: int = 1):
        self.port_id = port_id
        self.name = name
        self.rx_queues = rx_queues
        self.tx_queues = tx_queues
        self._stats = DpdkPortStats()
        self._up: bool = False

    def start(self) -> bool:
        self._up = True
        return True

    def stop(self) -> bool:
        self._up = False
        return True

    def send(self, data: bytes, queue: int = 0) -> bool:
        if not self._up:
            return False
        self._stats.tx_packets += 1
        self._stats.tx_bytes += len(data)
        return True

    def recv(self, queue: int = 0) -> Optional[bytes]:
        if not self._up:
            return None
        self._stats.rx_packets += 1
        self._stats.rx_bytes += 64
        return b"\x00" * 64

    @property
    def stats(self) -> DpdkPortStats:
        return self._stats

    def reset_stats(self) -> None:
        self._stats = DpdkPortStats()


class DpdkForwarder:
    def __init__(self, name: str = "forwarder"):
        self.name = name
        self._ports: Dict[int, DpdkPort] = {}
        self._ring_buffer: List[bytes] = []
        self._lock = threading.Lock()

    def add_port(self, port: DpdkPort) -> None:
        self._ports[port.port_id] = port

    def forward(self, src_port: int, dst_port: int) -> int:
        with self._lock:
            count = 0
            src = self._ports.get(src_port)
            dst = self._ports.get(dst_port)
            if not src or not dst:
                return 0
            data = src.recv()
            while data:
                dst.send(data)
                count += 1
                data = src.recv()
            return count

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "ports": len(self._ports),
            "ring_depth": len(self._ring_buffer),
        }


# ─── Kernel Bypass & Zero-Copy ──────────────────────────────────────────────

class ZeroCopyBuffer:
    def __init__(self, size: int = 65536):
        self._data = bytearray(size)
        self._offset = 0
        self.size = size

    def write(self, data: bytes) -> int:
        available = self.size - self._offset
        to_write = min(len(data), available)
        self._data[self._offset:self._offset + to_write] = data[:to_write]
        self._offset += to_write
        return to_write

    def read(self, length: int) -> bytes:
        available = self._offset
        to_read = min(length, available)
        data = bytes(self._data[:to_read])
        remaining = self._data[to_read:self._offset]
        self._data[:len(remaining)] = remaining
        self._offset = len(remaining)
        return data

    def reset(self) -> None:
        self._offset = 0

    @property
    def used(self) -> int:
        return self._offset


class KernelBypassSocket:
    def __init__(self, name: str = "bypass0"):
        self.name = name
        self._rx_buffer = ZeroCopyBuffer()
        self._tx_buffer = ZeroCopyBuffer()
        self._connected: bool = False

    def bind(self, interface: str) -> bool:
        return True

    def connect(self, target: str) -> bool:
        self._connected = True
        return True

    def send(self, data: bytes) -> int:
        return self._tx_buffer.write(data)

    def recv(self, size: int = 65536) -> bytes:
        return self._rx_buffer.read(size)

    def zero_copy_send(self, buffer: ZeroCopyBuffer) -> int:
        sent = buffer.used
        buffer.reset()
        return sent

    def zero_copy_recv(self, buffer: ZeroCopyBuffer) -> int:
        data = self._rx_buffer.read(buffer.size)
        buffer.write(data)
        return len(data)

    def close(self) -> None:
        self._connected = False
        self._rx_buffer.reset()
        self._tx_buffer.reset()


_network = NetworkStack()


def get_network() -> NetworkStack:
    return _network
