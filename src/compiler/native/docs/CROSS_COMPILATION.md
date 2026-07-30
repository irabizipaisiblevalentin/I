# Cross-Compilation Guide

## Target Triple Specification

Cross-compilation is controlled by specifying a `TargetDescription` with a triple different from the host system. The target triple uses the standard `<arch>-<vendor>-<os>` format.

### Target Triples

| Triple                              | Architecture | OS          |
|-------------------------------------|-------------|-------------|
| `x86_64-unknown-linux-gnu`          | x86-64      | Linux       |
| `x86_64-pc-windows-msvc`            | x86-64      | Windows     |
| `x86_64-apple-darwin`              | x86-64      | macOS       |
| `aarch64-unknown-linux-gnu`         | ARM64       | Linux       |
| `aarch64-apple-darwin`             | ARM64       | macOS       |
| `armv7-unknown-linux-gnueabihf`    | ARM32       | Linux       |
| `riscv64-unknown-linux-gnu`        | RISC-V 64   | Linux       |
| `wasm32-unknown-unknown`            | WebAssembly | None        |

### Specifying a Target

```python
from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind

# Cross-compile for ARM64 Linux
target = TargetDescription(
    kind=TargetKind.ARM64,
    bits=64,
    triple="aarch64-unknown-linux-gnu",
    features=frozenset({"neon"}),
)
```

### Automatic Target Detection

The `BackendManager.detect_target()` method detects the host target:

```python
manager = BackendManager()
host_target = manager.detect_target()
# Returns e.g. TargetDescription(kind=X86_64, triple="x86_64-unknown-linux-gnu", ...)
```

---

## Cross-Toolchain Requirements

### Linux Host

| Target            | Required Toolchain                   |
|-------------------|--------------------------------------|
| x86-64 Linux      | `gcc` or `ld` (native)              |
| ARM64 Linux       | `aarch64-linux-gnu-gcc` or `aarch64-linux-gnu-ld` |
| ARM32 Linux       | `arm-linux-gnueabihf-gcc`           |
| RISC-V 64 Linux   | `riscv64-linux-gnu-gcc`             |
| x86-64 Windows    | `x86_64-w64-mingw32-gcc` or MSVC cross-compiler |
| x86-64 macOS      | `osxcross` toolchain with `clang`   |

Installation (Debian/Ubuntu):

```bash
# ARM64 cross-toolchain
apt install gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu

# ARM32 cross-toolchain
apt install gcc-arm-linux-gnueabihf binutils-arm-linux-gnueabihf

# RISC-V cross-toolchain
apt install gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu

# Windows cross-toolchain (MinGW)
apt install gcc-mingw-w64-x86-64
```

### macOS Host (via `osxcross`)

```bash
# Install osxcross from https://github.com/tpoechtrager/osxcross
# Then:
export PATH=/path/to/osxcross/target/bin:$PATH

# Cross-compile to x86-64 macOS
target_triple="x86_64-apple-darwin"
```

### Windows Host

| Target            | Required                          |
|-------------------|-----------------------------------|
| x86-64 Windows    | MSVC `link.exe` (native)          |
| x86-64 Linux      | `gcc` from WSL or MinGW           |
| ARM64 Windows     | MSVC ARM64 cross-compiler          |

For Linux cross-compilation from Windows, use WSL:

```bash
wsl aarch64-linux-gnu-gcc -o output main.o
```

---

## Sysroot and Library Paths

### Linux Cross-Compilation

When using a cross-linker, the sysroot and library paths must be specified:

```python
from compiler.native.link.interface import SystemLinker

# Cross-link for ARM64
linker = SystemLinker(
    linker_path="aarch64-linux-gnu-gcc",
    use_gcc_frontend=True,
)

result = linker.link_executable(
    object_files=[Path("main.o")],
    output=Path("main.elf"),
    target=target,
    lib_paths=[
        Path("/usr/aarch64-linux-gnu/lib"),
        Path("/usr/lib/aarch64-linux-gnu"),
    ],
    entry="main",
)
```

### Common Sysroot Locations

| Target            | Sysroot Path                          |
|-------------------|---------------------------------------|
| ARM64 Linux       | `/usr/aarch64-linux-gnu`              |
| ARM32 Linux       | `/usr/arm-linux-gnueabihf`            |
| RISC-V 64 Linux   | `/usr/riscv64-linux-gnu`              |
| x86-64 Linux (musl)| `/usr/x86_64-linux-musl`             |

### Using Direct Linker (without frontend)

```python
linker = SystemLinker(linker_path="aarch64-linux-gnu-ld")
result = linker.link_executable(
    object_files=[...],
    output=Path("output"),
    target=target,
    libraries=["c", "gcc"],
    lib_paths=[Path("/usr/aarch64-linux-gnu/lib")],
)
```

---

## Object File Format Selection

The object file format is determined by the target triple:

```python
def select_object_writer(target: TargetDescription):
    triple = target.triple.lower()
    if "windows" in triple or "msvc" in triple:
        return PEWriter()
    if "apple" in triple or "darwin" in triple:
        return MachOWriter.for_target(target)
    return ELFWriter.for_target(target)
```

### Format-Specific Considerations

**ELF:**
- Default for Linux, most Unix-like systems
- `ELF64` with `EM_X86_64 = 62` or `EM_AARCH64 = 183`
- Relocation types: `R_X86_64_64`, `R_X86_64_PC32`, `R_X86_64_PLT32`, `R_AARCH64_ABS64`, `R_AARCH64_CALL26`

**PE/COFF:**
- Required for Windows targets
- Machine type: `IMAGE_FILE_MACHINE_AMD64 = 0x8664`
- Relocation types: `IMAGE_REL_AMD64_ADDR64`, `IMAGE_REL_AMD64_REL32`
- Section names: `.text` becomes `.text`, `.rodata` becomes `.rdata`

**Mach-O:**
- Required for macOS targets
- CPU type: `CPU_TYPE_X86_64 = 0x01000007` or `CPU_TYPE_ARM64 = 0x0100000C`
- Relocation types: `X86_64_RELOC_UNSIGNED`, `X86_64_RELOC_BRANCH`, `ARM64_RELOC_UNSIGNED`, `ARM64_RELOC_BRANCH26`
- Section names use Mach-O conventions: `__TEXT,__text`, `__DATA,__data`

---

## Cross-Compilation Pipeline

The full cross-compilation flow from an x86-64 Linux host to ARM64 Linux:

```
Source Code
     |
     v
NativeCompiler.compile(
    source="...",
    target=TargetKind.ARM64,
    backend=BackendKind.LLVM,  # LLVM backend for cross-compilation
)
     |
     v
BackendManager
     |
     v
1. Lex/Parser/Analyzer          (host-native, architecture-independent)
2. Type checking                (host-native)
3. IR construction              (host-native)
4. LLVM IR emission             (target triple set in IR)
5. llc -mtriple=aarch64-unknown-linux-gnu  (produces ARM64 object)
6. aarch64-linux-gnu-gcc        (links ARM64 object into ARM64 executable)
     |
     v
ARM64 Linux executable (runs under QEMU or on ARM64 hardware)
```

### Using Custom Backend for Cross-Compilation

```python
target = TargetDescription(
    kind=TargetKind.ARM64,
    bits=64,
    triple="aarch64-unknown-linux-gnu",
)

# Steps:
# 1. Lower IR to LIR
# 2. Legalize for ARM64
# 3. ARM64 instruction selection
# 4. ARM64 register allocation
# 5. ARM64 code emission
# 6. Write ELF64 object with EM_AARCH64
# 7. Link with aarch64-linux-gnu-gcc
```

---

## Testing Cross-Compiled Binaries

### Using QEMU User Mode

```bash
# Run ARM64 binary on x86-64 host
qemu-aarch64 -L /usr/aarch64-linux-gnu ./output

# Run RISC-V binary
qemu-riscv64 -L /usr/riscv64-linux-gnu ./output
```

### Using Wine for Windows Binaries

```bash
# Run Windows binary on Linux
wine ./output.exe
```

### Automated Integration Tests

```python
import subprocess
import platform

def test_cross_compile_arm64():
    source = "export fn main() -> int { return 42; }"
    compiler = NativeCompiler()
    result = compiler.compile(
        source=source,
        target=TargetKind.ARM64,
        backend=BackendKind.LLVM,
    )
    assert result.success

    # Verify with QEMU if available
    if shutil.which("qemu-aarch64"):
        qemu_output = subprocess.run(
            ["qemu-aarch64", "-L", "/usr/aarch64-linux-gnu", str(result.output_path)],
            capture_output=True,
        )
        assert qemu_output.returncode == 42
```

### Checking Binary Properties

```bash
# Verify architecture
file output
# Output: ELF 64-bit LSB executable, ARM aarch64, ...

readelf -h output
# Machine: AArch64

# For PE files
objdump -f output.exe
# file format pe-x86-64
```

---

## Platform-Specific Limitations

### ARM64 Cross-Compilation from x86-64
- Requires `aarch64-linux-gnu-gcc` package
- QEMU user mode for testing (limited performance with JIT)
- Some inline assembly or CPU-specific intrinsics may not be portable

### Windows Cross-Compilation from Linux
- Requires MinGW cross-compiler (`x86_64-w64-mingw32-gcc`)
- PE/COFF object format has stricter section name length limits (8 characters)
- Windows-specific features (SEH, TLS) require additional support
- Testing requires Wine or a Windows VM

### macOS Cross-Compilation from Linux
- Requires `osxcross` or similar toolchain
- Mach-O format differs significantly from ELF (no SHT_RELA, different symbol table format)
- macOS has stricter code signing requirements
- `-pagezero_size` and other macOS-specific linker flags may be needed
- Testing requires a macOS VM or hardware

### WebAssembly Cross-Compilation
- Not yet fully supported (WASM target kind exists but lacks emitter)
- Requires LLVM backend with `wasm32-unknown-unknown` triple
- Limited I/O capabilities
- No native linker; uses `wasm-ld` or `emcc`

### RISC-V Cross-Compilation
- Requires `riscv64-linux-gnu-gcc` toolchain
- RISC-V emitters are stubs and not yet production-ready
- QEMU support is mature for testing
- `-march=rv64gc` is the standard baseline for 64-bit RISC-V
