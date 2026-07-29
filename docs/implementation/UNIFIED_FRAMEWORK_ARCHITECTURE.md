# Unified Framework Architecture (UFA) — Implementation

**Sprint 11** | **Status: Complete** | **Tests: 250 passing**

## Overview

The UFA is the foundational framework platform that every official I language framework must build upon. It provides the engineering infrastructure that eliminates code duplication across frameworks and ensures consistent behavior.

## Architecture

```
src/ufa/
├── __init__.py          # Package version (0.1.0)
├── core.py              # Application orchestrator & context
├── lifecycle.py         # Phase management (CREATE→CONFIGURE→INIT→START→RUN→STOP→DESTROY)
├── container.py         # Dependency injection (singleton, transient, scoped, factory)
├── configuration.py     # Hierarchical config with env vars, profiles, deep merge
├── plugins.py           # Plugin discovery, lifecycle, permissions, dependency resolution
├── events.py            # Pub/sub event bus with wildcards, priority, filtering
├── middleware.py         # Ordered middleware pipeline with phases and error handling
├── commands.py          # Command/query message bus with pipeline behaviors
├── scheduler.py         # Task scheduling (once, interval, cron) & background workers
├── observability.py     # Structured logging, metrics collection, distributed tracing
├── security.py          # Identity, RBAC, tokens, encryption, audit logging
├── cache.py             # In-memory cache with TTL, LRU, multi-region cache manager
├── health.py            # Health checks, liveness/readiness probes, aggregated reports
├── localization.py      # Multi-language support with translation stores, pluralization
├── ai.py                # LLM provider abstraction, prompt templates, token tracking
└── modules.py           # Module system with dependency resolution and lifecycle
```

## Subsystems

### 1. Application Core (`core.py`)

The `Application` class is the top-level orchestrator:

```python
from ufa.core import Application

app = Application("my-framework", "1.0.0")
app.configure({"server": {"port": 8080}})
app.run()
# ... application lifecycle ...
app.shutdown()
```

`ApplicationContext` provides unified access to all subsystems.

### 2. Lifecycle (`lifecycle.py`)

Manages phases: `CREATED → CONFIGURED → INITIALIZED → STARTING → RUNNING → STOPPING → STOPPED → DESTROYING → DESTROYED`

- Hook registration with priority ordering
- One-time hooks
- Error propagation
- Phase history tracking

### 3. Dependency Injection (`container.py`)

- **Singleton**: One instance shared across the container
- **Transient**: New instance per resolution
- **Scoped**: One instance per scope
- **Factory**: Custom factory function
- **Instance**: Pre-created instance registration
- Parent-child container hierarchy
- Thread-safe operations

### 4. Configuration (`configuration.py`)

- Dot-notation access (`config.get("server.port")`)
- Deep merge of configuration dictionaries
- Environment variable loading (`I_SERVER__PORT=8080`)
- JSON file loading/saving
- Profile-based configuration switching

### 5. Plugin System (`plugins.py`)

- Plugin registration and lifecycle (REGISTERED → LOADED → INITIALIZED → STARTED)
- Topological dependency resolution
- Permission checking
- Metadata (name, version, author, framework, tags)

### 6. Event Bus (`events.py`)

- Pub/sub with wildcard patterns (`*`)
- Priority-based ordering
- One-time subscriptions
- Event propagation stopping
- Filter functions
- Event history

### 7. Middleware Pipeline (`middleware.py`)

- Phase-based execution (PRE → ROUTE → CONTROLLER → POST)
- Priority ordering
- Context stopping
- Terminal handler
- Error handlers

### 8. Command/Message Bus (`commands.py`)

- Command dispatch with handlers
- Query dispatch with handlers
- Pipeline behaviors (wrapping all handlers)
- Elapsed time tracking
- Batch dispatch

### 9. Task Scheduler (`scheduler.py`)

- Once, interval, and cron scheduling
- Background workers with stop signals
- Task lifecycle management (pause, resume, cancel)
- Tick-based execution

### 10. Observability (`observability.py`)

- **Logger**: Structured logging with levels, handlers, correlation IDs
- **MetricsCollector**: Counters, gauges, histograms
- **Tracer**: Span management with parent-child relationships

### 11. Security (`security.py`)

- Identity management with roles and permissions
- Token-based authentication
- Policy-based authorization
- Password hashing and verification
- Encryption
- Audit logging

### 12. Caching (`cache.py`)

- TTL-based expiration
- LRU eviction
- Multi-region cache manager
- Cache statistics (hit rate, misses)
- Cleanup of expired entries

### 13. Health Monitoring (`health.py`)

- Health check registration
- Liveness and readiness probes
- Critical vs non-critical checks
- Aggregated health reports
- History tracking

### 14. Localization (`localization.py`)

- Multi-language translation stores
- Variable interpolation (`{name}`)
- Pluralization support
- Locale detection
- JSON translation file loading
- Custom formatters

### 15. AI Integration (`ai.py`)

- LLM provider abstraction
- Prompt template rendering with variables
- Token usage tracking by provider/model
- Provider health checks
- Complete and chat API

### 16. Module System (`modules.py`)

- Module lifecycle (REGISTERED → LOADED → INITIALIZED → STARTED)
- Dependency resolution with topological sort
- Service registration per module
- Circular dependency detection

## Test Coverage

| Module | Tests |
|--------|-------|
| lifecycle | 11 |
| container | 12 |
| configuration | 18 |
| plugins | 12 |
| events | 16 |
| middleware | 9 |
| commands | 12 |
| scheduler | 11 |
| observability | 18 |
| security | 14 |
| cache | 15 |
| health | 13 |
| localization | 15 |
| ai | 16 |
| modules | 12 |
| integration | 34 |
| **Total** | **250** |

## Framework Integration

Every official I framework will inherit from the Application class:

```python
from ufa.core import Application

class UrubugaApp(Application):
    def __init__(self):
        super().__init__("urubuga", "1.0.0")
        self.configure({...})
```

## Next Steps

With UFA complete and approved, the next sprint (12) will implement **urubuga** (web framework), which will be the first framework built on UFA.
