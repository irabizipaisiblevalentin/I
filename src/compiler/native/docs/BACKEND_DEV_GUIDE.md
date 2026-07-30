# Backend Developer Guide

This guide explains how to add a new code generation backend to the I native compiler.

---

## How to Add a New Backend

Adding a new backend requires implementing the `Backend` abstract base class, registering it, and providing the necessary instruction selection, code emission, and object file generation components.

### Steps

1. **Define a `BackendKind`** -- Add a new member to the `BackendKind` enum in `backend/base.py`.

2. **Implement the `Backend` ABC** -- Create a new file in `backend/` (e.g., `backend/riscv64.py`) that subclasses `Backend` and implements all abstract methods.

3. **Implement instruction selection** -- Either extend `InstructionSelector` in `ir_lower/selector.py` or create a new selector. Build pattern rules using `PatternMatcher` in `ir_lower/patterns.py`.

4. **Implement code emission** -- Create an emitter class (like `X86_64Emitter` or `ARM64Emitter`) in `emit/` that produces raw machine code bytes.

5. **Implement object file writing** -- Use or extend the existing `ELFWriter`, `PEWriter`, or `MachOWriter` in `object/` as appropriate for the target.

6. **Register the backend** -- In the initialization code or via `BackendRegistry.register()`, associate the `BackendKind` with the new backend class.

7. **Wire up detection** -- Update `BackendRegistry.detect_best_backend()` to auto-detect the new backend when appropriate.

---

## Implementing the Backend ABC

The `Backend` class in `backend/base.py` defines three abstract methods and three abstract properties:

```python
from compiler.native.backend.base import Backend, BackendKind, BackendCapabilities

class MyBackend(Backend):
    @property
    def name(self) -> str:
        return "my_backend"

    @property
    def kind(self) -> BackendKind:
        return BackendKind.MY_BACKEND

    @property
    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            features=frozenset(),
            supports_debug=False,
            supports_optimization_levels=(0, 2),
            max_vector_width=128,
            preferred_alignment=16,
        )

    def compile(self, module: IRModule) -> CompileResult:
        # Full compilation pipeline
        ...

    def compile_to_object(self, module, target, format="elf") -> bytes:
        # Compile to object file bytes
        ...

    def compile_to_executable(self, module, target, output_path) -> Path:
        # Compile and link
        ...
```

### Typical `compile_to_object` Implementation Pattern

```python
def compile_to_object(self, module: IRModule, target, format="elf") -> bytes:
    # 1. Lower IRModule to LIR functions
    lir_funcs = lower_ir_to_lir(module)

    # 2. Legalize for target
    legalizer = Legalizer(target.kind)
    lir_funcs = [legalizer.legalize_function(f) for f in lir_funcs]

    # 3. Instruction selection: LIR -> MachineIR
    selector = MyInstructionSelector()
    machine_mod = selector.select_module(lir_funcs)

    # 4. Register allocation
    allocator = GraphColoringAllocator()
    for func in machine_mod.functions:
        alloc_result = allocator.allocate(func, target)

    # 5. Frame layout
    frame_mgr = FrameManager()
    for func in machine_mod.functions:
        frame = frame_mgr.allocate_frame(func, target)

    # 6. Code emission
    emitter = MyEmitter()
    code_bytes = emitter.emit(machine_mod)

    # 7. Object file packaging
    writer = ELFWriter.for_target(target)
    return writer.write_object(
        sections={".text": code_bytes},
        symbols={...},
        relocations=[],
    )
```

---

## Register Description Requirements

Register allocation requires describing the target's register file. Define `PhysicalRegister` objects in `register/allocator.py`:

```python
from compiler.native.register.allocator import (
    PhysicalRegister, RegisterClass
)

# Register classes
class RegisterClass(Enum):
    GPR = "gpr"      # General-purpose registers
    XMM = "xmm"      # Floating-point/SIMD registers
    MASK = "mask"    # AVX-512 mask registers

# Physical register description
PhysRegister = PhysicalRegister(
    name="x0",           # Register name
    reg_class=RegisterClass.GPR,  # Register class
    is_caller_save=True, # Caller-saved (scratch) vs callee-saved
    index=0,             # Physical index for coloring
)
```

For a new target, provide a list of available registers and implement `register_class_for()` to map IR value types to register classes. The target description in `target/` should also expose register information via a `Registers` class:

```python
class MyTargetRegisters:
    GPR: tuple[str, ...] = ("r0", "r1", "r2", ...)
    FPR: tuple[str, ...] = ("f0", "f1", ...)

    @classmethod
    def caller_saved(cls) -> tuple[str, ...]: ...
    @classmethod
    def callee_saved(cls) -> tuple[str, ...]: ...
    @classmethod
    def arg_registers(cls) -> tuple[str, ...]: ...
```

---

## Instruction Selection Patterns

Instruction selection uses a rule-based pattern matcher in `ir_lower/patterns.py`.

### Defining Rules

```python
from compiler.native.ir_lower.patterns import (
    PatternMatcher, MatchPattern, MatchRule
)

matcher = PatternMatcher()

# Simple direct mapping
matcher.add_rule(MatchRule(
    name="my_add",
    pattern=MatchPattern(LIRInstKind.IADD),
    emitter=lambda ops, dest, ctx: [
        MachineInst(MachineOp.MY_ADD, [
            MachineOperand.reg(dest),
            MachineOperand.reg(ops[0]),
            MachineOperand.reg(ops[1]),
        ])
    ],
))
```

### Peephole Optimizations

Peephole rules are tried before normal rules:

```python
matcher.add_peephole_rule(MatchRule(
    name="add_zero",
    pattern=MatchPattern(
        LIRInstKind.IADD,
        operand_predicate=lambda ops, d, c: ops[1] == "0",
    ),
    emitter=_emit_nop,
    is_peephole=True,
))
```

### Pattern Predicates

Predicates allow conditional matching based on operands, destination, or context:

```python
def _is_immediate(operands, dest, ctx) -> bool:
    """Check if first operand is a numeric immediate."""
    try:
        int(operands[0])
        return True
    except ValueError:
        return False
```

### Building a Complete Pattern Set

Create a function that returns a fully configured `PatternMatcher`:

```python
def build_my_target_patterns() -> PatternMatcher:
    matcher = PatternMatcher()
    _add_alu_rules(matcher, MyOp.ADD, MyOp.SUB, MyOp.MUL)
    _add_bitwise_rules(matcher, MyOp.AND, MyOp.OR, MyOp.XOR)
    _add_shift_rules(matcher, MyOp.SHL, MyOp.SHR, MyOp.SAR)
    _add_load_store_rules(matcher)
    _add_control_flow_rules(matcher)
    _add_peephole_rules(matcher)
    return matcher
```

---

## Testing a New Backend

### Unit Tests

Create tests in `tests/` that verify each stage of the pipeline:

```python
def test_my_backend_instruction_selection():
    selector = MyInstructionSelector()
    lir_func = make_test_lir_function()
    mfunc = selector.select(lir_func)
    assert mfunc is not None
    assert mfunc.instruction_count > 0

def test_my_backend_code_emission():
    emitter = MyEmitter()
    mfunc = make_test_machine_function()
    code = emitter.emit(mfunc)
    assert len(code) > 0
    # Verify expected instruction bytes
    assert code[:4] == b"\x00\x01\x02\x03"
```

### Integration Tests

```python
def test_my_backend_compile_to_object():
    backend = MyBackend()
    module = make_test_ir_module()
    obj = backend.compile_to_object(module, target=TargetKind.MY_TARGET)
    assert obj.startswith(ELF_MAGIC)  # or PE/Mach-O magic
```

### End-to-End Tests

```python
def test_my_backend_executable():
    compiler = NativeCompiler()
    result = compiler.compile(
        source='export fn main() -> int { return 42; }',
        target=TargetKind.MY_TARGET,
        backend=BackendKind.MY_BACKEND,
    )
    assert result.success
    assert result.output_path.exists()
```

### Running Tests

```bash
# Run all native compiler tests
python -m pytest src/compiler/native/tests/

# Run backend-specific tests
python -m pytest src/compiler/native/tests/test_my_backend.py
```

---

## Example: Adding a Minimal RISC-V Backend

This example walks through the key files to create for a RISC-V backend.

### 1. Add BackendKind (`backend/base.py`)

```python
class BackendKind(Enum):
    LLVM = "llvm"
    CRANELIFT = "cranelift"
    CUSTOM_X86_64 = "custom_x86_64"
    CUSTOM_ARM64 = "custom_arm64"
    CUSTOM_RISCV64 = "custom_riscv64"  # NEW
```

### 2. Create Target Description (`target/riscv64.py`)

```python
class RISCV64Registers:
    GPR: tuple[str, ...] = (
        "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2",
        "s0", "s1", "a0", "a1", "a2", "a3", "a4", "a5",
        "a6", "a7", "s2", "s3", "s4", "s5", "s6", "s7",
        "s8", "s9", "s10", "s11", "t3", "t4", "t5", "t6",
    )
    _ARG_GPR: tuple[str, ...] = ("a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7")
    _CALLEE_SAVED: tuple[str, ...] = ("s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11")
```

### 3. Create Instruction Selector

```python
class RISCV64InstructionSelector(InstructionSelector):
    def _build_patterns(self) -> PatternMatcher:
        return build_riscv64_patterns()

    def _lower_instruction(self, inst, block, func, ctx):
        # Map LIR opcodes to RISC-V machine instructions
        if kind == LIRInstKind.IADD:
            return [MachineInst(MachineOp.RV_ADD, [
                MachineOperand.reg(dest),
                MachineOperand.reg(ops[0]),
                MachineOperand.reg(ops[1]),
            ])]
        if kind == LIRInstKind.LOAD_CONST:
            return [MachineInst(MachineOp.RV_LI, [
                MachineOperand.reg(dest),
                MachineOperand.imm(int(ops[0])),
            ])]
        ...
```

### 4. Create Binary Emitter (`emit/riscv64.py`)

```python
class RISCV64Emitter:
    def __init__(self):
        self._buffer = bytearray()

    def emit_add(self, rd: int, rs1: int, rs2: int) -> bytes:
        # R-type: opcode=0x33, funct3=0, funct7=0
        insn = 0x00000033 | (rd & 0x1F) | ((rs1 & 0x1F) << 15) | ((rs2 & 0x1F) << 20)
        self._buffer.extend(struct.pack("<I", insn))
        return bytes(self._buffer[-4:])
```

### 5. Register and Test

```python
# In initialization code:
registry = BackendRegistry()
registry.register(BackendKind.CUSTOM_RISCV64, RISCV64Backend)

# Test:
compiler = NativeCompiler(registry=registry)
result = compiler.compile("export fn add(a: int, b: int) -> int { return a + b; }",
                           target=TargetKind.RISCV64,
                           backend=BackendKind.CUSTOM_RISCV64)
```
