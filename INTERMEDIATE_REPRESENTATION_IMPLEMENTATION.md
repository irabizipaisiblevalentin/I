# Intermediate Representation (IR) Implementation

## Overview

The I Programming Language compiler uses a multi-level Intermediate Representation (IR) system designed for analysis, optimization, and code generation. The IR is purely representational with no optimizer or VM logic embedded within it.

## Architecture

### Three IR Levels

1. **HIR (High-Level IR)**: Preserves source-level semantics including functions, classes, traits, enums, pattern matching, and exceptions.
2. **MIR (Mid-Level IR)**: Normalized representation ideal for analysis with CFG, dominator trees, loop detection, and ownership metadata.
3. **LIR (Low-Level IR)**: Portable assembly representation for backend code generation.

## Core Components

### IR Types (`types.py`)
- Primitive types: `VoidType`, `IntegerType`, `FloatType`, `PointerType`
- Compound types: `ArrayType`, `StructType`, `IRFunctionType`, `VectorType`
- Type constructors: `int_type()`, `float_type()`, `ptr_type()`, `array_type()`, `struct_type()`, `func_type()`, `vec_type()`

### IR Values (`values.py`)
- Constants: `IntConstant`, `FloatConstant`, `BoolConstant`, `StringConstant`, `NullConstant`, `UndefinedConstant`, `PoisonConstant`, `ZeroConstant`, `AggregateConstant`
- Mutable values: `Argument`, `GlobalVariable`
- Factory functions: `make_int_constant()`, `make_float_constant()`, `make_bool_constant()`, `make_string_constant()`, `make_null_constant()`

### IR Instructions (`instructions.py`)
- **Terminators**: `Branch`, `CondBranch`, `Switch`, `Return`, `Unreachable`
- **Arithmetic**: `Add`, `Sub`, `Mul`, `SDiv`, `UDiv`, `SRem`, `URem`, `FAdd`, `FSub`, `FMul`, `FDiv`, `FRem`
- **Bitwise**: `And`, `Or`, `Xor`, `Shl`, `LShr`, `AShr`
- **Unary**: `Not`, `Neg`, `FNeg`
- **Comparison**: `ICmp`, `FCmp` with predicates
- **Memory**: `Alloca`, `Load`, `Store`, `GEP`, `MemCpy`, `MemSet`
- **Cast**: `Trunc`, `ZExt`, `SExt`, `FPTrunc`, `FPExt`, `UIToFP`, `SIToFP`, `FPToUI`, `FPToSI`, `PtrToInt`, `IntToPtr`, `BitCast`, `AddrSpaceCast`
- **Control Flow**: `Phi`, `Call`, `Invoke`, `LandingPad`, `Resume`
- **Aggregate**: `ExtractValue`, `InsertValue`
- **Vector**: `ExtractElement`, `InsertElement`, `ShuffleVector`
- **Atomic**: `AtomicRMW`, `CmpXchg`, `Fence`

### IR Structure
- **BasicBlock** (`basic_block.py`): Sequence of instructions with terminators
- **IRFunction** (`function.py`): Collection of basic blocks with arguments and return type
- **IRModule** (`module.py`): Top-level container with functions, globals, and metadata
- **FunctionMap** (`module.py`): Dual-access collection supporting both dict-like and list-like access

### IR Construction
- **IRContext** (`context.py`): Type and constant uniquing
- **IRBuilder** (`builder.py`): Fluent API for constructing IR instructions

### IR Utilities
- **IRValidator** (`validator.py`): Validates IR structural and type correctness
- **IRPrinter** (`printer.py`): Human-readable IR text output
- **IRSerializer** (`serialization.py`): JSON and binary serialization/deserialization
- **IRVisualizer** (`visualizer.py`): CFG and call graph visualization

## Analysis Passes

### CFG Analysis (`cfg.py`)
- Dominator tree computation
- Post-dominator tree computation
- Loop detection via back-edge analysis
- Critical edge identification
- Dominance frontier computation

### SSA Construction (`ssa.py`)
- Def-use chain construction
- Liveness analysis
- SSA form with phi insertion (Cytron et al.)

## HIR Components (`hir.py`)

High-level nodes preserving source semantics:
- `HIRModule`, `HIRFunctionDecl`, `HIRParameter`
- `HIRClassDecl`, `HIRTraitDecl`, `HIREnumDecl`, `HIRInterfaceDecl`
- `HIRBlock`, `HIRStatement`, `HIRReturn`, `HIRIf`, `HIRWhile`
- `HIRVariable`, `HIRConstant`, `HIRAssignment`
- `HIRFor`, `HIRForEach`, `HIRBreak`, `HIRContinue`
- `HIRMatch`, `HIRThrow`, `HIRTry`
- `hir_to_ir_module()` for lowering HIR to IR

## MIR Components (`mir.py`)

Mid-level analysis representation:
- `MIRFunction`: Wraps IRFunction with analysis results
- `MIRModule`: Provides global analysis views
- `OwnershipKind`/`OwnershipMeta`: Ownership metadata for values
- `MIRNormalizePass`: Normalizes IR for analysis
- `split_critical_edges()`: Critical edge splitting
- `compute_ownership()`: Ownership computation

## LIR Components (`lir.py`)

Low-level portable assembly:
- `LIRInstruction`: Low-level instruction representation
- `LIRBlock`: Basic block with phi and phi_args support
- `LIRFunction`: Function with local variables and target info
- `LIRModule`: Module container
- `LIRBuilder`: Builder for LIR instructions
- `lower_ir_to_lir()`: IR to LIR lowering

## Usage Examples

### Building IR
```python
from compiler.ir import IRContext, IRBuilder, IRModule, IRFunction
from compiler.ir import IRFunctionType, IR_I32, IR_VOID

ctx = IRContext()
builder = IRBuilder(ctx)
module = IRModule("example")

func_type = IRFunctionType([IR_I32], IR_I32)
func = IRFunction("double", func_type)
module.add_function(func)

entry = builder.create_block("entry")
func.append_block(entry)
builder.position_at_end(entry)

param = func.args[0]
result = builder.add(param, param)
builder.ret(result)
```

### Analysis
```python
from compiler.ir import CFG, SSABuilder, LivenessAnalysis

cfg = CFG(func)
print(f"Loops: {len(cfg.loops)}")
print(f"Blocks: {len(cfg.blocks)}")

ssa = SSABuilder(func)
liveness = LivenessAnalysis(cfg)
```

### Serialization
```python
from compiler.ir import serialize_json, deserialize_json

json_str = serialize_json(module)
restored = deserialize_json(json_str)
```

## Design Principles

1. **No optimizer logic** inside IR
2. **No VM logic** inside IR
3. **No machine-specific instructions** in core IR
4. **Immutable value objects** using `object.__setattr__`
5. **Structural equality** for types and instructions
6. **Every instruction documented**
7. **Every instruction tested**

## Testing

All IR components are tested in `tests/unit/test_ir_sprint6.py` with 233 tests covering:
- Type construction and equality
- Value creation and constants
- Instruction construction and properties
- Builder operations
- CFG analysis
- SSA construction
- Serialization round-trips
- Validation
- Fuzz testing for edge cases
