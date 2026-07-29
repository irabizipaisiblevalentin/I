# IBIRO — Desktop Application Platform

## Overview

IBIRO (I-BI-RO, meaning "to see" in Kinyarwanda) is the desktop application platform for the I Programming Language ecosystem. Built on the Unified Framework Architecture (UFA), it provides a complete widget toolkit, layout engine, graphics system, and platform integration layer for building native desktop applications in Python.

## Architecture Layers

```
┌─────────────────────────────────────────────┐
│                 Applications                  │
├─────────────────────────────────────────────┤
│           Widget Toolkit (18 widgets)        │
│  Button  Label  Text  Table  Tree  List      │
│  Menu  Dialog  Form  Canvas  Tabs  Toolbar  │
│  StatusBar  Sidebar  Notification  Image     │
│  Slider  Progress  Card                      │
├─────────────────────────────────────────────┤
│            Layout Engine (9 layouts)         │
│  Row  Column  Grid  Stack  Dock  Scroll      │
│  Responsive  SplitView                       │
├─────────────────────────────────────────────┤
│         Graphics System (3 modules)          │
│  Color  Theme  Animation                     │
├───────────────────┬─────────────────────────┤
│   State Mgmt (3)  │   Platform Backends (5)  │
│  Reactive  Binding │  Windows  Linux  Darwin  │
│  Store             │  Headless               │
├───────────────────┴─────────────────────────┤
│         Native Integration (3 modules)       │
│  Clipboard  Notifications  Shortcuts         │
├─────────────────────────────────────────────┤
│        AI Features (2) / Plugins (1)         │
├─────────────────────────────────────────────┤
│    Dev Tools (3) / Packaging (1) / CLI (2)   │
└─────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Zero external dependencies** — Pure Python stdlib only, with optional integration for speech recognition
2. **Platform abstraction** — `PlatformBackend` ABC with concrete implementations per OS; runtime detection via `platform/detect.py`
3. **Widget tree** — Each widget has a parent, children, styles, state flags, and accessibility data
4. **Reactive state** — `ReactiveProperty` and `ComputedProperty` enable automatic UI updates via watchers
5. **Two-way binding** — `Binding` objects connect widget properties to state with pluggable converters
6. **Theming** — `Theme` defines color palette + style overrides; built-in light, dark, high-contrast themes
7. **Plugin system** — `AppPlugin`, `ThemePlugin`, `WidgetPlugin`, `LanguagePack`, `EnterpriseExtension`
8. **CLI integration** — Accessible via `isoko ibiro <command>` with new, run, build, package, deploy, analyze, themes

## Module Map

| Module | File | Description |
|--------|------|-------------|
| App | `app.py` | `IbiroApplication` — top-level app lifecycle |
| Window | `window.py` | `Window`, `WindowManager`, window states |
| Widgets | `widgets/` | 18 widget types (base + 17 concrete) |
| Layout | `layout/` | 9 layout containers |
| Graphics | `graphics/` | Color, Theme, Animation engines |
| State | `state/` | Reactive properties, binding, store |
| Platform | `platform/` | OS backends + detection |
| Native | `native/` | Clipboard, notifications, shortcuts |
| AI | `ai/` | Assistant integration, speech recognition |
| Plugins | `plugins/` | Plugin system with manifests |
| Tools | `tools/` | Hot-reload, inspector, profiler |
| Packaging | `packaging/` | App bundling (AppImage, Flatpak, MSI, DMG) |
| CLI | `cli/` | `isoko ibiro` subcommand handlers |

## CLI Commands

| Command | Description |
|---------|-------------|
| `isoko ibiro new <name>` | Scaffold new desktop app project |
| `isoko ibiro run [path]` | Run an IBIRO app |
| `isoko ibiro build [path]` | Build the app |
| `isoko ibiro package <format>` | Package for distribution |
| `isoko ibiro deploy <target>` | Deploy app |
| `isoko ibiro analyze [path]` | Analyze widget tree |
| `isoko ibiro themes` | List available themes |
| `isoko ibiro help` | Show help |

## Testing

- Tests live in `tests/unit/ibiro/`
- Run with: `pytest tests/unit/ibiro/`
- Headless backend available for CI/testing environments
