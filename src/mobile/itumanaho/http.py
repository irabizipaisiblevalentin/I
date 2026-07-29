"""HTTP client with caching, retry, interception, and streaming support."""

import asyncio
import json
import os
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import (Any, Callable, Dict, List, Optional, Protocol, Tuple,
                    TypeVar)

T = TypeVar("T")

ProgressCallback = Callable[[int, int], None]


class HTTPMethod(Enum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"


@dataclass
class HTTPRequest:
    """Represents an HTTP request.

    Args:
        url: Target URL.
        method: HTTP method.
        headers: Request headers.
        body: Request body.
        params: URL query parameters.
        timeout: Request timeout in seconds.
        retry: Number of retry attempts on failure.
    """

    url: str
    method: HTTPMethod = HTTPMethod.GET
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Any] = None
    params: Dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0
    retry: int = 0


@dataclass
class HTTPResponse:
    """Represents an HTTP response.

    Args:
        status: HTTP status code.
        headers: Response headers.
        body: Response body content.
    """

    status: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Any] = None

    def json(self) -> Any:
        """Parse the response body as JSON.

        Returns:
            Parsed JSON data.

        Raises:
            ValueError: If body is not valid JSON or is None.
        """
        if self.body is None:
            raise ValueError("response body is empty")
        if isinstance(self.body, dict):
            return self.body
        return json.loads(self.body)


class HTTPInterceptor(Protocol):
    """Protocol for HTTP request/response interceptors."""

    def intercept_request(self, request: HTTPRequest) -> HTTPRequest:
        """Intercept and optionally modify a request before sending.

        Args:
            request: The outgoing HTTP request.

        Returns:
            The (possibly modified) request.
        """
        ...

    def intercept_response(
        self, request: HTTPRequest, response: HTTPResponse
    ) -> HTTPResponse:
        """Intercept and optionally modify a response before returning.

        Args:
            request: The original request.
            response: The incoming HTTP response.

        Returns:
            The (possibly modified) response.
        """
        ...


class HTTPCacheEntry:
    """Internal cache entry with expiry."""

    def __init__(
        self, response: HTTPResponse, ttl: float
    ) -> None:
        self.response = response
        self.expires_at = time.time() + ttl


class HTTPCache:
    """Simple in-memory HTTP response cache.

    Args:
        default_ttl: Default cache lifetime in seconds.
    """

    def __init__(self, default_ttl: float = 60.0) -> None:
        self._cache: Dict[str, HTTPCacheEntry] = {}
        self._default_ttl: float = default_ttl

    def get(self, key: str) -> Optional[HTTPResponse]:
        """Get a cached response if it hasn't expired.

        Args:
            key: Cache key (typically the URL).

        Returns:
            The cached response or None.
        """
        entry = self._cache.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            del self._cache[key]
            return None
        return entry.response

    def set(
        self, key: str, response: HTTPResponse, ttl: Optional[float] = None
    ) -> None:
        """Cache a response.

        Args:
            key: Cache key.
            response: The response to cache.
            ttl: Time-to-live in seconds (uses default if None).
        """
        self._cache[key] = HTTPCacheEntry(
            response, ttl if ttl is not None else self._default_ttl
        )

    def invalidate(self, key: str) -> None:
        """Remove an entry from the cache.

        Args:
            key: Cache key to remove.
        """
        self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


class AuthProvider(Protocol):
    """Protocol for authentication providers."""

    def authenticate(self, request: HTTPRequest) -> HTTPRequest:
        """Apply authentication to a request.

        Args:
            request: The HTTP request to authenticate.

        Returns:
            The authenticated request.
        """
        ...


class BearerAuth:
    """Bearer token authentication.

    Args:
        token: The bearer token.
    """

    def __init__(self, token: str) -> None:
        self._token: str = token

    def authenticate(self, request: HTTPRequest) -> HTTPRequest:
        """Apply bearer authentication header.

        Args:
            request: The HTTP request.

        Returns:
            Request with Authorization header set.
        """
        request.headers["Authorization"] = f"Bearer {self._token}"
        return request


class BasicAuth:
    """Basic HTTP authentication.

    Args:
        username: The username.
        password: The password.
    """

    def __init__(self, username: str, password: str) -> None:
        self._username: str = username
        self._password: str = password

    def authenticate(self, request: HTTPRequest) -> HTTPRequest:
        """Apply basic authentication header.

        Args:
            request: The HTTP request.

        Returns:
            Request with Authorization header set.
        """
        import base64

        credentials = f"{self._username}:{self._password}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        request.headers["Authorization"] = f"Basic {encoded}"
        return request


class MultipartFormData:
    """Multipart form data builder.

    Args:
        fields: Dictionary of form fields.
        files: Dictionary of field name to file path.
    """

    def __init__(
        self,
        fields: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, str]] = None,
    ) -> None:
        self._fields: Dict[str, str] = fields or {}
        self._files: Dict[str, str] = files or {}

    def add_field(self, name: str, value: str) -> None:
        """Add a text field.

        Args:
            name: Field name.
            value: Field value.
        """
        self._fields[name] = value

    def add_file(self, name: str, file_path: str) -> None:
        """Add a file field.

        Args:
            name: Field name.
            file_path: Path to the file.
        """
        self._files[name] = file_path


class HTTPClient:
    """HTTP client with caching, retry, interception, and streaming.

    Args:
        base_url: Base URL for relative requests.
        default_timeout: Default timeout in seconds.
        cache: Optional HTTPCache instance.
        interceptors: List of HTTPInterceptor instances.
        auth: Optional authentication provider.
    """

    def __init__(
        self,
        base_url: str = "",
        default_timeout: float = 30.0,
        cache: Optional[HTTPCache] = None,
        interceptors: Optional[List[HTTPInterceptor]] = None,
        auth: Optional[AuthProvider] = None,
    ) -> None:
        self._base_url: str = base_url.rstrip("/")
        self._default_timeout: float = default_timeout
        self._cache: HTTPCache = cache or HTTPCache()
        self._interceptors: List[HTTPInterceptor] = interceptors or []
        self._auth: Optional[AuthProvider] = auth

    def _resolve_url(self, url: str) -> str:
        """Resolve a potentially relative URL against the base URL.

        Args:
            url: The URL to resolve.

        Returns:
            The absolute URL.
        """
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return f"{self._base_url}/{url.lstrip('/')}"

    def _build_full_url(self, request: HTTPRequest) -> str:
        """Build the full URL including query parameters.

        Args:
            request: The HTTP request.

        Returns:
            The full URL string.
        """
        url = self._resolve_url(request.url)
        if request.params:
            import urllib.parse

            query_string = urllib.parse.urlencode(request.params)
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{query_string}"
        return url

    def _build_cache_key(self, request: HTTPRequest) -> str:
        """Build a cache key for a request.

        Args:
            request: The HTTP request.

        Returns:
            A string cache key.
        """
        full_url = self._build_full_url(request)
        return f"{request.method.value}:{full_url}"

    async def request(
        self,
        method: HTTPMethod,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        retry: Optional[int] = None,
        use_cache: bool = False,
        stream: bool = False,
        progress: Optional[ProgressCallback] = None,
    ) -> HTTPResponse:
        """Execute an HTTP request.

        Args:
            method: HTTP method.
            url: Target URL.
            headers: Request headers.
            body: Request body.
            params: URL query parameters.
            timeout: Request timeout.
            retry: Number of retries on failure.
            use_cache: Whether to check the cache first.
            stream: Whether to stream the response.
            progress: Progress callback (current, total).

        Returns:
            The HTTP response.
        """
        request_obj = HTTPRequest(
            url=url,
            method=method,
            headers=headers or {},
            body=body,
            params=params or {},
            timeout=timeout or self._default_timeout,
            retry=retry if retry is not None else 0,
        )

        if self._auth is not None:
            request_obj = self._auth.authenticate(request_obj)

        for interceptor in self._interceptors:
            request_obj = interceptor.intercept_request(request_obj)

        if use_cache and method == HTTPMethod.GET:
            cache_key = self._build_cache_key(request_obj)
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        full_url = self._build_full_url(request_obj)
        attempts = 0
        max_attempts = request_obj.retry + 1
        last_error: Optional[Exception] = None

        while attempts < max_attempts:
            attempts += 1
            try:
                response = await self._send(
                    request_obj, full_url, stream, progress
                )
                break
            except Exception as e:
                last_error = e
                if attempts >= max_attempts:
                    raise
                await asyncio.sleep(2**attempts)

        for interceptor in self._interceptors:
            response = interceptor.intercept_response(request_obj, response)

        if use_cache and method == HTTPMethod.GET and response.status == 200:
            cache_key = self._build_cache_key(request_obj)
            self._cache.set(cache_key, response)

        return response

    async def _send(
        self,
        request: HTTPRequest,
        url: str,
        stream: bool = False,
        progress: Optional[ProgressCallback] = None,
    ) -> HTTPResponse:
        """Internal send method - simulates HTTP transport.

        In a real implementation this would use aiohttp or httpx.
        """
        import urllib.request as urllib

        req = urllib.Request(
            url,
            data=request.body if isinstance(request.body, bytes) else None,
            headers=request.headers,
            method=request.method.value,
        )
        try:
            with urllib.urlopen(req, timeout=request.timeout) as resp:
                body = resp.read()
                if progress:
                    progress(len(body), len(body))
                headers = dict(resp.headers)
                return HTTPResponse(
                    status=resp.status,
                    headers=headers,
                    body=body,
                )
        except Exception as e:
            raise IOError(f"HTTP request failed: {e}") from e

    async def get(
        self,
        url: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_cache: bool = False,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Send a GET request.

        Args:
            url: Target URL.
            params: Query parameters.
            headers: Request headers.
            use_cache: Whether to use cache.
            timeout: Request timeout.

        Returns:
            The HTTP response.
        """
        return await self.request(
            HTTPMethod.GET,
            url,
            headers=headers,
            params=params,
            timeout=timeout,
            use_cache=use_cache,
        )

    async def post(
        self,
        url: str,
        body: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Send a POST request.

        Args:
            url: Target URL.
            body: Request body.
            headers: Request headers.
            params: Query parameters.
            timeout: Request timeout.

        Returns:
            The HTTP response.
        """
        return await self.request(
            HTTPMethod.POST,
            url,
            headers=headers,
            body=body,
            params=params,
            timeout=timeout,
        )

    async def put(
        self,
        url: str,
        body: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Send a PUT request.

        Args:
            url: Target URL.
            body: Request body.
            headers: Request headers.
            params: Query parameters.
            timeout: Request timeout.

        Returns:
            The HTTP response.
        """
        return await self.request(
            HTTPMethod.PUT,
            url,
            headers=headers,
            body=body,
            params=params,
            timeout=timeout,
        )

    async def patch(
        self,
        url: str,
        body: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Send a PATCH request.

        Args:
            url: Target URL.
            body: Request body.
            headers: Request headers.
            params: Query parameters.
            timeout: Request timeout.

        Returns:
            The HTTP response.
        """
        return await self.request(
            HTTPMethod.PATCH,
            url,
            headers=headers,
            body=body,
            params=params,
            timeout=timeout,
        )

    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Send a DELETE request.

        Args:
            url: Target URL.
            headers: Request headers.
            params: Query parameters.
            timeout: Request timeout.

        Returns:
            The HTTP response.
        """
        return await self.request(
            HTTPMethod.DELETE,
            url,
            headers=headers,
            params=params,
            timeout=timeout,
        )

    async def upload(
        self,
        url: str,
        multipart: MultipartFormData,
        headers: Optional[Dict[str, str]] = None,
        progress: Optional[ProgressCallback] = None,
        timeout: Optional[float] = None,
    ) -> HTTPResponse:
        """Upload files using multipart form data.

        Args:
            url: Target URL.
            multipart: The multipart form data.
            headers: Additional headers.
            progress: Progress callback.
            timeout: Request timeout.

        Returns:
            The HTTP response.
        """
        import io
        import mimetypes

        boundary = uuid.uuid4().hex
        body_parts: List[bytes] = []
        total_size = 0

        for name, value in multipart._fields.items():
            part = (
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                f'{value}\r\n'
            ).encode("utf-8")
            body_parts.append(part)
            total_size += len(part)

        for name, file_path in multipart._files.items():
            with open(file_path, "rb") as f:
                file_data = f.read()
            content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            filename = os.path.basename(file_path)
            part_header = (
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                f'Content-Type: {content_type}\r\n\r\n'
            ).encode("utf-8")
            body_parts.append(part_header)
            body_parts.append(file_data)
            body_parts.append(b"\r\n")
            total_size += len(part_header) + len(file_data) + 2

        body_parts.append(f'--{boundary}--\r\n'.encode("utf-8"))
        total_size += len(body_parts[-1])

        body = b"".join(body_parts)
        merged_headers = headers or {}
        merged_headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"

        if progress:
            progress(0, total_size)
            progress(total_size, total_size)

        return await self.request(
            HTTPMethod.POST,
            url,
            headers=merged_headers,
            body=body,
            timeout=timeout,
        )

    async def download(
        self,
        url: str,
        destination: str,
        headers: Optional[Dict[str, str]] = None,
        progress: Optional[ProgressCallback] = None,
        timeout: Optional[float] = None,
    ) -> str:
        """Download a file to a local path.

        Args:
            url: Source URL.
            destination: Local file path.
            headers: Request headers.
            progress: Progress callback.
            timeout: Request timeout.

        Returns:
            The path to the downloaded file.
        """
        response = await self.request(
            HTTPMethod.GET,
            url,
            headers=headers,
            timeout=timeout,
            stream=True,
            progress=progress,
        )
        dest_dir = os.path.dirname(os.path.abspath(destination))
        os.makedirs(dest_dir, exist_ok=True)
        with open(destination, "wb") as f:
            if isinstance(response.body, bytes):
                f.write(response.body)
            elif response.body is not None:
                f.write(str(response.body).encode("utf-8"))
        return destination
