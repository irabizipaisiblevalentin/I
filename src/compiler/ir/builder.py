"""
IR Builder

Fluent API for constructing IR instructions. Positions the builder
at a specific block/instruction and inserts new instructions there.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .types import IRType, IRVoid, IR_I1, IR_I32, IR_I64
from .values import Value, Constant, IntConstant, FloatConstant, BoolConstant
from .instructions import (
    Instruction, TerminatorInst, Opcode,
    Add, Sub, Mul, SDiv, UDiv, SRem, URem,
    FAdd, FSub, FMul, FDiv, FRem,
    And, Or, Xor, Shl, LShr, AShr,
    Not, Neg, FNeg,
    ICmp, FCmp, ICmpPredicate, FCmpPredicate,
    Alloca, Load, Store, GEP,
    Branch, CondBranch, Switch, Return, Unreachable,
    Phi, Call, Invoke, LandingPad, Resume,
    Trunc, ZExt, SExt, FPTrunc, FPExt,
    UIToFP, SIToFP, FPToUI, FPToSI,
    PtrToInt, IntToPtr, BitCast, AddrSpaceCast,
    ExtractValue, InsertValue,
    ExtractElement, InsertElement, ShuffleVector,
    MemCpy, MemSet,
    AtomicRMW, CmpXchg, Fence,
)
from .basic_block import BasicBlock
from .function import IRFunction
from .context import IRContext
from .metadata import DebugLocation

if TYPE_CHECKING:
    from typing import List, Tuple


# ══════════════════════════════════════════════════════════════════
# IR Builder
# ══════════════════════════════════════════════════════════════════


class IRBuilder:
    """Fluent API for constructing IR instructions."""
    __slots__ = ("_context", "_block", "_insert_before", "_dbg_loc")

    def __init__(self, context: Optional[IRContext] = None) -> None:
        object.__setattr__(self, "_context", context or IRContext())
        object.__setattr__(self, "_block", None)
        object.__setattr__(self, "_insert_before", None)
        object.__setattr__(self, "_dbg_loc", None)

    # ── Positioning ──────────────────────────────────────────────

    def position_at(self, block: BasicBlock, insert_before: Optional[Instruction] = None) -> None:
        """Position the builder at a specific block."""
        object.__setattr__(self, "_block", block)
        object.__setattr__(self, "_insert_before", insert_before)

    def position_at_end(self, block: BasicBlock) -> None:
        """Position the builder at the end of a block."""
        object.__setattr__(self, "_block", block)
        object.__setattr__(self, "_insert_before", None)

    def position_before(self, instruction: Instruction) -> None:
        """Position the builder before a specific instruction."""
        object.__setattr__(self, "_block", instruction.parent)
        object.__setattr__(self, "_insert_before", instruction)

    @property
    def block(self) -> Optional[BasicBlock]:
        return self._block

    # ── Debug Location ───────────────────────────────────────────

    def set_debug_location(self, loc: Optional[DebugLocation]) -> None:
        """Set the current debug location for new instructions."""
        object.__setattr__(self, "_dbg_loc", loc)

    # ── Insert ───────────────────────────────────────────────────

    def _insert(self, instruction: Instruction) -> Instruction:
        """Insert the instruction at the current position."""
        if self._block is None:
            raise RuntimeError("IRBuilder: no block positioned")
        if self._dbg_loc and not instruction.dbg_location:
            instruction.dbg_location = self._dbg_loc
        if self._insert_before:
            self._block.insert_before(self._insert_before, instruction)
        else:
            self._block.append(instruction)
        return instruction

    # ── Terminators ──────────────────────────────────────────────

    def branch(self, target: BasicBlock) -> Branch:
        """Unconditional branch."""
        inst = Branch(target)
        self._block.add_successor(target)
        target.add_predecessor(self._block)
        return self._insert(inst)

    def cond_branch(
        self,
        condition: Value,
        true_block: BasicBlock,
        false_block: BasicBlock,
    ) -> CondBranch:
        """Conditional branch."""
        inst = CondBranch(condition, true_block, false_block)
        self._block.add_successor(true_block)
        self._block.add_successor(false_block)
        true_block.add_predecessor(self._block)
        false_block.add_predecessor(self._block)
        return self._insert(inst)

    def switch(
        self,
        value: Value,
        default: BasicBlock,
        cases: Optional[List[Tuple[Constant, BasicBlock]]] = None,
    ) -> Switch:
        cases = cases or []
        inst = Switch(value, default, cases)
        self._block.add_successor(default)
        default.add_predecessor(self._block)
        for _, case_block in cases:
            self._block.add_successor(case_block)
            case_block.add_predecessor(self._block)
        return self._insert(inst)

    def ret(self, value: Optional[Value] = None) -> Return:
        """Return instruction."""
        inst = Return(value)
        return self._insert(inst)

    def unreachable(self) -> Unreachable:
        """Unreachable."""
        return self._insert(Unreachable())

    # ── Binary Arithmetic ────────────────────────────────────────

    def add(self, lhs: Value, rhs: Value, name: str = "") -> Add:
        n = name or self._context.unique_name("add")
        return self._insert(Add(n, lhs, rhs))

    def sub(self, lhs: Value, rhs: Value, name: str = "") -> Sub:
        n = name or self._context.unique_name("sub")
        return self._insert(Sub(n, lhs, rhs))

    def mul(self, lhs: Value, rhs: Value, name: str = "") -> Mul:
        n = name or self._context.unique_name("mul")
        return self._insert(Mul(n, lhs, rhs))

    def sdiv(self, lhs: Value, rhs: Value, name: str = "") -> SDiv:
        n = name or self._context.unique_name("sdiv")
        return self._insert(SDiv(n, lhs, rhs))

    def udiv(self, lhs: Value, rhs: Value, name: str = "") -> UDiv:
        n = name or self._context.unique_name("udiv")
        return self._insert(UDiv(n, lhs, rhs))

    def srem(self, lhs: Value, rhs: Value, name: str = "") -> SRem:
        n = name or self._context.unique_name("srem")
        return self._insert(SRem(n, lhs, rhs))

    def urem(self, lhs: Value, rhs: Value, name: str = "") -> URem:
        n = name or self._context.unique_name("urem")
        return self._insert(URem(n, lhs, rhs))

    def fadd(self, lhs: Value, rhs: Value, name: str = "") -> FAdd:
        n = name or self._context.unique_name("fadd")
        return self._insert(FAdd(n, lhs, rhs))

    def fsub(self, lhs: Value, rhs: Value, name: str = "") -> FSub:
        n = name or self._context.unique_name("fsub")
        return self._insert(FSub(n, lhs, rhs))

    def fmul(self, lhs: Value, rhs: Value, name: str = "") -> FMul:
        n = name or self._context.unique_name("fmul")
        return self._insert(FMul(n, lhs, rhs))

    def fdiv(self, lhs: Value, rhs: Value, name: str = "") -> FDiv:
        n = name or self._context.unique_name("fdiv")
        return self._insert(FDiv(n, lhs, rhs))

    def frem(self, lhs: Value, rhs: Value, name: str = "") -> FRem:
        n = name or self._context.unique_name("frem")
        return self._insert(FRem(n, lhs, rhs))

    # ── Bitwise ──────────────────────────────────────────────────

    def and_(self, lhs: Value, rhs: Value, name: str = "") -> And:
        n = name or self._context.unique_name("and")
        return self._insert(And(n, lhs, rhs))

    def or_(self, lhs: Value, rhs: Value, name: str = "") -> Or:
        n = name or self._context.unique_name("or")
        return self._insert(Or(n, lhs, rhs))

    def xor(self, lhs: Value, rhs: Value, name: str = "") -> Xor:
        n = name or self._context.unique_name("xor")
        return self._insert(Xor(n, lhs, rhs))

    def shl(self, lhs: Value, rhs: Value, name: str = "") -> Shl:
        n = name or self._context.unique_name("shl")
        return self._insert(Shl(n, lhs, rhs))

    def lshr(self, lhs: Value, rhs: Value, name: str = "") -> LShr:
        n = name or self._context.unique_name("lshr")
        return self._insert(LShr(n, lhs, rhs))

    def ashr(self, lhs: Value, rhs: Value, name: str = "") -> AShr:
        n = name or self._context.unique_name("ashr")
        return self._insert(AShr(n, lhs, rhs))

    # ── Unary ────────────────────────────────────────────────────

    def not_(self, operand: Value, name: str = "") -> Not:
        n = name or self._context.unique_name("not")
        return self._insert(Not(n, operand))

    def neg(self, operand: Value, name: str = "") -> Neg:
        n = name or self._context.unique_name("neg")
        return self._insert(Neg(n, operand))

    def fneg(self, operand: Value, name: str = "") -> FNeg:
        n = name or self._context.unique_name("fneg")
        return self._insert(FNeg(n, operand))

    # ── Comparison ───────────────────────────────────────────────

    def icmp(self, pred: ICmpPredicate, lhs: Value, rhs: Value,
             name: str = "") -> ICmp:
        n = name or self._context.unique_name("cmp")
        return self._insert(ICmp(n, pred, lhs, rhs))

    def fcmp(self, pred: FCmpPredicate, lhs: Value, rhs: Value,
             name: str = "") -> FCmp:
        n = name or self._context.unique_name("cmp")
        return self._insert(FCmp(n, pred, lhs, rhs))

    # ── Memory ───────────────────────────────────────────────────

    def alloca(self, typ: IRType, name: str = "",
               alignment: int = 0) -> Alloca:
        n = name or self._context.unique_name("alloca")
        return self._insert(Alloca(n, typ, alignment=alignment))

    def load(self, typ: IRType, pointer: Value, name: str = "",
             alignment: int = 0) -> Load:
        n = name or self._context.unique_name("load")
        return self._insert(Load(n, typ, pointer, alignment=alignment))

    def store(self, value: Value, pointer: Value,
              alignment: int = 0) -> Store:
        return self._insert(Store(value, pointer, alignment=alignment))

    def gep(self, source_type: IRType, pointer: Value,
            indices: List[Value], name: str = "",
            in_bounds: bool = False) -> GEP:
        n = name or self._context.unique_name("gep")
        return self._insert(GEP(n, source_type, pointer, indices, in_bounds))

    def memcpy(self, dest: Value, src: Value, length: Value,
               is_volatile: bool = False) -> MemCpy:
        return self._insert(MemCpy(dest, src, length, is_volatile))

    def memset(self, dest: Value, value: Value, length: Value,
               is_volatile: bool = False) -> MemSet:
        return self._insert(MemSet(dest, value, length, is_volatile))

    # ── Cast ─────────────────────────────────────────────────────

    def trunc(self, value: Value, dest_type: IRType, name: str = "") -> Trunc:
        n = name or self._context.unique_name("trunc")
        return self._insert(Trunc(n, value, dest_type))

    def zext(self, value: Value, dest_type: IRType, name: str = "") -> ZExt:
        n = name or self._context.unique_name("zext")
        return self._insert(ZExt(n, value, dest_type))

    def sext(self, value: Value, dest_type: IRType, name: str = "") -> SExt:
        n = name or self._context.unique_name("sext")
        return self._insert(SExt(n, value, dest_type))

    def bitcast(self, value: Value, dest_type: IRType, name: str = "") -> BitCast:
        n = name or self._context.unique_name("bitcast")
        return self._insert(BitCast(n, value, dest_type))

    def fptrunc(self, value: Value, dest_type: IRType, name: str = "") -> FPTrunc:
        n = name or self._context.unique_name("fptrunc")
        return self._insert(FPTrunc(n, value, dest_type))

    def fpext(self, value: Value, dest_type: IRType, name: str = "") -> FPExt:
        n = name or self._context.unique_name("fpext")
        return self._insert(FPExt(n, value, dest_type))

    def uitofp(self, value: Value, dest_type: IRType, name: str = "") -> UIToFP:
        n = name or self._context.unique_name("uitofp")
        return self._insert(UIToFP(n, value, dest_type))

    def sitofp(self, value: Value, dest_type: IRType, name: str = "") -> SIToFP:
        n = name or self._context.unique_name("sitofp")
        return self._insert(SIToFP(n, value, dest_type))

    def fptoui(self, value: Value, dest_type: IRType, name: str = "") -> FPToUI:
        n = name or self._context.unique_name("fptoui")
        return self._insert(FPToUI(n, value, dest_type))

    def fptosi(self, value: Value, dest_type: IRType, name: str = "") -> FPToSI:
        n = name or self._context.unique_name("fptosi")
        return self._insert(FPToSI(n, value, dest_type))

    def ptrtoint(self, value: Value, dest_type: IRType, name: str = "") -> PtrToInt:
        n = name or self._context.unique_name("ptrtoint")
        return self._insert(PtrToInt(n, value, dest_type))

    def inttoptr(self, value: Value, dest_type: IRType, name: str = "") -> IntToPtr:
        n = name or self._context.unique_name("inttoptr")
        return self._insert(IntToPtr(n, value, dest_type))

    def addrspace_cast(self, value: Value, dest_type: IRType, name: str = "") -> AddrSpaceCast:
        n = name or self._context.unique_name("addrspacecast")
        return self._insert(AddrSpaceCast(n, value, dest_type))

    # ── Control Flow ─────────────────────────────────────────────

    def phi(self, typ: IRType, name: str = "",
            incoming: Optional[List[Tuple[Value, BasicBlock]]] = None) -> Phi:
        n = name or self._context.unique_name("phi")
        return self._insert(Phi(n, typ, incoming))

    def call(self, func_type: 'IRFunctionType', function: Value,
             arguments: Optional[List[Value]] = None,
             name: str = "") -> Call:
        from .types import IRFunctionType
        n = name or self._context.unique_name("call")
        return self._insert(Call(n, func_type, function, arguments))

    def invoke(
        self,
        name: str,
        func_type: 'IRFunctionType',
        function: Value,
        arguments: List[Value],
        normal_block: BasicBlock,
        unwind_block: BasicBlock,
    ) -> Invoke:
        from .types import IRFunctionType
        n = name or self._context.unique_name("invoke")
        inst = Invoke(n, func_type, function, arguments, normal_block, unwind_block)
        self._block.add_successor(normal_block)
        self._block.add_successor(unwind_block)
        normal_block.add_predecessor(self._block)
        unwind_block.add_predecessor(self._block)
        return self._insert(inst)

    def landing_pad(
        self,
        name: str,
        result_type: IRType,
        catch_types: Optional[List[Value]] = None,
        cleanup: bool = False,
    ) -> LandingPad:
        n = name or self._context.unique_name("lpad")
        return self._insert(LandingPad(n, result_type, catch_types, cleanup))

    def resume(self, value: Value) -> Resume:
        return self._insert(Resume(value))

    # ── Aggregate ────────────────────────────────────────────────

    def extract_value(self, aggregate: Value, indices: List[int],
                      name: str = "") -> ExtractValue:
        n = name or self._context.unique_name("extractval")
        return self._insert(ExtractValue(n, aggregate, indices))

    def insert_value(self, aggregate: Value, element: Value,
                     indices: List[int], name: str = "") -> InsertValue:
        n = name or self._context.unique_name("insertval")
        return self._insert(InsertValue(n, aggregate, element, indices))

    # ── Vector ─────────────────────────────────────────────────

    def extract_element(self, vector: Value, index: Value,
                        name: str = "") -> ExtractElement:
        n = name or self._context.unique_name("extractelement")
        return self._insert(ExtractElement(n, vector, index))

    def insert_element(self, vector: Value, element: Value, index: Value,
                       name: str = "") -> InsertElement:
        n = name or self._context.unique_name("insertelement")
        return self._insert(InsertElement(n, vector, element, index))

    def shuffle_vector(self, v1: Value, v2: Value, mask: Value,
                       name: str = "") -> ShuffleVector:
        n = name or self._context.unique_name("shufflevector")
        return self._insert(ShuffleVector(n, v1, v2, mask))

    # ── Atomic ─────────────────────────────────────────────────

    def atomicrmw(self, operation: str, pointer: Value, value: Value,
                  name: str = "", ordering: str = "seq_cst") -> AtomicRMW:
        n = name or self._context.unique_name("atomicrmw")
        return self._insert(AtomicRMW(n, operation, pointer, value, ordering))

    def cmpxchg(self, pointer: Value, cmp_val: Value, new_val: Value,
                name: str = "", success_ordering: str = "seq_cst",
                failure_ordering: str = "seq_cst") -> CmpXchg:
        n = name or self._context.unique_name("cmpxchg")
        return self._insert(CmpXchg(n, pointer, cmp_val, new_val,
                                    success_ordering, failure_ordering))

    def fence(self, ordering: str = "seq_cst") -> Fence:
        return self._insert(Fence(ordering))

    # ── Constants ────────────────────────────────────────────────

    def const_int(self, value: int, bit_width: int = 64) -> IntConstant:
        from .types import IntegerType
        return IntConstant(value, IntegerType(bit_width))

    def const_float(self, value: float, bit_width: int = 64) -> FloatConstant:
        from .types import FloatType
        return FloatConstant(value, FloatType(bit_width))

    def const_bool(self, value: bool) -> BoolConstant:
        return BoolConstant(value)

    def const_string(self, value: str) -> 'StringConstant':
        from .values import StringConstant
        return StringConstant(value)

    def const_null(self, ptr_type=None) -> 'NullConstant':
        from .values import NullConstant
        return NullConstant(ptr_type)

    # ── Block Creation ───────────────────────────────────────────

    def create_block(self, name: str = "", func: Optional[IRFunction] = None) -> BasicBlock:
        """Create a new basic block, optionally appending it to a function."""
        n = name or self._context.unique_name("bb")
        block = BasicBlock(n)
        if func is not None:
            func.append_block(block)
        return block

    def append_to(self, func: IRFunction, name: str = "") -> BasicBlock:
        """Create and append a block to a function, positioning the builder there."""
        block = self.create_block(name)
        func.append_block(block)
        self.position_at_end(block)
        return block

    def __repr__(self) -> str:
        pos = f"block:{self._block.name}" if self._block else "none"
        return f"IRBuilder(position={pos})"
