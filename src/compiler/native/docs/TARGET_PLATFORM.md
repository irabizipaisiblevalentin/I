# Target Platform Guide

## Supported Targets

| TargetKind    | Architecture | Pointer Width | Endianness |
|---------------|-------------|---------------|------------|
| `X86_64`      | AMD64       | 64-bit        | Little     |
| `X86_32`      | IA-32       | 32-bit        | Little     |
| `ARM64`       | AArch64     | 64-bit        | Little     |
| `ARM32`       | ARM         | 32-bit        | Little     |
| `RISCV64`     | RISC-V 64   | 64-bit        | Little     |
| `RISCV32`     | RISC-V 32   | 32-bit        | Little     |
| `WASM32`      | WebAssembly | 32-bit        | N/A        |
| `WASM64`      | WebAssembly | 64-bit        | N/A        |

Primary supported targets for production use: **x86-64** and **ARM64**.

---

## Platform Matrix

| Feature                | Linux (x86-64)           | Windows (x86-64)        | macOS (ARM64)           |
|------------------------|--------------------------|--------------------------|--------------------------|
| Object format          | ELF64                    | PE/COFF                  | Mach-O 64               |
| Calling convention     | System V AMD64           | Microsoft x64            | ARM64 AAPCS             |
| Linker                 | `ld` / `gcc`             | `link.exe` (MSVC)        | `ld` / `clang`           |
| Default entry point    | `main`                   | `WinMain`                | `main`                   |
| Dynamic linker         | `/lib64/ld-linux-x86-64.so.2` | N/A                | `/usr/lib/dyld`          |
| Standard libraries     | `libc`, `libgcc`         | `kernel32.lib`, `msvcrt` | `libSystem`              |
| Shadow space           | 0 bytes                  | 32 bytes                 | 0 bytes                  |
| Stack alignment        | 16 bytes                 | 16 bytes                 | 16 bytes                 |
| Red zone               | 128 bytes (leaf funcs)   | 0 bytes                  | 0 bytes                  |

### Linux (x86-64 and ARM64)

- Uses ELF64 relocatable object format (`ELFWriter`)
- System V AMD64 ABI on x86-64; ARM64 AAPCS on ARM64
- Linker: `ld` (default) or `gcc`/`clang` frontend
- Dynamic linking via `-dynamic-linker` flag
- C runtime linked via `-lc -lgcc`
- Stack canary (`--stack-protector`) reads from `fs:0x28` (x86-64) or a stack guard global

### Windows (x86-64)

- Uses PE/COFF object format (`PEWriter`)
- Microsoft x64 ABI calling convention
- Linker: `link.exe` from MSVC toolchain (auto-detected from Visual Studio installation paths)
- 32 bytes of shadow space allocated by the caller
- Default libraries: `kernel32.lib`, `user32.lib`, `msvcrt`
- Entry point: `main` or `WinMain`
- No red zone

### macOS (ARM64 and x86-64)

- Uses Mach-O relocatable object format (`MachOWriter`)
- ARM64 AAPCS on Apple Silicon; System V AMD64 on Intel Macs
- Linker: `clang` frontend (preferred) or `ld`
- Links `libSystem` which includes `libc`
- Position-independent code (PIC) required for shared libraries
- Page size: 16 KB (ARM64) or 4 KB (x86-64)

---

## Target Triple Format

Target triples follow the standard `<arch>-<vendor>-<system>` format:

```
<architecture>-<vendor>-<operating-system>
```

Examples:

| Triple                              | Target                          |
|-------------------------------------|---------------------------------|
| `x86_64-unknown-linux-gnu`          | Linux x86-64                    |
| `x86_64-pc-windows-msvc`            | Windows x86-64                  |
| `aarch64-apple-darwin`              | macOS ARM64                     |
| `x86_64-apple-darwin`               | macOS x86-64                    |
| `aarch64-unknown-linux-gnu`         | Linux ARM64                     |
| `riscv64-unknown-linux-gnu`         | Linux RISC-V 64                 |

The `platform.py` module constructs host triples automatically:

```python
def host_triple() -> str:
    arch = platform.machine().lower()
    system = platform.system().lower()
    # Maps "amd64" -> "x86_64", "darwin" -> "apple-darwin", etc.
    return f"{arch_str}-{os_str}"
```

---

## Feature Detection

### CPU Features (`BackendFeature`)

Defined in `backend/base.py`:

| Feature       | Architecture | Description               |
|---------------|-------------|---------------------------|
| `SSE2`        | x86-64      | SSE2 instructions         |
| `SSE3`        | x86-64      | SSE3 instructions         |
| `SSSE3`       | x86-64      | Supplemental SSE3         |
| `SSE4.1`      | x86-64      | SSE 4.1                   |
| `SSE4.2`      | x86-64      | SSE 4.2                   |
| `AVX`         | x86-64      | Advanced Vector Extensions|
| `AVX2`        | x86-64      | AVX2                      |
| `AVX512F`     | x86-64      | AVX-512 Foundation        |
| `NEON`        | ARM64       | NEON SIMD                 |
| `SVE`         | ARM64       | Scalable Vector Extensions|
| `SVE2`        | ARM64       | SVE version 2             |
| `FP16`        | ARM64       | Half-precision float      |
| `BMI1/BMI2`   | x86-64      | Bit manipulation          |
| `FMA`         | x86-64      | Fused multiply-add        |

### Platform Detection

The `target/platform.py` module provides:

```python
def detect_platform() -> Platform:     # LINUX, WINDOWS, MACOS
def detect_architecture() -> str:      # "x86_64", "arm64", etc.
def detect_target() -> TargetDescription:  # Full target description
def is_windows() -> bool
def is_linux() -> bool
def is_macos() -> bool
```

---

## Cross-Compilation Support

Cross-compilation is supported by specifying a target triple different from the host.

### Object Format Selection

The object file writer is selected based on the target triple:

```python
def select_object_writer(target: TargetDescription):
    triple = target.triple.lower()
    if "windows" in triple or "msvc" in triple:
        return PEWriter()
    if "apple" in triple or "darwin" in triple:
        return MachOWriter.for_target(target)
    return ELFWriter.for_target(target)
```

### Linker Selection for Cross-Compilation

When cross-compiling, the linker must target a different architecture. The `SystemLinker` class accepts linker path and type overrides:

```python
# Cross-compile from x86-64 to ARM64
linker = SystemLinker(
    linker_path="aarch64-linux-gnu-gcc",
    use_gcc_frontend=True,
)
```

---

## Platform-Specific Limitations

### Windows
- No red zone optimization (Microsoft x64 ABI does not define a red zone)
- 32-byte shadow space must be allocated for every function call
- COFF object format does not support `.rodata` as a separate section name; read-only data goes into `.rdata`
- SEH (Structured Exception Handling) requires additional metadata not yet implemented
- TLS (Thread-Local Storage) support is limited
- DLL generation requires `.def` files or `__declspec(dllexport)` annotations

### macOS
- Mach-O does not support `SHT_RELA` relocations; uses `SHT_REL` instead (though the writer uses a simplified model)
- Position-independent code (PIC) is required for all shared libraries
- Hardened runtime may interfere with JIT compilation
- ARM64 on macOS uses `x18` as a reserved register (not available for general use)
- Page alignment for `__TEXT` segment is 16 KB on Apple Silicon (vs 4 KB on Intel)

### Linux
- Dynamic linking requires `ld-linux-x86-64.so.2` or `ld-linux-aarch64.so.1`
- Stack canary support uses thread-local storage (`fs:0x28` on x86-64)
- Position-independent executables (PIE) require `-pie` linker flag and PIC code
- GLIBC version compatibility may affect linked executables
- musl-based distributions (Alpine) use different dynamic linker paths

### ARM64 (General)
- No integer division/modulo in some older implementations (though all modern implementations have it); the legalizer handles this
- `str/ldr` immediate offset must be a multiple of the access size (8 for 64-bit, 4 for 32-bit)
- Conditional branch range is limited to +/- 1 MB (B.cond) or +/- 128 MB (B)
- No dedicated flags register; comparisons write to the general-purpose register `xzr`
