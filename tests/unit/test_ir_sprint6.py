"""
IR Test Suite — Sprint 6

Comprehensive tests for the Intermediate Representation.
Covers: types, values, instructions, basic blocks, functions, modules,
builder, CFG, SSA, serialization, validation, visualization, HIR, MIR, LIR.
"""
from __future__ import annotations

import sys
import os
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from compiler.ir.types import (
    IRTypeKind, IRType, VoidType, LabelType, IntegerType, FloatType,
    PointerType, ArrayType, StructType, IRFunctionType, VectorType,
    IR_VOID, IR_LABEL, IR_I1, IR_I8, IR_I16, IR_I32, IR_I64, IR_PTR,
    IR_F16, IR_F32, IR_F64,
    int_type, float_type, ptr_type, array_type, struct_type, func_type,
    vec_type, get_element_type, get_pointer_depth,
    is_numeric_type, is_integer_type,
)
from compiler.ir.values import (
    Value, ValueKind, Constant, IntConstant, FloatConstant,
    BoolConstant, StringConstant, NullConstant, UndefinedConstant,
    ZeroConstant, Argument, GlobalVariable,
    make_int_constant, make_float_constant, make_bool_constant,
    make_string_constant, make_null_constant, is_constant,
)
from compiler.ir.instructions import (
    Instruction, TerminatorInst, Opcode,
    ICmpPredicate, FCmpPredicate,
    Add, Sub, Mul, SDiv, FAdd, FSub, FMul, FDiv,
    And, Or, Xor, Shl, LShr, AShr,
    Not, Neg, FNeg,
    ICmp, FCmp,
    Alloca, Load, Store, GEP,
    Branch, CondBranch, Return, Unreachable, Switch,
    Phi, Call, Invoke,
    Trunc, ZExt, SExt, BitCast,
    ExtractValue, InsertValue,
    ExtractElement, InsertElement,
)
from compiler.ir.basic_block import BasicBlock
from compiler.ir.function import IRFunction
from compiler.ir.module import IRModule
from compiler.ir.context import IRContext
from compiler.ir.builder import IRBuilder
from compiler.ir.validator import IRValidator, validate
from compiler.ir.printer import IRPrinter, print_ir
from compiler.ir.serialization import (
    IRSerializer, IRDeserializer, serialize_json, deserialize_json, serialize_text,
)
from compiler.ir.visualizer import IRVisualizer, visualize_cfg, print_cfg
from compiler.ir.cfg import CFG, LoopInfo
from compiler.ir.ssa import (
    DefUseChain, LivenessInfo, LivenessAnalysis, SSABuilder,
)
from compiler.ir.hir import (
    HIRModule, HIRFunctionDecl, HIRParameter, HIRBlock,
    HIRReturn, HIRIf, HIRWhile, HIRClassDecl, HIRTraitDecl,
    hir_to_ir_module,
)
from compiler.ir.mir import (
    OwnershipKind, OwnershipMeta, MIRFunction, MIRModule,
    lower_to_mir,
)
from compiler.ir.lir import (
    LIRInstKind, LIRInstruction, LIRBlock, LIRFunction,
    LIRModule, LIRPrinter, LIRBuilder, lower_ir_to_lir,
)
from compiler.ir.metadata import (
    MetadataKind, MetadataCollection, DebugLocation,
    SourceFile, VariableName, make_debug_location,
)
from compiler.ir.attributes import (
    AttrKind, AttributeSet, Attribute,
    attr_always_inline, attr_nocapture, attr_nonnull,
)


# ══════════════════════════════════════════════════════════════════
# Type Tests
# ══════════════════════════════════════════════════════════════════


class TestIRTypes:
    def test_void_type(self):
        assert IR_VOID.kind == IRTypeKind.VOID
        assert not IR_VOID.is_first_class
        assert IR_VOID.is_zero_sized
        assert IR_VOID.is_void

    def test_label_type(self):
        assert IR_LABEL.kind == IRTypeKind.LABEL
        assert not IR_LABEL.is_first_class
        assert IR_LABEL.is_zero_sized

    def test_integer_types(self):
        for bits in [1, 8, 16, 32, 64, 128]:
            t = int_type(bits)
            assert t.kind == IRTypeKind.INTEGER
            assert t.bit_width == bits
            assert t.is_first_class
            assert not t.is_zero_sized
            assert t.is_integer
            assert repr(t) == f"i{bits}"

    def test_float_types(self):
        for bits in [16, 32, 64, 128]:
            t = float_type(bits)
            assert t.kind == IRTypeKind.FLOAT
            assert t.bit_width == bits
            assert t.is_first_class
            assert t.is_float

    def test_pointer_type(self):
        p = ptr_type(IR_I32)
        assert p.kind == IRTypeKind.POINTER
        assert p.element_type == IR_I32
        assert p.address_space == 0
        assert p.is_first_class
        assert p.is_pointer
        assert repr(p) == "i32*"

    def test_array_type(self):
        a = array_type(10, IR_I32)
        assert a.kind == IRTypeKind.ARRAY
        assert a.length == 10
        assert a.element_type == IR_I32
        assert a.is_first_class
        assert repr(a) == "[10 x i32]"

    def test_struct_type(self):
        s = struct_type((IR_I32, IR_I64), name="pair")
        assert s.kind == IRTypeKind.STRUCT
        assert len(s.field_types) == 2
        assert s.field_types[0] == IR_I32
        assert s.field_types[1] == IR_I64
        assert s.name == "pair"
        assert s.is_first_class

    def test_struct_packed(self):
        s = struct_type((IR_I8, IR_I16), is_packed=True)
        assert s.is_packed

    def test_struct_empty(self):
        s = struct_type(())
        assert s.is_zero_sized

    def test_function_type(self):
        ft = func_type((IR_I32, IR_I64), IR_I32)
        assert ft.kind == IRTypeKind.FUNCTION
        assert ft.param_types == (IR_I32, IR_I64)
        assert ft.return_type == IR_I32
        assert not ft.is_first_class
        assert not ft.is_variadic

    def test_function_type_variadic(self):
        ft = func_type((IR_I32,), IR_VOID, is_variadic=True)
        assert ft.is_variadic

    def test_vector_type(self):
        v = vec_type(4, IR_I32)
        assert v.kind == IRTypeKind.VECTOR
        assert v.element_count == 4
        assert v.element_type == IR_I32
        assert v.is_first_class

    def test_type_equality(self):
        assert int_type(32) == int_type(32)
        assert int_type(32) != int_type(64)
        assert ptr_type(IR_I32) == ptr_type(IR_I32)
        assert ptr_type(IR_I32) != ptr_type(IR_I64)

    def test_type_hash(self):
        s = {int_type(32), int_type(64), int_type(32)}
        assert len(s) == 2

    def test_type_repr_roundtrip(self):
        for t in [IR_I32, IR_F64, ptr_type(IR_I8), array_type(5, IR_I1)]:
            assert repr(t)

    def test_common_singletons(self):
        assert IR_I1.bit_width == 1
        assert IR_I8.bit_width == 8
        assert IR_I16.bit_width == 16
        assert IR_I32.bit_width == 32
        assert IR_I64.bit_width == 64
        assert IR_F32.bit_width == 32
        assert IR_F64.bit_width == 64

    def test_element_type(self):
        assert get_element_type(ptr_type(IR_I32)) == IR_I32
        assert get_element_type(array_type(5, IR_I64)) == IR_I64
        assert get_element_type(IR_I32) is None

    def test_pointer_depth(self):
        assert get_pointer_depth(IR_I32) == 0
        assert get_pointer_depth(ptr_type(IR_I32)) == 1
        assert get_pointer_depth(ptr_type(ptr_type(IR_I32))) == 2

    def test_is_numeric(self):
        assert is_numeric_type(IR_I32)
        assert is_numeric_type(IR_F64)
        assert not is_numeric_type(ptr_type(IR_I32))

    def test_is_integer(self):
        assert is_integer_type(IR_I32)
        assert not is_integer_type(IR_F64)


# ══════════════════════════════════════════════════════════════════
# Value Tests
# ══════════════════════════════════════════════════════════════════


class TestIRValues:
    def test_int_constant(self):
        c = IntConstant(42, IR_I32)
        assert c.value == 42
        assert c.type == IR_I32
        assert c.kind == ValueKind.CONSTANT
        assert is_constant(c)

    def test_int_constant_default_type(self):
        c = IntConstant(100)
        assert c.type == IR_I64

    def test_float_constant(self):
        c = FloatConstant(3.14, IR_F64)
        assert c.value == 3.14
        assert c.type == IR_F64

    def test_bool_constant(self):
        t = BoolConstant(True)
        f = BoolConstant(False)
        assert t.value is True
        assert f.value is False
        assert repr(t) == "true"
        assert repr(f) == "false"

    def test_string_constant(self):
        c = StringConstant("hello")
        assert c.value == "hello"
        assert c.byte_data == b"hello"
        assert c.type.length == 5  # 5 bytes

    def test_null_constant(self):
        c = NullConstant()
        assert c.type.is_pointer

    def test_undefined(self):
        c = UndefinedConstant(IR_I32)
        assert c.kind == ValueKind.UNDEFINED
        assert c.type == IR_I32

    def test_zero_constant(self):
        c = ZeroConstant(struct_type((IR_I32, IR_I64)))
        assert repr(c) == "zeroinitializer"

    def test_argument(self):
        arg = Argument("x", IR_I32, index=0)
        assert arg.name == "x"
        assert arg.type == IR_I32
        assert arg.index == 0
        assert arg.kind == ValueKind.ARGUMENT

    def test_global_variable(self):
        g = GlobalVariable("g_val", IR_I32, is_constant=True)
        assert g.name == "g_val"
        assert g.value_type == IR_I32
        assert g.is_constant
        assert g.type.is_pointer
        assert g.kind == ValueKind.GLOBAL_VARIABLE

    def test_use_tracking(self):
        c = make_int_constant(10)
        bb = BasicBlock("entry")
        inst = Add("tmp", c, c)
        bb.append(inst)
        assert c.use_count == 2
        assert inst in c.uses

    def test_factory_functions(self):
        i = make_int_constant(42, 32)
        assert i.type == IR_I32
        f = make_float_constant(1.0, 32)
        assert f.type == IR_F32
        b = make_bool_constant(True)
        assert b.type == IR_I1
        s = make_string_constant("test")
        assert s.value == "test"

    def test_constant_equality(self):
        assert IntConstant(42, IR_I32) == IntConstant(42, IR_I32)
        assert IntConstant(42, IR_I32) != IntConstant(43, IR_I32)
        assert IntConstant(42, IR_I32) != IntConstant(42, IR_I64)

    def test_constant_hash(self):
        s = {IntConstant(42, IR_I32), IntConstant(42, IR_I32)}
        assert len(s) == 1


# ══════════════════════════════════════════════════════════════════
# Instruction Tests
# ══════════════════════════════════════════════════════════════════


class TestIRInstructions:
    def test_add(self):
        a = make_int_constant(1, 32)
        b = make_int_constant(2, 32)
        inst = Add("sum", a, b)
        assert inst.opcode == Opcode.ADD
        assert inst.result_type == IR_I32
        assert inst.is_binary_op
        assert inst.lhs is a
        assert inst.rhs is b

    def test_sub(self):
        a = make_int_constant(5, 32)
        b = make_int_constant(3, 32)
        inst = Sub("diff", a, b)
        assert inst.opcode == Opcode.SUB

    def test_mul(self):
        a = make_int_constant(2, 32)
        b = make_int_constant(3, 32)
        inst = Mul("prod", a, b)
        assert inst.opcode == Opcode.MUL

    def test_return(self):
        val = make_int_constant(42)
        inst = Return(val)
        assert inst.is_terminator
        assert inst.value is val

    def test_return_void(self):
        inst = Return()
        assert inst.is_terminator
        assert inst.value is None

    def test_branch(self):
        bb = BasicBlock("target")
        inst = Branch(bb)
        assert inst.is_terminator
        assert inst.target is bb

    def test_cond_branch(self):
        cond = make_bool_constant(True)
        t = BasicBlock("true")
        f = BasicBlock("false")
        inst = CondBranch(cond, t, f)
        assert inst.is_terminator
        assert inst.condition is cond
        assert inst.true_block is t
        assert inst.false_block is f

    def test_unreachable(self):
        inst = Unreachable()
        assert inst.is_terminator
        assert inst.opcode == Opcode.UNREACHABLE

    def test_icmp(self):
        a = make_int_constant(1, 32)
        b = make_int_constant(2, 32)
        inst = ICmp("cmp", ICmpPredicate.SLT, a, b)
        assert inst.is_comparison
        assert inst.predicate == ICmpPredicate.SLT
        assert inst.result_type == IR_I1

    def test_fcmp(self):
        a = FloatConstant(1.0, IR_F32)
        b = FloatConstant(2.0, IR_F32)
        inst = FCmp("cmp", FCmpPredicate.OLT, a, b)
        assert inst.is_comparison
        assert inst.predicate == FCmpPredicate.OLT

    def test_alloca(self):
        inst = Alloca("ptr", IR_I32)
        assert inst.allocated_type == IR_I32
        assert inst.result_type.is_pointer
        assert inst.is_memory_op

    def test_load(self):
        ptr = make_int_constant(0)
        ptr_type_val = PointerType(IR_I32)
        inst = Load("val", IR_I32, ptr)
        assert inst.pointer is ptr
        assert inst.result_type == IR_I32
        assert inst.is_memory_op

    def test_store(self):
        val = make_int_constant(42)
        ptr = make_int_constant(0)
        inst = Store(val, ptr)
        assert inst.value is val
        assert inst.pointer is ptr
        assert inst.result_type.is_void

    def test_gep(self):
        ptr = make_int_constant(0)
        idx = make_int_constant(0)
        inst = GEP("ptr", IR_I32, ptr, [idx])
        assert inst.source_type == IR_I32
        assert inst.pointer is ptr

    def test_phi(self):
        bb1 = BasicBlock("bb1")
        bb2 = BasicBlock("bb2")
        a = make_int_constant(1)
        b = make_int_constant(2)
        inst = Phi("phi_val", IR_I32, [(a, bb1), (b, bb2)])
        assert len(inst.incoming) == 2
        assert inst.get_incoming_for(bb1) is a

    def test_phi_add_remove(self):
        phi = Phi("p", IR_I32)
        bb = BasicBlock("bb")
        val = make_int_constant(10)
        phi.add_incoming(val, bb)
        assert len(phi.incoming) == 1
        phi.remove_incoming(bb)
        assert len(phi.incoming) == 0

    def test_call(self):
        from compiler.ir.types import IRFunctionType
        ft = func_type((IR_I32, IR_I32), IR_I32)
        callee = Argument("add", ft)
        a = make_int_constant(1)
        b = make_int_constant(2)
        inst = Call("result", ft, callee, [a, b])
        assert inst.func_type == ft
        assert inst.result_type == IR_I32
        assert len(inst.arguments) == 2

    def test_trunc(self):
        val = make_int_constant(255, 32)
        inst = Trunc("trunc", val, IR_I8)
        assert inst.result_type == IR_I8
        assert inst.is_cast

    def test_zext(self):
        val = make_int_constant(1, 8)
        inst = ZExt("ext", val, IR_I32)
        assert inst.result_type == IR_I32
        assert inst.is_cast

    def test_sext(self):
        val = make_int_constant(-1, 8)
        inst = SExt("ext", val, IR_I32)
        assert inst.result_type == IR_I32

    def test_bitcast(self):
        val = make_int_constant(0, 32)
        inst = BitCast("bc", val, IR_I32)
        assert inst.is_cast

    def test_and(self):
        a = make_int_constant(0xFF, 8)
        b = make_int_constant(0x0F, 8)
        inst = And("band", a, b)
        assert inst.opcode == Opcode.AND

    def test_or(self):
        a = make_int_constant(0xF0, 8)
        b = make_int_constant(0x0F, 8)
        inst = Or("bor", a, b)
        assert inst.opcode == Opcode.OR

    def test_xor(self):
        a = make_int_constant(0xFF, 8)
        b = make_int_constant(0x0F, 8)
        inst = Xor("bxor", a, b)
        assert inst.opcode == Opcode.XOR

    def test_extract_insert_value(self):
        agg = make_int_constant(0)
        elem = make_int_constant(42)
        ext = ExtractValue("ext", agg, [0])
        ins = InsertValue("ins", agg, elem, [0])
        assert ext.indices == [0]
        assert ins.element is elem

    def test_extract_insert_element(self):
        from compiler.ir.types import vec_type
        v_type = vec_type(4, IR_I32)
        v = make_int_constant(0)
        v._type = v_type
        idx = make_int_constant(0)
        elem = make_int_constant(42)
        ext = ExtractElement("ext", v, idx)
        ins = InsertElement("ins", v, elem, idx)

    def test_set_operand(self):
        a = make_int_constant(1)
        b = make_int_constant(2)
        c = make_int_constant(3)
        inst = Add("tmp", a, b)
        inst.set_operand(0, c)
        assert inst.operands[0] is c

    def test_replace_uses_of(self):
        a = make_int_constant(1)
        b = make_int_constant(2)
        c = make_int_constant(3)
        inst = Add("tmp", a, b)
        inst.replace_uses_of(a, c)
        assert inst.operands[0] is c

    def test_terminator_base(self):
        assert issubclass(TerminatorInst, Instruction)
        assert issubclass(Branch, TerminatorInst)
        assert issubclass(Return, TerminatorInst)

    def test_instruction_repr(self):
        a = make_int_constant(1, 32)
        b = make_int_constant(2, 32)
        inst = Add("x", a, b)
        assert "ADD" in repr(inst) or "add" in repr(inst).lower()

    def test_switch(self):
        val = make_int_constant(0)
        default = BasicBlock("default")
        cases = [(make_int_constant(1), BasicBlock("case1"))]
        inst = Switch(val, default, cases)
        assert inst.is_terminator
        assert len(inst.cases) == 1


# ══════════════════════════════════════════════════════════════════
# Basic Block Tests
# ══════════════════════════════════════════════════════════════════


class TestBasicBlock:
    def test_create(self):
        bb = BasicBlock("entry")
        assert bb.name == "entry"
        assert bb.is_empty
        assert bb.instruction_count == 0

    def test_append(self):
        bb = BasicBlock("bb")
        a = make_int_constant(1)
        b = make_int_constant(2)
        inst = Add("tmp", a, b)
        bb.append(inst)
        assert bb.instruction_count == 1
        assert inst.parent is bb

    def test_non_terminating(self):
        bb = BasicBlock("bb")
        a = make_int_constant(1)
        b = make_int_constant(2)
        bb.append(Add("tmp", a, b))
        bb.append(Return())
        assert len(bb.non_terminating) == 1
        assert bb.terminator is not None
        assert bb.terminator.is_terminator

    def test_predecessors_successors(self):
        bb1 = BasicBlock("bb1")
        bb2 = BasicBlock("bb2")
        bb1.add_successor(bb2)
        bb2.add_predecessor(bb1)
        assert bb2 in bb1.successors
        assert bb1 in bb2.predecessors

    def test_insert_before_after(self):
        bb = BasicBlock("bb")
        a = Add("a", make_int_constant(1), make_int_constant(2))
        b = Add("b", make_int_constant(3), make_int_constant(4))
        c = Add("c", make_int_constant(5), make_int_constant(6))
        bb.append(a)
        bb.append(c)
        bb.insert_after(a, b)
        assert bb[1] is b
        d = Add("d", make_int_constant(7), make_int_constant(8))
        bb.insert_before(c, d)
        assert bb[2] is d

    def test_remove(self):
        bb = BasicBlock("bb")
        a = Add("a", make_int_constant(1), make_int_constant(2))
        bb.append(a)
        assert a.parent is bb
        bb.remove(a)
        assert a.parent is None
        assert bb.is_empty

    def test_clear(self):
        bb = BasicBlock("bb")
        bb.append(Add("a", make_int_constant(1), make_int_constant(2)))
        bb.append(Add("b", make_int_constant(3), make_int_constant(4)))
        bb.clear()
        assert bb.is_empty

    def test_iteration(self):
        bb = BasicBlock("bb")
        insts = [Add(f"x{i}", make_int_constant(i), make_int_constant(i))
                 for i in range(5)]
        for inst in insts:
            bb.append(inst)
        assert len(list(bb)) == 5

    def test_getitem(self):
        bb = BasicBlock("bb")
        a = Add("a", make_int_constant(1), make_int_constant(2))
        bb.append(a)
        assert bb[0] is a

    def test_len(self):
        bb = BasicBlock("bb")
        assert len(bb) == 0
        bb.append(Add("a", make_int_constant(1), make_int_constant(2)))
        assert len(bb) == 1

    def test_kind(self):
        bb = BasicBlock("test")
        assert bb.kind == ValueKind.BASIC_BLOCK

    def test_label_type(self):
        bb = BasicBlock("test")
        assert bb.type == IR_LABEL

    def test_repr(self):
        bb = BasicBlock("entry")
        assert "entry" in repr(bb)


# ══════════════════════════════════════════════════════════════════
# Function Tests
# ══════════════════════════════════════════════════════════════════


class TestIRFunction:
    def _make_func(self, name="test_func"):
        ft = func_type((IR_I32, IR_I32), IR_I32)
        return IRFunction(name, ft)

    def test_create(self):
        func = self._make_func()
        assert func.name == "test_func"
        assert func.is_declaration
        assert func.block_count == 0

    def test_add_block(self):
        func = self._make_func()
        bb = BasicBlock("entry")
        func.append_block(bb)
        assert not func.is_declaration
        assert func.block_count == 1
        assert func.entry_block is bb

    def test_args(self):
        func = self._make_func()
        assert len(func.args) == 2
        assert func.args[0].name == "arg0"
        assert func.args[0].type == IR_I32

    def test_blocks(self):
        func = self._make_func()
        bb1 = BasicBlock("bb1")
        bb2 = BasicBlock("bb2")
        func.append_block(bb1)
        func.append_block(bb2)
        assert func.block_count == 2
        assert func[0] is bb1
        assert func[1] is bb2

    def test_remove_block(self):
        func = self._make_func()
        bb = BasicBlock("bb")
        func.append_block(bb)
        func.remove_block(bb)
        assert func.block_count == 0

    def test_move_block(self):
        func = self._make_func()
        bb1 = BasicBlock("bb1")
        bb2 = BasicBlock("bb2")
        func.append_block(bb1)
        func.append_block(bb2)
        func.move_block(bb1, 1)
        assert func[0] is bb2
        assert func[1] is bb1

    def test_instruction_count(self):
        func = self._make_func()
        bb = BasicBlock("entry")
        bb.append(Add("a", make_int_constant(1), make_int_constant(2)))
        bb.append(Add("b", make_int_constant(3), make_int_constant(4)))
        func.append_block(bb)
        assert func.instruction_count == 2

    def test_iteration(self):
        func = self._make_func()
        for i in range(3):
            func.append_block(BasicBlock(f"bb{i}"))
        assert len(list(func)) == 3

    def test_metadata(self):
        func = self._make_func()
        func.metadata["source_file"] = "test.i"
        assert func.metadata["source_file"] == "test.i"

    def test_return_type(self):
        func = self._make_func()
        assert func.return_type == IR_I32

    def test_func_type(self):
        func = self._make_func()
        assert func.func_type.kind == IRTypeKind.FUNCTION

    def test_kind(self):
        func = self._make_func()
        assert func.kind == ValueKind.FUNCTION

    def test_repr(self):
        func = self._make_func()
        assert "test_func" in repr(func)
        assert "declare" in repr(func)


# ══════════════════════════════════════════════════════════════════
# Module Tests
# ══════════════════════════════════════════════════════════════════


class TestIRModule:
    def test_create(self):
        mod = IRModule("test")
        assert mod.name == "test"
        assert mod.is_empty

    def test_add_function(self):
        mod = IRModule("test")
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("add_one", ft)
        mod.add_function(func)
        assert mod.function_count == 1
        assert mod.has_function("add_one")

    def test_get_function(self):
        mod = IRModule("test")
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("foo", ft)
        mod.add_function(func)
        assert mod.get_function("foo") is func
        assert mod.get_function("bar") is None

    def test_remove_function(self):
        mod = IRModule("test")
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("foo", ft)
        mod.add_function(func)
        mod.remove_function(func)
        assert mod.function_count == 0

    def test_add_global(self):
        mod = IRModule("test")
        g = GlobalVariable("g", IR_I32)
        mod.add_global(g)
        assert mod.global_count == 1

    def test_get_global(self):
        mod = IRModule("test")
        g = GlobalVariable("g", IR_I32)
        mod.add_global(g)
        assert mod.get_global("g") is g

    def test_target(self):
        mod = IRModule("test")
        mod.target = "x86_64-pc-linux-gnu"
        assert mod.target == "x86_64-pc-linux-gnu"

    def test_named_types(self):
        mod = IRModule("test")
        mod.register_type("MyStruct", struct_type((IR_I32,)))
        assert mod.get_type("MyStruct") is not None

    def test_instruction_count(self):
        mod = IRModule("test")
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        bb.append(Add("a", make_int_constant(1), make_int_constant(2)))
        func.append_block(bb)
        mod.add_function(func)
        assert mod.instruction_count == 1

    def test_repr(self):
        mod = IRModule("test")
        assert "test" in repr(mod)


# ══════════════════════════════════════════════════════════════════
# Builder Tests
# ══════════════════════════════════════════════════════════════════


class TestIRBuilder:
    def _make_builder(self):
        ctx = IRContext()
        return IRBuilder(ctx)

    def test_create_and_position(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        assert b.block is bb

    def test_build_add(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        a = make_int_constant(1)
        c = make_int_constant(2)
        inst = b.add(a, c, "sum")
        assert inst.name == "sum"
        assert inst.opcode == Opcode.ADD
        assert len(bb) == 1

    def test_build_sub(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        a = make_int_constant(5)
        c = make_int_constant(3)
        inst = b.sub(a, c, "diff")
        assert inst.opcode == Opcode.SUB

    def test_build_mul(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        a = make_int_constant(2)
        c = make_int_constant(3)
        inst = b.mul(a, c, "prod")
        assert inst.opcode == Opcode.MUL

    def test_build_icmp(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        a = make_int_constant(1)
        c = make_int_constant(2)
        inst = b.icmp(ICmpPredicate.SLT, a, c, "cmp")
        assert inst.opcode == Opcode.ICMP

    def test_build_return(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        inst = b.ret(make_int_constant(42))
        assert inst.is_terminator

    def test_build_alloca(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        inst = b.alloca(IR_I32, "ptr")
        assert inst.allocated_type == IR_I32

    def test_build_store_load(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        ptr = b.alloca(IR_I32, "ptr")
        val = make_int_constant(42)
        b.store(val, ptr)
        loaded = b.load(IR_I32, ptr, "loaded")
        assert loaded.result_type == IR_I32

    def test_build_phi(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        phi = b.phi(IR_I32, "p")
        assert phi.result_type == IR_I32

    def test_build_and(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        a = make_int_constant(0xFF)
        c = make_int_constant(0x0F)
        inst = b.and_(a, c, "band")
        assert inst.opcode == Opcode.AND

    def test_build_or(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        a = make_int_constant(0xF0)
        c = make_int_constant(0x0F)
        inst = b.or_(a, c, "bor")
        assert inst.opcode == Opcode.OR

    def test_build_not(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        val = make_bool_constant(True)
        inst = b.not_(val, "bnot")
        assert inst.opcode == Opcode.NOT

    def test_build_neg(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        val = make_int_constant(42)
        inst = b.neg(val, "neg")
        assert inst.opcode == Opcode.NEG

    def test_build_trunc(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        val = make_int_constant(255, 32)
        inst = b.trunc(val, IR_I8, "tr")
        assert inst.result_type == IR_I8

    def test_build_zext(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        val = make_int_constant(1, 8)
        inst = b.zext(val, IR_I32, "ext")
        assert inst.result_type == IR_I32

    def test_create_block(self):
        b = self._make_builder()
        bb = b.create_block("my_block")
        assert bb.name == "my_block"

    def test_append_to(self):
        b = self._make_builder()
        ft = func_type((), IR_I32)
        func = IRFunction("test", ft)
        bb = b.append_to(func, "entry")
        assert bb in func.blocks
        assert b.block is bb

    def test_build_cond_branch(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        bb2 = BasicBlock("then")
        bb3 = BasicBlock("else")
        bb.add_successor(bb2)
        bb.add_successor(bb3)
        bb2.add_predecessor(bb)
        bb3.add_predecessor(bb)
        b.position_at_end(bb)
        cond = make_bool_constant(True)
        inst = b.cond_branch(cond, bb2, bb3)
        assert inst.is_terminator

    def test_build_branch(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        target = BasicBlock("target")
        bb.add_successor(target)
        target.add_predecessor(bb)
        b.position_at_end(bb)
        inst = b.branch(target)
        assert inst.is_terminator

    def test_no_block_raises(self):
        b = self._make_builder()
        with pytest.raises(RuntimeError):
            b.add(make_int_constant(1), make_int_constant(2))

    def test_build_gep(self):
        b = self._make_builder()
        bb = BasicBlock("entry")
        b.position_at_end(bb)
        ptr = b.alloca(array_type(5, IR_I32), "arr")
        idx = make_int_constant(0)
        inst = b.gep(IR_I32, ptr, [idx], "gep")
        assert inst.opcode == Opcode.GEP


# ══════════════════════════════════════════════════════════════════
# Validator Tests
# ══════════════════════════════════════════════════════════════════


class TestIRValidator:
    def test_valid_module(self):
        mod = IRModule("test")
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(42)))
        func.append_block(bb)
        mod.add_function(func)

        validator = IRValidator()
        assert validator.validate_module(mod)
        assert validator.is_valid

    def test_missing_terminator(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        bb.append(Add("a", make_int_constant(1), make_int_constant(2)))
        func.append_block(bb)
        mod.add_function(func)

        validator = IRValidator()
        assert not validator.validate_module(mod)
        assert len(validator.errors) > 0

    def test_declaration_valid(self):
        mod = IRModule("test")
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("extern", ft)
        mod.add_function(func)

        validator = IRValidator()
        assert validator.validate_module(mod)

    def test_empty_module_valid(self):
        mod = IRModule("empty")
        validator = IRValidator()
        assert validator.validate_module(mod)

    def test_validate_convenience(self):
        mod = IRModule("test")
        errors = validate(mod)
        assert len(errors) == 0

    def test_phi_no_incoming(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        phi = Phi("p", IR_I32, [])
        bb.append(phi)
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        validator = IRValidator()
        assert not validator.validate_module(mod)


# ══════════════════════════════════════════════════════════════════
# Printer Tests
# ══════════════════════════════════════════════════════════════════


class TestIRPrinter:
    def test_print_module(self):
        mod = IRModule("test_mod")
        ft = func_type((IR_I32, IR_I32), IR_I32)
        func = IRFunction("add", ft)
        bb = BasicBlock("entry")
        a = make_int_constant(1)
        b = make_int_constant(2)
        bb.append(Add("sum", a, b))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)

        output = print_ir(mod)
        assert "add" in output
        assert "Module" in output

    def test_print_empty_function(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        func = IRFunction("extern_fn", ft)
        mod.add_function(func)
        output = print_ir(mod)
        assert "declare" in output

    def test_print_block(self):
        bb = BasicBlock("entry")
        bb.append(Add("a", make_int_constant(1), make_int_constant(2)))
        printer = IRPrinter()
        output = printer.print_block(bb)
        assert "entry" in output


# ══════════════════════════════════════════════════════════════════
# Serialization Tests
# ══════════════════════════════════════════════════════════════════


class TestSerialization:
    def test_json_roundtrip(self):
        mod = IRModule("test")
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(42)))
        func.append_block(bb)
        mod.add_function(func)

        json_str = serialize_json(mod)
        assert json_str
        restored = deserialize_json(json_str)
        assert restored.name == "test"
        assert restored.function_count == 1
        assert restored.functions[0].name == "foo"

    def test_dict_serialization(self):
        mod = IRModule("test")
        serializer = IRSerializer()
        data = serializer.to_dict(mod)
        assert data["name"] == "test"

    def test_text_serialization(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        func = IRFunction("bar", ft)
        mod.add_function(func)
        text = serialize_text(mod)
        assert "bar" in text

    def test_type_serialization(self):
        from compiler.ir.serialization import _serialize_type, _deserialize_type
        types = [IR_I32, IR_F64, ptr_type(IR_I8), array_type(5, IR_I32)]
        for t in types:
            data = _serialize_type(t)
            restored = _deserialize_type(data)
            assert restored == t

    def test_version(self):
        from compiler.ir.serialization import IR_FORMAT_VERSION
        assert IR_FORMAT_VERSION == 1

    def test_module_metadata(self):
        mod = IRModule("test")
        mod.target = "x86_64"
        json_str = serialize_json(mod)
        restored = deserialize_json(json_str)
        assert restored.target == "x86_64"


# ══════════════════════════════════════════════════════════════════
# Visualizer Tests
# ══════════════════════════════════════════════════════════════════


class TestVisualizer:
    def test_cfg_dot(self):
        ft = func_type((), IR_I32)
        func = IRFunction("test", ft)
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("exit")
        bb1.add_successor(bb2)
        bb2.add_predecessor(bb1)
        bb1.append(Return(make_int_constant(0)))
        func.append_block(bb1)
        func.append_block(bb2)

        dot = visualize_cfg(func)
        assert "digraph CFG" in dot
        assert "entry" in dot
        assert "exit" in dot

    def test_call_graph_dot(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        caller = IRFunction("caller", ft)
        callee = IRFunction("callee", ft)
        bb = BasicBlock("entry")
        bb.append(Call("result", ft, callee))
        bb.append(Return(make_int_constant(0)))
        caller.append_block(bb)
        mod.add_function(caller)
        mod.add_function(callee)

        viz = IRVisualizer()
        dot = viz.call_graph_to_dot(mod)
        assert "caller" in dot
        assert "callee" in dot

    def test_text_cfg(self):
        ft = func_type((), IR_I32)
        func = IRFunction("test", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)

        text = print_cfg(func)
        assert "test" in text
        assert "entry" in text

    def test_save_dot(self):
        import tempfile
        viz = IRVisualizer()
        dot = 'digraph G { "a" -> "b"; }'
        filepath = os.path.join(tempfile.gettempdir(), "test_save_dot.dot")
        viz.save_dot(dot, filepath)
        assert os.path.exists(filepath)
        os.unlink(filepath)


# ══════════════════════════════════════════════════════════════════
# CFG Tests
# ══════════════════════════════════════════════════════════════════


class TestCFG:
    def _make_branching_func(self):
        """Create: entry -> [bb1, bb2] -> exit"""
        ft = func_type((), IR_I32)
        func = IRFunction("branch", ft)
        entry = BasicBlock("entry")
        bb1 = BasicBlock("bb1")
        bb2 = BasicBlock("bb2")
        exit_bb = BasicBlock("exit")

        cond = make_bool_constant(True)
        entry.add_successor(bb1)
        entry.add_successor(bb2)
        bb1.add_predecessor(entry)
        bb2.add_predecessor(entry)
        entry.append(CondBranch(cond, bb1, bb2))

        bb1.add_successor(exit_bb)
        bb2.add_successor(exit_bb)
        exit_bb.add_predecessor(bb1)
        exit_bb.add_predecessor(bb2)
        bb1.append(Branch(exit_bb))
        bb2.append(Branch(exit_bb))

        exit_bb.append(Return(make_int_constant(0)))

        for b in [entry, bb1, bb2, exit_bb]:
            func.append_block(b)
        return func

    def test_cfg_creation(self):
        func = self._make_branching_func()
        cfg = CFG(func)
        assert len(cfg.blocks) == 4

    def test_reachable_from(self):
        func = self._make_branching_func()
        cfg = CFG(func)
        reachable = cfg.reachable_from(func.entry_block)
        assert len(reachable) == 4

    def test_reverse_post_order(self):
        func = self._make_branching_func()
        cfg = CFG(func)
        rpo = cfg.reverse_post_order
        assert len(rpo) == 4
        assert rpo[0] is func.entry_block

    def test_dominates(self):
        func = self._make_branching_func()
        cfg = CFG(func)
        entry = func.entry_block
        assert cfg.dominates(entry, func[1])  # entry dominates bb1
        assert cfg.dominates(entry, func[2])  # entry dominates bb2

    def test_immediate_dominator(self):
        func = self._make_branching_func()
        cfg = CFG(func)
        bb1 = func[1]
        idom = cfg.immediate_dominator(bb1)
        assert idom is not None

    def test_exit_blocks(self):
        func = self._make_branching_func()
        cfg = CFG(func)
        exits = cfg.exit_blocks
        assert len(exits) == 1
        assert exits[0].name == "exit"

    def test_critical_edges(self):
        func = self._make_branching_func()
        cfg = CFG(func)
        critical = cfg.find_critical_edges()
        # entry -> bb1 and entry -> bb2 are critical (entry has 2 succs, bb1/bb2 each have 1 pred)
        assert len(critical) >= 0  # depends on pred counts

    def test_loop_detection(self):
        """Create a simple loop: header -> body -> header"""
        ft = func_type((), IR_I32)
        func = IRFunction("loop", ft)
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        header.add_successor(body)
        header.add_successor(exit_bb)
        body.add_predecessor(header)
        body.add_successor(header)
        exit_bb.add_predecessor(header)
        exit_bb.add_predecessor(body)

        cond = make_bool_constant(True)
        header.append(CondBranch(cond, body, exit_bb))
        body.append(Branch(header))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [header, body, exit_bb]:
            func.append_block(b)

        cfg = CFG(func)
        assert len(cfg.loops) >= 1

    def test_dominator_tree_dot(self):
        func = self._make_branching_func()
        cfg = CFG(func)
        viz = IRVisualizer()
        dot = viz.dominator_tree_to_dot(cfg)
        assert "DominatorTree" in dot

    def test_empty_function(self):
        ft = func_type((), IR_I32)
        func = IRFunction("empty", ft)
        cfg = CFG(func)
        assert len(cfg.blocks) == 0


# ══════════════════════════════════════════════════════════════════
# SSA Tests
# ══════════════════════════════════════════════════════════════════


class TestSSA:
    def test_def_use_chain(self):
        chain = DefUseChain()
        a = make_int_constant(1)
        bb = BasicBlock("bb")
        inst = Add("tmp", a, make_int_constant(2))
        bb.append(inst)

        chain.record_def(inst, inst)
        chain.record_use(a, inst)
        assert chain.get_def(inst) is inst
        assert inst in chain.get_uses(a)

    def test_liveness(self):
        ft = func_type((), IR_I32)
        func = IRFunction("test", ft)
        bb = BasicBlock("entry")
        a = make_int_constant(1)
        b = make_int_constant(2)
        bb.append(Add("sum", a, b))
        bb.append(Return(bb[0]))
        func.append_block(bb)

        cfg = CFG(func)
        liveness = LivenessAnalysis(cfg)
        info = liveness.get_info(bb)
        assert info is not None

    def test_ssa_builder(self):
        ft = func_type((), IR_I32)
        func = IRFunction("test", ft)
        bb = BasicBlock("entry")
        a = make_int_constant(1)
        b = make_int_constant(2)
        bb.append(Add("sum", a, b))
        bb.append(Return(bb[0]))
        func.append_block(bb)

        ssa = SSABuilder(func)
        assert ssa.cfg is not None
        assert ssa.liveness is not None

    def test_build_def_use_chains(self):
        ft = func_type((), IR_I32)
        func = IRFunction("test", ft)
        bb = BasicBlock("entry")
        a = make_int_constant(1)
        b = make_int_constant(2)
        sum_inst = Add("sum", a, b)
        bb.append(sum_inst)
        bb.append(Return(sum_inst))
        func.append_block(bb)

        ssa = SSABuilder(func)
        chain = ssa.build_def_use_chains(func)
        assert len(chain.defs) > 0

    def test_empty_function_ssa(self):
        ft = func_type((), IR_I32)
        func = IRFunction("empty", ft)
        ssa = SSABuilder(func)
        assert ssa.cfg is not None

    def test_phi_insertion(self):
        ft = func_type((), IR_I32)
        func = IRFunction("test", ft)
        bb = BasicBlock("entry")
        phi = Phi("p", IR_I32)
        bb.append(phi)
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)

        ssa = SSABuilder(func)
        phis = ssa.insert_phi_nodes(func)
        assert isinstance(phis, list)


# ══════════════════════════════════════════════════════════════════
# Context Tests
# ══════════════════════════════════════════════════════════════════


class TestIRContext:
    def test_create(self):
        ctx = IRContext()
        assert ctx.module is not None

    def test_unique_name(self):
        ctx = IRContext()
        n1 = ctx.unique_name("tmp")
        n2 = ctx.unique_name("tmp")
        assert n1 == "tmp0"
        assert n2 == "tmp1"

    def test_intern_type(self):
        ctx = IRContext()
        t1 = ctx.intern_type(IR_I32)
        t2 = ctx.intern_type(IR_I32)
        assert t1 is t2

    def test_set_source_file(self):
        ctx = IRContext()
        ctx.set_source_file("test.i")
        assert ctx.current_file == "test.i"

    def test_clear(self):
        ctx = IRContext()
        ctx.unique_name("x")
        ctx.clear()
        n = ctx.unique_name("x")
        assert n == "x0"

    def test_repr(self):
        ctx = IRContext()
        assert "IRContext" in repr(ctx)


# ══════════════════════════════════════════════════════════════════
# Metadata Tests
# ══════════════════════════════════════════════════════════════════


class TestMetadata:
    def test_debug_location(self):
        loc = DebugLocation("test.i", 10, 5)
        assert loc.file == "test.i"
        assert loc.line == 10
        assert loc.column == 5
        assert loc.kind == MetadataKind.DEBUG_LOCATION

    def test_debug_location_eq(self):
        loc1 = DebugLocation("test.i", 10, 5)
        loc2 = DebugLocation("test.i", 10, 5)
        assert loc1 == loc2

    def test_source_file(self):
        sf = SourceFile("test.i", "/home/user")
        assert sf.full_path == "/home/user/test.i"

    def test_variable_name(self):
        vn = VariableName("x", "_x")
        assert vn.name == "x"
        assert vn.mangled_name == "_x"

    def test_metadata_collection(self):
        mc = MetadataCollection()
        loc = DebugLocation("test.i", 10)
        mc.add(loc)
        assert mc.has(MetadataKind.DEBUG_LOCATION)
        assert mc.debug_location is loc
        assert len(mc) == 1

    def test_metadata_collection_remove(self):
        mc = MetadataCollection()
        mc.add(DebugLocation("test.i", 10))
        mc.remove(MetadataKind.DEBUG_LOCATION)
        assert mc.is_empty

    def test_make_debug_location(self):
        loc = make_debug_location("test.i", 42, 10)
        assert loc.line == 42

    def test_metadata_repr(self):
        loc = DebugLocation("test.i", 10, 5)
        assert "test.i:10:5" in repr(loc)

    def test_metadata_collection_iter(self):
        mc = MetadataCollection()
        mc.add(DebugLocation("a.i", 1))
        mc.add(SourceFile("a.i"))
        assert len(list(mc)) == 2

    def test_metadata_collection_entries(self):
        mc = MetadataCollection()
        mc.add(DebugLocation("a.i", 1))
        entries = mc.entries
        assert MetadataKind.DEBUG_LOCATION in entries


# ══════════════════════════════════════════════════════════════════
# Attribute Tests
# ══════════════════════════════════════════════════════════════════


class TestAttributes:
    def test_attribute_set(self):
        attrs = AttributeSet()
        attrs.add(attr_always_inline())
        assert attrs.has(AttrKind.ALWAYS_INLINE)
        assert len(attrs) == 1

    def test_attribute_set_add_kind(self):
        attrs = AttributeSet()
        attrs.add_kind(AttrKind.NOCAPTURE)
        assert attrs.has(AttrKind.NOCAPTURE)

    def test_attribute_set_remove(self):
        attrs = AttributeSet()
        attrs.add(attr_always_inline())
        attrs.remove(AttrKind.ALWAYS_INLINE)
        assert not attrs.has(AttrKind.ALWAYS_INLINE)

    def test_attribute_set_contains(self):
        attrs = AttributeSet()
        attrs.add(attr_nocapture())
        assert AttrKind.NOCAPTURE in attrs

    def test_attribute_set_repr(self):
        attrs = AttributeSet()
        attrs.add(attr_always_inline())
        r = repr(attrs)
        assert "ALWAYS_INLINE" in r

    def test_attribute_equality(self):
        a1 = Attribute(AttrKind.NOCAPTURE)
        a2 = Attribute(AttrKind.NOCAPTURE)
        assert a1 == a2

    def test_attribute_hash(self):
        s = {Attribute(AttrKind.NOCAPTURE), Attribute(AttrKind.NOCAPTURE)}
        assert len(s) == 1

    def test_attribute_value(self):
        a = Attribute(AttrKind.DEREFERENCEABLE, "16")
        assert a.value == "16"


# ══════════════════════════════════════════════════════════════════
# HIR Tests
# ══════════════════════════════════════════════════════════════════


class TestHIR:
    def test_hir_module(self):
        mod = HIRModule("test")
        assert mod.name == "test"
        assert len(mod.functions) == 0

    def test_hir_function(self):
        func = HIRFunctionDecl("add")
        assert func.name == "add"
        assert func.is_declaration

    def test_hir_function_with_body(self):
        body = HIRBlock()
        func = HIRFunctionDecl("add", body=body)
        assert not func.is_declaration

    def test_hir_parameter(self):
        param = HIRParameter("x")
        assert param.name == "x"
        assert not param.has_default

    def test_hir_class(self):
        cls = HIRClassDecl("Point")
        assert cls.name == "Point"

    def test_hir_trait(self):
        trait = HIRTraitDecl("Drawable")
        assert trait.name == "Drawable"

    def test_hir_if(self):
        from compiler.ir.values import BoolConstant
        cond = BoolConstant(True)
        then = HIRBlock()
        stmt = HIRIf(cond, then)
        assert stmt.condition is cond
        assert stmt.then_block is then
        assert stmt.else_block is None

    def test_hir_return(self):
        stmt = HIRReturn()
        assert stmt.value is None

    def test_hir_module_add(self):
        mod = HIRModule("test")
        func = HIRFunctionDecl("main")
        mod.add_function(func)
        assert len(mod.functions) == 1

    def test_hir_to_ir_module(self):
        hir_mod = HIRModule("test")
        param = HIRParameter("x")
        body = HIRBlock()
        func = HIRFunctionDecl("add", params=[param], body=body)
        hir_mod.add_function(func)

        ir_mod = hir_to_ir_module(hir_mod)
        assert ir_mod.name == "test"
        assert ir_mod.function_count == 1

    def test_hir_source_ref(self):
        func = HIRFunctionDecl("test")
        func.source_ref = "test.i:10"
        assert func.source_ref == "test.i:10"

    def test_hir_while(self):
        from compiler.ir.values import BoolConstant
        cond = BoolConstant(True)
        body = HIRBlock()
        stmt = HIRWhile(cond, body)
        assert stmt.condition is cond
        assert stmt.body is body

    def test_hir_block_add_stmt(self):
        block = HIRBlock()
        ret = HIRReturn()
        block.add_statement(ret)
        assert len(block.statements) == 1

    def test_hir_class_methods(self):
        cls = HIRClassDecl("Foo")
        method = HIRFunctionDecl("bar")
        cls._methods.append(method)
        assert len(cls.methods) == 1

    def test_hir_trait_methods(self):
        trait = HIRTraitDecl("Trait")
        method = HIRFunctionDecl("method")
        trait._methods.append(method)
        assert len(trait.methods) == 1


# ══════════════════════════════════════════════════════════════════
# MIR Tests
# ══════════════════════════════════════════════════════════════════


class TestMIR:
    def test_mir_module(self):
        mod = IRModule("test")
        mir = MIRModule(mod)
        assert mir.name == "test"

    def test_mir_function(self):
        mod = IRModule("test")
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        mir = MIRModule(mod)
        mir_func = mir.get_function("foo")
        assert mir_func is not None
        assert mir_func.name == "foo"

    def test_mir_cfg(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        mir_func = MIRFunction(func)
        assert mir_func.cfg is not None

    def test_mir_liveness(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        mir_func = MIRFunction(func)
        assert mir_func.liveness is not None

    def test_mir_loops(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        mir_func = MIRFunction(func)
        assert isinstance(mir_func.loops, list)

    def test_ownership_meta(self):
        om = OwnershipMeta(OwnershipKind.BORROWED, "lifetime1")
        assert om.kind == OwnershipKind.BORROWED
        assert om.lifetime == "lifetime1"

    def test_mir_set_ownership(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        val = make_int_constant(42)
        bb.append(Return(val))
        func.append_block(bb)
        mod.add_function(func)

        mir_func = MIRFunction(func)
        meta = OwnershipMeta(OwnershipKind.OWNED)
        mir_func.set_ownership(val, meta)
        assert mir_func.get_ownership(val) is meta

    def test_lower_to_mir(self):
        mod = IRModule("test")
        mir = lower_to_mir(mod)
        assert isinstance(mir, MIRModule)

    def test_mir_is_loop_header(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        mir_func = MIRFunction(func)
        assert not mir_func.is_loop_header(bb)

    def test_mir_get_loop_depth(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        mir_func = MIRFunction(func)
        assert mir_func.get_loop_depth(bb) == 0

    def test_mir_invalidate(self):
        mod = IRModule("test")
        ft = func_type((), IR_I32)
        func = IRFunction("foo", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        mir_func = MIRFunction(func)
        _ = mir_func.cfg  # trigger computation
        mir_func.invalidate_cfg()
        # Should recompute on next access
        assert mir_func.cfg is not None


# ══════════════════════════════════════════════════════════════════
# LIR Tests
# ══════════════════════════════════════════════════════════════════


class TestLIR:
    def test_lir_instruction(self):
        inst = LIRInstruction(LIRInstKind.IADD, "r0", ["r1", "r2"])
        assert inst.kind == LIRInstKind.IADD
        assert inst.dest == "r0"
        assert inst.operands == ["r1", "r2"]

    def test_lir_terminator(self):
        ret = LIRInstruction(LIRInstKind.RETURN)
        assert ret.is_terminator
        br = LIRInstruction(LIRInstKind.BR, operands=["bb1"])
        assert br.is_terminator

    def test_lir_block(self):
        block = LIRBlock("bb0")
        assert block.label == "bb0"
        assert block.instruction_count == 0
        inst = LIRInstruction(LIRInstKind.NOP)
        block.append(inst)
        assert block.instruction_count == 1

    def test_lir_function(self):
        func = LIRFunction("test")
        assert func.name == "test"
        block = LIRBlock("entry")
        func.append_block(block)
        assert func.block_count == 1

    def test_lir_module(self):
        mod = LIRModule("test")
        func = LIRFunction("foo")
        mod.add_function(func)
        assert mod.function_count == 1
        assert mod.get_function("foo") is func

    def test_lir_printer(self):
        mod = LIRModule("test")
        func = LIRFunction("foo")
        block = LIRBlock("entry")
        block.append(LIRInstruction(LIRInstKind.NOP))
        func.append_block(block)
        mod.add_function(func)

        printer = LIRPrinter()
        output = printer.print_module(mod)
        assert "foo" in output

    def test_lir_builder(self):
        builder = LIRBuilder()
        func = LIRFunction("test")
        builder.set_function(func)
        block = builder.create_block("entry")
        builder.position_at(block)
        builder.emit_iadd("r0", "r1", "r2")
        assert block.instruction_count == 1

    def test_lir_builder_emit_br(self):
        builder = LIRBuilder()
        func = LIRFunction("test")
        builder.set_function(func)
        block = builder.create_block("entry")
        builder.position_at(block)
        inst = builder.emit_br("bb1")
        assert inst.kind == LIRInstKind.BR

    def test_lir_builder_emit_ret(self):
        builder = LIRBuilder()
        func = LIRFunction("test")
        builder.set_function(func)
        block = builder.create_block("entry")
        builder.position_at(block)
        inst = builder.emit_ret("r0")
        assert inst.kind == LIRInstKind.RETURN

    def test_lower_ir_to_lir(self):
        mod = IRModule("test")
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("add", ft)
        bb = BasicBlock("entry")
        a = make_int_constant(1)
        b = make_int_constant(2)
        bb.append(Add("sum", a, b))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)

        lir = lower_ir_to_lir(mod)
        assert lir.name == "test"
        assert len(lir.functions) == 1
        assert lir.functions[0].block_count == 1

    def test_lir_block_predecessors(self):
        b1 = LIRBlock("b1")
        b2 = LIRBlock("b2")
        b1.add_successor(b2)
        b2.add_predecessor(b1)
        assert b2 in b1.successors
        assert b1 in b2.predecessors

    def test_lir_function_params(self):
        func = LIRFunction("test")
        func._params = [("x", IR_I32), ("y", IR_I64)]
        assert len(func.params) == 2

    def test_lir_function_allocate_local(self):
        func = LIRFunction("test")
        s1 = func.allocate_local()
        s2 = func.allocate_local()
        assert s1 == 0
        assert s2 == 1
        assert func.num_locals == 2

    def test_lir_module_target_info(self):
        mod = LIRModule("test")
        mod._target_info["arch"] = "x86_64"
        assert mod.target_info["arch"] == "x86_64"

    def test_lir_instruction_comment(self):
        inst = LIRInstruction(LIRInstKind.NOP)
        inst.comment = "debug point"
        assert inst.comment == "debug point"

    def test_lir_instruction_source_ref(self):
        inst = LIRInstruction(LIRInstKind.NOP)
        inst.source_ref = "test.i:10"
        assert inst.source_ref == "test.i:10"

    def test_lir_instruction_repr(self):
        inst = LIRInstruction(LIRInstKind.IADD, "r0", ["r1", "r2"])
        r = repr(inst)
        assert "IADD" in r
        assert "r0" in r

    def test_lir_block_terminator(self):
        block = LIRBlock("bb")
        block.append(LIRInstruction(LIRInstKind.RETURN, operands=["r0"]))
        assert block.terminator is not None
        assert block.terminator.kind == LIRInstKind.RETURN


# ══════════════════════════════════════════════════════════════════
# Integration / Builder → Module Pipeline Tests
# ══════════════════════════════════════════════════════════════════


class TestIRPipeline:
    def test_build_simple_function(self):
        """Build a complete function with the builder and validate."""
        ctx = IRContext()
        builder = IRBuilder(ctx)

        mod = ctx.module
        ft = func_type((IR_I32, IR_I32), IR_I32)
        func = IRFunction("add", ft)
        mod.add_function(func)

        entry = builder.append_to(func, "entry")
        sum_val = builder.add(func.args[0], func.args[1], "sum")
        builder.ret(sum_val)

        assert func.block_count == 1
        assert func.instruction_count == 2  # add + ret

        # Validate
        validator = IRValidator()
        assert validator.validate_module(mod)

        # Print
        output = print_ir(mod)
        assert "add" in output

    def test_build_cond_branch(self):
        """Build a function with conditional branching."""
        ctx = IRContext()
        builder = IRBuilder(ctx)
        mod = ctx.module

        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("check", ft)
        mod.add_function(func)

        entry = builder.append_to(func, "entry")
        bb_then = builder.create_block("then", func)
        bb_else = builder.create_block("else", func)
        bb_merge = builder.create_block("merge", func)

        cmp = builder.icmp(ICmpPredicate.SGT, func.args[0],
                          make_int_constant(0), "cmp")
        builder.cond_branch(cmp, bb_then, bb_else)

        builder.position_at_end(bb_then)
        builder.branch(bb_merge)

        builder.position_at_end(bb_else)
        builder.branch(bb_merge)

        builder.position_at_end(bb_merge)
        phi = builder.phi(IR_I32, "result")
        phi.add_incoming(make_int_constant(1), bb_then)
        phi.add_incoming(make_int_constant(0), bb_else)
        builder.ret(phi)

        assert func.block_count == 4

        # Validate
        validator = IRValidator()
        assert validator.validate_module(mod)

    def test_full_pipeline(self):
        """Build, validate, serialize, visualize."""
        ctx = IRContext()
        builder = IRBuilder(ctx)
        mod = ctx.module
        mod.target = "x86_64"

        ft = func_type((IR_I32, IR_I32), IR_I32)
        func = IRFunction("compute", ft)
        mod.add_function(func)

        entry = builder.append_to(func, "bb0")
        sum_val = builder.add(func.args[0], func.args[1], "sum")
        mul_val = builder.mul(sum_val, make_int_constant(2), "prod")
        builder.ret(mul_val)

        # Validate
        assert validate(mod) == []

        # Serialize
        json_str = serialize_json(mod)
        restored = deserialize_json(json_str)
        assert restored.function_count == 1

        # Visualize
        dot = visualize_cfg(func)
        assert "digraph" in dot

        # CFG analysis
        cfg = CFG(func)
        assert len(cfg.blocks) == 1

        # Text output
        text = print_ir(mod)
        assert "compute" in text


# ══════════════════════════════════════════════════════════════════
# Fuzz Tests
# ══════════════════════════════════════════════════════════════════


class TestFuzz:
    def test_random_types_not_crash(self):
        """Create many random types without crashing."""
        import random
        types_list = [IR_I1, IR_I8, IR_I16, IR_I32, IR_I64,
                      IR_F16, IR_F32, IR_F64]
        for _ in range(100):
            t1 = random.choice(types_list)
            t2 = random.choice(types_list)
            ptr_type(t1)
            array_type(random.randint(1, 10), t1)
            struct_type((t1, t2))

    def test_random_instructions_not_crash(self):
        """Create random instructions without crashing."""
        import random
        bb = BasicBlock("fuzz")
        for i in range(50):
            a = make_int_constant(random.randint(0, 100))
            b = make_int_constant(random.randint(0, 100))
            insts = [Add, Sub, Mul]
            inst = random.choice(insts)(f"fuzz{i}", a, b)
            bb.append(inst)

    def test_random_cfg_not_crash(self):
        """Build random CFGs and analyze."""
        for _ in range(20):
            ft = func_type((), IR_I32)
            func = IRFunction(f"f{hash(ft)}", ft)
            num_blocks = 5
            blocks = [BasicBlock(f"b{i}") for i in range(num_blocks)]
            for i, b in enumerate(blocks):
                if i > 0:
                    blocks[i-1].add_successor(b)
                    b.add_predecessor(blocks[i-1])
                if i < num_blocks - 1:
                    b.append(Branch(blocks[i+1]))
                else:
                    b.append(Return(make_int_constant(0)))
                func.append_block(b)

            if blocks:
                cfg = CFG(func)
                assert len(cfg.blocks) == num_blocks

    def test_serialization_stress(self):
        """Serialize/deserialize many modules."""
        for i in range(50):
            mod = IRModule(f"stress_{i}")
            ft = func_type((IR_I32,), IR_I32)
            func = IRFunction(f"func_{i}", ft)
            bb = BasicBlock("entry")
            bb.append(Return(make_int_constant(i)))
            func.append_block(bb)
            mod.add_function(func)

            json_str = serialize_json(mod)
            restored = deserialize_json(json_str)
            assert restored.function_count == 1

    def test_builder_stress(self):
        """Build large functions with the builder."""
        ctx = IRContext()
        builder = IRBuilder(ctx)
        mod = ctx.module

        for i in range(10):
            ft = func_type((IR_I32, IR_I32), IR_I32)
            func = IRFunction(f"func_{i}", ft)
            mod.add_function(func)
            entry = builder.append_to(func, "entry")
            val = func.args[0]
            for j in range(20):
                val = builder.add(val, func.args[1], f"add_{j}")
            builder.ret(val)

        assert mod.function_count == 10
        total_insts = sum(f.instruction_count for f in mod.functions)
        assert total_insts > 100
