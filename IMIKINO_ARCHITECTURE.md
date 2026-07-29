# IMIKINO Architecture — The Official Interactive Simulation Platform of the I Language

## Overview

IMIKINO (Kinyarwanda: "games/plays") is the official game engine and interactive
simulation platform of the I Programming Language. It is a complete game development
ecosystem **and** professional simulation platform — providing ECS, rendering, physics,
audio, animation, input, networking, AI, scripting, editor tooling, plus robotics,
autonomous vehicle, smart city, digital twin, and general-purpose simulation.

## Design Principles

1. **Complete ecosystem** — everything needed for game development and simulation in one platform
2. **ECS-first architecture** — data-oriented design for performance and flexibility
3. **UBWENGE AI integration** — first-class AI for NPCs, behaviour trees, dialogue, and simulation agents
4. **Cross-platform** — 2D, 3D, mobile, desktop, web, and future console support
5. **Extensible** — plugin system, scripting, custom pipelines
6. **Simulation-first** — deterministic mode, time scaling, replay, scenario management
7. **Professional-grade** — robotics kinematics, sensor models, traffic simulation, digital twins

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                             IMIKINO Platform (Games + Simulation)                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Rendering │  │ Physics  │  │  Audio   │  │Animation │  │  Input   │              │
│  │(ishush.) │  │(ubwonek.)│  │(amajwi.) │  │(imikor.) │  │(inyand.)│              │
│  └─────┬────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│        │            │              │              │              │                    │
│  ┌─────┴────────────┴──────────────┴──────────────┴──────────────┴─────────────────┐ │
│  │                          Entity Component System (imiyoborere)                    │ │
│  │                           World · Entity · Component · System                     │ │
│  └──────────────────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────┐  ┌────────────────────────────────────────────────┐ │
│  │  Game Engine (ikorwa)       │  │  Simulation Engine (ikigereranyo)              │ │
│  │  Scene Graph · Game Loop    │  │  Clock · Scenarios · Recording · Replay        │ │
│  └─────────────────────────────┘  └────────────────────────────────────────────────┘ │
│                                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │Network   │  │  Assets  │  │Scripting │  │AI (UBW.)│  │   Simulation Domains  │  │
│  │(gukoresh)│  │(ibikore.)│  │(guhind.)│  │(inyenz.)│  │                       │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │  Robotics (ibintu_)  │  │
│  ┌──────────────────────────────────────────────────────┐ │  Autonomous Vehicles  │  │
│  │          Editor (uguhindura) — Full Tooling          │ │  Smart City (umujyi)  │  │
│  └──────────────────────────────────────────────────────┘ │  Digital Twin (inganda)│  │
│                                                           └──────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                        CLI (itegeko) — isoko imikino [...]                            │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Modules

| Module | File | Purpose |
|--------|------|---------|
| ikorwa | `ikorwa.py` | Core engine, scene graph, game loop, layers |
| imiyoborere | `imiyoborere.py` | Entity Component System (World, Entity, Component, System) |
| ishushanyo | `ishushanyo.py` | 2D/3D rendering, PBR, meshes, materials, particles, cameras, lights |
| ubwonekano | `ubwonekano.py` | Physics: rigid bodies, collision detection, raycasting, joints |
| amajwi_imikino | `amajwi_imikino.py` | Audio: 3D spatial, streaming, effects, mixing |
| imikorere_animation | `imikorere_animation.py` | Animation: skeleton, blend trees, IK, timeline |
| inyandikwa | `inyandikwa.py` | Input: keyboard, mouse, touch, gamepad, action bindings |
| gukoreshana | `gukoreshana.py` | Networking: client-server, P2P, replication, matchmaking |
| ibikoresho | `ibikoresho.py` | Asset pipeline: import, textures, meshes, materials, prefabs |
| guhindura | `guhindura.py` | Scripting: I language integration, hot reload, plugins |
| inyenzure | `inyenzure.py` | AI integration: behaviour trees, navmesh, pathfinding, dialogue |
| uguhindura | `uguhindura.py` | Editor: scene/material/animation editors, undo/redo |
| ibikoreshingiro | `ibikoreshingiro.py` | Math: vectors, matrices, quaternions, transforms, color |
| ikigereranyo | `ikigereranyo.py` | Simulation core: engine, clock, scenarios, recording, replay |
| ibintu_nyabutatu | `ibintu_nyabutatu.py` | Robotics: robot models, kinematics, sensors (LiDAR, camera, IMU, GPS) |
| imodoka | `imodoka.py` | Autonomous vehicles: dynamics, traffic scenarios, ADAS |
| umujyi | `umujyi.py` | Smart city: zones, buildings, infrastructure, environment, pedestrians |
| inganda | `inganda.py` | Digital twin: factories, production lines, machines, supply chain |
| itegeko | `itegeko.py` | CLI: isoko imikino subcommands |

## Key Features

### ECS
- `World` manages entities and systems; `Entity` holds `Component` instances
- `EntityQuery` with required/excluded component filters
- System lifecycle: start, update, render, on_entity_added, on_entity_removed

### Rendering
- Mesh generation: quad, cube, sphere with vertex/normal/UV data
- PBR material properties: albedo, metallic, roughness, emissive
- Camera system with perspective/orthographic projection
- Particle system with emission, gravity, color/size over lifetime
- Sprite and text rendering components
- Render queues: background, opaque, transparent, overlay

### Physics
- Rigid bodies (static, dynamic, kinematic) with mass/drag/gravity
- Colliders: sphere, box, capsule, plane, mesh, cylinder
- Collision detection with contact points and penetration
- Raycasting for picking and line-of-sight
- Joints: fixed, connected entity constraints

### Audio
- 3D spatial audio with rolloff, min/max distance
- Audio effects: reverb, echo, low-pass filter
- Mixer groups with volume/mute/solo
- Streaming audio support

### Animation
- Skeleton system with bone hierarchy
- Animation curves with keyframes and wrap modes
- Blend trees for smooth transitions
- Inverse kinematics for procedural animation
- Timeline system for cutscenes

### Networking
- Client-server and peer-to-peer modes
- Reliable/unreliable message delivery
- Object replication with property synchronization
- Matchmaker for lobby/room management
- Latency measurement

### AI (UBWENGE Bridge)
- NPC state machine: idle, patrol, chase, attack, flee, etc.
- Behaviour trees with selector, sequence, condition, action nodes
- Navigation mesh with pathfinding
- Dialogue system with branching conversations
- Perception system with field-of-view

### Editor
- Scene, game, hierarchy, inspector, project, console views
- Undo/redo history (100 states)
- Gizmo tools: select, move, rotate, scale
- Grid snapping

### Scripting
- `ScriptComponent` attaches I scripts to entities
- Plugin system for engine extensions
- Hot reload support

### Simulation (ikigereranyo)
- Configurable simulation clock: real-time, stepped, scaled, fixed-step, catch-up
- Scenario system with parameters, setup/teardown, completion conditions
- Simulation recording and replay for analysis
- Deterministic mode with configurable random seed
- Simulator runs for duration or step count with callbacks

### Robotics (ibintu_nyabutatu)
- Robot model with joint/link tree and forward/inverse kinematics
- Sensor models: LiDAR (beam simulation), Camera, IMU, GPS
- Sensor noise modeling and configurable update rates
- URDF export for interoperability
- ROS2-compatible architecture patterns

### Autonomous Vehicles (imodoka)
- Vehicle dynamics: bicycle model with throttle/brake/steering
- Traffic scenario editor with participants, traffic lights, road types
- ADAS system: adaptive cruise control, lane keep assist, automatic emergency braking
- Collision detection and reporting
- Weather and time-of-day conditions

### Smart City (umujyi)
- Zoning system: residential, commercial, industrial, mixed-use
- Building management: types, occupants, energy/water consumption
- Infrastructure networks: power, water, telecom, transport
- Environment simulation: day/night cycle, weather, temperature, pollution
- Pedestrian simulation with goal-seeking behavior

### Digital Twin (inganda)
- Factory layout with machines, conveyors, production lines
- Machine states: idle, running, paused, maintenance, fault, offline
- OEE (Overall Equipment Effectiveness) calculation
- Supply chain nodes with inventory, lead time, capacity
- Equipment sensors with alerting thresholds
- Product tracking: raw → in-progress → quality check → completed → shipped

## CLI Usage

```bash
# Create a new game project
isoko imikino new MyGame --template 3d

# Build for target platform
isoko imikino build --target windows --config release

# Run the game
isoko imikino run --scene MainScene

# Profile performance
isoko imikino profile --duration 30

# Package for distribution
isoko imikino package --platform windows --version 1.0

# Deploy to platform
isoko imikino deploy --platform steam --version 1.0

# Manage assets
isoko imikino asset list
isoko imikino asset import models/character.glb

# Manage scenes
isoko imikino scene create MainScene
isoko imikino scene list

# Run simulations
isoko imikino simulate robot --duration 30 --deterministic
isoko imikino simulate vehicle --duration 60 --output results.json
isoko imikino simulate city --duration 120
isoko imikino simulate factory --duration 300

# Robotics commands
isoko imikino robot create ArmBot
isoko imikino robot fk
isoko imikino robot sensors
```

## Domain-Specific Guides

See [docs/imikino/](docs/imikino/) for:
- [Rendering Guide](docs/imikino/rendering.md)
- [Physics Guide](docs/imikino/physics.md)
- [Animation Guide](docs/imikino/animation.md)
- [Networking Guide](docs/imikino/networking.md)
- [AI Guide](docs/imikino/ai.md)
- [Editor Guide](docs/imikino/editor.md)
- [Performance Guide](docs/imikino/performance.md)
- [Plugin Guide](docs/imikino/plugin.md)
- [Simulation Guide](docs/imikino/simulation.md)
