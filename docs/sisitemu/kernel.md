# Kernel Development Guide

## Overview

SISITEMU provides a complete kernel development framework for building OS kernels
from scratch. The `umuyobora` module handles boot, virtual memory management,
IPC, shared memory, driver management, power management, and syscalls.

## Getting Started

```bash
isoko sisitemu new my_kernel --type kernel
isoko sisitemu kernel build --target x86_64
isoko sisitemu kernel run --target qemu
```

## Kernel Structure

A minimal kernel consists of:

1. **Boot sequence** — architecture detection, page table setup, interrupt init
2. **Kernel main** — scheduler, driver probe, syscall handlers
3. **Services** — memory management, IPC, process management

## Kernel API

```python
from sisitemu.umuyobora import Kernel, KernelConfig, VirtualMemoryManager

config = KernelConfig(
    name="MyKernel",
    version="0.1.0",
    max_processes=256,
    page_size=4096,
)
kernel = Kernel(config)
kernel.boot()

vmm = VirtualMemoryManager()
vmm.map_page(0x1000, 0x2000, permissions="rw-")
```

## Power Management

```python
from sisitemu.umuyobora import PowerManager
pm = PowerManager()
pm.set_state("sleep")
pm.set_wake_alarm(10)  # wake in 10 seconds
```
