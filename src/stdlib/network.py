"""network — Network utilities for the I language.

Provides socket operations, DNS lookup, and URL parsing.
"""

from __future__ import annotations

import socket
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# DNS
# ---------------------------------------------------------------------------

def resolve(host: str) -> List[str]:
    """Resolve hostname to IP addresses."""
    try:
        results = socket.getaddrinfo(host, None)
        return list({r[4][0] for r in results})
    except socket.gaierror:
        return []


def reverse_dns(ip: str) -> Optional[str]:
    """Reverse DNS lookup."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        return None


# ---------------------------------------------------------------------------
# Socket
# ---------------------------------------------------------------------------

def hostname() -> str:
    return socket.gethostname()


def connect(host: str, port: int, timeout: float = 5.0) -> socket.socket:
    """Create a TCP connection."""
    sock = socket.create_connection((host, port), timeout=timeout)
    return sock


def is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (ConnectionRefusedError, OSError, socket.timeout):
        return False


# ---------------------------------------------------------------------------
# URL parsing
# ---------------------------------------------------------------------------

class URL:
    """Parsed URL."""

    def __init__(self, url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        self.scheme = parsed.scheme
        self.host = parsed.hostname or ""
        self.port = parsed.port
        self.path = parsed.path
        self.query = dict(urllib.parse.parse_qsl(parsed.query))
        self.fragment = parsed.fragment
        self.username = parsed.username
        self.password = parsed.password
        self._raw = url

    @property
    def base(self) -> str:
        return f"{self.scheme}://{self.host}" + (f":{self.port}" if self.port else "")

    @property
    def origin(self) -> str:
        return self.base

    def __str__(self) -> str:
        return self._raw

    def __repr__(self) -> str:
        return f"URL({self._raw!r})"


def parse_url(url: str) -> URL:
    return URL(url)


def build_url(base: str, path: str = "", query: Optional[Dict[str, str]] = None) -> str:
    """Build a URL from components."""
    url = base.rstrip("/") + "/" + path.lstrip("/")
    if query:
        qs = urllib.parse.urlencode(query)
        url += "?" + qs
    return url


def encode_query(params: Dict[str, str]) -> str:
    return urllib.parse.urlencode(params)


def decode_query(qs: str) -> Dict[str, str]:
    return dict(urllib.parse.parse_qsl(qs))


def url_encode(s: str) -> str:
    return urllib.parse.quote(s)


def url_decode(s: str) -> str:
    return urllib.parse.unquote(s)
