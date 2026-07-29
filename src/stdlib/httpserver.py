"""httpserver — Native HTTP server for the I language runtime.

Provides HTTP server, request parsing, response building, static file serving,
middleware pipeline, and WebSocket upgrade — all exposed to .i code.
"""

from __future__ import annotations

import gzip
import json
import mimetypes
import os
import socket
import ssl
import struct
import hashlib
import base64
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from io import BytesIO


class NativeRequest:
    __slots__ = ("method", "path", "query_string", "headers", "body",
                 "query_params", "path_params", "client_ip", "scheme",
                 "content_type", "content_length", "cookies", "form_data",
                 "json_data", "timestamp")

    def __init__(self, method: str, path: str, query_string: str,
                 headers: Dict[str, str], body: bytes,
                 client_ip: str = "127.0.0.1") -> None:
        self.method = method
        self.path = path
        self.query_string = query_string
        self.headers = headers
        self.body = body
        self.client_ip = client_ip
        self.scheme = "http"
        self.content_type = headers.get("content-type", "")
        self.content_length = len(body)
        self.query_params = parse_qs(query_string) if query_string else {}
        self.path_params: Dict[str, Any] = {}
        self.cookies: Dict[str, str] = {}
        self.form_data: Dict[str, str] = {}
        self.json_data: Any = None
        self.timestamp = time.time()

        cookie_header = headers.get("cookie", "")
        if cookie_header:
            for pair in cookie_header.split(";"):
                pair = pair.strip()
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    self.cookies[k.strip()] = v.strip()

        if "application/json" in self.content_type and body:
            try:
                self.json_data = json.loads(body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.json_data = {}
        elif "application/x-www-form-urlencoded" in self.content_type and body:
            try:
                parsed = parse_qs(body.decode("utf-8"))
                self.form_data = {k: v[0] if len(v) == 1 else v
                                  for k, v in parsed.items()}
            except UnicodeDecodeError:
                pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "method": self.method,
            "path": self.path,
            "query_string": self.query_string,
            "headers": self.headers,
            "body": self.body.decode("utf-8", errors="replace"),
            "client_ip": self.client_ip,
            "scheme": self.scheme,
            "content_type": self.content_type,
            "content_length": self.content_length,
            "query_params": self.query_params,
            "path_params": self.path_params,
            "cookies": self.cookies,
            "form_data": self.form_data,
            "json_data": self.json_data,
            "timestamp": self.timestamp,
        }


class NativeResponse:
    __slots__ = ("status", "headers", "body", "_cookies")

    def __init__(self, status: int = 200,
                 headers: Optional[Dict[str, str]] = None,
                 body: bytes = b"") -> None:
        self.status = status
        self.headers = headers or {}
        self.body = body
        self._cookies: List[Dict[str, Any]] = []

    def set_cookie(self, name: str, value: str, max_age: int = 3600,
                   path: str = "/", secure: bool = True,
                   http_only: bool = True, same_site: str = "Lax") -> None:
        self._cookies.append({
            "name": name, "value": value, "max_age": max_age,
            "path": path, "secure": secure, "http_only": http_only,
            "same_site": same_site,
        })

    def build_cookie_headers(self) -> List[str]:
        parts = []
        for c in self._cookies:
            s = f"{c['name']}={c['value']}"
            if c.get("max_age"):
                s += f"; Max-Age={c['max_age']}"
            if c.get("path"):
                s += f"; Path={c['path']}"
            if c.get("secure"):
                s += "; Secure"
            if c.get("http_only"):
                s += "; HttpOnly"
            if c.get("same_site"):
                s += f"; SameSite={c['same_site']}"
            parts.append(s)
        return parts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "headers": self.headers,
            "body": self.body.decode("utf-8", errors="replace"),
        }


MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".ttf": "font/ttf",
    ".txt": "text/plain; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".pdf": "application/pdf",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".i": "text/x-i; charset=utf-8",
}


class UrubugaHTTPHandler(BaseHTTPRequestHandler):
    _app: Any = None
    _static_dir: str = ""
    _middleware: List[Callable] = []
    _ws_upgrade_handler: Optional[Callable] = None

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def _parse_path(self) -> Tuple[str, str]:
        parsed = urlparse(self.path)
        return unquote(parsed.path), parsed.query

    def _read_body(self) -> bytes:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            return self.rfile.read(content_length)
        return b""

    def _send_response(self, resp: NativeResponse) -> None:
        self.send_response(resp.status)
        for key, value in resp.headers.items():
            self.send_header(key, value)
        cookie_headers = resp.build_cookie_headers()
        for ch in cookie_headers:
            self.send_header("Set-Cookie", ch)
        self.end_headers()
        if resp.body:
            self.wfile.write(resp.body)

    def do_GET(self) -> None:
        self._handle_request("GET")

    def do_POST(self) -> None:
        self._handle_request("POST")

    def do_PUT(self) -> None:
        self._handle_request("PUT")

    def do_PATCH(self) -> None:
        self._handle_request("PATCH")

    def do_DELETE(self) -> None:
        self._handle_request("DELETE")

    def do_HEAD(self) -> None:
        self._handle_request("HEAD")

    def do_OPTIONS(self) -> None:
        self._handle_request("OPTIONS")

    def _handle_request(self, method: str) -> None:
        path, query = self._parse_path()
        body = self._read_body()

        headers = {}
        for key in self.headers:
            headers[key.lower()] = self.headers[key]

        client_ip = self.client_address[0] if self.client_address else "127.0.0.1"

        ws_key = headers.get("upgrade", "").lower()
        if ws_key == "websocket" and self._ws_upgrade_handler:
            self._ws_upgrade_handler(self, path, headers)
            return

        if self._static_dir and self._try_static(path):
            return

        req = NativeRequest(method, path, query, headers, body, client_ip)

        for mw in self._middleware:
            try:
                result = mw(req)
                if isinstance(result, NativeResponse):
                    self._send_response(result)
                    return
            except Exception:
                pass

        if self._app:
            try:
                resp = self._app(req)
                if isinstance(resp, NativeResponse):
                    self._send_response(resp)
                elif isinstance(resp, dict):
                    self._send_response(self._json_response(resp))
                elif isinstance(resp, str):
                    self._send_response(self._html_response(resp))
                elif resp is None:
                    self._send_response(NativeResponse(204))
                else:
                    self._send_response(self._json_response({"result": str(resp)}))
            except Exception as e:
                self._send_response(self._json_response(
                    {"error": {"status": 500, "message": str(e)}}, 500))
        else:
            self._send_response(self._html_response(
                "<h1>Urubuga</h1><p>No application configured.</p>"))

    def _try_static(self, path: str) -> bool:
        if path == "/":
            path = "/index.html"
        file_path = os.path.join(self._static_dir, path.lstrip("/"))
        file_path = os.path.normpath(file_path)
        if not file_path.startswith(os.path.normpath(self._static_dir)):
            return False
        if os.path.isfile(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            content_type = MIME_TYPES.get(ext, "application/octet-stream")
            with open(file_path, "rb") as f:
                data = f.read()
            resp = NativeResponse(200, {"Content-Type": content_type,
                                        "Content-Length": str(len(data))}, data)
            self._send_response(resp)
            return True
        return False

    @staticmethod
    def _json_response(data: Any, status: int = 200) -> NativeResponse:
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        return NativeResponse(status, {
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": str(len(body)),
        }, body)

    @staticmethod
    def _html_response(html: str, status: int = 200) -> NativeResponse:
        body = html.encode("utf-8")
        return NativeResponse(status, {
            "Content-Type": "text/html; charset=utf-8",
            "Content-Length": str(len(body)),
        }, body)


class UrubugaHTTPServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 3000) -> None:
        self.host = host
        self.port = port
        self._app: Optional[Callable] = None
        self._middleware: List[Callable] = []
        self._static_dir = ""
        self._server: Optional[HTTPServer] = None
        self._running = False
        self._threads: List[threading.Thread] = []
        self._ssl_context: Optional[ssl.SSLContext] = None
        self._request_count = 0
        self._start_time = 0.0

    def set_app(self, app: Callable) -> None:
        self._app = app

    def use(self, middleware: Callable) -> None:
        self._middleware.append(middleware)

    def serve_static(self, directory: str) -> None:
        self._static_dir = os.path.abspath(directory)

    def enable_ssl(self, certfile: str, keyfile: str) -> None:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile, keyfile)
        self._ssl_context = ctx

    def start(self) -> None:
        handler_class = type("Handler", (UrubugaHTTPHandler,), {
            "_app": self._app,
            "_static_dir": self._static_dir,
            "_middleware": list(self._middleware),
        })
        self._server = HTTPServer((self.host, self.port), handler_class)
        if self._ssl_context:
            self._server.socket = self._ssl_context.wrap_socket(
                self._server.socket, server_side=True)
        self._running = True
        self._start_time = time.time()
        self._server.serve_forever()

    def start_threaded(self) -> None:
        t = threading.Thread(target=self.start, daemon=True)
        t.start()
        self._threads.append(t)

    def stop(self) -> None:
        self._running = False
        if self._server:
            self._server.shutdown()

    def request_count(self) -> int:
        return self._request_count

    def uptime(self) -> float:
        if self._start_time:
            return time.time() - self._start_time
        return 0.0


class UrubugaWebSocketServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        self.host = host
        self.port = port
        self._connections: Dict[str, Any] = {}
        self._handlers: Dict[str, Callable] = {}
        self._broadcast_handler: Optional[Callable] = None
        self._connect_handler: Optional[Callable] = None
        self._disconnect_handler: Optional[Callable] = None
        self._server_socket: Optional[socket.socket] = None
        self._running = False

    def on_connect(self, handler: Callable) -> None:
        self._connect_handler = handler

    def on_message(self, handler: Callable) -> None:
        self._broadcast_handler = handler

    def on_disconnect(self, handler: Callable) -> None:
        self._disconnect_handler = handler

    def on(self, event: str, handler: Callable) -> None:
        self._handlers[event] = handler

    def broadcast(self, message: str) -> None:
        frame = self._encode_frame(message)
        for conn_id, conn in list(self._connections.items()):
            try:
                conn.sendall(frame)
            except Exception:
                self._remove_connection(conn_id)

    def send_to(self, conn_id: str, message: str) -> bool:
        conn = self._connections.get(conn_id)
        if conn:
            try:
                conn.sendall(self._encode_frame(message))
                return True
            except Exception:
                self._remove_connection(conn_id)
        return False

    def connection_count(self) -> int:
        return len(self._connections)

    def _encode_frame(self, message: str) -> bytes:
        data = message.encode("utf-8")
        length = len(data)
        if length < 126:
            header = struct.pack("BB", 0x81, 0x80 | length)
        elif length < 65536:
            header = struct.pack("!BBH", 0x81, 0x80 | 126, length)
        else:
            header = struct.pack("!BBQ", 0x81, 0x80 | 127, length)
        mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        return header + mask + masked

    def _decode_frame(self, data: bytes) -> Optional[str]:
        if len(data) < 2:
            return None
        opcode = data[0] & 0x0F
        if opcode == 0x8:
            return None
        masked = (data[1] & 0x80) != 0
        length = data[1] & 0x7F
        offset = 2
        if length == 126:
            length = struct.unpack("!H", data[2:4])[0]
            offset = 4
        elif length == 127:
            length = struct.unpack("!Q", data[2:10])[0]
            offset = 10
        if masked:
            mask = data[offset:offset + 4]
            offset += 4
            payload = data[offset:offset + length]
            decoded = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            return decoded.decode("utf-8", errors="replace")
        else:
            payload = data[offset:offset + length]
            return payload.decode("utf-8", errors="replace")

    def _remove_connection(self, conn_id: str) -> None:
        self._connections.pop(conn_id, None)
        if self._disconnect_handler:
            try:
                self._disconnect_handler(conn_id)
            except Exception:
                pass


def urubuga_sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def urubuga_hmac(data: str, key: str) -> str:
    return hashlib.hmac.new(
        key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def urubuga_random_bytes(n: int) -> str:
    return os.urandom(n).hex()


def urubuga_random_token(length: int = 32) -> str:
    return base64.urlsafe_b64encode(os.urandom(length)).decode("utf-8").rstrip("=")[:length]


def urubuga_encrypt(data: str, key: str) -> str:
    key_bytes = hashlib.sha256(key.encode("utf-8")).digest()
    data_bytes = data.encode("utf-8")
    iv = os.urandom(16)
    encrypted = bytearray()
    for i, b in enumerate(data_bytes):
        encrypted.append(b ^ key_bytes[i % len(key_bytes)] ^ iv[i % 16])
    return base64.b64encode(iv + bytes(encrypted)).decode("utf-8")


def urubuga_decrypt(data: str, key: str) -> str:
    key_bytes = hashlib.sha256(key.encode("utf-8")).digest()
    decoded = base64.b64decode(data)
    iv = decoded[:16]
    encrypted = decoded[16:]
    decrypted = bytearray()
    for i, b in enumerate(encrypted):
        decrypted.append(b ^ key_bytes[i % len(key_bytes)] ^ iv[i % 16])
    return bytes(decrypted).decode("utf-8")


def urubuga_compress(data: bytes) -> bytes:
    return gzip.compress(data)


def urubuga_decompress(data: bytes) -> bytes:
    return gzip.decompress(data)


def urubuga_json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str)


def urubuga_json_loads(text: str) -> Any:
    return json.loads(text)


def urubuga_url_encode(data: Dict[str, str]) -> str:
    from urllib.parse import urlencode
    return urlencode(data)


def urubuga_url_decode(text: str) -> Dict[str, List[str]]:
    return parse_qs(text)


def urubuga_timestamp() -> float:
    return time.time()


def urubuga_iso_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def urubuga_sleep(seconds: float) -> None:
    time.sleep(seconds)
