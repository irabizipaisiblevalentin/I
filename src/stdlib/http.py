"""http — HTTP client for the I language.

Provides a simple HTTP client for making requests.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


class HTTPResponse:
    """HTTP response wrapper."""

    __slots__ = ("status", "headers", "body", "_text")

    def __init__(self, status: int, headers: Dict[str, str], body: bytes) -> None:
        self.status = status
        self.headers = headers
        self.body = body
        self._text: Optional[str] = None

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    @property
    def text(self) -> str:
        if self._text is None:
            self._text = self.body.decode("utf-8", errors="replace")
        return self._text

    def json(self) -> Any:
        return json.loads(self.text)

    def __repr__(self) -> str:
        return f"HTTPResponse(status={self.status})"


def request(method: str, url: str, data: Optional[bytes] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: float = 30.0) -> HTTPResponse:
    """Make an HTTP request."""
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return HTTPResponse(resp.status, dict(resp.headers), resp.read())
    except urllib.error.HTTPError as e:
        return HTTPResponse(e.code, dict(e.headers), e.read() if e.fp else b"")
    except urllib.error.URLError as e:
        raise ConnectionError(f"HTTP request failed: {e.reason}") from e


def get(url: str, headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0) -> HTTPResponse:
    return request("GET", url, headers=headers, timeout=timeout)


def post(url: str, data: Any = None, headers: Optional[Dict[str, str]] = None,
         timeout: float = 30.0) -> HTTPResponse:
    if data is not None and not isinstance(data, bytes):
        data = json.dumps(data).encode("utf-8")
        headers = headers or {}
        headers.setdefault("Content-Type", "application/json")
    return request("POST", url, data=data, headers=headers, timeout=timeout)


def put(url: str, data: Any = None, headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0) -> HTTPResponse:
    if data is not None and not isinstance(data, bytes):
        data = json.dumps(data).encode("utf-8")
        headers = headers or {}
        headers.setdefault("Content-Type", "application/json")
    return request("PUT", url, data=data, headers=headers, timeout=timeout)


def delete(url: str, headers: Optional[Dict[str, str]] = None,
           timeout: float = 30.0) -> HTTPResponse:
    return request("DELETE", url, headers=headers, timeout=timeout)


def head(url: str, headers: Optional[Dict[str, str]] = None,
         timeout: float = 30.0) -> HTTPResponse:
    return request("HEAD", url, headers=headers, timeout=timeout)
