"""
Intermediate Representation (IR)

Multi-level IR for the I Programming Language compiler.
Three official IR levels:
  - HIR (High-Level IR): source-level semantics
  - MIR (Mid-Level IR): normalized for analysis, CFG-based
  - LIR (Low-Level IR): portable assembly for backends

Design principles:
- No optimizer logic inside IR
- No VM logic
- No machine-specific instructions
- Every instruction documented
- Every instruction tested
"""
from __future__ import annotations

# ══════════════════════════════════════════════════════════════════
# IR Types
# ══════════════════════════════════════════════════════════════════

from .types import (
    IRType, IRTypeKind,
    VoidType, LabelType, MetadataType, TokenType,
    IntegerType, FloatType, PointerType, ArrayType,
    StructType, IRFunctionType, VectorType,
    IR_VOID, IR_LABEL, IR_METADATA, IR_TOKEN,
    IR_I1, IR_I8, IR_I16, IR_I32, IR_I64, IR_I128,
    IR_F16, IR_F32, IR_F64, IR_F128, IR_PTR,
    int_type, float_type, ptr_type, array_type, struct_type,
    func_type, vec_type, get_element_type, get_pointer_depth,
    is_numeric_type, is_integer_type,
)

# ══════════════════════════════════════════════════════════════════
# IR Values
# ══════════════════════════════════════════════════════════════════

from .values import (
    Value, ValueKind, Constant,
    IntConstant, FloatConstant, BoolConstant, StringConstant,
    NullConstant, UndefinedConstant, PoisonConstant,
    ZeroConstant, AggregateConstant,
    Argument, GlobalVariable,
    make_int_constant, make_float_constant, make_bool_constant,
    make_string_constant, make_null_constant,
    is_constant,
)

# ══════════════════════════════════════════════════════════════════
# IR Metadata
# ══════════════════════════════════════════════════════════════════

from .metadata import (
    Metadata, MetadataKind, MetadataCollection,
    DebugLocation, SourceFile, VariableName,
    FunctionName, ModuleName, CustomMetadata,
    make_debug_location, make_source_file,
)

# ══════════════════════════════════════════════════════════════════
# IR Attributes
# ══════════════════════════════════════════════════════════════════

from .attributes import (
    Attribute, AttrKind, AttributeSet,
    attr_noreturn, attr_no_unwind, attr_readnone, attr_readonly,
    attr_writeonly, attr_noalias, attr_nocapture, attr_nonnull,
    attr_always_inline, attr_no_inline, attr_inline_hint,
    attr_optnone, attr_signext, attr_zeroext,
    attr_dereferenceable, attr_dereferenceable_or_null,
)

# ══════════════════════════════════════════════════════════════════
# IR Instructions
# ══════════════════════════════════════════════════════════════════

from .instructions import (
    Instruction, TerminatorInst, Opcode,
    ICmpPredicate, FCmpPredicate,
    # Terminators
    Branch, CondBranch, Switch, Return, Unreachable,
    # Arithmetic
    Add, Sub, Mul, SDiv, UDiv, SRem, URem,
    FAdd, FSub, FMul, FDiv, FRem,
    # Bitwise
    And, Or, Xor, Shl, LShr, AShr,
    # Unary
    Not, Neg, FNeg,
    # Comparison
    ICmp, FCmp,
    # Memory
    Alloca, Load, Store, GEP, MemCpy, MemSet,
    # Cast
    Trunc, ZExt, SExt, FPTrunc, FPExt,
    UIToFP, SIToFP, FPToUI, FPToSI,
    PtrToInt, IntToPtr, BitCast, AddrSpaceCast,
    # Control Flow
    Phi, Call, Invoke, LandingPad, Resume,
    # Aggregate
    ExtractValue, InsertValue,
    # Vector
    ExtractElement, InsertElement, ShuffleVector,
    # Atomic
    AtomicRMW, CmpXchg, Fence,
)

# ══════════════════════════════════════════════════════════════════
# IR Structure
# ══════════════════════════════════════════════════════════════════

from .basic_block import BasicBlock
from .function import IRFunction
from .module import IRModule, FunctionMap

# ══════════════════════════════════════════════════════════════════
# IR Construction
# ══════════════════════════════════════════════════════════════════

from .context import IRContext
from .builder import IRBuilder

# ══════════════════════════════════════════════════════════════════
# IR Utilities
# ══════════════════════════════════════════════════════════════════

from .validator import IRValidator, validate
from .printer import IRPrinter, print_ir
from .serialization import (
    IRSerializer, IRDeserializer, IR_FORMAT_VERSION,
    serialize_json, deserialize_json, serialize_text,
)
from .visualizer import IRVisualizer, visualize_cfg, visualize_call_graph, print_cfg

# ══════════════════════════════════════════════════════════════════
# CFG Analysis
# ══════════════════════════════════════════════════════════════════

from .cfg import CFG, LoopInfo

# ══════════════════════════════════════════════════════════════════
# SSA Utilities
# ══════════════════════════════════════════════════════════════════

from .ssa import (
    DefUseChain, LivenessInfo, LivenessAnalysis, SSABuilder,
)

# ══════════════════════════════════════════════════════════════════
# HIR — High-Level IR
# ══════════════════════════════════════════════════════════════════

from .hir import (
    HIRNode, HIRNodeKind, HIRModule, HIRFunctionDecl,
    HIRParameter, HIRClassDecl, HIRTraitDecl,
    HIRBlock, HIRStatement, HIRReturn, HIRIf, HIRWhile,
    HIREnumDecl, HIRInterfaceDecl, HIRVariable, HIRConstant,
    HIRAssignment, HIRFor, HIRForEach, HIRBreak, HIRContinue,
    HIRExpression, HIRMatch, HIRThrow, HIRTry,
    hir_to_ir_module,
)

# ══════════════════════════════════════════════════════════════════
# MIR — Mid-Level IR
# ══════════════════════════════════════════════════════════════════

from .mir import (
    OwnershipKind, OwnershipMeta,
    MIRFunction, MIRModule,
    MIRNormalizePass, split_critical_edges, compute_ownership,
    lower_to_mir, compute_mir_function,
)

# ══════════════════════════════════════════════════════════════════
# LIR — Low-Level IR
# ══════════════════════════════════════════════════════════════════

from .lir import (
    LIRInstKind, LIRInstruction, LIRBlock, LIRFunction,
    LIRModule, LIRPrinter, LIRBuilder,
    lower_ir_to_lir,
)


# ══════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════

__all__ = [
    # ── IR Types ─────────────────────────────────────────────
    'IRType', 'IRTypeKind',
    'VoidType', 'LabelType', 'MetadataType', 'TokenType',
    'IntegerType', 'FloatType', 'PointerType', 'ArrayType',
    'StructType', 'IRFunctionType', 'VectorType',
    'IR_VOID', 'IR_LABEL', 'IR_METADATA', 'IR_TOKEN',
    'IR_I1', 'IR_I8', 'IR_I16', 'IR_I32', 'IR_I64', 'IR_I128',
    'IR_F16', 'IR_F32', 'IR_F64', 'IR_F128', 'IR_PTR',
    'int_type', 'float_type', 'ptr_type', 'array_type',
    'struct_type', 'func_type', 'vec_type',
    'get_element_type', 'get_pointer_depth',
    'is_numeric_type', 'is_integer_type',

    # ── IR Values ────────────────────────────────────────────
    'Value', 'ValueKind', 'Constant',
    'IntConstant', 'FloatConstant', 'BoolConstant', 'StringConstant',
    'NullConstant', 'UndefinedConstant', 'PoisonConstant',
    'ZeroConstant', 'AggregateConstant',
    'Argument', 'GlobalVariable',
    'make_int_constant', 'make_float_constant', 'make_bool_constant',
    'make_string_constant', 'make_null_constant', 'is_constant',

    # ── IR Metadata ──────────────────────────────────────────
    'Metadata', 'MetadataKind', 'MetadataCollection',
    'DebugLocation', 'SourceFile', 'VariableName',
    'FunctionName', 'ModuleName', 'CustomMetadata',
    'make_debug_location', 'make_source_file',

    # ── IR Attributes ────────────────────────────────────────
    'Attribute', 'AttrKind', 'AttributeSet',
    'attr_noreturn', 'attr_no_unwind', 'attr_readnone', 'attr_readonly',
    'attr_writeonly', 'attr_noalias', 'attr_nocapture', 'attr_nonnull',
    'attr_always_inline', 'attr_no_inline', 'attr_inline_hint',
    'attr_optnone', 'attr_signext', 'attr_zeroext',

    # ── IR Instructions ──────────────────────────────────────
    'Instruction', 'TerminatorInst', 'Opcode',
    'ICmpPredicate', 'FCmpPredicate',
    'Branch', 'CondBranch', 'Switch', 'Return', 'Unreachable',
    'Add', 'Sub', 'Mul', 'SDiv', 'UDiv', 'SRem', 'URem',
    'FAdd', 'FSub', 'FMul', 'FDiv', 'FRem',
    'And', 'Or', 'Xor', 'Shl', 'LShr', 'AShr',
    'Not', 'Neg', 'FNeg',
    'ICmp', 'FCmp',
    'Alloca', 'Load', 'Store', 'GEP', 'MemCpy', 'MemSet',
    'Trunc', 'ZExt', 'SExt', 'FPTrunc', 'FPExt',
    'UIToFP', 'SIToFP', 'FPToUI', 'FPToSI',
    'PtrToInt', 'IntToPtr', 'BitCast', 'AddrSpaceCast',
    'Phi', 'Call', 'Invoke', 'LandingPad', 'Resume',
    'ExtractValue', 'InsertValue',
    'ExtractElement', 'InsertElement', 'ShuffleVector',
    'AtomicRMW', 'CmpXchg', 'Fence',

    # ── IR Structure ─────────────────────────────────────────
    'BasicBlock', 'IRFunction', 'IRModule', 'FunctionMap',

    # ── IR Construction ──────────────────────────────────────
    'IRContext', 'IRBuilder',

    # ── IR Utilities ─────────────────────────────────────────
    'IRValidator', 'validate',
    'IRPrinter', 'print_ir',
    'IRSerializer', 'IRDeserializer', 'IR_FORMAT_VERSION',
    'serialize_json', 'deserialize_json', 'serialize_text',
    'IRVisualizer', 'visualize_cfg', 'visualize_call_graph', 'print_cfg',

    # ── CFG Analysis ─────────────────────────────────────────
    'CFG', 'LoopInfo',

    # ── SSA Utilities ────────────────────────────────────────
    'DefUseChain', 'LivenessInfo', 'LivenessAnalysis', 'SSABuilder',

    # ── HIR ──────────────────────────────────────────────────
    'HIRNode', 'HIRNodeKind', 'HIRModule', 'HIRFunctionDecl',
    'HIRParameter', 'HIRClassDecl', 'HIRTraitDecl',
    'HIRBlock', 'HIRStatement', 'HIRReturn', 'HIRIf', 'HIRWhile',
    'HIREnumDecl', 'HIRInterfaceDecl', 'HIRVariable', 'HIRConstant',
    'HIRAssignment', 'HIRFor', 'HIRForEach', 'HIRBreak', 'HIRContinue',
    'HIRExpression', 'HIRMatch', 'HIRThrow', 'HIRTry',
    'hir_to_ir_module',

    # ── MIR ──────────────────────────────────────────────────
    'OwnershipKind', 'OwnershipMeta',
    'MIRFunction', 'MIRModule',
    'MIRNormalizePass', 'split_critical_edges', 'compute_ownership',
    'lower_to_mir', 'compute_mir_function',

    # ── LIR ──────────────────────────────────────────────────
    'LIRInstKind', 'LIRInstruction', 'LIRBlock', 'LIRFunction',
    'LIRModule', 'LIRPrinter', 'LIRBuilder',
    'lower_ir_to_lir',
]
