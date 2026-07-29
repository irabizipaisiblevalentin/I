# Unified Application Model (UAM) — Cross-Platform Architecture

Version: 0.1.0
Status: DRAFT

## Vision

The Unified Application Model (UAM) is the defining architectural innovation of the I Programming Language ecosystem. It enables developers to write **a single application codebase** that deploys to web, desktop, and mobile platforms without modification, while still allowing platform-specific adaptations where needed.

## Architecture Principle

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Application                        │
├────────────┬────────────┬────────────┬──────────────────────┤
│  shared/   │    ui/     │   web/     │   desktop/  mobile/  │
│  (logic)   │  (ui def)  │  (adapt)   │   (adapt)   (adapt)  │
├────────────┴────────────┴────────────┴──────────────────────┤
│                    UAM Abstraction Layer                      │
├────────────┬────────────┬────────────────────────────────────┤
│  urubuga   │   ibiro    │              mobile                │
│   (web)    │  (desktop) │             (mobile)               │
├────────────┴────────────┴────────────────────────────────────┤
│                   UFA (Unified Framework Architecture)        │
├─────────────────────────────────────────────────────────────┤
│                    I Language VM / Native Runtimes            │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
my-app/
├── shared/                        # Platform-independent business logic
│   ├── logic/                     # Business logic, use cases
│   │   └── counter.i              # Example: counter logic
│   ├── models/                    # Data models and types
│   │   └── user.i                 # Example: user model
│   ├── validation/                # Validation rules
│   │   └── forms.i                # Form validation
│   ├── services/                  # Application services
│   │   ├── auth.i                 # Authentication service
│   │   └── api.i                  # API client service
│   ├── networking/                # HTTP, WebSocket clients
│   │   └── http.i                 # HTTP client abstraction
│   ├── database/                  # Data access layer
│   │   └── repository.i           # Repository pattern
│   └── state/                     # State management
│       └── app_state.i            # Application state
├── ui/                            # Platform-independent UI definitions
│   ├── components/                # Reusable UI components
│   │   ├── button.i               # Generic button
│   │   ├── card.i                 # Generic card
│   │   └── header.i               # Generic header
│   ├── screens/                   # Screen/page definitions
│   │   ├── home.i                 # Home screen
│   │   └── settings.i             # Settings screen
│   ├── layouts/                   # Layout templates
│   │   └── main_layout.i          # Main layout
│   ├── navigation/                # Navigation structure
│   │   └── routes.i               # Route definitions
│   └── theme/                     # Theming/styling
│       ├── colors.i               # Color palette
│       └── typography.i           # Typography
├── web/                           # Web-specific adaptations
│   ├── components/                # Web component overrides
│   ├── layouts/                   # Web-specific layouts
│   ├── public/                    # Static assets
│   └── main.i                     # Web entry point
├── desktop/                       # Desktop-specific adaptations
│   ├── components/                # Desktop component overrides
│   ├── menus/                     # Desktop menus
│   ├── windows/                   # Window configuration
│   └── main.i                     # Desktop entry point
├── mobile/                        # Mobile-specific adaptations
│   ├── components/                # Mobile component overrides
│   ├── screens/                   # Mobile-specific screens
│   └── main.i                     # Mobile entry point
├── uam.yaml                       # UAM project configuration
└── ilang.toml                     # I Language project config
```

## Key Concepts

### 1. Platform Abstraction Layer (PAL)

Every framework (urubuga, ibiro, mobile) implements the same PAL interface:

```i
# Platform service that all targets provide
urwego PlatformService:
    # Filesystem
    umurimo soma_dosiye(inzira: Ikurugamba) -> Ikurugamba
    umurimo andika_dosiye(inzira: Ikurugamba, ibirimo: Ikurugamba) -> Inyokwera
    
    # Clipboard
    umurimo kopisha(indangamuntu: Ikurugamba) -> Inyokwera
    
    # Window/Screen info
    umurimo ubugari_bw'igikoranabugari -> Inyobora
    umurimo uburebure_bw'igikoranabugari -> Inyobora
    
    # Storage
    umurimo kubika(urufunguzo: Ikurugamba, agaciro: Ikintu) -> Inyokwera
    umurimo gupakura(urufunguzo: Ikurugamba) -> Ikintu
    
    # Notifications
    umurimo menyesha(umutwe: Ikurugamba, ubutumwa: Ikurugamba) -> Inyokwera
```

### 2. Component Registry

Components are defined in `ui/` and can be overridden per platform:

```
ui/components/button.i     → Default implementation
web/components/button.i    → Web override (optional)
desktop/components/button.i → Desktop override (optional)
mobile/components/button.i  → Mobile override (optional)
```

The UAM build system resolves the correct implementation based on target platform.

### 3. Dependency Injection

Platform services are injected via the UFA container:

```i
# In shared/logic/auth.i
shyira service = uam.shaka_platform_service("http")
# Returns: urubuga HTTP client on web, ibiro on desktop, mobile on mobile
```

### 4. Build Targets

```bash
isoko uam build --target web        # Build for web (urubuga)
isoko uam build --target desktop    # Build for desktop (ibiro)
isoko uam build --target mobile     # Build for mobile (MOBILE)
isoko uam build --target all        # Build for all platforms
```

### 5. Conditional Code

Use platform detection for conditional logic:

```i
# Platform-specific customization
niba uam.ikoranabugari == uam.URUBUGA:
    # Web-specific code
cyangwa uam.ikoranabugari == uam.IBIRO:
    # Desktop-specific code
cyangwa uam.ikoranabugari == uam.MOBILE:
    # Mobile-specific code
```

## File-by-File Resolution Order

When a component is imported, UAM resolves in this order:

1. Platform-specific override: `web/components/button.i` (if exists)
2. Shared UI: `ui/components/button.i` (fallback)
3. Framework default: urubuga/ibiro/mobile built-in

## Services Layer

The `shared/services/` directory uses a provider pattern:

```i
urwego ServiceProvider:
    umurimo http -> HTTPService
    umurimo database -> DatabaseService
    umurimo auth -> AuthService
    umurimo storage -> StorageService
    umurimo notifications -> NotificationService
    umurimo platform -> PlatformService
```

Each framework registers its own implementation of these services.

## Benefits

- **Write once, deploy everywhere** — 80%+ code shared across platforms
- **Native performance** — Each platform compiles to its native runtime
- **Platform excellence** — Full access to platform-specific features
- **Gradual adaptation** — Start with shared code, add platform tweaks as needed
- **Consistent architecture** — Same patterns across all platforms
- **Reduced maintenance** — Fix bugs once, fix everywhere

## CLI Commands

```bash
isoko uam new <name>                  # Create new UAM project
isoko uam build --target <platform>   # Build for specific platform
isoko uam run --target <platform>     # Run on specific platform
isoko uam add <component>             # Add component to ui/
isoko uam override <component>        # Create platform override
isoko uam doctor                      # Diagnose project structure
isoko uam analyze                     # Analyze cross-platform coverage
```

## Comparison with Other Approaches

| Feature | UAM | Flutter | React Native | .NET MAUI |
|---------|-----|---------|--------------|-----------|
| Single codebase | ✓ | ✓ | ✓ | ✓ |
| Multi-target project | ✓ | ✗ | ✗ | ✓ |
| Platform-specific overrides | ✓ | Widgets | Native modules | Custom handlers |
| Native rendering | ✓ | Skia | Bridge | Native |
| Shared business logic | ✓ | Separate pkg | Separate pkg | Shared project |
| Component inheritance | ✓ | Composition | Composition | Composition |
| Build-time resolution | ✓ | Runtime | Runtime | Runtime |
| No lock-in | ✓ | ✗ | ✗ | ✗ |
