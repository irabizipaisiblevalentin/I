# SISITEMU Architecture — The Unified Infrastructure Foundation of the I Language

## Overview

SISITEMU (Kinyarwanda: "system") is the unified foundation for **all infrastructure
built with I**. It is NOT merely a systems programming library — it is the shared
substrate that powers operating systems, embedded devices, database engines,
distributed systems, cloud infrastructure, AI inference servers, edge computing,
robotics controllers, and high-performance networking.

Every higher-level framework in the I ecosystem builds on SISITEMU:
- **UBWENGE** (AI) → uses SISITEMU for GPU compute, tensor ops, model serving
- **IMIKINO** (Games/Simulation) → uses SISITEMU for real-time control, DDS, networking
- **IGICU** (Cloud) → uses SISITEMU for containers, VMs, orchestration, load balancing
- **Web/API** → uses SISITEMU for HTTP servers, TLS, connection pooling

This unified approach eliminates duplication and ensures consistent performance,
security, and reliability across all domains.

## Design Principles

1. **Unified foundation** — all infrastructure shares the same core, no duplication
2. **Layered architecture** — hardware abstraction → core primitives → system services → infrastructure domains
3. **Memory safety** — compile-time and runtime guarantees without a garbage collector
4. **Zero-cost abstractions** — pay only for what you use, no hidden overhead
5. **Deterministic execution** — predictable performance, no GC pauses
6. **Cross-platform** — x86, ARM, RISC-V, embedded, edge, cloud
7. **Interoperability** — C ABI, FFI, POSIX emulation

## Layered Architecture

```
                    ┌─────────────────────────────────────────────────────┐
                    │          Built on SISITEMU Foundation                │
                    │  UBWENGE (AI)  │  IMIKINO  │  IGICU  │  Web/API    │
                    └──────────────────────────┬──────────────────────────┘
                                               ▲
              ┌────────────────────────────────┴────────────────────────────┐
              │            LAYER 3 — INFRASTRUCTURE DOMAINS                  │
              │                                                              │
              │  ububiko_db      gukwirakwiza          ibicu                │
              │  ┌──────────┐   ┌────────────────┐   ┌─────────────────┐    │
              │  │ B+Tree   │   │ Raft Consensus │   │ Container       │    │
              │  │ LSM Tree │   │ RPC Framework  │   │ VM Manager      │    │
              │  │ WAL      │   │ Service Disc.  │   │ Load Balancer   │    │
              │  │ Buffer   │   │ Distributed    │   │ Orchestrator    │    │
              │  │ Pool     │   │ Locks          │   │ Secrets Mgmt    │    │
              │  │ Txn Mgr  │   │ Message Queues │   │ Config Mgmt     │    │
              │  └──────────┘   └────────────────┘   └─────────────────┘    │
              │                                                              │
              │  inkomoko                                                    │
              │  ┌──────────────────────────────────────────────────────┐    │
              │  │ Edge Runtime │ IoT Gateway │ GPU Compute │ Tensor    │    │
              │  │ Model Serving │ RT Control │ Low Power               │    │
              │  └──────────────────────────────────────────────────────┘    │
              └──────────────────────────┬───────────────────────────────────┘
                                         ▲
              ┌──────────────────────────┴───────────────────────────────────┐
              │              LAYER 2 — SYSTEM SERVICES                        │
              │                                                              │
              │  ububiko         itumanaho          ibikorwa     umuyobora   │
              │  ┌──────────┐   ┌──────────────┐   ┌─────────┐  ┌─────────┐ │
              │  │ VFS      │   │ TCP/UDP      │   │Processes│  │ Boot    │ │
              │  │ FAT/Ext  │   │ HTTP/DNS     │   │Scheduler│  │ VMM     │ │
              │  │ MMap IO  │   │ RDMA/DPDK    │   │Timers   │  │ IPC     │ │
              │  │ AIO/ur   │   │ KernelBypass │   │Signals  │  │ Drivers │ │
              │  │ io_uring │   │ ZeroCopy     │   │Contain. │  │ Power   │ │
              │  └──────────┘   └──────────────┘   └─────────┘  └─────────┘ │
              └──────────────────────────┬───────────────────────────────────┘
                                         ▲
              ┌──────────────────────────┴───────────────────────────────────┐
              │              LAYER 1 — CORE PRIMITIVES                        │
              │                                                              │
              │  ibikoresho_sisitemu    umutekano_sisitemu  imikorere_sisitemu│
              │  ┌──────────────────┐  ┌────────────────┐  ┌───────────────┐ │
              │  │ Memory Mgmt     │  │ MPU            │  │ Benchmarks    │ │
              │  │ Allocators      │  │ Sandbox        │  │ Latency       │ │
              │  │ Pointers/Slices │  │ Crypto         │  │ Throughput    │ │
              │  │ BitOps/Atomics  │  │ Secure IPC     │  │ Memory Track  │ │
              │  │ Endianness      │  │ Audit/Stack    │  │ Optimizer     │ │
              │  └──────────────────┘  └────────────────┘  └───────────────┘ │
              └──────────────────────────┬───────────────────────────────────┘
                                         ▲
              ┌──────────────────────────┴───────────────────────────────────┐
              │              LAYER 0 — HARDWARE ABSTRACTION                    │
              │                                                              │
              │  ibyinjijwe           ibikoresho_byinjijwe    igenzura        │
              │  ┌────────────────┐  ┌──────────────────┐  ┌─────────────┐  │
              │  │ MCU/GPIO      │  │ USB/PCIe         │  │ Tracer      │  │
              │  │ SPI/I2C/UART  │  │ Storage/Graphics │  │ Profiler    │  │
              │  │ PWM/ADC/Timer │  │ Sensors/Display  │  │ Memory Insp │  │
              │  │ RTOS          │  │ Touch/Industrial │  │ Debugger    │  │
              │  │ DDS/RT Ctrl   │  │                  │  │ Crash Dump  │  │
              │  └────────────────┘  └──────────────────┘  └─────────────┘  │
              └─────────────────────────────────────────────────────────────┘
```

## Modules

### Layer 0 — Hardware Abstraction
| Module | File | Purpose |
|--------|------|---------|
| ibyinjijwe | `ibyinjijwe.py` | MCU, GPIO, SPI, I2C, UART, PWM, ADC, timers, RTOS, DDS, real-time control |
| ibikoresho_byinjijwe | `ibikoresho_byinjijwe.py` | USB, PCIe, storage, graphics, sensors, displays, touch, industrial |
| igenzura_sisitemu | `igenzura_sisitemu.py` | Tracer, profiler, memory inspector, crash dump, debugger |

### Layer 1 — Core Primitives
| Module | File | Purpose |
|--------|------|---------|
| ibikoresho_sisitemu | `ibikoresho_sisitemu.py` | Memory model, allocators, pointers, slices, bit ops, atomics, endianness |
| umutekano_sisitemu | `umutekano_sisitemu.py` | MPU, sandbox, crypto, secure IPC, stack protection, audit |
| imikorere_sisitemu | `imikorere_sisitemu.py` | Benchmarks, latency, memory tracking, throughput, optimization |

### Layer 2 — System Services
| Module | File | Purpose |
|--------|------|---------|
| ububiko | `ububiko.py` | VFS, FAT, Ext, memory FS, native FS, mmap IO, async IO, io_uring |
| itumanaho_sisitemu | `itumanaho_sisitemu.py` | TCP, UDP, HTTP, DNS, DHCP, serial, CAN, RDMA, DPDK, kernel bypass, zero-copy |
| ibikorwa_sisitemu | `ibikorwa_sisitemu.py` | Processes, scheduler, timers, signals, environment |
| umuyobora | `umuyobora.py` | Kernel, VMM, IPC, shared memory, drivers, power, cgroups, namespaces, unikernel |
| igaragaza | `igaragaza.py` | Display server, compositor, window manager, theme engine, font rendering, input dispatch |
| ibikoresho_bya_GUI | `ibikoresho_bya_GUI.py` | GUI widget toolkit: buttons, text boxes, lists, menus, tabs, trees |
| ikigoroba | `ikigoroba.py` | Desktop shell: taskbar, start menu, desktop icons, system tray |

### Layer 3 — Infrastructure Domains
| Module | File | Purpose |
|--------|------|---------|
| ububiko_db | `ububiko_db.py` | B+trees, LSM trees, WAL, buffer pool, transactions, indexing, storage engine |
| gukwirakwiza | `gukwirakwiza.py` | Raft consensus, RPC, service discovery, distributed locks, message queues, CRDT |
| ibicu | `ibicu.py` | Containers, VMs, load balancing, orchestration, secrets, config management |
| inkomoko | `inkomoko.py` | Edge runtime, IoT gateway, GPU compute, tensor ops, model serving, RT control, low power |

### CLI
| Module | File | Purpose |
|--------|------|---------|
| itegeko_sisitemu | `itegeko_sisitemu.py` | CLI: `isoko sisitemu new/kernel/driver/embedded/benchmark/deploy/inspect` |

## CLI Usage

```bash
# Create projects
isoko sisitemu new my_kernel --type kernel
isoko sisitemu new my_db --type database
isoko sisitemu new my_service --type distributed

# Kernel development
isoko sisitemu kernel build --target x86_64
isoko sisitemu kernel run --target qemu

# Database engine
isoko sisitemu db create my_store --engine lsm
isoko sisitemu db benchmark --iterations 10000

# Distributed systems
isoko sisitemu raft start --peers node2:9001,node3:9002
isoko sisitemu queue create events --partitions 3

# Cloud infrastructure
isoko sisitemu container run nginx:latest --port 80:80
isoko sisitemu vm create worker --cpus 4 --memory 8192

# Edge / AI
isoko sisitemu edge device add sensor-01 --type temperature
isoko sisitemu model deploy my_model --version 2.0 --runtime edge

# Embedded
isoko sisitemu embedded flash --port /dev/ttyUSB0 --firmware kernel.bin

# Benchmark
isoko sisitemu benchmark --module all --iterations 5000
```

## Domain-Specific Guides

See [docs/sisitemu/](docs/sisitemu/) for:
- [Kernel Guide](docs/sisitemu/kernel.md)
- [Embedded Guide](docs/sisitemu/embedded.md)
- [Networking Guide](docs/sisitemu/networking.md)
- [Security Guide](docs/sisitemu/security.md)
- [Performance Guide](docs/sisitemu/performance.md)
- [Cross-Platform Guide](docs/sisitemu/cross-platform.md)
- [Database Engine Guide](docs/sisitemu/database.md)
- [Distributed Systems Guide](docs/sisitemu/distributed.md)
- [Cloud Infrastructure Guide](docs/sisitemu/cloud.md)
- [Edge & AI Compute Guide](docs/sisitemu/edge-ai.md)
