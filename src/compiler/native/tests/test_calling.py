from __future__ import annotations

import unittest

from compiler.ir.types import (
    IR_F32,
    IR_F64,
    IR_I32,
    IR_I64,
    IR_PTR,
    IR_VOID,
    IRFunctionType,
)
from compiler.native.calling.convention import (
    ArgLocation,
    ARM64Convention,
    MicrosoftConvention,
    SystemVConvention,
    select_convention,
)
from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind


class TestSystemVConvention(unittest.TestCase):
    def setUp(self) -> None:
        self.conv = SystemVConvention()

    def test_return_register_int(self) -> None:
        self.assertEqual(self.conv.return_register(IR_I64), "rax")

    def test_return_register_float(self) -> None:
        self.assertEqual(self.conv.return_register(IR_F64), "xmm0")

    def test_arg_registers(self) -> None:
        regs = self.conv.arg_registers()
        self.assertIn("rdi", regs)
        self.assertIn("rsi", regs)
        self.assertIn("xmm0", regs)
        self.assertIn("xmm7", regs)

    def test_assign_args_empty(self) -> None:
        ft = IRFunctionType((), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(len(locs), 0)

    def test_assign_args_integer(self) -> None:
        ft = IRFunctionType((IR_I64, IR_I32), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(len(locs), 2)
        self.assertEqual(locs[0].register, "rdi")
        self.assertEqual(locs[1].register, "rsi")

    def test_assign_args_float(self) -> None:
        ft = IRFunctionType((IR_F64, IR_F32), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(len(locs), 2)
        self.assertEqual(locs[0].float_reg, "xmm0")
        self.assertEqual(locs[1].float_reg, "xmm1")

    def test_assign_args_mixed(self) -> None:
        ft = IRFunctionType((IR_I64, IR_F64), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(locs[0].register, "rdi")
        self.assertEqual(locs[1].float_reg, "xmm0")

    def test_assign_args_spill_integer(self) -> None:
        ft = IRFunctionType(tuple(IR_I64 for _ in range(10)), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(locs[0].register, "rdi")
        self.assertEqual(locs[5].register, "r9")
        self.assertTrue(locs[6].is_stack)
        self.assertTrue(locs[9].is_stack)

    def test_assign_args_spill_float(self) -> None:
        ft = IRFunctionType(tuple(IR_F64 for _ in range(10)), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(locs[0].float_reg, "xmm0")
        self.assertEqual(locs[7].float_reg, "xmm7")
        self.assertTrue(locs[8].is_stack)

    def test_caller_saved(self) -> None:
        regs = self.conv.caller_saved_registers()
        self.assertIn("rax", regs)
        self.assertIn("rcx", regs)
        self.assertIn("xmm15", regs)

    def test_callee_saved(self) -> None:
        regs = self.conv.callee_saved_registers()
        self.assertIn("rbx", regs)
        self.assertIn("rbp", regs)
        self.assertIn("r12", regs)

    def test_shadow_space_zero(self) -> None:
        self.assertEqual(self.conv.shadow_space_bytes(), 0)

    def test_stack_alignment(self) -> None:
        self.assertEqual(self.conv.stack_alignment(), 16)


class TestMicrosoftConvention(unittest.TestCase):
    def setUp(self) -> None:
        self.conv = MicrosoftConvention()

    def test_return_register_int(self) -> None:
        self.assertEqual(self.conv.return_register(IR_I64), "rax")

    def test_return_register_float(self) -> None:
        self.assertEqual(self.conv.return_register(IR_F64), "xmm0")

    def test_arg_registers(self) -> None:
        regs = self.conv.arg_registers()
        self.assertIn("rcx", regs)
        self.assertIn("rdx", regs)
        self.assertIn("r8", regs)
        self.assertIn("r9", regs)
        self.assertNotIn("rdi", regs)
        self.assertIn("xmm0", regs)

    def test_assign_args_integer(self) -> None:
        ft = IRFunctionType((IR_I64, IR_I32), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(locs[0].register, "rcx")
        self.assertEqual(locs[1].register, "rdx")

    def test_assign_args_spill_integer(self) -> None:
        ft = IRFunctionType(tuple(IR_I64 for _ in range(6)), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(locs[0].register, "rcx")
        self.assertEqual(locs[3].register, "r9")
        self.assertTrue(locs[4].is_stack)
        self.assertEqual(locs[4].stack_offset, 32)

    def test_assign_args_float_spill(self) -> None:
        ft = IRFunctionType(tuple(IR_F64 for _ in range(6)), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(locs[0].float_reg, "xmm0")
        self.assertEqual(locs[3].float_reg, "xmm3")
        self.assertTrue(locs[4].is_stack)
        self.assertEqual(locs[4].stack_offset, 32)

    def test_assign_args_mixed(self) -> None:
        ft = IRFunctionType((IR_I64, IR_F64, IR_I32), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(locs[0].register, "rcx")
        self.assertEqual(locs[1].float_reg, "xmm0")
        self.assertEqual(locs[2].register, "rdx")

    def test_caller_saved(self) -> None:
        regs = self.conv.caller_saved_registers()
        self.assertIn("rax", regs)
        self.assertIn("rcx", regs)
        self.assertIn("r11", regs)
        self.assertIn("xmm15", regs)

    def test_callee_saved(self) -> None:
        regs = self.conv.callee_saved_registers()
        self.assertIn("rbx", regs)
        self.assertIn("rdi", regs)
        self.assertIn("rsi", regs)

    def test_shadow_space_32(self) -> None:
        self.assertEqual(self.conv.shadow_space_bytes(), 32)

    def test_stack_alignment(self) -> None:
        self.assertEqual(self.conv.stack_alignment(), 16)


class TestARM64Convention(unittest.TestCase):
    def setUp(self) -> None:
        self.conv = ARM64Convention()

    def test_return_register_int(self) -> None:
        self.assertEqual(self.conv.return_register(IR_I64), "x0")

    def test_return_register_float(self) -> None:
        self.assertEqual(self.conv.return_register(IR_F64), "v0")

    def test_arg_registers(self) -> None:
        regs = self.conv.arg_registers()
        for i in range(8):
            self.assertIn(f"x{i}", regs)
            self.assertIn(f"v{i}", regs)
        self.assertNotIn("x8", regs)

    def test_assign_args_integer(self) -> None:
        ft = IRFunctionType((IR_I64, IR_I32, IR_I64), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(locs[0].register, "x0")
        self.assertEqual(locs[1].register, "x1")
        self.assertEqual(locs[2].register, "x2")

    def test_assign_args_float(self) -> None:
        ft = IRFunctionType((IR_F64, IR_F32, IR_F64), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(locs[0].float_reg, "v0")
        self.assertEqual(locs[1].float_reg, "v1")
        self.assertEqual(locs[2].float_reg, "v2")

    def test_assign_args_spill(self) -> None:
        ft = IRFunctionType(tuple(IR_I64 for _ in range(10)), IR_VOID)
        locs = self.conv.assign_args(ft)
        self.assertEqual(locs[0].register, "x0")
        self.assertEqual(locs[7].register, "x7")
        self.assertTrue(locs[8].is_stack)

    def test_caller_saved(self) -> None:
        regs = self.conv.caller_saved_registers()
        self.assertIn("x0", regs)
        self.assertIn("x18", regs)
        self.assertNotIn("x19", regs)

    def test_callee_saved(self) -> None:
        regs = self.conv.callee_saved_registers()
        self.assertIn("x19", regs)
        self.assertIn("x29", regs)
        self.assertNotIn("x18", regs)

    def test_shadow_space_zero(self) -> None:
        self.assertEqual(self.conv.shadow_space_bytes(), 0)

    def test_stack_alignment(self) -> None:
        self.assertEqual(self.conv.stack_alignment(), 16)


class TestArgLocation(unittest.TestCase):
    def test_register(self) -> None:
        loc = ArgLocation(register="rax")
        self.assertTrue(loc.is_register)
        self.assertFalse(loc.is_stack)

    def test_float_reg(self) -> None:
        loc = ArgLocation(float_reg="xmm0")
        self.assertTrue(loc.is_register)

    def test_stack(self) -> None:
        loc = ArgLocation(stack_offset=16)
        self.assertTrue(loc.is_stack)
        self.assertFalse(loc.is_register)


class TestSelectConvention(unittest.TestCase):
    def test_systemv_linux(self) -> None:
        target = TargetDescription(kind=TargetKind.X86_64, triple="x86_64-unknown-linux-gnu")
        conv = select_convention(target)
        self.assertIsInstance(conv, SystemVConvention)

    def test_systemv_macos(self) -> None:
        target = TargetDescription(kind=TargetKind.X86_64, triple="x86_64-apple-darwin")
        conv = select_convention(target)
        self.assertIsInstance(conv, SystemVConvention)

    def test_microsoft_windows(self) -> None:
        target = TargetDescription(kind=TargetKind.X86_64, triple="x86_64-pc-windows-msvc")
        conv = select_convention(target)
        self.assertIsInstance(conv, MicrosoftConvention)

    def test_arm64(self) -> None:
        target = TargetDescription(kind=TargetKind.ARM64, triple="aarch64-unknown-linux-gnu")
        conv = select_convention(target)
        self.assertIsInstance(conv, ARM64Convention)


class TestConventionHelpers(unittest.TestCase):
    def test_is_float_type(self) -> None:
        conv = SystemVConvention()
        self.assertTrue(conv.is_float_type(IR_F64))
        self.assertTrue(conv.is_float_type(IR_F32))
        self.assertFalse(conv.is_float_type(IR_I64))
        self.assertFalse(conv.is_float_type(IR_PTR))

    def test_is_integer_or_pointer(self) -> None:
        conv = SystemVConvention()
        self.assertTrue(conv.is_integer_or_pointer(IR_I64))
        self.assertTrue(conv.is_integer_or_pointer(IR_I32))
        self.assertTrue(conv.is_integer_or_pointer(IR_PTR))
        self.assertFalse(conv.is_integer_or_pointer(IR_F64))

    def test_type_width(self) -> None:
        conv = SystemVConvention()
        self.assertEqual(conv.type_width(IR_I64), 64)
        self.assertEqual(conv.type_width(IR_I32), 32)
        self.assertEqual(conv.type_width(IR_F64), 64)
        self.assertEqual(conv.type_width(IR_PTR), 64)
