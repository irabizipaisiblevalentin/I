# Cross-Platform Development Guide

## Overview

SISITEMU supports multiple architectures and platforms. This guide covers
building and deploying for different targets.

## Supported Architectures

| Architecture | Target Name | Use Case |
|-------------|-------------|----------|
| x86_64 | `x86_64` | Desktop, server |
| i386 | `i386` | Legacy systems |
| ARMv8-A | `aarch64` | Server, mobile, Raspberry Pi |
| RISC-V 64 | `riscv64` | Open hardware, embedded |
| Cortex-M4 | `cortex-m4` | Embedded MCU |
| ESP32 | `esp32` | IoT |
| AVR | `avr` | Arduino, 8-bit MCU |

## Building for Different Targets

```bash
# x86_64 desktop kernel
isoko sisitemu kernel build --target x86_64

# ARM64 server kernel
isoko sisitemu kernel build --target aarch64

# RISC-V embedded firmware
isoko sisitemu embedded build --target riscv64 --firmware firmware.bin
```

## Memory Model Differences

```python
from sisitemu.ibikoresho_sisitemu import Endianness

# x86_64 is little-endian
if Endianness.native() == Endianness.LITTLE:
    val = Endianness.swap_32(raw)
```

## Deploy Targets

```bash
# QEMU emulation (development)
isoko sisitemu deploy --target qemu --image kernel.bin

# Bare metal (USB/ISO)
isoko sisitemu deploy --target baremetal --image kernel.iso

# Embedded flashing
isoko sisitemu embedded flash --port /dev/ttyUSB0 --firmware kernel.bin
```

## ABI Compatibility

SISITEMU follows the C ABI on each platform for FFI compatibility:

```python
from sisitemu.ibikoresho_sisitemu import Pointer

# Call C functions via FFI
libc = Pointer.ffi_load("libc.so.6")
result = libc.call("printf", "Hello from I\n")
```
