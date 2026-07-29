"""app — The urubuga Application class.

Central orchestrator that combines UFA with web-specific capabilities:
routing, middleware, authentication, templates, static files, and more.
"""

from __future__ import annotations

import json
import time
from typing import Any, Callable, Dict, List, Optional, Type, Union

from ufa.core import Application as UFAApplication, ApplicationContext
from ufa.lifecycle import Phase

from urubuga.http.request_response import (
    Headers, HTTPMethod, Request, Response, StatusCode,
)
from urubuga.routing.router import Route, RouteGroup, RouteMatch, Router
from urubuga.middleware.builtin import (
    CompressionMiddleware, CORSMiddleware, CSRFMiddleware,
    ExceptionHandlerMiddleware, MiddlewareResult,
    RateLimitMiddleware, RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from urubuga.auth.authentication import (
    APIKeyManager, AuthMethod, AuthorizationManager, JWTConfig,
    JWTManager, Policy, Role, SessionStore, User,
)
from urubuga.validation import Schema, ValidationResult


class WebApplicationContext(ApplicationContext):
    """Extended context with web-specific services."""

    def __init__(self, app: "UrubugaApplication") -> None:
        super().__init__(app)
        self.router: Router = app.router
        self.jwt: JWTManager = app.jwt
        self.sessions: SessionStore = app.sessions
        self.api_keys: APIKeyManager = app.api_keys
        self.authorization: AuthorizationManager = app.authorization


class UrubugaApplication(UFAApplication):
    """The urubuga web application.

    Extends UFA Application with web-specific capabilities:
    - HTTP routing with parameters
    - Middleware pipeline
    - JWT / session / API key authentication
    - RBAC authorization
    - Request validation
    - Template rendering
    - Static file serving
    - WebSocket support
    - GraphQL foundation
    - Server-Sent Events
    """

    def __init__(self, name: str = "urubuga-app",
                 version: str = "0.1.0",
                 debug: bool = False) -> None:
        super().__init__(name, version)
        self.debug = debug

        self.router = Router()
        self.jwt = JWTManager()
        self.sessions = SessionStore()
        self.api_keys = APIKeyManager()
        self.authorization = AuthorizationManager()

        self._middleware: List[Callable] = []
        self._error_handlers: Dict[type, Callable] = {}
        self._startup_time: float = 0.0

        self._exception_handler = ExceptionHandlerMiddleware()
        self._request_logger = RequestLoggingMiddleware()
        self._cors = CORSMiddleware()
        self._rate_limiter: Optional[RateLimitMiddleware] = None
        self._security_headers = SecurityHeadersMiddleware()
        self._csrf = CSRFMiddleware()
        self._compression = CompressionMiddleware()

        self._register_builtins()

    @property
    def context(self) -> WebApplicationContext:
        if self._context is None:
            self._context = WebApplicationContext(self)
        return self._context

    def route(self, pattern: str, method: str = "GET",
              name: str = "", middleware: Optional[List[str]] = None,
              **kw: Any) -> Callable:
        return self.router.route(pattern, method, name, middleware, **kw)

    def get(self, pattern: str, **kw: Any) -> Callable:
        return self.router.get(pattern, **kw)

    def post(self, pattern: str, **kw: Any) -> Callable:
        return self.router.post(pattern, **kw)

    def put(self, pattern: str, **kw: Any) -> Callable:
        return self.router.put(pattern, **kw)

    def patch(self, pattern: str, **kw: Any) -> Callable:
        return self.router.patch(pattern, **kw)

    def delete(self, pattern: str, **kw: Any) -> Callable:
        return self.router.delete(pattern, **kw)

    def head(self, pattern: str, **kw: Any) -> Callable:
        return self.router.head(pattern, **kw)

    def group(self, prefix: str = "",
              middleware: Optional[List[str]] = None,
              **kw: Any) -> RouteGroup:
        return self.router.group(prefix, middleware, **kw)

    def use(self, middleware: Callable, **kw: Any) -> None:
        self._middleware.append(middleware)

    def error_handler(self, exception_type: type) -> Callable:
        def decorator(fn: Callable) -> Callable:
            self._error_handlers[exception_type] = fn
            self._exception_handler._handlers[exception_type] = fn
            return fn
        return decorator

    def url_for(self, name: str, **kwargs: Any) -> str:
        return self.router.url_for(name, **kwargs)

    def configure_cors(self, **kwargs: Any) -> None:
        self._cors = CORSMiddleware(**kwargs)

    def configure_rate_limiting(self, max_requests: int = 100,
                                window_sec: int = 60) -> None:
        self._rate_limiter = RateLimitMiddleware(max_requests, window_sec)
        self.use(self._rate_limiter)

    def configure_csrf(self, secret: str = "") -> None:
        self._csrf = CSRFMiddleware(secret=secret)

    def configure_jwt(self, **kwargs: Any) -> None:
        self.jwt = JWTManager(JWTConfig(**kwargs))

    def add_role(self, role: Role) -> None:
        self.authorization.add_role(role)

    def add_policy(self, policy: Policy) -> None:
        self.authorization.add_policy(policy)

    def authenticate_jwt(self, handler: Callable) -> Callable:
        def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                user = self.jwt.extract_user(token)
                if user:
                    request.user = user
                    return handler(request, *args, **kwargs)
            return Response.error(StatusCode.UNAUTHORIZED,
                                  "Authentication required")
        return wrapper

    def authenticate_session(self, handler: Callable) -> Callable:
        def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
            session_id = request.cookie("session_id")
            if session_id:
                session = self.sessions.get(session_id)
                if session:
                    user_data = session.get("user", {})
                    user = User(**{k: v for k, v in user_data.items()
                                   if k in User.__slots__})
                    user.authenticated_at = session.get("created_at")
                    user.auth_method = AuthMethod.SESSION
                    request.user = user
                    return handler(request, *args, **kwargs)
            return Response.error(StatusCode.UNAUTHORIZED,
                                  "Session required")
        return wrapper

    def authenticate_api_key(self, handler: Callable) -> Callable:
        def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
            api_key = request.headers.get("x-api-key", "")
            if not api_key:
                api_key = request.query_param("api_key")
            key_data = self.api_keys.validate_key(api_key)
            if key_data:
                user = User(id=key_data.get("user_id", ""),
                            auth_method=AuthMethod.API_KEY)
                user.authenticated_at = key_data.get("created_at")
                request.user = user
                return handler(request, *args, **kwargs)
            return Response.error(StatusCode.UNAUTHORIZED,
                                  "Invalid API key")
        return wrapper

    def authorize(self, permission: str,
                  policy_name: Optional[str] = None) -> Callable:
        def decorator(handler: Callable) -> Callable:
            def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
                if not request.user:
                    return Response.error(StatusCode.UNAUTHORIZED,
                                          "Authentication required")
                if not self.authorization.authorize(
                        request.user, permission,
                        policy_name=policy_name):
                    return Response.error(StatusCode.FORBIDDEN,
                                          "Insufficient permissions")
                return handler(request, *args, **kwargs)
            return wrapper
        return decorator

    def validate(self, schema: Schema) -> Callable:
        def decorator(handler: Callable) -> Callable:
            def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
                data = request.json() if request.is_json else request.form()
                result = schema.validate(data)
                if not result.is_valid:
                    return Response.json(
                        {"errors": result.to_dict()["errors"]},
                        StatusCode.UNPROCESSABLE_ENTITY)
                request.state["validated"] = result.data
                return handler(request, *args, **kwargs)
            return wrapper
        return decorator

    def json_response(self, data: Any,
                      status: int = 200,
                      headers: Optional[Dict[str, str]] = None) -> Response:
        return Response.json(data, status, headers)

    def text_response(self, text: str,
                      status: int = 200) -> Response:
        return Response.text(text, status)

    def html_response(self, html: str,
                      status: int = 200) -> Response:
        return Response.html(html, status)

    def redirect(self, url: str,
                 status: int = 302) -> Response:
        return Response.redirect(url, status)

    def handle_request(self, method: str, path: str,
                       headers: Optional[Dict[str, str]] = None,
                       body: bytes = b"",
                       query_string: str = "") -> Response:
        request = Request(method, path, query_string, headers, body)

        match = self.router.match(method, path)

        if match:
            request._path_params = match.params
            result = self._execute_pipeline(request, match)
            if isinstance(result, Response):
                return result
            if isinstance(result, dict):
                return Response.json(result)
            if isinstance(result, str):
                return Response.html(result)
            if result is None:
                return Response.no_content()
            return Response.json(result)

        for mw in self._middleware:
            if mw is self._exception_handler:
                continue
            try:
                mw_result = mw(request)
                if isinstance(mw_result, MiddlewareResult):
                    if not mw_result.continue_processing:
                        return mw_result.response
            except Exception:
                pass

        allowed = self.router.method_allowed(path, method)
        if allowed:
            return Response.error(StatusCode.METHOD_NOT_ALLOWED,
                                  f"Method {method} not allowed. "
                                  f"Allowed: {', '.join(allowed)}")
        return Response.error(StatusCode.NOT_FOUND,
                              f"No route for {method} {path}")

    def _execute_pipeline(self, request: Request,
                          match: RouteMatch) -> Any:
        for mw in self._middleware:
            if mw is self._exception_handler:
                continue
            try:
                mw_result = mw(request)
                if isinstance(mw_result, MiddlewareResult):
                    if not mw_result.continue_processing:
                        return mw_result.response
            except Exception as e:
                return self._handle_exception(request, e)

        return self._exception_handler.invoke(request, match.handler)

    def _handle_exception(self, request: Request,
                          error: Exception) -> Response:
        handler = self._error_handlers.get(type(error))
        if handler:
            try:
                return handler(request, error)
            except Exception:
                pass
        for exc_type, handler in self._error_handlers.items():
            if isinstance(error, exc_type):
                try:
                    return handler(request, error)
                except Exception:
                    pass
        message = str(error) if self.debug else "Internal Server Error"
        return Response.error(StatusCode.INTERNAL_SERVER_ERROR, message)

    def _register_builtins(self) -> None:
        self.use(self._exception_handler)
        self.use(self._request_logger)
        self.use(self._cors)
        self.use(self._security_headers)
        self.use(self._compression)

    def run(self) -> None:
        self._startup_time = time.time()
        super().run()

    def route_count(self) -> int:
        return self.router.route_count()

    def middleware_count(self) -> int:
        return len(self._middleware)

    def openapi(self) -> Dict[str, Any]:
        """Generate OpenAPI specification."""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.name,
                "version": self.version,
            },
            "paths": self.router.openapi_paths(),
        }
