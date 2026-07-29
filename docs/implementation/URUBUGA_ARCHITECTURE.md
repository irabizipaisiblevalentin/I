# Urubuga — Official Web Platform of the I Programming Language

**Sprint 12** | **Status: Complete** | **Tests: 237 passing**

## Overview

Urubuga is the official web platform built on UFA (Unified Framework Architecture). It provides a complete web application framework including HTTP, routing, middleware, authentication, real-time communication, GraphQL, templating, AI features, and CLI tooling.

## Architecture

```
src/urubuga/
├── __init__.py                  # Package version (0.1.0)
├── app.py                       # UrubugaApplication — main entry point
├── validation.py                # Schema validation with Field types and custom validators
├── staticfiles.py               # Static file serving with path traversal protection
├── http/
│   └── request_response.py      # Request, Response, Headers, StatusCode
├── routing/
│   └── router.py                # Router with dynamic params, groups, wildcards
├── middleware/
│   └── builtin.py               # CORS, rate limiting, security headers, CSRF, compression, exception handler
├── auth/
│   └── authentication.py        # User, JWT, sessions, API keys, RBAC, policies
├── realtime/
│   ├── websocket.py             # WebSocket connections, rooms, presence
│   └── sse.py                   # Server-Sent Events, SSEManager
├── graphql/
│   └── schema.py                # GraphQL schema, types, queries, mutations
├── templating/
│   └── engine.py                # Template engine with variables, loops, conditionals, inheritance
├── ai/
│   └── features.py              # Prompt pipelines, streaming, AI middleware
└── cli/
    └── commands.py              # CLI scaffolding, build, doctor, analyze, templates
```

## Module Details

### app.py — UrubugaApplication
The main application class extending `Application` from UFA.

```python
from urubuga.app import UrubugaApplication

app = UrubugaApplication(name="myapp", debug=True)

@app.get("/users/{user_id}")
def get_user(req):
    user_id = req.path_param("user_id")
    return {"id": user_id, "name": "Alice"}

app.run()
```

**Key methods:**
- `route(pattern, method)`, `get()`, `post()`, `put()`, `patch()`, `delete()`, `head()`
- `group(prefix)` — route groups with shared prefix/middleware
- `use(middleware)` — add middleware
- `error_handler(exception_type)` — register error handlers
- `handle_request(method, path, headers, body)` — synchronous request handling
- `configure_cors()`, `configure_rate_limiting()`, `configure_csrf()`

### http/request_response.py — Request & Response
- `Request(method, path, query_string, headers, body)` — immutable request representation
- `Response(status, headers, body)` — response with class methods: `.json()`, `.text()`, `.html()`, `.error()`, `.redirect()`
- `Headers` — case-insensitive header container
- `StatusCode` — enum with all HTTP status codes

### routing/router.py — Router
- Pattern matching: `/users/{id}`, `/files/{path:path}`, `/items/{id:int}`
- `RouteGroup` — route groups with prefix, middleware, versioning
- `Router.match(method, path)` → `RouteMatch` with params, handler, metadata
- Named routes with `url_for(name, **params)`
- OpenAPI spec generation via `router.openapi_paths()`

### middleware/builtin.py — Built-in Middleware
All middleware follow the `(request) → MiddlewareResult` convention:

| Middleware | Description |
|-----------|-------------|
| `CORSMiddleware` | Cross-origin resource sharing with preflight |
| `RateLimitMiddleware` | Sliding window rate limiting per IP/key |
| `SecurityHeadersMiddleware` | CSP, HSTS, X-Frame-Options, etc. |
| `CSRFMiddleware` | Token-based CSRF protection |
| `CompressionMiddleware` | Response compression detection |
| `RequestLoggingMiddleware` | Request logging and counting |
| `ExceptionHandlerMiddleware` | Global exception handling (wraps handler execution) |

### auth/authentication.py — Authentication & Authorization
- `User(id, username, roles, permissions)` — user model
- `JWTManager` — JWT token creation and validation
- `SessionStore` — server-side session management
- `APIKeyManager` — API key generation and validation
- `AuthorizationManager` — RBAC role/permission management
- `Policy` — role-based access control policies
- Decorators: `@app.authenticate_jwt`, `@app.authorize("admin")`

### realtime/websocket.py — WebSocket
- `WebSocketConnection` — individual connection with send/close
- `Room` — group messaging with join/leave/broadcast
- `WebSocketManager` — connection and room management
- `Presence` — online/offline user tracking

### realtime/sse.py — Server-Sent Events
- `SSEEvent` — event with data, event type, id, retry
- `SSEClient` — client connection with send
- `SSEManager` — client management, topic subscriptions, broadcasting

### graphql/schema.py — GraphQL
- `TypeDef`, `FieldDef` — type definitions
- `GraphQLSchema` — schema with queries, mutations, type registry
- `schema.execute(query)` — synchronous query execution
- `schema.toSDL()` — SDL introspection generation

### templating/engine.py — Template Engine
- Variable interpolation: `{{variable}}`
- For loops: `{% for item in items %}...{% endfor %}`
- Conditionals: `{% if visible %}...{% else %}...{% endif %}`
- Template inheritance and partials
- Global variables and custom filters

### validation.py — Request Validation
- `Schema(name, fields)` — validation schema
- `Field(name, field_type, required, ...)` — field definition with type, default, validators
- Types: `string`, `integer`, `float`, `boolean`, `list`, `dict`
- Built-in validators: `min_length`, `max_length`, `min_value`, `max_value`, `pattern`, `choices`
- Custom validators: `Field("x", custom=my_validator)`

### ai/features.py — AI Integration
- `PromptStep` — single prompt template with variable mapping
- `PromptPipeline` — multi-step prompt chain with context passing
- `AIRouteHandler` — AI-powered route with streaming support
- `AIMiddleware` — request/response enrichment with AI context

### cli/commands.py — CLI Tools
- `new(name)` — scaffold new project
- `build()` — project build
- `doctor()` — environment diagnostics
- `analyze()` — code quality analysis
- `templates()` — template management

## Middleware Pipeline

```
Request → CORS → RateLimit → SecurityHeaders → CSRF → Compression → ExceptionHandler → Handler → Response
```

The `_execute_pipeline` method in `UrubugaApplication`:
1. Runs each middleware in order — middleware returns `MiddlewareResult.proceed()` or `MiddlewareResult.respond(response)`
2. If no middleware short-circuits, `ExceptionHandlerMiddleware.invoke()` wraps the handler call
3. If no route matches, middleware still runs (enables CORS preflight on any path)

## Testing

237 tests across 8 test files:
- `test_auth.py` (25) — JWT, sessions, API keys, RBAC, policies
- `test_features.py` (48) — WebSocket, SSE, GraphQL, templates, AI, static files
- `test_http.py` (44) — Request, Response, Headers, StatusCode
- `test_routing.py` (36) — Router, patterns, groups, wildcards
- `test_urubuga_integration.py` (34) — Full application integration
- `test_urubuga_middleware.py` (23) — All built-in middleware
- `test_validation.py` (22) — Schema validation
