# Frameworks Architecture

This document specifies the complete architecture of all official I Programming Language frameworks.

## Table of Contents

- [Overview](#overview)
- [urubuga — Web Framework](#urubuga--web-framework)
- [ibiro — Desktop Framework](#ibiro--desktop-framework)
- [mobile — Mobile Framework](#mobile--mobile-framework)
- [ubwenge — AI Framework](#ubwenge--ai-framework)
- [imikino — Game Engine](#imikino--game-engine)
- [sisitemu — Systems Framework](#sisitemu--systems-framework)
- [igicu — Cloud Framework](#igicu--cloud-framework)
- [Cross-Framework Patterns](#cross-framework-patterns)

## Overview

The I ecosystem includes seven official frameworks, each designed as an independent project with its own architecture, release cycle, and team. All frameworks share common patterns:

1. **Consistent API style**: Kinyarwanda naming, builder pattern, error handling
2. **Composable**: Frameworks work together (e.g., urubuga + igicu)
3. **Async-first**: All I/O-bound operations support async/await
4. **Testable**: Built-in testing support in every framework
5. **Documented**: Auto-generated documentation from source

---

## urubuga — Web Framework

### Purpose

Modern web framework for building SSR, SPA, static sites, REST APIs, GraphQL APIs, and WebSockets.

### Architecture

```
urubuga/
├── core/           # Core framework
│   ├── app.i       # Application
│   ├── route.i     # Router
│   ├── request.i   # Request handling
│   ├── response.i  # Response building
│   └── context.i   # Request context
├── mvc/            # MVC pattern
│   ├── model.i     # Model layer
│   ├── view.i      # View engine
│   └── controller.i # Controller base
├── auth/           # Authentication
│   ├── session.i   # Session management
│   ├── jwt.i       # JWT tokens
│   ├── oauth.i     # OAuth 2.0
│   ├── password.i  # Password hashing
│   └── rbac.i      # Role-based access
├── orm/            # Object-relational mapping
│   ├── model.i     # Model definition
│   ├── query.i     # Query builder
│   ├── migration.i # Schema migration
│   └── relation.i  # Relationships
├── template/       # Templating engine
│   ├── engine.i    # Template engine
│   ├── html.i      # HTML helpers
│   └── component.i # Component system
├── middleware/      # Middleware
│   ├── cors.i      # CORS
│   ├── csrf.i      # CSRF protection
│   ├── rate.i      # Rate limiting
│   ├── compress.i  # Compression
│   └── static.i    # Static file serving
├── websocket/      # WebSocket support
│   ├── server.i    # WebSocket server
│   ├── channel.i   # Pub/sub channels
│   └── event.i     # Event handling
├── graphql/        # GraphQL support
│   ├── schema.i    # Schema definition
│   ├── resolver.i  # Resolver base
│   └── scalar.i    # Custom scalars
├── scheduler/      # Task scheduling
│   ├── cron.i      # Cron jobs
│   └── queue.i     # Background tasks
└── cli/            # CLI tools
    ├── dev.i       # Development server
    ├── migrate.i   # Migration runner
    └── generate.i  # Code generation
```

### Core API

```
igiceri App
    __init__(name: string)
    
    # Routing
    get(self, path: string, handler: Handler) -> Self
    post(self, path: string, handler: Handler) -> Self
    put(self, path: string, handler: Handler) -> Self
    delete(self, path: string, handler: Handler) -> Self
    patch(self, path: string, handler: Handler) -> Self
    route(self, method: string, path: string, handler: Handler) -> Self
    
    # Groups
    group(self, prefix: string, middleware: List<Middleware> = []) -> RouteGroup
    
    # Middleware
    use(self, middleware: Middleware) -> Self
    
    # Static files
    static(self, path: string, directory: string) -> Self
    
    # Start server
    serve(self, host: string = "0.0.0.0", port: int = 8000) -> void
iherezo

# Handler type
type Handler = async (Context) -> Response

# Context
igiceri Context
    request: Request
    response: Response
    params: Map<string, string>
    query: Map<string, string>
    body: Any
    session: Session
    user: Any?
    
    # Response helpers
    json(self, data: Any, status: int = 200) -> Response
    html(self, content: string, status: int = 200) -> Response
    text(self, content: string, status: int = 200) -> Response
    redirect(self, url: string, status: int = 302) -> Response
    file(self, path: string) -> Response
    error(self, status: int, message: string) -> Response
iherezo
```

### Example Application

```
shyiramo urubuga

app = urubuga.App("my_api")

# Middleware
app.use(urubuga.middleware.cors())
app.use(urubuga.middleware.rate_limit(max_requests=100, per=60))

# Routes
app.get("/api/users", async (ctx) => {
    users = await db.query("SELECT * FROM users")
    ctx.json(users)
})

app.post("/api/users", async (ctx) => {
    user = await db.insert("users", ctx.body)
    ctx.json(user, status=201)
})

app.get("/api/users/:id", async (ctx) => {
    user = await db.find("users", ctx.params["id"])
    niba user == null:
        ctx.error(404, "User not found")
    ctx.json(user)
})

# Start server
app.serve(port=3000)
```

### Features Roadmap

| Version | Features |
|---------|----------|
| v0.1 | Core routing, middleware, request/response |
| v0.2 | Template engine, static files, sessions |
| v0.3 | ORM, migrations, authentication |
| v0.4 | WebSocket, GraphQL |
| v0.5 | Background tasks, scheduler |
| v1.0 | Production-ready, full documentation |

---

## ibiro — Desktop Framework

### Purpose

Native desktop application framework for Windows, Linux, and macOS.

### Architecture

```
ibiro/
├── core/           # Core framework
│   ├── app.i       # Application lifecycle
│   ├── window.i    # Window management
│   ├── event.i     # Event system
│   └── platform.i  # Platform abstraction
├── widgets/        # UI widgets
│   ├── button.i    # Button
│   ├── text.i      # Text input/display
│   ├── list.i      # List view
│   ├── tree.i      # Tree view
│   ├── table.i     # Table view
│   ├── image.i     # Image display
│   ├── menu.i      # Menu bar
│   ├── toolbar.i   # Toolbar
│   ├── statusbar.i # Status bar
│   ├── dialog.i    # Dialog boxes
│   ├── tab.i       # Tab view
│   ├── panel.i     # Panel/container
│   ├── scroll.i    # Scroll area
│   └── custom.i    # Custom widget base
├── layout/         # Layout managers
│   ├── box.i       # Box layout (horizontal/vertical)
│   ├── grid.i      # Grid layout
│   ├── stack.i     # Stack layout
│   └── anchor.i    # Anchor layout
├── drawing/        # Custom drawing
│   ├── canvas.i    # Canvas
│   ├── paint.i     # Paint operations
│   ├── path.i      # Path drawing
│   └── gradient.i  # Gradients
├── data/           # Data binding
│   ├── binding.i   # Property binding
│   ├── model.i     # Data models
│   └── viewmodel.i # View models
├── navigation/     # Navigation
│   ├── router.i    # View router
│   └── transition.i # Animations
├── storage/        # Local storage
│   ├── settings.i  # App settings
│   ├── database.i  # Local database
│   └── cache.i     # Local cache
├── system/         # System integration
│   ├── tray.i      # System tray
│   ├── notify.i    # Notifications
│   ├── clipboard.i # Clipboard
│   ├── file.i      # File dialogs
│   ├── print.i     # Printing
│   └── update.i    # Auto-update
└── accessibility/  # Accessibility
    ├── screen_reader.i
    └── keyboard.i
```

### Core API

```
igiceri App
    __init__(title: string, width: int = 800, height: int = 600)
    
    # Window
    set_title(self, title: string) -> void
    set_size(self, width: int, height: int) -> void
    set_position(self, x: int, y: int) -> void
    center(self) -> void
    maximize(self) -> void
    minimize(self) -> void
    fullscreen(self) -> void
    
    # Content
    set_content(self, widget: Widget) -> void
    
    # Menu
    set_menu(self, menu: Menu) -> void
    
    # Events
    on_close(self, handler: () -> bool) -> void
    on_resize(self, handler: (int, int) -> void) -> void
    
    # Run
    run(self) -> void
    
    # Quit
    guhagarika(self) -> void
iherezo

# Widget base
igiceri Widget
    visible: bool
    enabled: bool
    
    show(self) -> void
    hide(self) -> void
    enable(self) -> void
    disable(self) -> void
    update(self) -> void
iherezo

# Button
igiceri Button(Widget)
    __init__(label: string, on_click: () -> void = null)
    
    set_label(self, label: string) -> void
    set_icon(self, icon: string) -> void
iherezo

# Text input
igiceri TextInput(Widget)
    __init__(value: string = "", placeholder: string = "")
    
    get_value(self) -> string
    set_value(self, value: string) -> void
    on_change(self, handler: (string) -> void) -> void
iherezo
```

### Example Application

```
shyiramo ibiro

app = ibiro.App("My App", width=1024, height=768)

# Create layout
layout = ibiro.layout.Box(direction=ibiro.Vertical)

# Add text input
input = ibiro.TextInput(placeholder="Enter your name")
layout.add(input)

# Add button
button = ibiro.Button("Greeting", on_click=() => {
    name = input.get_value()
    ibiro.dialog.message("Muraho, " + name + "!")
})
layout.add(button)

# Set content and run
app.set_content(layout)
app.run()
```

---

## mobile — Mobile Framework

### Purpose

Cross-platform mobile application framework for Android and iOS.

### Architecture

```
mobile/
├── core/           # Core framework
│   ├── app.i       # Application lifecycle
│   ├── screen.i    # Screen management
│   ├── navigation.i # Navigation
│   └── platform.i  # Platform detection
├── widgets/        # UI widgets
│   ├── button.i    # Button
│   ├── text.i      # Text
│   ├── input.i     # Text input
│   ├── image.i     # Image
│   ├── list.i      # List view
│   ├── scroll.i    # Scroll view
│   ├── switch.i    # Switch toggle
│   ├── slider.i    # Slider
│   ├── picker.i    # Picker
│   ├── tab.i       # Tab bar
│   ├── nav.i       # Navigation bar
│   └── modal.i     # Modal
├── layout/         # Layout
│   ├── flex.i      # Flexbox
│   ├── grid.i      # Grid
│   └── stack.i     # Stack
├── style/          # Styling
│   ├── theme.i     # Theme system
│   ├── colors.i    # Color palette
│   ├── typography.i # Fonts
│   └── spacing.i   # Spacing
├── navigation/     # Navigation
│   ├── stack.i     # Stack navigator
│   ├── tab.i       # Tab navigator
│   ├── drawer.i    # Drawer navigator
│   └── modal.i     # Modal presentation
├── storage/        # Storage
│   ├── async.i     # Async storage
│   ├── database.i  # SQLite
│   ├── file.i      # File system
│   └── secure.i    # Secure storage
├── services/       # Device services
│   ├── camera.i    # Camera
│   ├── location.i  # GPS
│   ├── sensors.i   # Accelerometer, gyroscope
│   ├── permissions.i # Permissions
│   ├── notifications.i # Push notifications
│   ├── haptics.i   # Haptic feedback
│   └── biometric.i # Fingerprint/face
├── network/        # Networking
│   ├── http.i      # HTTP client
│   ├── websocket.i # WebSocket
│   └── offline.i   # Offline support
├── animation/      # Animations
│   ├── spring.i    # Spring physics
│   ├── timing.i    # Timing curves
│   └── layout.i    # Layout animations
└── build/          # Build system
    ├── android.i   # Android build
    ├── ios.i       # iOS build
    └── deploy.i    # Deployment
```

### Core API

```
igiceri App
    __init__(name: string)
    
    # Navigation
    navigate(self, screen: string, params: Map<string, Any> = {}) -> void
    go_back(self) -> void
    replace(self, screen: string) -> void
    
    # Theme
    set_theme(self, theme: Theme) -> void
    
    # Run
    run(self) -> void
iherezo

# Screen
igiceri Screen
    title: string
    
    build(self) -> Widget
    on_mount(self) -> void
    on_unmount(self) -> void
    on_resume(self) -> void
    on_pause(self) -> void
iherezo

# State management
igiceri State<T>
    __init__(initial: T)
    
    get(self) -> T
    set(self, value: T) -> void
    update(self, f: (T) -> T) -> void
iherezo
```

---

## ubwenge — AI Framework

### Purpose

Machine learning, deep learning, LLM integration, and AI application development.

### Architecture

```
ubwenge/
├── core/           # Core types
│   ├── tensor.i    # Tensor operations
│   ├── model.i     # Model base
│   └── device.i    # CPU/GPU device
├── ml/             # Classical ML
│   ├── linear.i    # Linear regression
│   ├── logistic.i  # Logistic regression
│   ├── tree.i      # Decision trees
│   ├── forest.i    # Random forests
│   ├── svm.i       # Support vector machines
│   ├── cluster.i   # Clustering
│   └── reduce.i    # Dimensionality reduction
├── nn/             # Neural networks
│   ├── layers.i    # Layer types
│   ├── activation.i # Activation functions
│   ├── loss.i      # Loss functions
│   ├── optim.i     # Optimizers
│   ├── init.i      # Weight initialization
│   └── regular.i   # Regularization
├── llm/            # Large Language Models
│   ├── model.i     # LLM model loading
│   ├── prompt.i    # Prompt engineering
│   ├── chain.i     # Chain of thought
│   ├── agent.i     # AI agents
│   ├── embed.i     # Embeddings
│   ├── vector.i    # Vector database
│   └── rag.i       # Retrieval augmented generation
├── vision/         # Computer vision
│   ├── image.i     # Image processing
│   ├── detect.i    # Object detection
│   ├── segment.i   # Image segmentation
│   ├── recognize.i # Image recognition
│   └── ocr.i       # Optical character recognition
├── speech/         # Speech processing
│   ├── recognize.i # Speech recognition
│   ├── synthesize.i # Text-to-speech
│   ├── diarize.i   # Speaker diarization
│   └── translate.i # Speech translation
├── nlp/            # Natural language processing
│   ├── tokenize.i  # Tokenization
│   ├── parse.i     # Parsing
│   ├── sentiment.i # Sentiment analysis
│   ├── classify.i  # Text classification
│   └── generate.i  # Text generation
├── data/           # Data processing
│   ├── dataset.i   # Dataset loading
│   ├── transform.i # Data transforms
│   ├── augment.i   # Data augmentation
│   └── pipeline.i  # Data pipelines
├── train/          # Training
│   ├── loop.i      # Training loop
│   ├── callback.i  # Callbacks
│   ├── checkpoint.i # Checkpointing
│   ├── metric.i    # Metrics
│   └── schedule.i  # Learning rate schedules
├── serve/          # Model serving
│   ├── server.i    # Model server
│   ├── batch.i     # Batch inference
│   ├── cache.i     # Result caching
│   └── monitor.i   # Monitoring
└── gpu/            # GPU support
    ├── cuda.i      # CUDA operations
    ├── metal.i     # Metal (macOS)
    └── vulkan.i    # Vulkan
```

### Core API

```
# Tensor
igiceri Tensor
    @staticmethod
    data(data: List<List<float>>, device: Device = CPU) -> Tensor
    
    @staticmethod
    zeros(shape: List<int>, device: Device = CPU) -> Tensor
    
    @staticmethod
    ones(shape: List<int>, device: Device = CPU) -> Tensor
    
    @staticmethod
    random(shape: List<int>, device: Device = CPU) -> Tensor
    
    # Operations
    add(self, other: Tensor) -> Tensor
    sub(self, other: Tensor) -> Tensor
    mul(self, other: Tensor) -> Tensor
    div(self, other: Tensor) -> Tensor
    matmul(self, other: Tensor) -> Tensor
    sum(self, axis: int? = null) -> Tensor
    mean(self, axis: int? = null) -> Tensor
    reshape(self, shape: List<int>) -> Tensor
    
    # Properties
    shape(self) -> List<int>
    device(self) -> Device
    to(self, device: Device) -> Tensor
iherezo

# Neural network layer
igiceri Layer
    forward(self, input: Tensor) -> Tensor
    backward(self, gradient: Tensor) -> Tensor
    parameters(self) -> List<Tensor>
    train(self) -> void
    eval(self) -> void
iherezo

# Sequential model
igiceri Sequential
    __init__(layers: List<Layer>)
    
    forward(self, input: Tensor) -> Tensor
    train(self) -> void
    eval(self) -> void
iherezo

# LLM
igiceri LLM
    @staticmethod
    from_pretrained(model_name: string, device: Device = CPU) -> LLM
    
    generate(self, prompt: string, max_tokens: int = 100, temperature: float = 0.7) -> string
    
    embed(self, text: string) -> Tensor
    
    chat(self, messages: List<Message>) -> string
iherezo
```

---

## imikino — Game Engine

### Purpose

2D/3D game engine with physics, audio, networking, and editor.

### Architecture

```
imikino/
├── core/           # Core engine
│   ├── engine.i    # Game engine
│   ├── scene.i     # Scene graph
│   ├── entity.i    # Entity system (ECS)
│   ├── component.i # Components
│   ├── system.i    # Systems
│   └── event.i     # Event bus
├── graphics/       # Rendering
│   ├── renderer.i  # Renderer
│   ├── camera.i    # Camera
│   ├── light.i     # Lighting
│   ├── material.i  # Materials
│   ├── mesh.i      # Meshes
│   ├── sprite.i    # 2D sprites
│   ├── tilemap.i   # Tile maps
│   ├── animation.i # Sprite animation
│   ├── particle.i  # Particle system
│   ├── post.i      # Post-processing
│   └── shader.i    # Shader system
├── physics/        # Physics
│   ├── world.i     # Physics world
│   ├── body.i      # Rigid bodies
│   ├── collider.i  # Colliders
│   ├── joint.i     # Joints
│   ├── raycast.i   # Raycasting
│   └── vehicle.i   # Vehicle physics
├── audio/          # Audio
│   ├── listener.i  # Audio listener
│   ├── source.i    # Audio source
│   ├── clip.i      # Audio clips
│   ├── mixer.i     # Audio mixer
│   ├── spatial.i   # 3D audio
│   └── music.i     # Music playback
├── input/          # Input
│   ├── keyboard.i  # Keyboard
│   ├── mouse.i     # Mouse
│   ├── gamepad.i   # Gamepad
│   ├── touch.i     # Touch
│   └── action.i    # Input actions
├── ui/             # Game UI
│   ├── canvas.i    # UI canvas
│   ├── text.i      # Text rendering
│   ├── button.i    # UI buttons
│   └── layout.i    # UI layout
├── networking/     # Multiplayer
│   ├── server.i    # Game server
│   ├── client.i    # Game client
│   ├── sync.i      # State synchronization
│   └── lobby.i     # Lobby system
├── assets/         # Asset management
│   ├── loader.i    # Asset loading
│   ├── cache.i     # Asset caching
│   ├── import.i    # Asset import
│   └── bundle.i    # Asset bundling
├── editor/         # Game editor
│   ├── window.i    # Editor window
│   ├── inspector.i # Property inspector
│   ├── hierarchy.i # Scene hierarchy
│   ├── viewport.i  # Scene viewport
│   └── console.i   # Console
└── build/          # Build & export
    ├── desktop.i   # Desktop build
    ├── web.i       # Web build
    └── mobile.i    # Mobile build
```

### Core API

```
igiceri Engine
    __init__(config: EngineConfig)
    
    # Scene management
    load_scene(self, path: string) -> void
    create_scene(self) -> Scene
    
    # Run
    run(self) -> void
    stop(self) -> void
iherezo

igiceri Scene
    # Entity management
    create_entity(self, name: string) -> Entity
    destroy_entity(self, entity: Entity) -> void
    find_entity(self, name: string) -> Entity?
    
    # Query
    query(self, components: List<Type>) -> List<Entity>
iherezo

igiceri Entity
    name: string
    
    add_component(self, component: Component) -> void
    get_component(self, type: Type) -> Component?
    remove_component(self, type: Type) -> void
    
    destroy(self) -> void
iherezo

# Components
igiceri Transform
    position: Vec3
    rotation: Quat
    scale: Vec3
iherezo

igiceri SpriteRenderer
    sprite: Sprite
    color: Color
    layer: int
iherezo

igiceri Rigidbody
    mass: float
    velocity: Vec3
    is_kinematic: bool
iherezo

igiceri BoxCollider
    size: Vec3
    offset: Vec3
iherezo
```

---

## sisitemu — Systems Programming Framework

### Purpose

Low-level systems programming: drivers, kernel modules, OS components.

### Architecture

```
sisitemu/
├── core/           # Core types
│   ├── ptr.i       # Raw pointers
│   ├── alloc.i     # Allocators
│   ├── volatile.i  # Volatile operations
│   └── atomic.i    # Atomic operations
├── memory/         # Memory management
│   ├── page.i      # Page tables
│   ├── heap.i      # Heap allocator
│   ├── pool.i      # Pool allocator
│   └── arena.i     # Arena allocator
├── process/        # Process management
│   ├── process.i   # Process control
│   ├── thread.i    # Thread management
│   ├── scheduler.i # Scheduler
│   └── ipc.i       # Inter-process communication
├── filesystem/     # Filesystem
│   ├── vfs.i       # Virtual filesystem
│   ├── inode.i     # Inode management
│   ├── buffer.i    # Buffer cache
│   └── ext2.i      # ext2 driver
├── network/        # Networking
│   ├── socket.i    # Socket layer
│   ├── tcp.i       # TCP stack
│   ├── udp.i       # UDP stack
│   ├── ip.i        # IP layer
│   └── ethernet.i  # Ethernet driver
├── drivers/        # Device drivers
│   ├── pci.i       # PCI bus
│   ├── usb.i       # USB
│   ├── disk.i      # Block devices
│   ├── serial.i    # Serial ports
│   ├── vga.i       # VGA/display
│   └── input.i     # Input devices
├── interrupt/      # Interrupt handling
│   ├── idt.i       # Interrupt descriptor table
│   ├── irq.i       # IRQ handling
│   └── timer.i     # Timer
└── boot/           # Boot
    ├── multiboot.i # Multiboot
    ├── elf.i       # ELF loading
    └── init.i      # Init process
```

### Core API

```
# Raw pointer operations
igiceri Ptr<T>
    offset(self, count: int) -> Ptr<T>
    read(self) -> T
    write(self, value: T) -> void
    is_null(self) -> bool
iherezo

# Allocators
igiceri Allocator
    allocate(self, size: int, alignment: int = 8) -> *u8
    deallocate(self, ptr: *u8, size: int) -> void
    reallocate(self, ptr: *u8, old_size: int, new_size: int) -> *u8
iherezo

# Page table
igiceri PageTable
    map(self, virtual: u64, physical: u64, flags: PageFlags) -> void
    unmap(self, virtual: u64) -> void
    translate(self, virtual: u64) -> u64?
iherezo
```

---

## igicu — Cloud Framework

### Purpose

Cloud-native application development: microservices, containers, serverless.

### Architecture

```
igicu/
├── core/           # Core framework
│   ├── service.i   # Service base
│   ├── config.i    # Configuration
│   ├── health.i    # Health checks
│   └── metric.i    # Metrics
├── micro/          # Microservices
│   ├── grpc.i      # gRPC support
│   ├── rest.i      # REST support
│   ├── event.i     # Event-driven
│   ├── saga.i      # Saga pattern
│   └── circuit.i   # Circuit breaker
├── container/      # Container support
│   ├── docker.i    # Docker integration
│   ├── kube.i      # Kubernetes
│   └── compose.i   # Docker Compose
├── serverless/     # Serverless
│   ├── function.i  # Function runtime
│   ├── trigger.i   # Triggers
│   └── gateway.i   # API gateway
├── queue/          # Message queues
│   ├── producer.i  # Message producer
│   ├── consumer.i  # Message consumer
│   ├── topic.i     # Topics
│   └── stream.i    # Streams
├── cache/          # Caching
│   ├── redis.i     # Redis client
│   ├── memory.i    # In-memory cache
│   └── distributed.i # Distributed cache
├── secret/         # Secrets management
│   ├── vault.i     # Vault integration
│   ├── env.i       # Environment variables
│   └── encrypt.i   # Encryption at rest
├── observe/        # Observability
│   ├── trace.i     # Distributed tracing
│   ├── log.i       # Structured logging
│   ├── metric.i    # Metrics collection
│   └── alert.i     # Alerting
└── deploy/         # Deployment
    ├── kubernetes.i # K8s deployment
    ├── docker.i    # Docker deployment
    └── serverless.i # Serverless deployment
```

### Core API

```
igiceri Service
    __init__(name: string)
    
    # Lifecycle
    on_start(self, handler: () -> void) -> void
    on_stop(self, handler: () -> void) -> void
    on_health(self, handler: () -> HealthStatus) -> void
    
    # Configuration
    config(self, key: string, default: Any = null) -> Any
    
    # Run
    run(self) -> void
iherezo

# Health check
igiceri HealthStatus
    healthy: bool
    message: string
    details: Map<string, Any>
iherezo

# Circuit breaker
igiceri CircuitBreaker
    __init__(failure_threshold: int = 5, recovery_timeout: int = 30)
    
    call(self, fn: () -> T) -> T
iherezo
```

---

## Cross-Framework Patterns

### Shared Conventions

1. **Builder Pattern**: All configuration uses builder pattern
2. **Error Handling**: All frameworks use `Result<T, E>` for fallible operations
3. **Async-First**: All I/O operations are async by default
4. **Event-Driven**: All frameworks use event-driven architecture
5. **Plugin System**: All frameworks support plugins/extensions
6. **Testing**: All frameworks include built-in testing utilities
7. **Documentation**: All frameworks generate docs from source

### Dependency Graph

```
imikino (Game Engine)
    └── depends on: core, graphics, physics, audio

urubuga (Web Framework)
    └── depends on: http, database, json, crypto

ibiro (Desktop Framework)
    └── depends on: window, ui, graphics

mobile (Mobile Framework)
    └── depends on: ui, storage, services, network

ubwenge (AI Framework)
    └── depends on: math, tensor, gpu

sisitemu (Systems Framework)
    └── depends on: memory, process, filesystem

igicu (Cloud Framework)
    └── depends on: network, queue, cache, secret
```

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
