# URUBUGA_ARCHITECTURE.md — Urubuga Framework Architecture

## Urubuga — Uburyo bwo Gukora Amatafari y'Urubuga

**The official full-stack web platform of the I Programming Language.**

Urubuga competes with Django, Laravel, Rails, Express.js, Next.js, and all major web frameworks. It is built entirely in the I language using `.i` files, providing a batteries-included web development experience.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Framework Modules](#framework-modules)
4. [Native Modules](#native-modules)
5. [CLI Commands](#cli-commands)
6. [Project Templates](#project-templates)
7. [Database Layer](#database-layer)
8. [Authentication](#authentication)
9. [Real-time Platform](#real-time-platform)
10. [AI Integration](#ai-integration)
11. [Deployment](#deployment)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Application (.i)                     │
├─────────────────────────────────────────────────────────────┤
│                    Urubuga Framework (.i)                    │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │  Router  │Middleware│  Auth    │   ORM    │Template  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Native Modules (Python)                   │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │HTTPServer│WebSocket │Database  │Security  │   JSON   │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    I Language VM (Python)                    │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │  Lexer   │  Parser  │Codegen  │ Executor │   GC     │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### UrubugaApplication (`urubuga/ubatse.i`)

The central orchestrator that combines all framework capabilities:

```i
shyiramo "urubuga/ubatse"

shyira app = gukora_urubuga("my-app", "0.1.0", ukuri)

app.GET("/", lambda req: app.dorera("index", {"izina": "My App"}))
app.gukora(3000)
```

**Key methods:**
- `gukora_urubuga(izina, ubuvandimwe, debug)` — Create application
- `GET/POST/PUT/DELETE/PATCH/HEAD/OPTIONS(inzira, handler)` — Register routes
- `shakisha_porogaramu(handler)` — Add middleware
- `gukora(port)` — Start server
- `gukora_threaded(port)` — Start server in background thread
- `dorera(template, data)` — Render template
- `json_(data, status)` — JSON response
- `html_(html, status)` — HTML response
- `redirect(url, status)` — Redirect response
- `error_(status, message)` — Error response

### Router (`urubuga/ubatse.i` — UrubugaUmuyoboro)

Enterprise-grade URL routing:

```i
# Static routes
app.GET("/", home_handler)
app.POST("/api/users", create_user)

# Dynamic routes
app.GET("/users/{id}", get_user)
app.GET("/posts/{slug}/comments/{cid}", get_comment)
```

**Features:**
- Static routes
- Dynamic parameters `{param}`
- Route groups via `icamba()`
- Named routes
- OpenAPI generation

### Middleware Pipeline (`urubuga/ubatse.i` — UrubugaPorogaramu)

```i
# Add middleware
app.shakisha_porogaramu(lambda req: check_auth(req))
app.shakisha_porogaramu(lambda req: rate_limit(req))

# Security middleware
app.shakisha_porogaramu(app.uburinzi_.kuba(handler))
```

---

## Framework Modules

### Module Structure

```
urubuga/
├── ubatse.i              # Core framework, router, middleware, cache, logger
├── api.i                 # REST API platform, CRUD, validation, CORS, rate limiting
├── realtime.i            # WebSocket, SSE, presence, rooms
├── graphql.i             # GraphQL schema, queries, mutations, playground
├── inyandikorumurongo.i  # Template engine, components, CSS framework
├── ai.i                  # AI integration, chat, embeddings, search
├── ssr.i                 # Server-side rendering, static site generation
├── amashusho/            # Theme files
└── ibikubiyemo/          # Component library
```

### API Platform (`urubuga/api.i`)

```i
shyiramo "urubuga/api"

shyira api = UrubugaAPI.nshya(app)

# Auto-generate CRUD endpoints
api.CRUD("/api/v1/users", "users")
# Creates: GET /, GET /{id}, POST /, PUT /{id}, DELETE /{id}

# Pagination
shyira paginator = UrubugaPagination.nshya()
shyira page = paginator.paginate(items, 1, 20)

# Validation
shyira validator = UrubugaValidation.nshya()
validator.shakisha("user", {
    "izina": {"ubwoko": "umuntu", "birakenewe": ukuri, "min": 2, "max": 100},
    "email": {"ubwoko": "umuntu", "birakenewe": ukuri},
})
shyira result = validator.kugenzura("user", data)

# Rate limiting
shyira limiter = UrubugaRateLimit.nshya(100, 60)  # 100 requests per 60 seconds
```

### Real-time Platform (`urubuga/realtime.i`)

```i
shyiramo "urubuga/realtime"

# WebSocket
shyira ws = UrubugaWebSocket.nshya("0.0.0.0", 8080)

ws.on("message", lambda conn_id, data: ws.broadcast("message", data))
ws.on("join_room", lambda conn_id, data: ws.join_room(conn_id, data["room"]))

# Server-Sent Events
shyira sse = UrubugaSSE.nshya()
sse.broadcast("update", {"status": "new"})

# Presence
shyira presence = UrubugaPresence.nshya()
presence.presence("user123", {"name": "Jean"})
```

### Template Engine (`urubuga/inyandikorumurongo.i`)

```i
shyiramo "urubuga/inyandikorumurongo"

# Register templates
shyira tmpl = UrubugaInyandikorumurongoAdvanced.nshya()
tmpl.shakisha("index", "<h1>{{ umutwe }}</h1><p>{{ inkuru }}</p>")

# Render
shyira html = tmpl.dorera("index", {"umutwe": "Muraho", "inkuru": "Ibi ni urubuga"})

# Built-in components
andika umugerereka({"umutwe": "Welcome", "inkuru": "Hello world"})
andika ibiciro({"umutwe": "Card", "inkuru": "Content"})
andika ibiciro_byinama({"ibiciro": [{"izina": "Home", "inzira": "/"}]})
andika impera({"copyright": "© 2024 Urubuga"})
```

### GraphQL (`urubuga/graphql.i`)

```i
shyiramo "urubuga/graphql"

shyira schema = UrubugaGraphQLSchema.nshya()

schema.query("hello", "String", lambda vars: "Muraho!")
schema.query("users", "[User]", lambda vars: get_users())
schema.mutation("createUser", "User", lambda vars: create_user(vars))

app.POST("/graphql", lambda req: schema.execute(req.json_data["query"]))
app.GET("/graphql", lambda req: app.html_(graphql_playground()))
```

### AI Integration (`urubuga/ai.i`)

```i
shyiramo "urubuga/ai"

shyira ai = UrubugaAI.nshya()

# Chat endpoint
app.POST("/api/chat", lambda req: ai.chat(req))

# Embeddings
app.POST("/api/embeddings", lambda req: ai.embeddings(req))

# Semantic search
app.POST("/api/search", lambda req: ai.search(req))

# Prompt pipeline
ai.shakisha_prompt("greeting", "Muraho {{izina}}!")
shyira prompt = ai.gukora_prompt("greeting", {"izina": "Jean"})
```

### Server-Side Rendering (`urubuga/ssr.i`)

```i
shyiramo "urubuga/ssr"

shyira ssr = UrubugaSSR.nshya()
ssr.shakisha_template("index", "ibubuyemo/index.html")

# Register components
ssr.shakisha_component("Header", lambda props: "<header>...</header>")

# Render
shyira html = ssr.render("index", {"izina": "My App"})

# Static Site Generation
shyira ssg = UrubugaSSG.nshya(ssr, "ubwoko/")
ssg.generate_page("/about", "about.html", {"title": "About"})
```

---

## Database Layer

### ORM (`urubuga/ubatse.i` — UrubugaUbubiko)

```i
# Configure database
app.shakisha_ububiko("urubuga.db")

# Create tables
app.gukora_icyumba("users", {
    "izina": {"ubwoko": "TEXT", "birakenewe": ukuri},
    "email": {"ubwoko": "TEXT", "birakenewe": ukuri},
    "password": {"ubwoko": "TEXT", "birakenewe": ukuri},
})

# CRUD operations
app.ububiko.injiza("users", {"izina": "Jean", "email": "jean@example.com"})
app.ububiko.shakisha("users", {"email": "jean@example.com"})
app.ububiko.shakisha_id("users", 1)
app.ububiko.hindura("users", {"izina": "Pierre"}, "id = ?", [1])
app.ububiko.siba("users", "id = ?", [1])

# Raw queries
shyira results = app.ububiko.guharura("SELECT * FROM users WHERE imyaka > ?", [18])
```

### Migrations

```i
# Migration support
app.gukora_icyumba("users", {
    "izina": {"ubwoko": "TEXT", "birakenewe": ukuri},
    "created_at": {"ubwoko": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
})
```

---

## Authentication

### JWT Authentication

```i
# Configure JWT
app.shakisha_jwt("my-secret-key", 3600)

# Login
shyira result = app.kwinjira("username", "password")
# Returns: {"token": "...", "username": "..."}

# Validate token
shyira user = app.guhita(token)
# Returns: {"username": "...", "authenticated_at": 1234567890}
```

### API Key Authentication

```i
shyira api_keys = UrubugaAPIKeyManager.nshya()
shyira key = api_keys.create_key("user123", "My API Key")
shyira valid = api_keys.validate_key(key)
```

### Password Hashing

```i
shyira hashed = app.uburinzi_.hash_password("mypassword")
shyira valid = app.uburinzi_.check_password("mypassword", hashed)
```

---

## Security

```i
# CSRF Protection
app.shakisha_porogaramu(app.uburinzi_.kingira(handler))

# Password hashing
shyira hash = app.uburinzi_.hash_password(password)
shyira valid = app.uburinzi_.check_password(password, hash)

# Token generation
shyira token = app.uburinzi_.generate_token()

# Encryption
shyira encrypted = app.uburinzi_.encrypt(data, key)
shyira decrypted = app.uburinzi_.decrypt(encrypted, key)
```

---

## CLI Commands

```bash
# Create new project
isoko urubuga new my-project website
isoko urubuga new my-api rest-api
isoko urubuga new my-app fullstack

# Development server
isoko urubuga dev --port 3000

# Build for production
isoko urubuga build

# Run in production
isoko urubuga serve --port 8080

# Database migrations
isoko urubuga migrate

# Health check
isoko urubuga doctor

# Analyze project
isoko urubuga analyze

# List templates
isoko urubuga templates
```

---

## Project Templates

| Template | Description |
|----------|-------------|
| `website` | Basic website with pages |
| `rest-api` | REST API with CRUD |
| `fullstack` | Full-stack with SSR, API, GraphQL |
| `graphql` | GraphQL server |
| `microservice` | Lightweight microservice |
| `blog` | Blog platform |
| `e-commerce` | E-commerce platform |
| `school` | School management system |

---

## Performance

- **Fast startup** — Minimal overhead
- **Low memory** — Efficient resource usage
- **High throughput** — Optimized request handling
- **Scalable** — Threaded server support
- **Cached** — Built-in cache system

---

## Deployment

Urubuga supports deployment to:
- Linux servers
- Windows servers
- Docker containers
- Kubernetes
- Cloud providers (AWS, GCP, Azure)
- Edge platforms
- Serverless platforms

---

## I Language Syntax Reference

All framework code uses valid I language constructs:

```i
# Variables
shyira name = "value"
shyira_ko NAME = "constant"

# Functions
umurimo my_func(param1, param2)
    subira param1 + param2
iherezo

# Classes
urwego MyClass kora
    umurimo __init__(self, value)
        self.value = value
    iherezo

    umurimo get_value(self)
        subira self.value
    iherezo
iherezo

# Control flow
niba condition kora
    # do something
cyangwa
    # do something else
iherezo

# Loops
buri item muri items kora
    andika(item)
iherezo

# Type conversions
shobora_int("123")
shobora_float("3.14")
shobora_umuntu(123)

# String concatenation (no f-strings)
"Hello " + name + "!"
```

---

## License

MIT License — Part of the I Programming Language ecosystem.
