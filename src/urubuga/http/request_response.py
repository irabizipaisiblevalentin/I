"""http — HTTP request, response, and status code definitions.

Provides the core HTTP abstractions used throughout urubuga.
"""

from __future__ import annotations

import enum
import json
import time
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import parse_qs, urlparse, urlencode


class HTTPMethod(enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    CONNECT = "CONNECT"

    def __str__(self) -> str:
        return self.value


class StatusCode(enum.IntEnum):
    """HTTP status codes."""
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    MOVED_PERMANENTLY = 301
    FOUND = 302
    NOT_MODIFIED = 304
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503

    @property
    def phrase(self) -> str:
        phrases = {
            200: "OK", 201: "Created", 202: "Accepted", 204: "No Content",
            301: "Moved Permanently", 302: "Found", 304: "Not Modified",
            400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
            404: "Not Found", 405: "Method Not Allowed", 409: "Conflict",
            422: "Unprocessable Entity", 429: "Too Many Requests",
            500: "Internal Server Error", 501: "Not Implemented",
            502: "Bad Gateway", 503: "Service Unavailable",
        }
        return phrases.get(self.value, "Unknown")

    @property
    def is_success(self) -> bool:
        return 200 <= self.value < 300

    @property
    def is_redirect(self) -> bool:
        return 300 <= self.value < 400

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.value < 500

    @property
    def is_server_error(self) -> bool:
        return 500 <= self.value < 600


class Headers:
    """HTTP headers container with case-insensitive access."""

    def __init__(self, initial: Optional[Dict[str, str]] = None) -> None:
        self._store: Dict[str, str] = {}
        if initial:
            for k, v in initial.items():
                self._store[k.lower()] = v

    def get(self, key: str, default: str = "") -> str:
        return self._store.get(key.lower(), default)

    def set(self, key: str, value: str) -> None:
        self._store[key.lower()] = value

    def add(self, key: str, value: str) -> None:
        existing = self._store.get(key.lower())
        if existing:
            self._store[key.lower()] = f"{existing}, {value}"
        else:
            self._store[key.lower()] = value

    def has(self, key: str) -> bool:
        return key.lower() in self._store

    def delete(self, key: str) -> bool:
        return self._store.pop(key.lower(), None) is not None

    def items(self) -> Dict[str, str]:
        return dict(self._store)

    def keys(self) -> List[str]:
        return list(self._store.keys())

    def values(self) -> List[str]:
        return list(self._store.values())

    def __contains__(self, key: str) -> bool:
        return key.lower() in self._store

    def __getitem__(self, key: str) -> str:
        return self._store[key.lower()]

    def __setitem__(self, key: str, value: str) -> None:
        self._store[key.lower()] = value

    def __len__(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return f"Headers({self._store})"


class Request:
    """HTTP request representation."""

    __slots__ = ("method", "path", "query_string", "headers", "body",
                 "_query_params", "_path_params", "_form_data", "_json_data",
                 "_cookies", "_client", "_scheme", "_host", "_port",
                 "_content_type", "_content_length", "_timestamp",
                 "_user", "_state")

    def __init__(self, method: str = "GET", path: str = "/",
                 query_string: str = "", headers: Optional[Dict[str, str]] = None,
                 body: bytes = b"",
                 client: Optional[tuple] = None) -> None:
        self.method = method.upper()
        self.path = path
        self.query_string = query_string
        self.headers = Headers(headers or {})
        self.body = body
        self._query_params: Optional[Dict[str, List[str]]] = None
        self._path_params: Dict[str, Any] = {}
        self._form_data: Optional[Dict[str, str]] = None
        self._json_data: Any = None
        self._cookies: Optional[Dict[str, str]] = None
        self._client = client
        self._scheme = "http"
        self._host = ""
        self._port = 80
        self._content_type = ""
        self._content_length = 0
        self._timestamp = time.time()
        self._user: Any = None
        self._state: Dict[str, Any] = {}

    @property
    def url(self) -> str:
        return f"{self._scheme}://{self._host}{self.path}"

    @property
    def query_params(self) -> Dict[str, List[str]]:
        if self._query_params is None:
            self._query_params = parse_qs(self.query_string)
        return self._query_params

    def query_param(self, key: str, default: str = "") -> str:
        params = self.query_params.get(key, [])
        return params[0] if params else default

    @property
    def path_params(self) -> Dict[str, Any]:
        return self._path_params

    @property
    def content_type(self) -> str:
        if not self._content_type:
            self._content_type = self.headers.get("content-type", "")
        return self._content_type

    @property
    def content_length(self) -> int:
        if not self._content_length:
            try:
                self._content_length = int(self.headers.get("content-length", "0"))
            except ValueError:
                self._content_length = 0
        return self._content_length

    @property
    def is_json(self) -> bool:
        return "application/json" in self.content_type

    @property
    def is_form(self) -> bool:
        return "application/x-www-form-urlencoded" in self.content_type

    @property
    def is_multipart(self) -> bool:
        return "multipart/form-data" in self.content_type

    def json(self) -> Any:
        if self._json_data is None:
            if self.body and self.is_json:
                try:
                    self._json_data = json.loads(self.body.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    self._json_data = {}
            else:
                self._json_data = {}
        return self._json_data

    def form(self) -> Dict[str, str]:
        if self._form_data is None:
            if self.body and self.is_form:
                self._form_data = dict(parse_qs(self.body.decode("utf-8")))
                for k in self._form_data:
                    if isinstance(self._form_data[k], list):
                        self._form_data[k] = self._form_data[k][0]
            else:
                self._form_data = {}
        return self._form_data

    def cookies(self) -> Dict[str, str]:
        if self._cookies is None:
            self._cookies = {}
            cookie_header = self.headers.get("cookie", "")
            if cookie_header:
                for pair in cookie_header.split(";"):
                    pair = pair.strip()
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        self._cookies[k.strip()] = v.strip()
        return self._cookies

    def cookie(self, name: str, default: str = "") -> str:
        return self.cookies().get(name, default)

    @property
    def user(self) -> Any:
        return self._user

    @user.setter
    def user(self, value: Any) -> None:
        self._user = value

    @property
    def state(self) -> Dict[str, Any]:
        return self._state

    def accept(self, media_type: str) -> bool:
        accept = self.headers.get("accept", "*/*")
        return media_type in accept or "*/*" in accept

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def client_ip(self) -> str:
        if self._client:
            return self._client[0]
        return self.headers.get("x-forwarded-for", "unknown")

    def __repr__(self) -> str:
        return f"Request({self.method} {self.path})"


class Response:
    """HTTP response representation."""

    __slots__ = ("status", "headers", "body", "_cookies", "_started")

    def __init__(self, status: Union[int, StatusCode] = StatusCode.OK,
                 headers: Optional[Dict[str, str]] = None,
                 body: bytes = b"") -> None:
        if isinstance(status, int):
            self.status = StatusCode(status) if status in StatusCode.__members__.values() else StatusCode.INTERNAL_SERVER_ERROR
        else:
            self.status = status
        self.headers = Headers(headers or {})
        self.body = body
        self._cookies: List[Dict[str, Any]] = []
        self._started = False

    @classmethod
    def json(cls, data: Any, status: Union[int, StatusCode] = StatusCode.OK,
             headers: Optional[Dict[str, str]] = None) -> "Response":
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        h = headers or {}
        h["content-type"] = "application/json"
        h["content-length"] = str(len(body))
        return cls(status, h, body)

    @classmethod
    def text(cls, text: str, status: Union[int, StatusCode] = StatusCode.OK,
             headers: Optional[Dict[str, str]] = None) -> "Response":
        body = text.encode("utf-8")
        h = headers or {}
        h["content-type"] = "text/plain; charset=utf-8"
        h["content-length"] = str(len(body))
        return cls(status, h, body)

    @classmethod
    def html(cls, html: str, status: Union[int, StatusCode] = StatusCode.OK,
             headers: Optional[Dict[str, str]] = None) -> "Response":
        body = html.encode("utf-8")
        h = headers or {}
        h["content-type"] = "text/html; charset=utf-8"
        h["content-length"] = str(len(body))
        return cls(status, h, body)

    @classmethod
    def redirect(cls, location: str,
                 status: Union[int, StatusCode] = StatusCode.FOUND,
                 headers: Optional[Dict[str, str]] = None) -> "Response":
        h = headers or {}
        h["location"] = location
        return cls(status, h)

    @classmethod
    def no_content(cls, headers: Optional[Dict[str, str]] = None) -> "Response":
        return cls(StatusCode.NO_CONTENT, headers)

    @classmethod
    def error(cls, status: Union[int, StatusCode],
              message: str = "",
              headers: Optional[Dict[str, str]] = None) -> "Response":
        data = {"error": {"status": int(status), "message": message or StatusCode(int(status)).phrase}}
        return cls.json(data, status, headers)

    def set_cookie(self, name: str, value: str, max_age: int = 3600,
                   path: str = "/", secure: bool = True,
                   http_only: bool = True,
                   same_site: str = "Lax") -> None:
        cookie = {
            "name": name, "value": value, "max_age": max_age,
            "path": path, "secure": secure, "http_only": http_only,
            "same_site": same_site,
        }
        self._cookies.append(cookie)

    def set_header(self, key: str, value: str) -> "Response":
        self.headers.set(key, value)
        return self

    def add_header(self, key: str, value: str) -> "Response":
        self.headers.add(key, value)
        return self

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

    def __repr__(self) -> str:
        return f"Response({self.status.value} {self.status.phrase})"
