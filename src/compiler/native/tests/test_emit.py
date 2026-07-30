from __future__ import annotations

import struct
import unittest

from compiler.ir.basic_block import BasicBlock
from compiler.ir.function import IRFunction
from compiler.ir.instructions import (
    Add,
    Alloca,
    Branch,
    Call,
    ICmp,
    ICmpPredicate,
    Load,
    Mul,
    Phi,
    Return,
    SDiv,
    SExt,
    Store,
    Sub,
    ZExt,
)
from compiler.ir.module import IRModule
from compiler.ir.types import (
    IR_I1,
    IR_I64,
    IR_VOID,
    IRFunctionType,
)
from compiler.ir.values import IntConstant
from compiler.native.emit.arm64 import SP, X0, X1, X2, ARM64Emitter
from compiler.native.emit.llvm import LLVMEmitter
from compiler.native.emit.x86_64 import R8, RAX, RBP, RBX, RCX, RDX, RSI, X86_64Emitter


def _make_i64_func(name: str) -> IRFunction:
    ft = IRFunctionType((), IR_VOID)
    return IRFunction(name, ft)


class TestLLVMEmitter(unittest.TestCase):
    def setUp(self) -> None:
        self.emitter = LLVMEmitter()

    def test_emit_empty_module(self) -> None:
        module = IRModule("test")
        result = self.emitter.emit_module(module)
        self.assertIn("test", result)

    def test_emit_simple_function(self) -> None:
        module = IRModule("test_mod")
        func = _make_i64_func("my_func")
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())
        module.add_function(func)

        result = self.emitter.emit_module(module)
        self.assertIn("define void @my_func", result)
        self.assertIn("entry:", result)
        self.assertIn("ret void", result)

    def test_emit_add(self) -> None:
        func = _make_i64_func("add_test")
        block = BasicBlock("entry")
        func.append_block(block)
        lhs = IntConstant(3, IR_I64)
        rhs = IntConstant(4, IR_I64)
        inst = Add("sum", lhs, rhs)
        block.append(inst)
        block.append(Return())
        module = IRModule("m")
        module.add_function(func)

        result = self.emitter.emit_module(module)
        self.assertIn("add", result)

    def test_emit_sub(self) -> None:
        func = _make_i64_func("sub_test")
        block = BasicBlock("entry")
        func.append_block(block)
        inst = Sub("diff", IntConstant(10, IR_I64), IntConstant(3, IR_I64))
        block.append(inst)
        block.append(Return())
        module = IRModule("m")
        module.add_function(func)

        result = self.emitter.emit_module(module)
        self.assertIn("sub", result)

    def test_emit_mul_sdiv(self) -> None:
        func = _make_i64_func("arith")
        block = BasicBlock("entry")
        func.append_block(block)
        a = Mul("p", IntConstant(6, IR_I64), IntConstant(7, IR_I64))
        b = SDiv("q", IntConstant(42, IR_I64), IntConstant(2, IR_I64))
        block.append(a)
        block.append(b)
        block.append(Return())
        module = IRModule("m")
        module.add_function(func)

        result = self.emitter.emit_module(module)
        self.assertIn("mul", result)
        self.assertIn("sdiv", result)

    def test_emit_return_with_value(self) -> None:
        func = IRFunction("ret_val", IRFunctionType((), IR_I64))
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return(IntConstant(42, IR_I64)))
        module = IRModule("m")
        module.add_function(func)

        result = self.emitter.emit_module(module)
        self.assertIn("ret i64 42", result)

    def test_emit_br(self) -> None:
        func = _make_i64_func("br_test")
        e = BasicBlock("entry")
        other = BasicBlock("other")
        func.append_block(e)
        func.append_block(other)
        e.append(Branch(other))
        other.append(Return())

        module = IRModule("m")
        module.add_function(func)
        result = self.emitter.emit_module(module)
        self.assertIn("br label", result)

    def test_emit_alloca(self) -> None:
        func = _make_i64_func("alloca_test")
        block = BasicBlock("entry")
        func.append_block(block)
        a = Alloca("ptr", IR_I64, alignment=8)
        block.append(a)
        block.append(Return())
        module = IRModule("m")
        module.add_function(func)

        result = self.emitter.emit_module(module)
        self.assertIn("alloca", result)

    def test_emit_load_store(self) -> None:
        func = _make_i64_func("loadstore")
        block = BasicBlock("entry")
        func.append_block(block)
        ptr = Alloca("p", IR_I64, alignment=8)
        block.append(ptr)
        st = Store(IntConstant(42, IR_I64), ptr, alignment=4)
        block.append(st)
        ld = Load("v", IR_I64, ptr, alignment=4)
        block.append(ld)
        block.append(Return())
        module = IRModule("m")
        module.add_function(func)

        result = self.emitter.emit_module(module)
        self.assertIn("load", result)
        self.assertIn("store", result)

    def test_emit_call(self) -> None:
        callee_type = IRFunctionType((IR_I64,), IR_I64)
        func = IRFunction("caller", IRFunctionType((), IR_I64))
        block = BasicBlock("entry")
        func.append_block(block)
        callee = IRFunction("callee", callee_type)
        call = Call("res", callee_type, callee, [IntConstant(7, IR_I64)])
        block.append(call)
        block.append(Return())
        module = IRModule("m")
        module.add_function(func)
        module.add_function(callee)

        result = self.emitter.emit_module(module)
        self.assertIn("call", result)

    def test_emit_icmp(self) -> None:
        func = _make_i64_func("cmp_test")
        block = BasicBlock("entry")
        func.append_block(block)
        cmp_inst = ICmp("c", ICmpPredicate.SGT, IntConstant(5, IR_I64), IntConstant(3, IR_I64))
        block.append(cmp_inst)
        block.append(Return())
        module = IRModule("m")
        module.add_function(func)

        result = self.emitter.emit_module(module)
        self.assertIn("icmp sgt", result)

    def test_emit_cast(self) -> None:
        func = _make_i64_func("cast_test")
        block = BasicBlock("entry")
        func.append_block(block)
        z = ZExt("z", IntConstant(1, IR_I1), IR_I64)
        s = SExt("s", IntConstant(1, IR_I1), IR_I64)
        block.append(z)
        block.append(s)
        block.append(Return())
        module = IRModule("m")
        module.add_function(func)

        result = self.emitter.emit_module(module)
        self.assertIn("zext", result)
        self.assertIn("sext", result)

    def test_emit_phi(self) -> None:
        func = _make_i64_func("phi_test")
        e = BasicBlock("entry")
        loop = BasicBlock("loop")
        func.append_block(e)
        func.append_block(loop)
        p = Phi("p", IR_I64, [(IntConstant(0, IR_I64), e), (IntConstant(1, IR_I64), loop)])
        loop.append(p)
        loop.append(Return())
        module = IRModule("m")
        module.add_function(func)

        result = self.emitter.emit_module(module)
        self.assertIn("phi", result)

    def test_emit_target_triple(self) -> None:
        module = IRModule("triple_test")
        module.target = "x86_64-unknown-linux-gnu"
        result = self.emitter.emit_module(module)
        self.assertIn("target triple", result)
        self.assertIn("x86_64-unknown-linux-gnu", result)


class TestX86_64Emitter(unittest.TestCase):  # noqa: N801
    def setUp(self) -> None:
        self.emitter = X86_64Emitter()

    def test_nop(self) -> None:
        result = self.emitter.emit_nop()
        self.assertEqual(result, b"\x90")

    def test_int3(self) -> None:
        result = self.emitter.emit_int3()
        self.assertEqual(result, b"\xcc")

    def test_ret(self) -> None:
        result = self.emitter.emit_ret()
        self.assertEqual(result, b"\xc3")

    def test_mov_reg_reg(self) -> None:
        result = self.emitter.emit_mov(RAX, RBX)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 0x48)
        self.assertEqual(result[1], 0x89)
        self.assertEqual(result[2], 0xD8)

    def test_mov_ri(self) -> None:
        result = self.emitter.emit_mov_ri(RAX, 42)
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0], 0x48)
        self.assertEqual(result[1], 0xB8 | RAX)
        self.assertEqual(struct.unpack_from("<q", result, 2)[0], 42)

    def test_mov_ri32(self) -> None:
        result = self.emitter.emit_mov_ri32(RBX, 100)
        self.assertEqual(len(result), 7)

    def test_add_reg_reg(self) -> None:
        result = self.emitter.emit_add(RAX, RCX)
        self.assertEqual(result[0], 0x48)
        self.assertEqual(result[1], 0x01)
        self.assertEqual(result[2], 0xC8)

    def test_sub_reg_reg(self) -> None:
        result = self.emitter.emit_sub(RAX, RDX)
        self.assertEqual(result[0], 0x48)
        self.assertEqual(result[1], 0x29)
        self.assertEqual(result[2], 0xD0)

    def test_xor_reg_reg(self) -> None:
        result = self.emitter.emit_xor(RAX, RAX)
        self.assertEqual(result[2], 0xC0)

    def test_imul(self) -> None:
        result = self.emitter.emit_imul(RAX, RBX)
        self.assertEqual(len(result), 4)

    def test_cmp(self) -> None:
        result = self.emitter.emit_cmp(RAX, RSI)
        self.assertEqual(result[1], 0x39)
        self.assertEqual(result[2], 0xF0)

    def test_test(self) -> None:
        result = self.emitter.emit_test(RAX, RAX)
        self.assertEqual(result[1], 0x85)
        self.assertEqual(result[2], 0xC0)

    def test_neg_not(self) -> None:
        neg_result = self.emitter.emit_neg(RAX)
        self.assertEqual(len(neg_result), 3)
        not_result = self.emitter.emit_not(RAX)
        self.assertEqual(len(not_result), 3)

    def test_shifts(self) -> None:
        shl = self.emitter.emit_shl(RAX, 3)
        self.assertEqual(len(shl), 4)
        shr = self.emitter.emit_shr(RAX, 1)
        self.assertEqual(len(shr), 4)
        sar = self.emitter.emit_sar(RAX, 2)
        self.assertEqual(len(sar), 4)

    def test_push_pop(self) -> None:
        push = self.emitter.emit_push(RAX)
        self.assertEqual(push[0], 0x50 | RAX)
        pop = self.emitter.emit_pop(RAX)
        self.assertEqual(pop[0], 0x58 | RAX)

    def test_push_pop_high(self) -> None:
        push = self.emitter.emit_push(R8)
        self.assertEqual(len(push), 2)
        pop = self.emitter.emit_pop(R8)
        self.assertEqual(len(pop), 2)

    def test_call_reg(self) -> None:
        result = self.emitter.emit_call(RAX)
        self.assertEqual(result[0], 0xFF)
        self.assertEqual(result[1], 0xD0)

    def test_jmp_rel32(self) -> None:
        result = self.emitter.emit_jmp(0x1000)
        self.assertEqual(result[0], 0xE9)
        self.assertEqual(len(result), 5)

    def test_jcc(self) -> None:
        je = self.emitter.emit_je(0x20)
        self.assertIn(je[0], (0x74, 0x0F))
        jne = self.emitter.emit_jne(-0x10)
        self.assertIn(jne[0], (0x75, 0x0F))

    def test_cdq_idiv(self) -> None:
        cdq = self.emitter.emit_cdq()
        self.assertEqual(cdq, b"\x48\x99")
        idiv = self.emitter.emit_idiv(RBX)
        self.assertEqual(len(idiv), 3)

    def test_align(self) -> None:
        self.emitter.emit_nop()
        self.emitter.emit_align(16)
        self.assertEqual(self.emitter.size % 16, 0)

    def test_label_resolve(self) -> None:
        self.emitter.emit_jmp_to_label("target")
        self.emitter.emit_label("target")
        self.emitter.emit_nop()
        result = self.emitter.resolve_labels()
        self.assertGreater(len(result), 0)

    def test_mov_memory_abs(self) -> None:
        from compiler.native.emit.x86_64 import abs_addr
        result = self.emitter.emit_mov_rm(RAX, abs_addr(0x1000))
        self.assertGreater(len(result), 0)

    def test_mov_memory_base_disp(self) -> None:
        from compiler.native.emit.x86_64 import reg_addr
        result = self.emitter.emit_mov_mr(reg_addr(RBP, -8), RAX)
        self.assertGreater(len(result), 0)

    def test_sse_movsd(self) -> None:
        from compiler.native.emit.x86_64 import XMM0, XMM1
        result = self.emitter.emit_movsd(XMM0, XMM1)
        self.assertEqual(len(result), 4)

    def test_sse_addsd(self) -> None:
        from compiler.native.emit.x86_64 import XMM0, XMM1
        result = self.emitter.emit_addsd(XMM0, XMM1)
        self.assertEqual(len(result), 4)

    def test_sse_cvtsi2sd(self) -> None:
        from compiler.native.emit.x86_64 import XMM0
        result = self.emitter.emit_cvtsi2sd(XMM0, RAX)
        self.assertEqual(len(result), 5)

    def test_sse_ucomisd(self) -> None:
        from compiler.native.emit.x86_64 import XMM0, XMM1
        result = self.emitter.emit_ucomisd(XMM0, XMM1)
        self.assertEqual(len(result), 4)

    def test_get_bytes(self) -> None:
        self.emitter.emit_nop()
        self.emitter.emit_ret()
        data = self.emitter.get_bytes()
        self.assertEqual(data, b"\x90\xc3")

    def test_buffer_property(self) -> None:
        self.emitter.emit_nop()
        self.assertIsInstance(self.emitter.buffer, bytearray)
        self.assertEqual(len(self.emitter.buffer), 1)


class TestARM64Emitter(unittest.TestCase):
    def setUp(self) -> None:
        self.emitter = ARM64Emitter()

    def test_nop(self) -> None:
        result = self.emitter.emit_nop()
        self.assertEqual(result, b"\x1f\x20\x03\xd5")

    def test_ret(self) -> None:
        result = self.emitter.emit_ret()
        self.assertEqual(result, b"\xc0\x03\x5f\xd6")

    def test_mov(self) -> None:
        result = self.emitter.emit_mov(X0, X1)
        self.assertEqual(len(result), 4)

    def test_add(self) -> None:
        result = self.emitter.emit_add(X0, X1, X2)
        insn = struct.unpack_from("<I", result, 0)[0]
        self.assertEqual((insn >> 24) & 0xFF, 0x8B)

    def test_sub(self) -> None:
        result = self.emitter.emit_sub(X0, X1, X2)
        insn = struct.unpack_from("<I", result, 0)[0]
        self.assertEqual((insn >> 24) & 0xFF, 0xCB)

    def test_mul(self) -> None:
        result = self.emitter.emit_mul(X0, X1, X2)
        self.assertEqual(len(result), 4)

    def test_sdiv(self) -> None:
        result = self.emitter.emit_sdiv(X0, X1, X2)
        self.assertEqual(len(result), 4)

    def test_add_imm(self) -> None:
        result = self.emitter.emit_add_imm(X0, X1, 0xFF)
        self.assertEqual(len(result), 4)

    def test_sub_imm(self) -> None:
        result = self.emitter.emit_sub_imm(X0, X1, 0x10)
        self.assertEqual(len(result), 4)

    def test_add_imm_out_of_range(self) -> None:
        with self.assertRaises(ValueError):
            self.emitter.emit_add_imm(X0, X1, 0x1000)

    def test_mov_imm(self) -> None:
        result = self.emitter.emit_mov_imm(X0, 0x42)
        self.assertEqual(len(result), 4)

    def test_movk(self) -> None:
        result = self.emitter.emit_movk(X0, 0x1234, shift=16)
        self.assertEqual(len(result), 4)

    def test_movk_invalid_shift(self) -> None:
        with self.assertRaises(ValueError):
            self.emitter.emit_movk(X0, 0x42, shift=8)

    def test_cmp(self) -> None:
        result = self.emitter.emit_cmp(X0, X1)
        self.assertEqual(len(result), 4)

    def test_cmp_imm(self) -> None:
        result = self.emitter.emit_cmp_imm(X0, 0x20)
        self.assertEqual(len(result), 4)

    def test_ldr_str(self) -> None:
        result = self.emitter.emit_ldr(X0, (X1, 16))
        self.assertEqual(len(result), 4)
        result = self.emitter.emit_str((X1, 32), X0)
        self.assertEqual(len(result), 4)

    def test_ldr_str_bad_offset(self) -> None:
        with self.assertRaises(ValueError):
            self.emitter.emit_ldr(X0, (X1, 7))
        with self.assertRaises(ValueError):
            self.emitter.emit_str((X1, 7), X0)

    def test_stp_ldp(self) -> None:
        result = self.emitter.emit_stp(X0, X1, (SP, -16))
        self.assertEqual(len(result), 4)
        result = self.emitter.emit_ldp(X0, X1, (SP, 0))
        self.assertEqual(len(result), 4)

    def test_b_bl(self) -> None:
        result = self.emitter.emit_b("label")
        self.assertEqual(len(result), 4)
        result = self.emitter.emit_bl("label")
        self.assertEqual(len(result), 4)

    def test_br_blr(self) -> None:
        result = self.emitter.emit_br(X0)
        self.assertEqual(len(result), 4)
        result = self.emitter.emit_blr(X0)
        self.assertEqual(len(result), 4)

    def test_bcond(self) -> None:
        result = self.emitter.emit_beq("label")
        self.assertEqual(len(result), 4)
        result = self.emitter.emit_bne("label")
        self.assertEqual(len(result), 4)

    def test_cbz_cbnz(self) -> None:
        result = self.emitter.emit_cbz(X0, "label")
        self.assertEqual(len(result), 4)
        result = self.emitter.emit_cbnz(X0, "label")
        self.assertEqual(len(result), 4)

    def test_brk_hlt(self) -> None:
        result = self.emitter.emit_brk(0)
        self.assertEqual(len(result), 4)
        result = self.emitter.emit_hlt(0)
        self.assertEqual(len(result), 4)

    def test_adr_adrp(self) -> None:
        result = self.emitter.emit_adr(X0, "label")
        self.assertEqual(len(result), 4)
        result = self.emitter.emit_adrp(X0, "label")
        self.assertEqual(len(result), 4)

    def test_align(self) -> None:
        self.emitter.emit_nop()
        self.emitter.emit_align(16)
        self.assertEqual(self.emitter.size % 16, 0)

    def test_label_resolve(self) -> None:
        self.emitter.emit_b("target")
        self.emitter.emit_label("target")
        self.emitter.emit_nop()
        result = self.emitter.resolve_labels()
        self.assertGreater(len(result), 0)

    def test_orr_and_eor(self) -> None:
        self.emitter.emit_orr(X0, X1, X2)
        self.emitter.emit_and(X0, X1, X2)
        self.emitter.emit_eor(X0, X1, X2)
        self.assertEqual(self.emitter.size, 12)
