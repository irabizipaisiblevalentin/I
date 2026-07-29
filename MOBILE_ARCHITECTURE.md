# MOBILE — The Official Mobile Application Platform of the I Programming Language

Version: 0.1.0
Status: DRAFT
Last Updated: 2026-07-29

## Overview

MOBILE is a complete mobile application platform for building native-quality Android and iOS applications from a single codebase written in the I Programming Language. It is **not** a wrapper around existing frameworks — it is a comprehensive mobile platform with its own runtime, UI engine, layout system, state management, navigation, device APIs, and packaging system.

## Philosophy

- **Native Performance**: Compile to native Android (Kotlin/Java) and iOS (Swift/Objective-C) code.
- **Single Codebase**: Write once in I Language, deploy to both platforms.
- **Unified API**: Every UI component, layout, and API has the same interface across platforms.
- **Platform Excellence**: Leverage full platform capabilities — not a lowest-common-denominator approach.
- **Offline-First**: Built for the realities of mobile connectivity.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           User Application (.i files)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                         MOBILE Framework (.i files)                         │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┬───────────────┐  │
│  │   UI     │  Layout  │  Nav     │  State   │  Device  │   Media       │  │
│  │Components│  System  │  System  │  Mgmt    │   APIs   │               │  │
│  ├──────────┼──────────┼──────────┼──────────┼──────────┼───────────────┤  │
│  │ Security │ Database │ Network  │   AI     │  Perf    │   Package     │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┴───────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                     MOBILE Native Runtime (Python)                          │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┬───────────────┐  │
│  │ Android  │   iOS    │  Core    │  Code    │  Build   │  Test         │  │
│  │Runtime   │ Runtime  │  Engine  │  Gen     │  System  │  Runner       │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┴───────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                           I Language VM                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                    Android Runtime / iOS Runtime                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/mobile/                     # Python native runtime
├── __init__.py                 # Package metadata
├── porogaramu.py              # MobileApplication class
├── ikiganiro.py               # Screen/Activity management
├── ubugenzuzi.py              # Navigation system
├── ibikoresho/                # UI components
│   ├── __init__.py
│   ├── buto.py                # Button
│   ├── ikimenyetso.py         # Label/Text
│   ├── ishusho.py             # Image
│   ├── urutonde.py            # List
│   ├── ifishi.py              # Form
│   ├── ikarita.py             # Card
│   ├── ikadiri.py             # Dialog
│   ├── ikubaza.py             # Navigation bar
│   └── umubare.py             # Progress
├── imiterere/                 # Layout system
│   ├── __init__.py
│   ├── inkingi.py             # Column
│   ├── umurongo.py            # Row
│   ├── urusobete.py           # Grid
│   ├── itemba.py              # Stack
│   └── ikinyabiziga.py        # Flex
├── kamere/                    # State management
│   ├── __init__.py
│   ├── imiterere.py           # State
│   ├── ibonwa.py              # Observable
│   └── ubuzima.py             # Lifecycle
├── itumanaho/                 # Networking
│   ├── __init__.py
│   ├── http.py                # HTTP client
│   ├── webosiketi.py          # WebSocket
│   └── bluetooth.py           # Bluetooth
├── ibikoresho_bya_porogaramu/ # Device features
│   ├── __init__.py
│   ├── kamela.py              # Camera
│   ├── mikorofone.py          # Microphone
│   ├── gps.py                 # Location
│   ├── biometrike.py          # Biometrics
│   └── push.py                # Notifications
├── ububiko/                   # Database
│   ├── __init__.py
│   └── ububiko.py             # Database manager
├── ubwenge/                   # AI features
│   ├── __init__.py
│   └── ijwi.py                # Speech/Vision
├── umutekano/                 # Security
│   ├── __init__.py
│   └── umutekano.py           # Security manager
├── ipakira/                   # Packaging
│   ├── __init__.py
│   └── ipakira.py             # Build/packaging system
├── gukoresha/                 # Performance
│   ├── __init__.py
│   └── gukoresha.py           # Performance optimization
└── itegeko/                   # CLI commands
    ├── __init__.py
    └── amategeko.py           # CLI command definitions

mobile/                        # I Language framework files
├── ubatse.i                   # Core framework
├── navigation.i               # Navigation system
├── ui.i                       # UI components
├── layout.i                   # Layout system
├── media.i                    # Media support
├── network.i                  # Networking
├── device.i                   # Device features
├── ai.i                       # AI features
├── security.i                 # Security
└── urugero/                   # Example apps
    └── mobile-rwa.i           # Example app

docs/mobile/                   # Documentation
├── ANDROID_GUIDE.md
├── IOS_GUIDE.md
├── DEVICE_API_GUIDE.md
├── STATE_MANAGEMENT_GUIDE.md
├── NAVIGATION_GUIDE.md
├── PACKAGING_GUIDE.md
├── PERFORMANCE_GUIDE.md
├── SECURITY_GUIDE.md
└── ACCESSIBILITY_GUIDE.md

MOBILE_ARCHITECTURE.md         # This file
```

## Key Concepts

### Application Model
- **Single Activity**: Android single-activity architecture
- **Screen-based**: Each screen is a self-contained unit
- **Navigation Stack**: Push/pop navigation with deep linking
- **Lifecycle-aware**: Components respond to lifecycle events
- **State Restoration**: Automatic state preservation

### Unified UI Model
Every component follows the same pattern:
```
ikoresho = Buto(
    indangamuntu="unique_id",
    umwandiko="Press Me",
    ibara="#007AFF",
    rikora=lambda: print("pressed")
)
```

### Layout System
- **Inkingi (Column)**: Vertical arrangement
- **Umurongo (Row)**: Horizontal arrangement
- **Urusobete (Grid)**: Grid arrangement
- **Itemba (Stack)**: Overlapping/z-order
- **Ikinyabiziga (Flex)**: Flexbox-like layout
- **Responsive**: Adapt to screen size, orientation, safe areas

### State Management
- **Imiterere (State)**: Base state class
- **Ibonwa (Observable)**: Reactive state with listeners
- **Ubuzima (Lifecycle)**: Lifecycle-aware state management
- **Persistence**: Automatic save/restore

### Navigation
- **Ubugenzuzi (Navigator)**: Stack-based navigation
- **Amateka (History)**: Navigation history
- **Ihuza (Links)**: Deep linking
- **Imyanzuro (Routes)**: Named routes with parameters

### Device APIs
All device features are accessed through a consistent API:
```i
kamela = Kamela()
kamera.fungura()
ishusho = kamera.fata_ishusho()
```

### Security
- **Umutekano (Security Manager)**: Root/jailbreak detection, app integrity
- **Ibimenyetso (Certificates)**: Certificate pinning
- **Ubutabire (Encryption)**: Secure storage
- **Igenzura (Permissions)**: Runtime permission management

### Performance
- **GPU Acceleration**: Hardware-accelerated rendering
- **60-120 FPS**: Smooth animations
- **Cold Start**: < 2 seconds
- **Memory Optimization**: Minimal footprint
- **Battery Efficiency**: Minimal power consumption

## Platform Support

| Platform  | Support | Status |
|-----------|---------|--------|
| Android   | 8.0+    | Planned |
| iOS       | 14.0+   | Planned |
| Android TV| 8.0+    | Planned |
| Wear OS   | 3.0+    | Planned |
| iPad      | 14.0+   | Planned |
| watchOS   | 7.0+    | Planned |
| visionOS  | 1.0+    | Future |

## CLI Commands

```
isoko mobile new <name>          Create a new mobile project
isoko mobile genda <file.i>      Run a mobile application
isoko mobile kubaka [dir]        Build the project
isoko mobile gupakira <format>   Package for distribution
isoko mobile emulator <device>   Launch emulator
isoko mobile isuzuma [dir]       Run diagnostics
isoko mobile profiler            Profile application
isoko mobile ingingo             List available components
isoko mobile gufasha             Show help
```

## Performance Targets

| Metric          | Target        |
|-----------------|---------------|
| Cold Start      | < 2 seconds   |
| Warm Start      | < 500ms       |
| Frame Rate      | 60-120 FPS    |
| APK Size        | < 8MB (min)   |
| IPA Size        | < 10MB (min)  |
| Memory Usage    | < 50MB (idle) |
| Battery Impact  | < 5% per hour |
| UI Latency      | < 16ms        |

## Build Output

| Format | Description              |
|--------|--------------------------|
| APK    | Android Package          |
| AAB    | Android App Bundle       |
| IPA    | iOS App Store Package    |
| Debug  | Debug build with symbols |
| Release| Optimized release build  |

## Dependencies

- Python 3.8+
- I Language VM
- UFA (Unified Framework Architecture)
- Platform SDKs (Android SDK, Xcode CLI tools)
