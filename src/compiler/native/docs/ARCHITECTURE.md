# Native Compiler Architecture

## Overview

The I language native compiler converts I source code into native machine code executables. It is organized as a multi-stage pipeline that progressively lowers high-level intermediate representations (IR) into target-specific machine code, object files, and linked executables.

The compiler is written in Python and supports three backend strategies: **LLVM** (external toolchain), **Cranelift** (via the `cranelift` Python package), and **Custom** (pure Python code generation for x86-64 and ARM64).

---

## Pipeline

```
Source Text
     |
     v
  Lexer / Parser / Semantic Analyzer / Type Checker
     |
     v
  IRModule (high-level IR)
     |
     v
  [NativeCompiler entry point]
     |
     v
  BackendManager: backend selection and dispatch
     |
     v
  +-----------+-----------+-----------+
  |  LLVM     |  Cranelift |  Custom   |
  |  backend  |  backend   |  backend  |
  +-----------+-----------+-----------+
     |
     v
  1. IR -> LIR lowering (ASTLowering)
  2. Legalization (type + operation legalization)
  3. Instruction Selection (LIR -> MachineIR)
  4. Register Allocation (graph coloring)
  5. Frame Layout (prologue/epilogue)
  6. Code Emission (raw bytes or LLVM IR text)
  7. Object File Generation (ELF/PE/Mach-O)
  8. Linking (system linker invocation)
     |
     v
  Executable / Object File
```

### Stage Details

**1. IR to LIR Lowering** (`ir_lower/`)
The high-level IRModule is lowered to a low-level LIR (LIRFunction, LIRBlock, LIRInstruction). This is performed by the `ASTLowering` component in `compiler.ir.lower`, which transforms the AST through the semantic analyzer into a linear instruction form.

**2. Legalization** (`ir_lower/legalizer.py`)
Before instruction selection, the `Legalizer` converts operations that the target cannot natively handle into equivalent legal sequences:
- i1 types are promoted to i8 (x86-64/ARM64 do not have 1-bit registers)
- Integer division/modulo on targets without hardware support is expanded
- i128 operations are split into pairs of i64 operations
- Target-specific legalization hooks exist for ARM64 and RISC-V

**3. Instruction Selection** (`ir_lower/selector.py`)
The `InstructionSelector` abstract base class maps LIR instructions to target-specific `MachineInst` sequences. Concrete implementations:
- `X86_64InstructionSelector` -- produces x86-64 machine instructions
- `ARM64InstructionSelector` -- produces ARM64 machine instructions

Pattern matching (`ir_lower/patterns.py`) provides a rule-based system where `MatchRule` objects declaratively map LIR opcodes to machine instruction sequences. Peephole optimization rules (e.g., `add 0` -> NOP, `mul 1` -> copy) are applied first.

The result is a `MachineFunction` containing `MachineBasicBlock`s of `MachineInst`s.

**4. Register Allocation** (`register/`)
The `GraphColoringAllocator` implements a Chaitin-Briggs-style graph coloring algorithm:
- `LiveRangeAnalysis` computes live intervals via dataflow analysis
- `InterferenceGraph` models register interference
- Coloring removes nodes with degree < K, then assigns colors
- Spill cost heuristics use loop nesting depth to prioritize
- `CoalescingOptimizer` applies Briggs and George criteria to eliminate copies
- `SpillManager` inserts spill/reload code with stack slot allocation

**5. Frame Layout** (`frame/manager.py`)
The `FrameManager` computes stack frame layouts:
- Local variable offsets
- Spill slot areas
- Callee-saved register save areas
- Shadow space (Windows x64: 32 bytes)
- Stack canary placement (optional)
- Red zone optimization (leaf functions on x86-64)
- Prologue/epilogue byte sequences

**6. Code Emission** (`emit/`)
- `x86_64.py`: `X86_64Emitter` -- raw x86-64 binary emission with full ModRM, SIB, REX prefix handling. Supports 64-bit integer and SSE2 floating-point instructions.
- `arm64.py`: `ARM64Emitter` -- ARM64 binary emission stub with basic arithmetic, memory, and control flow instructions.
- `llvm.py`: `LLVMEmitter` -- converts IRModule to textual LLVM IR (.ll format), then invokes `llc` to produce object files.

**7. Object File Generation** (`object/`)
- `elf.py`: `ELFWriter` -- ELF64 relocatable object files (x86-64 and ARM64)
- `pe.py`: `PEWriter` -- PE/COFF object files for Windows x64
- `macho.py`: `MachOWriter` -- Mach-O relocatable object files for macOS

**8. Linking** (`link/`)
The `SystemLinker` abstracts system linker invocation:
- Linux: `ld` or `gcc` frontend
- Windows: `link.exe` (MSVC)
- macOS: `ld` or `clang` frontend
- Supports executable, shared library, and object file output

---

## Backend Abstraction Layer

### BackendKinds

Defined in `backend/base.py`:

| BackendKind   | Description                                      |
|---------------|--------------------------------------------------|
| `LLVM`        | Emit LLVM IR then compile with `llc`             |
| `CRANELIFT`   | Use the `cranelift` Python package (if installed) |
| `CUSTOM_X86_64` | Pure Python x86-64 code generation             |
| `CUSTOM_ARM64`  | Pure Python ARM64 code generation              |

### Backend ABC (`backend/base.py`)

All backends implement the `Backend` abstract base class:

```python
class Backend(abc.ABC):
    @property
    def name(self) -> str: ...
    @property
    def kind(self) -> BackendKind: ...
    @property
    def capabilities(self) -> BackendCapabilities: ...
    def compile(self, module: IRModule) -> CompileResult: ...
    def compile_to_object(self, module, target, format) -> bytes: ...
    def compile_to_executable(self, module, target, output_path) -> Path: ...
```

### BackendCapabilities

Each backend advertises features via `BackendCapabilities`:
- CPU features (SSE2, AVX, NEON, SVE, etc.)
- Debug/profiling/LTO/PIC/PIE support
- Optimization level range (e.g., 0--3)
- Maximum vector width
- Preferred alignment
- Inline assembly, coverage, sanitizer support

### BackendRegistry (`backend/registry.py`)

Singleton registry mapping `BackendKind` to backend classes. Auto-detection priority:
1. LLVM (if `llc` or `opt` is on PATH)
2. Cranelift (if `cranelift` module imports successfully)
3. Custom x86-64 (on AMD64 hosts)
4. Custom ARM64 (on ARM64 hosts)

### BackendManager (`backend/manager.py`)

Orchestrates the full pipeline: selects backend, dispatches compilation, and returns results. Detects host target automatically via `platform.machine()`.

---

## Module Structure

```
native/
  compiler.py              # NativeCompiler entry point
  backend/
    base.py                # Backend ABC, BackendKind, BackendCapabilities
    registry.py            # BackendRegistry (singleton)
    manager.py             # BackendManager (orchestration)
  target/
    kind.py                # TargetKind enum (X86_64, ARM64, RISCV64, WASM32, etc.)
    desc.py                # TargetDescription dataclass
    platform.py            # Host platform detection
    x86_64.py              # X86_64Target, X86_64Registers, X86_64Features
    arm64.py               # ARM64Target, ARM64Registers, ARM64Features
  ir_lower/
    machine.py             # MachineOp, MachineInst, MachineBasicBlock,
                           # MachineFunction, MachineModule
    selector.py            # InstructionSelector, X86_64InstructionSelector,
                           # ARM64InstructionSelector
    legalizer.py           # Legalizer
    patterns.py            # PatternMatcher, MatchRule, pattern builders
  register/
    allocator.py           # GraphColoringAllocator, InterferenceGraph,
                           # RegisterClass, PhysicalRegister
    liveness.py            # LiveRangeAnalysis, LiveInterval
    spill.py               # SpillManager, StackSlot
    coalescing.py          # CoalescingOptimizer (Briggs/George)
  frame/
    manager.py             # FrameManager, StackFrame, FrameOptions
  emit/
    x86_64.py              # X86_64Emitter (raw binary)
    arm64.py               # ARM64Emitter (stub)
    llvm.py                # LLVMEmitter (textual IR)
  object/
    elf.py                 # ELFWriter
    pe.py                  # PEWriter (COFF)
    macho.py               # MachOWriter
  link/
    interface.py           # LinkerInterface, SystemLinker
    result.py              # CompileResult, OutputFormat
  calling/
    convention.py          # CallingConvention, SystemVConvention,
                           # MicrosoftConvention, ARM64Convention
```

---

## Key Design Decisions

### 1. Python as implementation language
The compiler is written in Python for rapid prototyping and ease of contribution. Performance-critical paths (code emission, register allocation) are carefully optimized using efficient data structures.

### 2. Three backend strategies
- **LLVM backend** leverages the mature LLVM optimization pipeline and code generator. It emits textual LLVM IR and invokes `llc`.
- **Cranelift backend** provides a fast, single-pass alternative suitable for JIT or debug builds.
- **Custom backends** (x86-64, ARM64) emit machine code directly in pure Python, eliminating external tool dependencies. This is the path for fully self-hosted compilation.

### 3. Machine IR as a middle layer
Between LIR and binary emission, `MachineIR` (`MachineInst`, `MachineBasicBlock`, `MachineFunction`) provides a target-specific but still abstract representation. This enables shared register allocation, frame layout, and optimization passes.

### 4. Rule-based instruction selection
The pattern matcher in `patterns.py` uses declarative `MatchRule` objects instead of a massive switch/if chain. This makes it easy to add new instructions, implement peephole optimizations, and retarget the compiler.

### 5. Chaitin-Briggs graph coloring
Register allocation uses an iterative graph coloring approach with:
- Briggs coalescing (conservative)
- George criterion as fallback
- Spill cost weighted by loop nesting depth (10^depth)
- Per-class allocation (GPR, XMM, Mask)

### 6. ABI abstraction
Calling conventions are abstracted behind `CallingConvention` ABC with concrete implementations for System V AMD64, Microsoft x64, and ARM64. The `FrameManager` automatically selects shadow space, alignment, and register save conventions based on the target.

### 7. Platform-independent object file generation
Object file writers for ELF, PE/COFF, and Mach-O share the same interface. Cross-compilation is supported by selecting the appropriate writer and machine type.

---

## Component Interactions

```
NativeCompiler
  |
  |-- BackendManager
  |     |-- BackendRegistry (selects backend)
  |     |-- Backend (LLVM | Cranelift | Custom)
  |           |
  |           |-- Legalizer (if applicable)
  |           |-- InstructionSelector (LIR -> MachineIR)
  |           |     |-- PatternMatcher (rule engine)
  |           |     |-- Legalizer (pre-selection legalization)
  |           |
  |           |-- GraphColoringAllocator
  |           |     |-- LiveRangeAnalysis
  |           |     |-- InterferenceGraph
  |           |     |-- CoalescingOptimizer
  |           |     |-- SpillManager
  |           |
  |           |-- FrameManager
  |           |
  |           |-- Emitter (X86_64Emitter | ARM64Emitter | LLVMEmitter)
  |           |
  |           |-- ObjectWriter (ELFWriter | PEWriter | MachOWriter)
  |
  |-- SystemLinker
        |-- LinuxLinker (ld / gcc)
        |-- WindowsLinker (link.exe)
        |-- macOSLinker (ld / clang)
```

The data flow is unidirectional: IR flows from left to right through the pipeline, with each stage producing input for the next. The `BackendManager` orchestrates this flow, while the `NativeCompiler` provides the top-level API.
