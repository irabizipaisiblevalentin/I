"""middleware — Web middleware layer.

Provides built-in middleware for CORS, rate limiting, security headers,
request logging, compression, CSRF protection, and request validation.
"""

from __future__ import annotations

import enum
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Callable, Dict, List, Optional, Set

from urubuga.http.request_response import Headers, Request, Response, StatusCode


class MiddlewarePriority:
    SECURITY = 100
    CORS = 90
    RATE_LIMIT = 80
    LOGGING = 70
    COMPRESSION = 60
    CSRF = 50
    AUTH = 40
    VALIDATION = 30
    CUSTOM = 0


class MiddlewareResult:
    __slots__ = ("continue_processing", "response")

    def __init__(self, continue_processing: bool = True,
                 response: Optional[Response] = None) -> None:
        self.continue_processing = continue_processing
        self.response = response

    @classmethod
    def proceed(cls) -> "MiddlewareResult":
        return cls(True)

    @classmethod
    def respond(cls, response: Response) -> "MiddlewareResult":
        return cls(False, response)


class CORSMiddleware:
    """Cross-Origin Resource Sharing middleware."""

    def __init__(self, allow_origins: Optional[List[str]] = None,
                 allow_methods: Optional[List[str]] = None,
                 allow_headers: Optional[List[str]] = None,
                 allow_credentials: bool = False,
                 expose_headers: Optional[List[str]] = None,
                 max_age: int = 86400) -> None:
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or [
            "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or [
            "content-type", "authorization", "x-requested-with"]
        self.expose_headers = expose_headers or []
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    def __call__(self, request: Request) -> MiddlewareResult:
        origin = request.headers.get("origin", "")

        if request.method == "OPTIONS":
            resp = Response(StatusCode.NO_CONTENT)
            self._apply_headers(resp, origin)
            return MiddlewareResult.respond(resp)

        if self._origin_allowed(origin):
            request.state["cors_origin"] = origin
        return MiddlewareResult.proceed()

    def apply_response(self, response: Response,
                       origin: str = "") -> None:
        self._apply_headers(response, origin)

    def _apply_headers(self, response: Response, origin: str) -> None:
        if "*" in self.allow_origins or origin in self.allow_origins:
            response.headers.set("access-control-allow-origin",
                                 origin or "*")
        if self.allow_credentials:
            response.headers.set("access-control-allow-credentials", "true")
        response.headers.set("access-control-allow-methods",
                             ", ".join(self.allow_methods))
        response.headers.set("access-control-allow-headers",
                             ", ".join(self.allow_headers))
        if self.expose_headers:
            response.headers.set("access-control-expose-headers",
                                 ", ".join(self.expose_headers))
        response.headers.set("access-control-max-age", str(self.max_age))

    def _origin_allowed(self, origin: str) -> bool:
        if "*" in self.allow_origins:
            return True
        return origin in self.allow_origins


class RateLimitMiddleware:
    """Rate limiting middleware using a sliding window."""

    def __init__(self, max_requests: int = 100,
                 window_sec: int = 60,
                 key_func: Optional[Callable] = None,
                 message: str = "Rate limit exceeded") -> None:
        self.max_requests = max_requests
        self.window_sec = window_sec
        self.key_func = key_func or self._default_key
        self.message = message
        self._windows: Dict[str, List[float]] = {}

    def __call__(self, request: Request) -> MiddlewareResult:
        key = self.key_func(request)
        now = time.time()
        window_start = now - self.window_sec

        timestamps = self._windows.setdefault(key, [])
        self._windows[key] = [t for t in timestamps if t > window_start]

        if len(self._windows[key]) >= self.max_requests:
            resp = Response.error(StatusCode.TOO_MANY_REQUESTS, self.message)
            retry_after = self._windows[key][0] + self.window_sec - now
            resp.headers.set("retry-after", str(max(1, int(retry_after))))
            resp.headers.set("x-ratelimit-limit", str(self.max_requests))
            resp.headers.set("x-ratelimit-remaining", "0")
            resp.headers.set("x-ratelimit-reset",
                             str(int(now + self.window_sec)))
            return MiddlewareResult.respond(resp)

        self._windows[key].append(now)
        return MiddlewareResult.proceed()

    def _default_key(self, request: Request) -> str:
        return request.client_ip

    def remaining(self, key: str) -> int:
        now = time.time()
        window_start = now - self.window_sec
        timestamps = [t for t in self._windows.get(key, []) if t > window_start]
        return max(0, self.max_requests - len(timestamps))


class SecurityHeadersMiddleware:
    """Adds security headers to responses."""

    def __init__(self, csp: str = "default-src 'self'",
                 hsts_max_age: int = 31536000,
                 frame_options: str = "DENY",
                 content_type_options: bool = True,
                 xss_protection: bool = True,
                 referrer_policy: str = "strict-origin-when-cross-origin",
                 permissions_policy: Optional[Dict[str, str]] = None) -> None:
        self.csp = csp
        self.hsts_max_age = hsts_max_age
        self.frame_options = frame_options
        self.content_type_options = content_type_options
        self.xss_protection = xss_protection
        self.referrer_policy = referrer_policy
        self.permissions_policy = permissions_policy or {}

    def __call__(self, request: Request) -> MiddlewareResult:
        return MiddlewareResult.proceed()

    def apply(self, response: Response) -> None:
        response.headers.set("content-security-policy", self.csp)
        response.headers.set("strict-transport-security",
                             f"max-age={self.hsts_max_age}; includeSubDomains")
        response.headers.set("x-frame-options", self.frame_options)
        if self.content_type_options:
            response.headers.set("x-content-type-options", "nosniff")
        if self.xss_protection:
            response.headers.set("x-xss-protection", "1; mode=block")
        response.headers.set("referrer-policy", self.referrer_policy)
        if self.permissions_policy:
            parts = [f'{k}="{v}"' for k, v in self.permissions_policy.items()]
            response.headers.set("permissions-policy", ", ".join(parts))


class CSRFMiddleware:
    """CSRF token-based protection middleware."""

    def __init__(self, secret: str = "", token_name: str = "_csrf_token",
                 header_name: str = "x-csrf-token",
                 safe_methods: Optional[Set[str]] = None) -> None:
        self.secret = secret or secrets.token_hex(32)
        self.token_name = token_name
        self.header_name = header_name
        self.safe_methods = safe_methods or {"GET", "HEAD", "OPTIONS"}

    def generate_token(self, session_id: str = "") -> str:
        payload = f"{self.secret}:{session_id}"
        return hmac.new(
            self.secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

    def validate_token(self, token: str, session_id: str = "") -> bool:
        if not token:
            return False
        expected = self.generate_token(session_id)
        return hmac.compare_digest(token, expected)

    def __call__(self, request: Request) -> MiddlewareResult:
        if request.method in self.safe_methods:
            return MiddlewareResult.proceed()

        token = (request.headers.get(self.header_name) or
                 request.form().get(self.token_name) or
                 request.query_param(self.token_name))

        if not self.validate_token(token):
            return MiddlewareResult.respond(
                Response.error(StatusCode.FORBIDDEN, "CSRF token invalid"))

        return MiddlewareResult.proceed()


class RequestLoggingMiddleware:
    """Logs request/response details."""

    def __init__(self, log_fn: Optional[Callable] = None) -> None:
        self.log_fn = log_fn or self._default_log
        self._request_count = 0

    def __call__(self, request: Request) -> MiddlewareResult:
        self._request_count += 1
        self.log_fn(request.method, request.path, 0.0)
        return MiddlewareResult.proceed()

    def _default_log(self, method: str, path: str, elapsed_ms: float) -> None:
        pass

    @property
    def request_count(self) -> int:
        return self._request_count


class CompressionMiddleware:
    """Response compression middleware."""

    def __init__(self, min_size: int = 1000) -> None:
        self.min_size = min_size

    def __call__(self, request: Request) -> MiddlewareResult:
        return MiddlewareResult.proceed()


class ExceptionHandlerMiddleware:
    """Global exception handler — wraps handler execution with error handling."""

    def __init__(self) -> None:
        self._handlers: Dict[type, Callable] = {}
        self._default_handler: Optional[Callable] = None
        self._error_log: List[Dict[str, Any]] = []

    def handle(self, exception_type: type,
               handler: Optional[Callable] = None) -> Callable:
        def decorator(fn: Optional[Callable] = None) -> Callable:
            if fn is None:
                self._handlers[exception_type] = handler or self._default_error
            else:
                self._handlers[exception_type] = fn
            return fn
        return decorator

    def set_default(self, handler: Callable) -> None:
        self._default_handler = handler

    def invoke(self, request: Request, handler_fn: Callable) -> Any:
        try:
            return handler_fn(request)
        except Exception as e:
            self._log_error(request, e)
            handler = self._handlers.get(type(e))
            if not handler:
                for exc_type, h in self._handlers.items():
                    if isinstance(e, exc_type):
                        handler = h
                        break
            if handler:
                try:
                    return handler(request, e)
                except Exception:
                    pass
            return Response.error(StatusCode.INTERNAL_SERVER_ERROR, str(e))

    def __call__(self, request: Request) -> MiddlewareResult:
        return MiddlewareResult.proceed()

    def _log_error(self, request: Request, error: Exception) -> None:
        self._error_log.append({
            "method": request.method,
            "path": request.path,
            "error": type(error).__name__,
            "message": str(error),
            "timestamp": time.time(),
        })

    def _default_error(self, request: Request,
                       error: Exception) -> Response:
        return Response.error(StatusCode.INTERNAL_SERVER_ERROR, str(error))

    @property
    def error_count(self) -> int:
        return len(self._error_log)

    @property
    def error_log(self) -> List[Dict[str, Any]]:
        return list(self._error_log)
